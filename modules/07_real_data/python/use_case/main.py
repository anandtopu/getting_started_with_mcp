"""Run: uv run python modules/07_real_data/python/use_case/main.py
Expected: PASS Module 07; actual server/client assertions use no external network.
"""

import asyncio

from scripts.tier2 import run

if __name__ == "__main__":
    asyncio.run(run(7))
