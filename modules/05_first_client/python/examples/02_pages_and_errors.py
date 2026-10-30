"""Traverse opaque cursors, including an empty page; handle a protocol failure.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/05_first_client/python/examples/02_pages_and_errors.py
Expected: Index, Bulletin; invalid cursor rejected
Inspect/capture: uv run python scripts/tier1.py --module 5 --capture
"""

import asyncio

from mcp import Client

from common.pagination import all_resources, paged_server


async def main() -> None:
    async with Client(paged_server()) as client:
        print([r.name for r in await all_resources(client)])
        try:
            await client.list_resources(cursor="not-a-cursor")
        except Exception as error:
            print(type(error).__name__, "Invalid cursor rejected; restart pagination.")


if __name__ == "__main__":
    asyncio.run(main())
