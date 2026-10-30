"""Measure task completion and catalog size; --live uses the shared model helper.
Run: uv run python modules/14_tool_design/python/examples/03_measure_change.py
Wire: uv run python scripts/tier4.py --module 14 --capture
Expected: PASS and real synthetic Lumen results.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

import argparse
import asyncio
import json

from mcp import Client

from common.tool_design import task_server
from common.tool_evaluation import evaluate


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--limit", type=int, default=6)
    args = parser.parse_args()
    print(json.dumps(await evaluate(args.live, args.limit), indent=2))
    server = task_server()
    async with Client(server) as client:
        assert len((await client.list_tools()).tools) == 6
        server.remove_tool("team_load")
        # KEY IDEA: refresh the catalog after a policy or definition change.
        assert len((await client.list_tools(cache_mode="refresh")).tools) == 5
        print("PASS dynamic catalog refreshed: 6 -> 5 tools")


if __name__ == "__main__":
    asyncio.run(main())
