"""Lumen Chat v3: framework + gateway + durable Tasks + MCP App.
Run: uv run --extra frameworks python checkpoints/04_ecosystem/acceptance.py
Expected: PASS Tier 4 checkpoint. No model service or GUI is contacted.
"""

import argparse
import asyncio

from common.config import ROOT
from common.frameworks import run_framework
from scripts.tier4 import run


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--framework", choices=["agents", "langgraph", "pydantic"], default="agents"
    )
    args = parser.parse_args()
    path = ROOT / "modules/16_composition/python/use_case/server.py"
    result = await run_framework(args.framework, path, "workflow__")
    assert "Week 2026-07-13" in result
    await run(16)
    print("PASS Tier 4 checkpoint: framework Chat, Gateway, Tasks and App resource")


if __name__ == "__main__":
    asyncio.run(main())
