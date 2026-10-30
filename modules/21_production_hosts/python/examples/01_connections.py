"""Load reviewed multi-server profiles and inspect negotiated capabilities.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/21_production_hosts/python/examples/01_connections.py
Capture the related server: uv run python scripts/tier5.py --module 21 --capture
Expected: notes, issues, gateway with actual protocol and extension capabilities
"""

import asyncio

from common.production_host import Connection, load_host_config
from common.web_chat import CONFIG


async def main() -> None:
    for server in load_host_config(CONFIG).servers:
        connection = await Connection(server, lambda *_: None).start()
        try:
            # KEY IDEA: negotiate before exposing tools to a model.
            print(connection.info)
            assert await connection.tools()
        finally:
            await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
