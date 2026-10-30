"""Lumen Chat v1: discover, namespace, validate, approve, execute, return, repeat."""

import asyncio
import json
import re
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from common.connections import discover
from common.schemas import portable_schema
from common.tool_formats import ToolCall, ToolReply


class Host:
    def __init__(self, clients: dict, approve, max_turns: int = 6, max_calls: int = 8):
        self.clients, self.approve = clients, approve
        self.max_turns, self.max_calls = max_turns, max_calls
        self.routes: dict = {}
        self.tools: list[dict] = []
        self.audit: list[ToolReply] = []

    async def discover(self) -> None:
        self.routes.clear()
        self.tools.clear()
        for alias, client in self.clients.items():
            await discover(client)
            cursor, seen = None, set()
            for _ in range(20):
                page = await client.list_tools(cursor=cursor)
                for tool in page.tools:
                    name = f"{alias}__{tool.name}"
                    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", name) or name in self.routes:
                        raise ValueError("Tool name is unsafe, too long, or collides.")
                    schema = portable_schema(tool.input_schema)
                    # KEY IDEA: the model cannot grant itself confirmation.
                    schema.get("properties", {}).pop("confirmed", None)
                    schema["required"] = [x for x in schema.get("required", []) if x != "confirmed"]
                    schema["additionalProperties"] = False
                    Draft202012Validator.check_schema(schema)
                    self.routes[name] = (client, tool, schema)
                    self.tools.append(
                        {
                            "name": name,
                            "description": tool.description or name,
                            "inputSchema": schema,
                        }
                    )
                cursor = page.next_cursor
                if cursor is None:
                    break
                if cursor in seen:
                    raise RuntimeError("Repeated tool cursor.")
                seen.add(cursor)
            else:
                raise RuntimeError("Tool catalog page budget exceeded.")

    async def execute(self, call: ToolCall) -> ToolReply:
        if call.name not in self.routes:
            return ToolReply(call, "Unknown tool: choose a listed name.", True)
        client, tool, schema = self.routes[call.name]
        try:
            Draft202012Validator(schema).validate(call.arguments)
        except ValidationError:
            return ToolReply(call, "Invalid arguments: use the advertised schema.", True)
        arguments = deepcopy(call.arguments)
        # Approve every tool, including reference tools; annotations are untrusted hints.
        if not await self.approve(call.name, deepcopy(arguments)):
            return ToolReply(call, "User denied this call. Do not retry it.", True)
        if "confirmed" in tool.input_schema.get("properties", {}):
            arguments["confirmed"] = True
        try:
            result = await self.call_tool(client, tool.name, arguments)
            text = json.dumps(result.model_dump(mode="json", by_alias=True), ensure_ascii=False)
            if len(text) > 16000:
                text = json.dumps({"error": "Result exceeds 16000 characters; request less data."})
                return ToolReply(call, text, True)
            return ToolReply(call, text, bool(result.is_error))
        except Exception:
            return ToolReply(call, "Tool request failed; check the server and arguments.", True)

    async def call_tool(self, client, name: str, arguments: dict):
        async with asyncio.timeout(15):
            return await client.call_tool(name, arguments)

    async def run(self, model) -> str:
        await self.discover()
        results, call_ids = [], set()
        for _ in range(self.max_turns):
            async with asyncio.timeout(60):
                turn = await model.turn(self.tools, results)
            if not turn.calls:
                return turn.text
            if len(call_ids) + len(turn.calls) > self.max_calls:
                raise RuntimeError("Tool call budget exceeded.")
            results = []
            for call in turn.calls:
                if not call.id or call.id in call_ids:
                    raise RuntimeError("Missing or repeated tool call ID.")
                call_ids.add(call.id)
                reply = await self.execute(call)
                results.append(reply)
                self.audit.append(reply)
        raise RuntimeError("Model turn budget exceeded.")
