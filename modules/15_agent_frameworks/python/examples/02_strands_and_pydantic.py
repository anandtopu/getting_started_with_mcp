"""Run Pydantic AI; add --strands after installing its isolated environment.
Run: uv run python modules/15_agent_frameworks/python/examples/02_strands_and_pydantic.py
Wire: uv run python scripts/tier4.py --module 15 --capture
Expected: PASS and real synthetic Lumen results.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

import argparse
import asyncio
import subprocess
import sys

from common.config import ROOT
from common.frameworks import run_framework


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strands", action="store_true")
    args = parser.parse_args()
    print("PASS pydantic:", await run_framework("pydantic"))
    if args.strands:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/framework_extras.py"), "strands"],
            check=True,
            timeout=45,
        )
    else:
        print("Strands native adapter: add --strands after uv sync --project frameworks/strands.")


if __name__ == "__main__":
    asyncio.run(main())
