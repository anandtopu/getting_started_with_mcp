"""Reject unknown names, model-supplied confirmation, and a denied write.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/06_building_a_host/python/examples/03_routing_and_approval.py
Expected: Unknown tool; Invalid arguments; User denied this call
Inspect/capture: uv run python scripts/tier1.py --module 6 --capture
"""

import asyncio

from mcp import Client

from common.host import Host
from common.notes import notes_server
from common.tool_formats import ToolCall


async def main() -> None:
    async def deny(name: str, arguments: dict) -> bool:
        return False

    async with Client(notes_server()) as client:
        host = Host({"notes": client}, deny)
        await host.discover()
        for call in [
            ToolCall("1", "unknown", {}),
            ToolCall("2", "notes__create_note", {"title": "x", "body": "x", "confirmed": True}),
            ToolCall("3", "notes__create_note", {"title": "x", "body": "x"}),
        ]:
            print((await host.execute(call)).text)


if __name__ == "__main__":
    asyncio.run(main())
