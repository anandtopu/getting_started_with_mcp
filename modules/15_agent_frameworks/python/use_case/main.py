"""Run the Module 15 Lumen use case without model credentials.
Run: uv run python modules/15_agent_frameworks/python/use_case/main.py
Expected: evidence-based results or PASS assertions.
Wire: uv run python scripts/tier4.py --module 15 --capture
"""

import asyncio

from common.frameworks import run_framework


async def main():
    for name in ["agents", "langgraph", "pydantic"]:
        print(name, await run_framework(name))


if __name__ == "__main__":
    asyncio.run(main())
