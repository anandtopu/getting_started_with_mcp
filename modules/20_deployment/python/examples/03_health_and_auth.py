"""Probe health, 401, then a real authenticated issue read over HTTP.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/20_deployment/python/examples/03_health_and_auth.py
Capture the related server: uv run python scripts/tier5.py --module 20 --capture
Expected: PASS health, unauthorized rejection, authenticated issue read
"""

import asyncio

from scripts.deployment_lab import run


def main() -> None:
    # KEY IDEA: health and a successful TCP connection do not authorize a tool call.
    asyncio.run(run())


if __name__ == "__main__":
    main()
