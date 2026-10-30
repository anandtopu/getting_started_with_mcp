"""Run: uv run python modules/08_server_utilities/python/examples/03_pages_completion.py
Expected: Index, Bulletin; Q1, Q2, Q3, Q4. Empty pages do not end enumeration.
"""

import asyncio

from mcp import Client
from mcp_types import PromptReference

from common.pagination import all_resources, paged_server
from common.reports import make_server


async def main() -> None:
    async with Client(paged_server()) as catalog:
        print([r.name for r in await all_resources(catalog)])
    async with Client(make_server()) as reports:
        result = await reports.complete(
            ref=PromptReference(name="report_brief"), argument={"name": "quarter", "value": "Q"}
        )
        print(result.completion.values)


if __name__ == "__main__":
    asyncio.run(main())
