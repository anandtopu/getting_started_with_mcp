"""Reject approval attached to an obsolete tool definition.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/21_production_hosts/python/examples/02_catalog_change.py
Capture the related server: uv run python scripts/tier5.py --module 21 --capture
Expected: Tool changed after review. Start again and review its new definition.
"""

import asyncio

from mcp_types import Tool

from common.production_host import Connection, ServerConfig


async def main() -> None:
    connection = await Connection(
        ServerConfig(alias="notes", profile="notes"), lambda *_: None
    ).start()
    try:
        old = next(t for t in await connection.tools() if t.name == "search_notes")
        stale = Tool.model_validate({**old.model_dump(), "description": "A previous definition"})
        # KEY IDEA: changed text/schema invalidates prior approval, before dispatch.
        try:
            await connection.checked_call(stale, {"query": "release"})
        except PermissionError as error:
            print(error)
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
