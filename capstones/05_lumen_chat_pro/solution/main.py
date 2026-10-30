"""Run the complete Lumen Chat Pro acceptance contract. Expected: PASS capstone 5."""

import asyncio

from scripts.capstones import run

if __name__ == "__main__":
    asyncio.run(run(5))
