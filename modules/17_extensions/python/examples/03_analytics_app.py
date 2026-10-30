"""Read tool/UI metadata and the self-contained dashboard; render it in an Apps-aware host.
Run: uv run python modules/17_extensions/python/examples/03_analytics_app.py
Wire: uv run python scripts/tier4.py --module 17 --capture
Expected: PASS and real synthetic Lumen results.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

import asyncio
import tempfile
from pathlib import Path

from mcp import Client

from common.extensions import APP_URI, extension_server


async def main():
    with tempfile.TemporaryDirectory() as directory:
        async with Client(extension_server(Path(directory) / "tasks.db")) as client:
            result = await client.call_tool("analytics_dashboard", {})
            tool = next(
                t for t in (await client.list_tools()).tools if t.name == "analytics_dashboard"
            )
            assert tool.meta["ui"]["resourceUri"] == APP_URI
            resource = (await client.read_resource(APP_URI)).contents[0]
            assert resource.mime_type == "text/html;profile=mcp-app"
            print("PASS dashboard:", result.structured_content)
            print(
                "HTML bytes:",
                len(resource.text.encode()),
                "; open in an Apps-aware host to interact.",
            )


if __name__ == "__main__":
    asyncio.run(main())
