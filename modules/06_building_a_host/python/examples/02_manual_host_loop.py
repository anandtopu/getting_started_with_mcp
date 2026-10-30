"""Step through model -> approved tool -> result -> model without a framework.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/06_building_a_host/python/examples/02_manual_host_loop.py
Expected: approved search, fixture final text, read-1
Inspect/capture: uv run python scripts/tier1.py --module 6 --capture
"""

import asyncio

from mcp import Client

from common.config import Settings
from common.host import Host
from common.llm import create_tool_model
from common.notes import notes_server


async def main() -> None:
    async def approve(name: str, arguments: dict) -> bool:
        print("Fixture approval:", name, arguments)
        return name == "notes__search_notes"  # Only this predetermined read is authorized.

    async with Client(notes_server()) as client:
        host = Host({"notes": client}, approve)
        print(await host.run(create_tool_model("Find release notes", Settings())))
        print("Returned tool-call ID:", host.audit[0].call.id)


if __name__ == "__main__":
    asyncio.run(main())
