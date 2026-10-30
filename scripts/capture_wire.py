"""Capture actual delivered server exchanges: uv run python scripts/capture_wire.py."""

import asyncio

from common.config import ROOT
from scripts.run_all_examples import smoke


def main() -> None:
    asyncio.run(smoke(ROOT / "docs/wire"))


if __name__ == "__main__":
    main()
