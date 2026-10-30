"""Run: uv run python modules/09_elicitation_sampling_roots/python/use_case/main.py
Expected: PASS Module 09; actual server/client assertions use no external network.
"""

import asyncio

from common.data import data_root
from common.files_model import summarize_file
from scripts.tier2 import run


async def main() -> None:
    await run(9)
    print(await summarize_file(data_root() / "wiki", "engineering/page-01.md", confirmed=True))


if __name__ == "__main__":
    asyncio.run(main())
