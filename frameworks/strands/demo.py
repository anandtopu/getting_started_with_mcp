"""Native Strands MCP adapter in its isolated, locked dependency environment.

Run from the course root: uv run python scripts/framework_extras.py strands
Expected: two successful read-only MCP calls and a draft; no Bedrock request.
"""

import argparse
import json
from pathlib import Path

from mcp import StdioServerParameters, stdio_client
from strands.tools.mcp import MCPClient

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-python", required=True)
    args = parser.parse_args()
    params = StdioServerParameters(
        command=args.server_python,
        args=[str(ROOT / "modules/15_agent_frameworks/python/use_case/server.py")],
        cwd=str(ROOT),
    )
    with MCPClient(lambda: stdio_client(params)) as client:
        tools = client.list_tools_sync()
        assert len(tools) == 6
        for index, name in enumerate(("triage_week", "draft_status")):
            result = client.call_tool_sync(f"call-{index}", name, {"week_start": "2026-07-13"})
            assert result["status"] == "success"
        print("PASS Strands adapter:", json.dumps(result))


if __name__ == "__main__":
    main()
