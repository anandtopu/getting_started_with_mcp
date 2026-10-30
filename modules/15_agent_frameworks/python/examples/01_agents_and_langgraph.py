"""Run the same triage-and-draft task in OpenAI Agents and LangGraph, without an API key.
Run: uv run python modules/15_agent_frameworks/python/examples/01_agents_and_langgraph.py
Wire: uv run python scripts/tier4.py --module 15 --capture
Expected: PASS and real synthetic Lumen results.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

import asyncio

from common.frameworks import run_framework


async def main():
    for name in ["agents", "langgraph"]:
        result = await run_framework(name)
        assert "Week 2026-07-13" in result
        print("PASS", name, result)


if __name__ == "__main__":
    asyncio.run(main())
