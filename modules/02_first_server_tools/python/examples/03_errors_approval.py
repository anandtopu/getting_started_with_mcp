"""Compare a rejected write with a user-confirmed write and a schema failure.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/02_first_server_tools/python/examples/03_errors_approval.py
Expected: Without approval True; Approved id 2; Invalid title True
Inspect/capture: uv run python scripts/tier1.py --module 2 --capture
"""

import asyncio

from mcp import Client

from common.notes import notes_server


async def main() -> None:
    async with Client(notes_server(), raise_exceptions=False) as client:
        args = {"title": "Handover", "body": "Check the release wiki."}
        refused = await client.call_tool("create_note", args)
        print("Without approval:", refused.is_error)
        # This fixed demo represents a reviewed user action, not a model decision.
        accepted = await client.call_tool("create_note", {**args, "confirmed": True})
        print("Approved:", accepted.structured_content)
        invalid = await client.call_tool(
            "create_note", {"title": "", "body": "x", "confirmed": True}
        )
        print("Invalid title:", invalid.is_error)


if __name__ == "__main__":
    asyncio.run(main())
