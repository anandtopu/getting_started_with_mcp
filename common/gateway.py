"""Lumen Gateway: fixed upstreams, per-principal catalogs and call-time policy."""

import asyncio
import json
import logging
import re
import time
from collections import deque
from contextlib import AsyncExitStack, asynccontextmanager
from contextvars import Context
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError
from mcp import Client
from mcp.server import MCPServer
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.settings import AuthSettings
from mcp.shared.exceptions import MCPError
from mcp_types import CallToolResult, ListToolsResult, TextContent

from common.analytics import make_server as analytics_server
from common.connections import discover
from common.data import data_root
from common.extensions import analytics_apps
from common.issues import issue_lifespan, register_issues
from common.notes import READ, notes_server
from common.protocol import SPEC_REVISION
from common.report_tasks import ReportTasks, report
from common.reports import make_server as reports_server
from common.tool_design import task_server
from common.wiki import wiki_server

LOG = logging.getLogger("lumen.gateway")


def calendar_server():
    server = MCPServer("Lumen calendar")

    @server.tool(annotations=READ)
    async def list_events(limit: int = 5) -> list[dict]:
        """Read up to 20 synthetic calendar events; never send invitations."""
        if not 1 <= limit <= 20:
            raise ValueError("Choose limit from 1 to 20.")
        return json.loads((data_root() / "calendar/events.json").read_text())[:limit]

    return server


def upstreams():
    issues = MCPServer("Lumen issues", lifespan=issue_lifespan)
    register_issues(issues)
    return {
        "notes": notes_server(),
        "wiki": wiki_server(),
        "issues": issues,
        "analytics": analytics_server(),
        "calendar": calendar_server(),
        "reports": reports_server(),
        "workflow": task_server(),
    }


class Gateway:
    def __init__(self, factories=None, principal=None, rate_limit=60):
        self.servers = factories if factories is not None else upstreams()
        self.identity = principal or (lambda: ("local-learner", frozenset({"workspace:read"})))
        self.rate_limit = rate_limit
        self.windows: dict[str, deque] = {}
        self.clients, self.cache, self.routes = {}, {}, {}
        self.lock = asyncio.Lock()
        self.references = 0
        self.revision = 1
        self.disabled: set[str] = set()

    @asynccontextmanager
    async def lifetime(self):
        async with self.lock:
            if self.references == 0:
                self.stack = AsyncExitStack()
                await self.stack.__aenter__()
                try:
                    for alias, server in self.servers.items():
                        if not re.fullmatch(r"[a-z][a-z0-9_]{0,15}", alias):
                            raise ValueError("Unsafe upstream alias.")
                        client = await self.stack.enter_async_context(
                            Client(server, mode=SPEC_REVISION, raise_exceptions=False)
                        )
                        await discover(client)
                        self.clients[alias] = client
                except BaseException:
                    await self.stack.aclose()
                    raise
            self.references += 1
        try:
            yield self
        finally:
            async with self.lock:
                self.references -= 1
                if self.references == 0:
                    await self.stack.aclose()
                    self.clients.clear()
                    self.cache.clear()

    def allowed(self, alias, tool, scopes):
        if alias in self.disabled or "workspace:read" not in scopes:
            return False
        return (
            bool(tool.annotations and tool.annotations.read_only_hint)
            or "workspace:write" in scopes
        )

    async def catalog(self, *, fresh=False):
        owner, scopes = self.identity()
        key = (owner, tuple(sorted(scopes)), self.revision, tuple(sorted(self.disabled)))
        cached = self.cache.get(key)
        if not fresh and cached and cached[0] > time.monotonic():
            return deepcopy(cached[1])
        result, routes = [], {}
        for alias, client in self.clients.items():
            cursor, seen = None, set()
            for _ in range(20):
                try:
                    async with asyncio.timeout(5):
                        page = await asyncio.create_task(
                            client.list_tools(cursor=cursor), context=Context()
                        )
                except Exception:
                    LOG.warning(json.dumps({"event": "upstream_unavailable", "route": alias}))
                    routes = {n: r for n, r in routes.items() if r[0] != alias}
                    result = [t for t in result if not t.name.startswith(alias + "__")]
                    break
                for tool in page.tools:
                    name = f"{alias}__{tool.name}"
                    if len(name) > 64 or name in routes:
                        raise MCPError(-32603, "Upstream tool name collision or excessive length.")
                    if self.allowed(alias, tool, scopes):
                        routes[name] = (alias, tool)
                        result.append(tool.model_copy(update={"name": name}))
                cursor = page.next_cursor
                if cursor is None:
                    break
                if cursor in seen:
                    raise MCPError(-32603, "Repeated upstream catalog cursor.")
                seen.add(cursor)
            else:
                raise MCPError(-32603, "Upstream catalog exceeds page budget.")
        result.sort(key=lambda tool: tool.name)
        if len(self.cache) >= 100:
            self.cache.clear()
        self.routes[key] = routes
        if len(self.routes) > 100:
            self.routes = {key: routes}
        self.cache[key] = (time.monotonic() + 2, result)
        return deepcopy(result)

    def throttle(self, owner):
        now = time.monotonic()
        if owner not in self.windows and len(self.windows) >= 100:
            self.windows = {k: v for k, v in self.windows.items() if v and v[-1] > now - 60}
            if len(self.windows) >= 100:
                raise MCPError(-32603, "Gateway principal capacity reached.")
        window = self.windows.setdefault(owner, deque())
        while window and window[0] <= now - 60:
            window.popleft()
        if len(window) >= self.rate_limit:
            raise MCPError(-32603, "Gateway rate limit reached; retry after 60 seconds.")
        window.append(now)

    async def call(self, name, arguments):
        owner, scopes = self.identity()
        self.throttle(owner)
        # KEY IDEA: visibility is not authorization; refresh policy at execution.
        await self.catalog(fresh=True)
        key = (owner, tuple(sorted(scopes)), self.revision, tuple(sorted(self.disabled)))
        route = self.routes.get(key, {}).get(name)
        if route is None:
            LOG.info(json.dumps({"event": "tool_denied", "principal": owner}))
            raise MCPError(-32602, "Tool is not available to this principal.")
        alias, tool = route
        try:
            Draft202012Validator(tool.input_schema).validate(arguments)
        except ValidationError as exc:
            raise MCPError(-32602, "Arguments do not match the advertised schema.") from exc
        LOG.info(json.dumps({"event": "tool_call", "principal": owner, "route": name}))
        try:
            async with asyncio.timeout(10):
                # Never forward the incoming bearer token to an upstream.
                return await asyncio.create_task(
                    self.clients[alias].call_tool(tool.name, deepcopy(arguments)), context=Context()
                )
        except Exception:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Upstream unavailable; retry this read later or inspect its logs.",
                    )
                ],
                is_error=True,
            )


def gateway_server(path: Path, gateway: Gateway | None = None, verifier=None):
    gateway = gateway or Gateway(principal=http_identity if verifier else None)
    tasks = ReportTasks(path, principal=lambda: gateway.identity()[0])

    @asynccontextmanager
    async def lifespan(server):
        try:
            async with gateway.lifetime():
                yield {"gateway": gateway}
        finally:
            if gateway.references == 0:
                await tasks.close()

    async def route(ctx, next_handler):
        if ctx.method == "tools/list":
            local = await next_handler(ctx)
            local = ListToolsResult.model_validate(local)
            return ListToolsResult(tools=[*await gateway.catalog(), *local.tools])
        if ctx.method == "tools/call":
            params = ctx.params or {}
            name = params.get("name", "")
            if not isinstance(name, str):
                raise MCPError(-32602, "Tool name must be a string.")
            if "__" in name:
                return await gateway.call(name, params.get("arguments", {}))
        if ctx.method in {
            "tools/call",
            "tasks/get",
            "tasks/update",
            "tasks/cancel",
            "resources/read",
        }:
            owner, scopes = gateway.identity()
            if "workspace:read" not in scopes:
                raise MCPError(-32602, "Workspace read permission required.")
            gateway.throttle(owner)
        return await next_handler(ctx)

    server = MCPServer(
        "Lumen Gateway",
        lifespan=lifespan,
        middleware=[route],
        extensions=[tasks, analytics_apps()],
        token_verifier=verifier,
        auth=AuthSettings(
            issuer_url=verifier.issuer,
            resource_server_url=verifier.resource,
            required_scopes=["workspace:read"],
            validate_token_resource=True,
        )
        if verifier
        else None,
    )

    @server.tool(annotations=READ)
    async def quarterly_report(quarter: str = "Q1", ask_details: bool = False) -> dict[str, object]:
        """Create the gateway's durable synthetic report, optionally asking about detail level."""
        return report(quarter)

    return server, gateway, tasks


def http_identity():
    token = get_access_token()
    if token is None or not token.subject:
        raise MCPError(-32602, "Authenticated subject required.")
    return token.subject, frozenset(token.scopes)
