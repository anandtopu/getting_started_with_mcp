"""Inspect the committed Lumen fixtures through the official MCP SDK.

Run: uv run python scripts/foundation_server.py
Inspector: npm run inspector -- uv run python scripts/foundation_server.py
Expected: protocol messages only on stdout; tool dataset_counts returns counts.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

import json

from mcp.server import MCPServer
from mcp_types import ToolAnnotations

from common.data import load_json, readonly_database

server = MCPServer("Lumen foundation")


@server.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False
    )
)
def dataset_counts() -> dict[str, int]:
    """Count synthetic employees and issues. Reads committed fixtures without changing them."""
    with readonly_database("issues.db") as db:
        issues = db.execute("SELECT COUNT(*) FROM issues").fetchone()[0]
    return {"employees": len(load_json("directory/employees.json")), "issues": issues}


@server.resource("lumen://dataset/summary", mime_type="application/json")
def summary() -> str:
    """The size of the synthetic workspace."""
    return json.dumps(dataset_counts())


@server.prompt()
def explain_dataset() -> str:
    """Ask an assistant to explain what the synthetic fixtures contain."""
    return "Explain this synthetic Lumen Labs dataset: " + summary()


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
