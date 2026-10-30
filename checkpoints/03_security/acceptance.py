"""Run the secured-workspace checkpoint without external credentials.
Run: uv run python checkpoints/03_security/acceptance.py
Expected: Tier 2 demo, modules 11-13 and all nine solution contracts pass.
"""

import asyncio
import subprocess
import sys

from common.config import ROOT
from scripts.check_exercise import check
from scripts.tier3 import run


async def main() -> None:
    subprocess.run(
        [sys.executable, "-m", "common.chat_v2", "--demo"], cwd=ROOT, check=True, timeout=30
    )
    for module in range(11, 14):
        await run(module)
        for exercise in range(1, 4):
            check(module, exercise, solution=True)
    print("PASS Tier 3 checkpoint: secured and tested fixture workspace")


if __name__ == "__main__":
    asyncio.run(main())
