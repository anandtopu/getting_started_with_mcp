"""Run the combined B4 acceptance; no external account required."""

import asyncio

from scripts.bonus import run

if __name__ == "__main__":
    asyncio.run(run("B4"))
