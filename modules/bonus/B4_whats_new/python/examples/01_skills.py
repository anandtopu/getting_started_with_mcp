"""Discover skills/list and skills/get, verify SHA-256 bytes, then read resources without
activating instructions.
Run: uv run python modules/bonus/B4_whats_new/python/examples/01_skills.py
Capture: uv run python scripts/bonus.py --module B4 --capture
"""

import asyncio

from mcp import Client

from common.skills_extension import load_skill, skills_server


async def main():
    async with Client(skills_server()) as client:
        print(await load_skill(client))


asyncio.run(main())
