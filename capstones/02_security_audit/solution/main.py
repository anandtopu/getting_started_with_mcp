"""Run the complete Security Audit Lab acceptance contract. Expected: PASS capstone 2."""

import asyncio

from scripts.capstones import run

if __name__ == "__main__":
    asyncio.run(run(2))
