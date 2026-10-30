"""Run: uv run python modules/08_server_utilities/python/use_case/main.py
Expected: PASS Module 08; actual server/client assertions use no external network.
"""

import asyncio

from scripts.tier2 import run

if __name__ == "__main__":
    asyncio.run(run(8))
