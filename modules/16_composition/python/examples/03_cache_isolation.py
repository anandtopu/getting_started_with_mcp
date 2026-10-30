"""Keep cached catalogs separate by verified identity and policy; recheck at execution.
Run: uv run python modules/16_composition/python/examples/03_cache_isolation.py
Wire: uv run python scripts/tier4.py --module 16 --capture
Expected: PASS and real synthetic Lumen results.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

import asyncio
import tempfile
from contextvars import ContextVar
from pathlib import Path

from mcp import Client
from mcp.shared.exceptions import MCPError

from common.gateway import Gateway, gateway_server


async def main():
    identity = ContextVar("identity", default=("reader", frozenset({"workspace:read"})))
    with tempfile.TemporaryDirectory() as directory:
        gateway = Gateway(principal=identity.get)
        server, _, _ = gateway_server(Path(directory) / "tasks.db", gateway)
        async with Client(server) as client:
            reader = {tool.name for tool in (await client.list_tools()).tools}
            token = identity.set(("editor", frozenset({"workspace:read", "workspace:write"})))
            editor = {tool.name for tool in (await client.list_tools()).tools}
            identity.reset(token)
            assert "notes__create_note" in editor - reader
            gateway.disabled.add("notes")
            try:
                await client.call_tool("notes__search_notes", {})
            except MCPError:
                print("PASS stale catalog cannot authorize a revoked tool")
            else:
                raise AssertionError("Revoked route was called")


if __name__ == "__main__":
    asyncio.run(main())
