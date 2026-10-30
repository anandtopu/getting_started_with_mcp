"""Read a poisoned resource, then reject injected exfiltration and salary calls.

Run: uv run python modules/12_security/python/examples/01_poisoned_content.py
Expected: PASS with the measured checks below.
"""

import asyncio

from mcp import Client

from common.defenses import make_server
from scripts.tier3 import exercise


async def main() -> None:
    async with Client(make_server(), raise_exceptions=False) as client:
        await exercise(client, 12)
    print("PASS poisoned content cannot expand the reviewed allow-list")


if __name__ == "__main__":
    asyncio.run(main())
