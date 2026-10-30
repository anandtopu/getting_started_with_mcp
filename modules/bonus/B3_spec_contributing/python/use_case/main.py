"""Run the combined B3 acceptance; no external account required."""

import asyncio

from scripts.bonus import run

if __name__ == "__main__":
    asyncio.run(run("B3"))
