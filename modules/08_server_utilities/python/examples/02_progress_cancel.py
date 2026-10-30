"""Run: uv run python modules/08_server_utilities/python/examples/02_progress_cancel.py
Expected: four progress events, cancellation cleanup, PASS Module 08.
"""

import asyncio

from scripts.tier2 import run

if __name__ == "__main__":
    asyncio.run(run(8))
