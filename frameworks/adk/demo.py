"""Native ADK MCP toolset, isolated from the course's newer telemetry packages.

Run: uv run python scripts/framework_extras.py adk
Expected: actual triage and draft tool results; no Gemini request.
"""

import argparse
import asyncio
import json
from pathlib import Path

from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters

ROOT = Path(__file__).resolve().parents[2]


async def run(python):
    params = StdioServerParameters(
        command=python,
        args=[str(ROOT / "modules/15_agent_frameworks/python/use_case/server.py")],
        cwd=str(ROOT),
    )
    toolset = McpToolset(
        connection_params=StdioConnectionParams(server_params=params),
        tool_filter=["triage_week", "draft_status"],
    )
    try:
        tools = {tool.name: tool for tool in await toolset.get_tools()}
        assert set(tools) == {"triage_week", "draft_status"}
        for name in ("triage_week", "draft_status"):
            result = await tools[name].run_async(
                args={"week_start": "2026-07-13"}, tool_context=None
            )
            assert "error" not in result
        print("PASS ADK adapter:", json.dumps(result))
    finally:
        await toolset.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-python", required=True)
    args = parser.parse_args()
    asyncio.run(run(args.server_python))


if __name__ == "__main__":
    main()
