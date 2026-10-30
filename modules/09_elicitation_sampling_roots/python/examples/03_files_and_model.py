"""Run: uv run python modules/09_elicitation_sampling_roots/python/examples/03_files_and_model.py
Expected: fake summary without network access. --live requires separate confirmation.
"""

import argparse
import asyncio

from common.data import data_root
from common.files_model import summarize_file
from common.llm import create_model


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    root = data_root() / "wiki"
    relative = "engineering/page-01.md"
    if args.live:
        answer = await asyncio.to_thread(
            input, "Send this synthetic wiki page to your configured provider? [y/N] "
        )
        if answer.lower() != "y":
            print("Cancelled; no model call made.")
            return
    print(await summarize_file(root, relative, create_model() if args.live else None, True))


if __name__ == "__main__":
    asyncio.run(main())
