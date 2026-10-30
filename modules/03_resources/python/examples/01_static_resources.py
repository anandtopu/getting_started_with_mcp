"""Read a static text resource and a base64-encoded PDF.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/03_resources/python/examples/01_static_resources.py
Expected: text/plain and application/pdf with nonzero content lengths
Inspect/capture: uv run python scripts/tier1.py --module 3 --capture
"""

import asyncio

from mcp import Client

from common.wiki import wiki_server


async def main() -> None:
    async with Client(wiki_server()) as client:
        print([r.uri for r in (await client.list_resources()).resources])
        for uri in ["wiki://index", "lumen://contract/1"]:
            result = await client.read_resource(uri)
            content = result.contents[0]
            print(
                content.mime_type, len(getattr(content, "text", "") or getattr(content, "blob", ""))
            )


if __name__ == "__main__":
    asyncio.run(main())
