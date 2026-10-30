"""Register a typed tool; its hints and description become the input schema.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/02_first_server_tools/python/examples/01_hello_server.py
Expected: Inspector welcome(name="Alex") -> Welcome to Lumen Labs, Alex!
Inspect/capture: uv run python scripts/tier1.py --module 2 --capture
"""

from typing import Annotated

from mcp.server import MCPServer
from pydantic import Field

from common.notes import READ

server = MCPServer("Lumen hello", version="1.0")


@server.tool(title="Welcome a teammate", annotations=READ)
def welcome(name: Annotated[str, Field(min_length=1, max_length=60)]) -> str:
    """Welcome a synthetic teammate to Lumen Labs; provide their display name."""
    return f"Welcome to Lumen Labs, {name}!"


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
