"""Check the public tool contract independently of package layout.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/18_packaging/python/examples/03_compatibility.py
Capture the related server: uv run python scripts/tier5.py --module 18 --capture
Expected: PASS existing search contract
"""

import asyncio

from mcp import Client

from common.distributed_notes import make_server


async def main() -> None:
    async with Client(make_server()) as client:
        # KEY IDEA: an existing call must keep working after a packaging change.
        result = await client.call_tool("search_notes", {"query": "RELEASE"})
        assert "Release handover" in result.content[0].text
        print("PASS existing search contract")


if __name__ == "__main__":
    asyncio.run(main())
