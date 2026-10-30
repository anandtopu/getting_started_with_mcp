"""Follow opaque registry cursors, with a bounded offline fixture by default.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/19_registry/python/examples/02_discovery.py
Capture the related server: uv run python scripts/tier5.py --module 19 --capture
Expected: Discovered 1 metadata entries; installed 0
"""

import argparse
import asyncio

from common.registry import fixture_transport, list_registry


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    records = await list_registry(None if args.live else fixture_transport(), live=args.live)
    # KEY IDEA: discovery returns metadata; it never executes an installation.
    print("Discovered", len(records), "metadata entries; installed 0")


if __name__ == "__main__":
    asyncio.run(main())
