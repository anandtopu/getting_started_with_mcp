"""Run the module 13 acceptance use case, offline.
Run: uv run python modules/13_testing_observability/python/use_case/main.py
Expected: PASS Module 13.
"""

import asyncio

from scripts.tier3 import run

if __name__ == "__main__":
    asyncio.run(run(13))
