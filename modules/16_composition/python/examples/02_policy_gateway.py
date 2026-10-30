"""Verify real HTTP OAuth, audience enforcement and browser-origin checks.
Run: uv run python modules/16_composition/python/examples/02_policy_gateway.py
Wire: uv run python scripts/tier4.py --module 16 --capture
Expected: PASS and real synthetic Lumen results.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

import asyncio

from scripts.gateway_lab import run


async def main():
    await run()


if __name__ == "__main__":
    asyncio.run(main())
