"""Own a subprocess lifetime with async with and use all three primitives.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/05_first_client/python/examples/01_stdio_client.py
Expected: release note, five wiki spaces, release instruction
Inspect/capture: uv run python scripts/tier1.py --module 5 --capture
"""

import asyncio

from common.connections import connection, discover


async def main() -> None:
    # A client is one connection. Exit closes pipes and its child process.
    async with (
        connection("notes") as notes,
        connection("wiki") as wiki,
        connection("prompts") as prompts,
    ):
        await discover(notes)
        await discover(wiki)
        if notes.server_capabilities.tools is None or wiki.server_capabilities.resources is None:
            raise RuntimeError("Expected tools/resources capabilities are unavailable.")
        print((await notes.call_tool("search_notes", {"query": "release"})).content)
        print((await wiki.read_resource("wiki://index")).contents[0].text)
        print((await prompts.get_prompt("release_notes", {"issue_ids": "1"})).messages)


if __name__ == "__main__":
    asyncio.run(main())
