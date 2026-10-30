"""Run the complete Lumen Ops Server acceptance contract. Expected: PASS capstone 4."""

import asyncio

from scripts.capstones import run

if __name__ == "__main__":
    asyncio.run(run(4))
