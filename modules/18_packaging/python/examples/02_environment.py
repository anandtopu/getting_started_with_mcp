"""Configure read-only versus confirmed-write notes.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/18_packaging/python/examples/02_environment.py
Capture the related server: uv run python scripts/tier5.py --module 18 --capture
Expected: true [search_notes]; false adds create_note and tag_note
"""

import asyncio
import os

from mcp import Client

from common.distributed_notes import make_server


async def main() -> None:
    for value in ("true", "false"):
        os.environ["LUMEN_NOTES_READ_ONLY"] = value
        # KEY IDEA: capabilities match the configured deployment policy.
        async with Client(make_server()) as client:
            print(value, [t.name for t in (await client.list_tools()).tools])


if __name__ == "__main__":
    asyncio.run(main())
