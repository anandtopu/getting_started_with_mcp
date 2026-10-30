"""Discover seven upstreams through a server that is also an MCP client.
Run: uv run python modules/16_composition/python/examples/01_server_as_client.py
Wire: uv run python scripts/tier4.py --module 16 --capture
Expected: PASS and real synthetic Lumen results.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

import asyncio
import tempfile
from pathlib import Path

from mcp import Client

from common.gateway import gateway_server


async def main():
    with tempfile.TemporaryDirectory() as directory:
        server, gateway, tasks = gateway_server(Path(directory) / "tasks.db")
        async with Client(server) as client:
            tools = (await client.list_tools()).tools
            assert "workflow__triage_week" in {tool.name for tool in tools}
            print("PASS namespaced tools:", [tool.name for tool in tools])
            print((await client.call_tool("workflow__draft_status", {})).structured_content)


if __name__ == "__main__":
    asyncio.run(main())
