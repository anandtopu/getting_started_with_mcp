"""Verify this shipping stage with synthetic data and real MCP.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/18_packaging/python/use_case/main.py
Capture the related server: uv run python scripts/tier5.py --module 18 --capture
Expected: PASS Module 18
"""

import argparse
import asyncio

from scripts.tier5 import run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    # KEY IDEA: verify the actual transport before attempting a public release.
    asyncio.run(run(18, args.capture))


if __name__ == "__main__":
    main()
