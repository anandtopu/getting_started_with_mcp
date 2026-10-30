"""Use six task-oriented tools, bounded pages and concise/detailed output.
Run: uv run python modules/14_tool_design/python/examples/02_task_tools.py
Wire: uv run python scripts/tier4.py --module 14 --capture
Expected: PASS and real synthetic Lumen results.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

import asyncio

from mcp import Client

from common.tool_design import task_server


async def main():
    async with Client(task_server()) as client:
        assert len((await client.list_tools()).tools) == 6
        first = (await client.call_tool("search_issues", {"limit": 2})).structured_content
        second = (
            await client.call_tool("search_issues", {"limit": 2, "after": first["next_after"]})
        ).structured_content
        print("PASS pages:", first, second)
        print(
            (
                await client.call_tool("issue_brief", {"issue_id": 1, "mode": "detailed"})
            ).structured_content
        )


if __name__ == "__main__":
    asyncio.run(main())
