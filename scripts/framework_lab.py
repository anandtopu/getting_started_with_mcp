"""Run actual framework orchestration without model keys or external requests.

Run: uv run --extra frameworks python scripts/framework_lab.py [--framework agents]
Expected: PASS and an evidence-based draft for each selected framework.
"""

import argparse
import asyncio

from common.frameworks import run_framework


async def run(name):
    result = await run_framework(name)
    assert "Week 2026-07-13" in result and "published" in result
    print(f"PASS {name}: {result}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework", choices=["agents", "langgraph", "pydantic"])
    args = parser.parse_args()
    for name in [args.framework] if args.framework else ["agents", "langgraph", "pydantic"]:
        asyncio.run(run(name))


if __name__ == "__main__":
    main()
