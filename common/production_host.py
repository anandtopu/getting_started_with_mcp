"""Bounded connections, reviewed catalogs and interactive Tasks for Lumen Chat v4."""

import asyncio
import hashlib
import json
import os
import re
import sys
from contextlib import asynccontextmanager
from copy import deepcopy
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

import anyio
import httpx2 as httpx
from dotenv import dotenv_values
from jsonschema import Draft202012Validator, ValidationError
from mcp import Client, StdioServerParameters
from mcp.client.streamable_http import streamable_http_client
from mcp_types import CallToolResult, InputRequiredResult
from pydantic import BaseModel, ConfigDict, Field

from common.config import ROOT
from common.connections import SERVERS, discover
from common.extensions import APP_URI
from common.host import Host
from common.input_support import decline_unhandled_input
from common.report_tasks import TaskHandle, TasksClient, task_request
from common.schemas import portable_schema
from common.tool_formats import ToolReply

PROFILES = {**SERVERS, "gateway": "16_composition/python/use_case/server.py"}
# Retry safety is local policy; untrusted tool annotations cannot grant it.
SAFE_READS = {
    "notes": {"search_notes"},
    "wiki": {"find_page"},
    "gateway": {"workflow__triage_week", "workflow__draft_status", "analytics_dashboard"},
}
TRANSPORT_ERRORS = (
    TimeoutError,
    ConnectionError,
    OSError,
    anyio.EndOfStream,
    anyio.BrokenResourceError,
    anyio.ClosedResourceError,
)


class ServerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    alias: str = Field(pattern=r"^[a-z][a-z0-9_]{0,15}$")
    profile: str
    mode: Literal["auto", "legacy"] = "auto"
    url: str | None = None
    token_env: str | None = Field(default=None, pattern=r"^[A-Z][A-Z0-9_]{0,63}$")


class HostConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    servers: list[ServerConfig] = Field(min_length=1, max_length=5)


def load_host_config(path: Path):
    if path.stat().st_size > 16000:
        raise ValueError("Host configuration exceeds 16000 bytes.")
    value = HostConfig.model_validate_json(path.read_text())
    aliases = [server.alias for server in value.servers]
    if len(set(aliases)) != len(aliases) or any(s.profile not in PROFILES for s in value.servers):
        raise ValueError("Use unique aliases and reviewed built-in server profiles.")
    for server in value.servers:
        if server.url:
            from common.deployment import public_url

            public_url(server.url)
            if urlsplit(server.url).path != "/mcp":
                raise ValueError("Configured MCP endpoints must use /mcp.")
        elif server.token_env:
            raise ValueError("A bearer token is only valid for a configured HTTP server.")
    return value


def fingerprint(tool):
    value = tool.model_dump(mode="json", by_alias=True, exclude_none=True)
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


class Connection:
    """One owner task enters/exits the SDK context; requests arrive through a queue."""

    def __init__(self, config: ServerConfig, emit, factory=None):
        self.config, self.emit, self.factory = config, emit, factory
        self.queue = asyncio.Queue(maxsize=16)
        self.worker = None
        self.generation = 0
        self.info = {}

    def client(self):
        if self.factory:
            return self.factory()
        if self.config.url:
            return self.http_client()
        return Client(
            StdioServerParameters(
                command=sys.executable,
                args=[str(ROOT / "modules" / PROFILES[self.config.profile])],
                cwd=str(ROOT),
            ),
            mode=self.config.mode,
            extensions=[TasksClient()] if self.config.mode != "legacy" else [],
            elicitation_callback=decline_unhandled_input,
            read_timeout_seconds=12,
        )

    @asynccontextmanager
    async def http_client(self):
        values = {**dotenv_values(ROOT / ".env"), **os.environ}
        token = values.get(self.config.token_env or "")
        if self.config.token_env and not token:
            raise ValueError("Configure the remote token on the host first.")
        headers = {"Authorization": "Bearer " + token} if token else {}
        async with httpx.AsyncClient(headers=headers, timeout=12, follow_redirects=False) as http:
            async with Client(
                streamable_http_client(self.config.url, http_client=http),
                mode=self.config.mode,
                read_timeout_seconds=12,
                extensions=[TasksClient()] if self.config.mode != "legacy" else [],
                elicitation_callback=decline_unhandled_input,
            ) as client:
                yield client

    async def start(self, timeout=20):
        self.ready = asyncio.get_running_loop().create_future()
        self.worker = asyncio.create_task(self._own_connection())
        try:
            async with asyncio.timeout(timeout):
                await self.ready
        except BaseException:
            # The caller has not acquired ownership yet, so it cannot close us.
            await self.close()
            raise
        return self

    async def _own_connection(self):
        action = None
        try:
            async with self.client() as client:
                if client.protocol_version.startswith("2026"):
                    await discover(client)
                self.generation += 1
                self.info = {
                    "alias": self.config.alias,
                    "profile": self.config.profile,
                    "protocol": client.protocol_version,
                    "generation": self.generation,
                    "tools": client.server_capabilities.tools is not None,
                    "extensions": list((client.server_capabilities.extensions or {}).keys()),
                }
                self.emit("connection", self.info)
                self.ready.set_result(None)
                while True:
                    callback, response = await self.queue.get()
                    if response.cancelled():
                        continue
                    action = asyncio.create_task(callback(client))
                    response.add_done_callback(
                        lambda future, task=action: task.cancel() if future.cancelled() else None
                    )
                    try:
                        result = await action
                        if not response.done():
                            response.set_result(result)
                    except asyncio.CancelledError:
                        if not response.done():
                            response.cancel()
                        if asyncio.current_task().cancelling():
                            raise
                    except Exception as exc:
                        if not response.done():
                            response.set_exception(exc)
        except BaseException as exc:
            if not self.ready.done():
                self.ready.set_exception(exc)
            if not isinstance(exc, asyncio.CancelledError):
                self.emit(
                    "connection_error",
                    {"alias": self.config.alias, "message": "Connection unavailable."},
                )
        finally:
            if action and not action.done():
                action.cancel()
                await asyncio.gather(action, return_exceptions=True)
            while not self.queue.empty():
                _, response = self.queue.get_nowait()
                if not response.done():
                    response.set_exception(ConnectionError("Connection closed."))

    async def close(self):
        if self.worker:
            self.worker.cancel()
            await asyncio.gather(self.worker, return_exceptions=True)
            self.worker = None

    async def restart(self):
        await self.close()
        await self.start()

    async def invoke(self, action, timeout=15):
        if self.worker is None or self.worker.done():
            raise ConnectionError("Server is disconnected; reconnect before sending a new request.")
        response = asyncio.get_running_loop().create_future()
        async with asyncio.timeout(timeout):
            await self.queue.put((action, response))
            return await response

    async def tools(self):
        async def collect(client):
            tools, cursor, seen = [], None, set()
            for _ in range(20):
                page = await client.list_tools(cursor=cursor, cache_mode="refresh")
                tools.extend(page.tools)
                cursor = page.next_cursor
                if cursor is None:
                    if len({t.name for t in tools}) != len(tools):
                        raise ValueError("Duplicate tools in catalog.")
                    return tools
                if cursor in seen:
                    raise ValueError("Repeated catalog cursor.")
                seen.add(cursor)
            raise ValueError("Catalog exceeds page budget.")

        return await self.invoke(collect)

    async def checked_call(self, tool, arguments, **kwargs):
        async def check():
            fresh = next((t for t in await self.tools() if t.name == tool.name), None)
            if fresh is None or fingerprint(fresh) != fingerprint(tool):
                raise PermissionError(
                    "Tool changed after review. Start again and review its new definition."
                )

        await check()
        try:
            return await self.invoke(
                lambda c: c.session.call_tool(
                    tool.name, arguments, allow_claimed=True, allow_input_required=True, **kwargs
                )
            )
        except TRANSPORT_ERRORS:
            if tool.name not in SAFE_READS.get(self.config.profile, set()):
                raise RuntimeError("Outcome unknown; this operation was not retried.") from None
            self.emit(
                "reconnect", {"alias": self.config.alias, "message": "Retrying one reviewed read."}
            )
            await self.restart()
            await check()
            return await self.invoke(
                lambda c: c.session.call_tool(
                    tool.name, arguments, allow_claimed=True, allow_input_required=True, **kwargs
                )
            )

    async def task(self, method, task_id, **kwargs):
        return await self.invoke(lambda c: task_request(c.session, method, task_id, **kwargs))


class ProductionHost(Host):
    def __init__(self, clients, approve, ask, emit, show_app):
        super().__init__(clients, approve)
        self.ask, self.emit, self.show_app = ask, emit, show_app

    async def discover(self):
        self.routes.clear()
        self.tools.clear()
        for alias, connection in self.clients.items():
            if not connection.info.get("tools"):
                continue
            for tool in await connection.tools():
                name = alias + "__" + tool.name
                if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", name) or name in self.routes:
                    raise ValueError("Unsafe or colliding tool name.")
                schema = portable_schema(tool.input_schema)
                schema.get("properties", {}).pop("confirmed", None)
                schema["required"] = [k for k in schema.get("required", []) if k != "confirmed"]
                schema["additionalProperties"] = False
                self.routes[name] = (connection, tool, schema)
                self.tools.append(
                    {"name": name, "description": tool.description or name, "inputSchema": schema}
                )
        if not self.tools:
            raise RuntimeError("No tool-capable server is configured.")

    async def execute(self, call):
        route = self.routes.get(call.name)
        if route is None:
            return ToolReply(call, "Unknown tool; choose from the current catalog.", True)
        connection, tool, schema = route
        try:
            Draft202012Validator(schema).validate(call.arguments)
        except ValidationError:
            return ToolReply(call, "Invalid arguments; use the displayed schema.", True)
        arguments = deepcopy(call.arguments)
        allowed = await self.approve(
            call.name,
            {
                "arguments": arguments,
                "description": tool.description,
                "schema": schema,
                "definition_hash": fingerprint(tool),
                "server": connection.info,
            },
        )
        if not allowed:
            self.emit("denied", {"tool": call.name})
            return ToolReply(call, "User denied the call. Do not retry.", True)
        if "confirmed" in tool.input_schema.get("properties", {}):
            arguments["confirmed"] = True
        try:
            result = await connection.checked_call(tool, arguments)
            if isinstance(result, TaskHandle):
                result = await self.resolve_task(connection, result)
            for _ in range(3):
                if not isinstance(result, InputRequiredResult):
                    break
                answers = {}
                for key, request in (result.input_requests or {}).items():
                    if request.method != "elicitation/create":
                        raise ValueError("Only human elicitation is supported.")
                    answers[key] = await self.ask(
                        request.params.model_dump(mode="json", by_alias=True)
                    )
                result = await connection.checked_call(
                    tool, arguments, input_responses=answers, request_state=result.request_state
                )
            if isinstance(result, InputRequiredResult):
                raise RuntimeError("Input retry limit reached.")
            result = CallToolResult.model_validate(result)
            payload = result.model_dump(mode="json", by_alias=True, exclude_none=True)
            text = json.dumps(payload, ensure_ascii=False)
            if len(text) > 16000:
                raise ValueError("Result too large; request less data.")
            self.emit("tool_result", {"tool": call.name, "result": payload})
            if (
                not result.is_error
                and (tool.meta or {}).get("ui", {}).get("resourceUri") == APP_URI
            ):
                resource = await connection.invoke(lambda c: c.read_resource(APP_URI))
                content = resource.contents[0]
                if (
                    content.mime_type != "text/html;profile=mcp-app"
                    or len(content.text) > 1_000_000
                ):
                    raise ValueError("Unsupported App resource.")
                self.show_app(connection, tool, content.text, payload)
            return ToolReply(call, text, bool(result.is_error))
        except (ValueError, PermissionError, RuntimeError, *TRANSPORT_ERRORS) as exc:
            self.emit("error", {"message": str(exc)[:250]})
            return ToolReply(call, str(exc)[:250], True)

    async def resolve_task(self, connection, handle):
        answered = set()
        try:
            while True:
                state = await connection.task("tasks/get", handle.task_id)
                self.emit("task", {"taskId": handle.task_id, "status": state["status"]})
                if state["status"] == "completed":
                    return CallToolResult.model_validate(state["result"])
                if state["status"] in {"failed", "cancelled"}:
                    raise RuntimeError("Report task " + state["status"])
                if state["status"] == "input_required":
                    for key, request in state["inputRequests"].items():
                        if key not in answered:
                            if request["method"] != "elicitation/create":
                                raise ValueError("Unsupported task input method.")
                            answer = await self.ask(request["params"])
                            await connection.task(
                                "tasks/update", handle.task_id, inputResponses={key: answer}
                            )
                            answered.add(key)
                await asyncio.sleep(0.25)
        except asyncio.CancelledError:
            # Best effort cancellation addresses the durable task, not just its original RPC.
            try:
                await connection.task("tasks/cancel", handle.task_id)
                self.emit("task", {"taskId": handle.task_id, "status": "cancelled"})
            except Exception:
                self.emit("error", {"message": "Cancellation outcome unknown; retain the task ID."})
            raise
