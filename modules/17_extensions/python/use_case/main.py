"""Run the Module 17 Lumen use case without model credentials.
Run: uv run python modules/17_extensions/python/use_case/main.py
Expected: evidence-based results or PASS assertions.
Wire: uv run python scripts/tier4.py --module 17 --capture
"""

import asyncio

from scripts.tier4 import run


async def main():
    await run(17)


if __name__ == "__main__":
    asyncio.run(main())
