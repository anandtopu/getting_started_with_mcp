"""Read the reference server allowed-directory boundary.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/00_setup/python/examples/03_reference_server.py
Expected: only this repository data/files directory
Inspect/capture: uv run python scripts/tier1.py --module 0 --capture
"""

import asyncio

from common.connections import connection


async def main() -> None:
    async with connection("files") as client:
        print(
            (await client.call_tool("list_allowed_directories", {})).model_dump_json(by_alias=True)
        )


if __name__ == "__main__":
    asyncio.run(main())
