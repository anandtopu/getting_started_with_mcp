"""Capture actual client requests through the transparent stdio proxy.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/01_architecture_wire/python/examples/03_wiretap_client.py
Expected: directory_count, 80 synthetic employees, .runtime/raw.jsonl
Inspect/capture: uv run python scripts/tier1.py --module 1 --capture
"""

import asyncio

from common.config import ROOT
from common.connections import connection


async def main() -> None:
    capture = ROOT / ".runtime/raw.jsonl"
    async with connection("raw", capture) as client:
        print([tool.name for tool in (await client.list_tools()).tools])
        print((await client.call_tool("directory_count", {})).content)
    print("Capture:", capture)


if __name__ == "__main__":
    asyncio.run(main())
