"""Serve the low-level pagination fixture over stdio.

Run: uv run python modules/05_first_client/python/use_case/paged_server.py
Inspect: uv run python scripts/tier1.py --module 5 --capture
"""

import asyncio

from mcp.server.stdio import stdio_server

from common.pagination import paged_server


async def main() -> None:
    server = paged_server()
    async with stdio_server() as (reader, writer):
        # This v2 runner parameter describes server identity/capabilities. The
        # current client still sends per-request metadata, as the capture proves.
        await server.run(reader, writer, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
