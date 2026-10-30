"""Run the complete Personal Knowledge Server acceptance contract. Expected: PASS capstone 1."""

import asyncio

from scripts.capstones import run

if __name__ == "__main__":
    asyncio.run(run(1))
