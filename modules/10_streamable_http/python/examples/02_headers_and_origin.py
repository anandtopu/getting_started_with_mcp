"""Run: uv run python modules/10_streamable_http/python/examples/02_headers_and_origin.py
Expected: PASS HTTP checks after rejecting bad headers and testing CORS preflight.
"""

import asyncio

from scripts.http_lab import http_client, running_server
from scripts.tier2 import header_checks


async def main() -> None:
    async with running_server(
        "modules/10_streamable_http/python/examples/01_http_server.py"
    ) as url:
        async with http_client(url) as (client, http):
            await header_checks(http, url)
    print("PASS HTTP checks")


if __name__ == "__main__":
    asyncio.run(main())
