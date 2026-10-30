"""Run the module 11 acceptance use case, offline.
Run: uv run python modules/11_authorization/python/use_case/main.py
Expected: PASS Module 11.
"""

import asyncio

from scripts.tier3 import run

if __name__ == "__main__":
    asyncio.run(run(11))
