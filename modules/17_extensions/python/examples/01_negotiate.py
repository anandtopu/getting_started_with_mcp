"""Plain clients receive a complete text report; Tasks clients negotiate per request.
Run: uv run python modules/17_extensions/python/examples/01_negotiate.py
Wire: uv run python scripts/tier4.py --module 17 --capture
Expected: PASS and real synthetic Lumen results.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

import asyncio
import tempfile
from pathlib import Path

from mcp import Client

from common.connections import discover
from common.extensions import extension_server
from common.report_tasks import TasksClient


async def main():
    with tempfile.TemporaryDirectory() as directory:
        for enabled in [False, True]:
            async with Client(
                extension_server(Path(directory) / "tasks.db"),
                extensions=[TasksClient()] if enabled else None,
            ) as client:
                capabilities = (await discover(client)).capabilities
                assert "io.modelcontextprotocol/tasks" in capabilities.extensions
                result = await client.call_tool("quarterly_report", {})
                assert result.structured_content["total"] == 400
                print(
                    "PASS negotiated Tasks:" if enabled else "PASS plain fallback:",
                    result.structured_content,
                )


if __name__ == "__main__":
    asyncio.run(main())
