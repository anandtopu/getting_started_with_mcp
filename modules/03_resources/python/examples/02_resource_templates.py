"""Resolve a URI template and follow a tool-produced resource link.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/03_resources/python/examples/02_resource_templates.py
Expected: wiki://{space}/{page} and the engineering page-01 Markdown
Inspect/capture: uv run python scripts/tier1.py --module 3 --capture
"""

import asyncio

from mcp import Client
from mcp_types import ResourceTemplateReference

from common.wiki import wiki_server


async def main() -> None:
    async with Client(wiki_server()) as client:
        print((await client.list_resource_templates()).resource_templates)
        suggestions = await client.complete(
            ref=ResourceTemplateReference(uri="wiki://{space}/{page}"),
            argument={"name": "space", "value": "eng"},
        )
        print("Template suggestions:", suggestions.completion.values)
        result = await client.call_tool("find_page", {"space": "engineering", "page": "page-01"})
        link = result.content[0]
        print((await client.read_resource(str(link.uri))).contents[0].text)


if __name__ == "__main__":
    asyncio.run(main())
