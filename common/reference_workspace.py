"""Read the reference server's allowed folder, then retrieve a synthetic file."""

import asyncio

from common.config import ROOT
from common.connections import connection


async def demo() -> None:
    async with connection("files") as client:
        result = await client.call_tool("list_directory", {"path": str(ROOT / "data/files")})
        print(result.model_dump_json(by_alias=True))
        print("In your host, ask: List the files in the allowed Lumen folder. Do not modify them.")


def main() -> None:
    asyncio.run(demo())
