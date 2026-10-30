"""DELIBERATELY VULNERABLE fixture-only lab. No real data access.

Run: uv run python data/security/vulnerable_server.py --lab
Expected: stdio MCP; fixture_salary exposes synthetic data without authorization.
"""
import argparse
from mcp.server import MCPServer
from mcp_types import ToolAnnotations

server = MCPServer("DELIBERATELY VULNERABLE synthetic lab")

@server.tool(annotations=ToolAnnotations(read_only_hint=True, destructive_hint=False,
                                       idempotent_hint=True, open_world_hint=False))
def fixture_salary(employee_id: int) -> dict[str, int | bool]:
    """Return a fake salary. LAB FLAW: missing per-user authorization."""
    return {"employee_id": employee_id, "salary": 100000, "synthetic": True}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lab", action="store_true", required=True)
    parser.parse_args()
    server.run()

if __name__ == "__main__":
    main()
