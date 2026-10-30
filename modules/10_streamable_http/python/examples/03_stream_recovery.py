"""Run: uv run python modules/10_streamable_http/python/examples/03_stream_recovery.py
Expected: PASS HTTP checks after closing, reissuing, and refetching a subscription.
"""

import asyncio

from scripts.http_lab import http_client, running_server
from scripts.tier2 import stream_checks


async def main() -> None:
    async with running_server(
        "modules/10_streamable_http/python/examples/01_http_server.py"
    ) as url:
        async with http_client(url) as (client, http):
            await stream_checks(client)
    print("PASS HTTP checks")


if __name__ == "__main__":
    asyncio.run(main())
