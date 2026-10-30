"""Assert tool schemas and output behavior without a transport or LLM.

Run: uv run python modules/13_testing_observability/python/examples/01_inmemory_contracts.py
Expected: PASS with the measured checks below.
"""

import asyncio

from common.quality import contracts


async def main() -> None:
    print("PASS", await contracts())


if __name__ == "__main__":
    asyncio.run(main())
