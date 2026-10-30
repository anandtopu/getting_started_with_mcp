"""Run: uv run python modules/10_streamable_http/python/use_case/main.py
Expected: PASS Module 10; actual server/client assertions use no external network.
"""

import asyncio

from scripts.tier2 import run

if __name__ == "__main__":
    asyncio.run(run(10))
