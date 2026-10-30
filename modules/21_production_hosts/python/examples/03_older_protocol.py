"""Connect with the SDK compatibility handshake and execute an approved read.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/21_production_hosts/python/examples/03_older_protocol.py
Capture the related server: uv run python scripts/tier5.py --module 21 --capture
Expected: PASS compatible read on the negotiated older revision
"""

import asyncio

from scripts.tier5 import host_demo


async def main() -> None:
    # KEY IDEA: legacy changes the handshake, not imports or server authorization.
    info = await host_demo(legacy=True)
    print("PASS compatible read on", info["protocol"])


if __name__ == "__main__":
    asyncio.run(main())
