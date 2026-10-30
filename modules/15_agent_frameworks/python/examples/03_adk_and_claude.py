"""Connect the Claude SDK locally without a model prompt; add --adk for its isolated adapter.
Run: uv run python modules/15_agent_frameworks/python/examples/03_adk_and_claude.py
Wire: uv run python scripts/tier4.py --module 15 --capture
Expected: PASS and real synthetic Lumen results.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

import argparse
import asyncio
import subprocess
import sys

from common.claude_adapter import probe
from common.config import ROOT


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adk", action="store_true")
    parser.add_argument("--live", action="store_true", help="Explicitly send a Claude model prompt")
    args = parser.parse_args()
    result = await probe(live=args.live)
    print("PASS Claude SDK connection:", result)
    if args.adk:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/framework_extras.py"), "adk"],
            check=True,
            timeout=45,
        )
    else:
        print("ADK native adapter: add --adk after uv sync --project frameworks/adk.")


if __name__ == "__main__":
    asyncio.run(main())
