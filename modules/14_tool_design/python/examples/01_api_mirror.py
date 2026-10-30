"""Explore 25 endpoint-shaped tools before redesigning their interface.
Run: uv run python modules/14_tool_design/python/examples/01_api_mirror.py
Wire: uv run python scripts/tier4.py --module 14 --capture
Expected: PASS and real synthetic Lumen results.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

import asyncio

from mcp import Client

from common.tool_design import mirror_server


async def main():
    async with Client(mirror_server()) as client:
        tools = (await client.list_tools()).tools
        assert len(tools) == 25
        print("PASS mirror:", [tool.name for tool in tools])
        print((await client.call_tool("get_issues", {"row_id": 1})).structured_content)


if __name__ == "__main__":
    asyncio.run(main())
