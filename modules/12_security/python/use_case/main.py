"""Run the module 12 acceptance use case, offline.
Run: uv run python modules/12_security/python/use_case/main.py
Expected: PASS Module 12.
"""

import asyncio

from scripts.tier3 import run

if __name__ == "__main__":
    asyncio.run(run(12))
