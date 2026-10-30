"""Run the complete Lumen Gateway acceptance contract. Expected: PASS capstone 3."""

import asyncio

from scripts.capstones import run

if __name__ == "__main__":
    asyncio.run(run(3))
