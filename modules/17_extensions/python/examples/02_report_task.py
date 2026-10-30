"""Observe a durable handle, polling, elicitation input, completion and cancellation.
Run: uv run python modules/17_extensions/python/examples/02_report_task.py
Wire: uv run python scripts/tier4.py --module 17 --capture
Expected: PASS and real synthetic Lumen results.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

import asyncio

from scripts.tier4 import run


async def main():
    await run(17)


if __name__ == "__main__":
    asyncio.run(main())
