"""Lumen Ops Server: protocol-only stdio. Inspect with the MCP Inspector CLI."""

from pathlib import Path
from tempfile import TemporaryDirectory

from common.ops import make_server

_temporary = TemporaryDirectory(prefix="lumen-ops-demo-")
server = make_server(Path(_temporary.name) / "tasks.db")

if __name__ == "__main__":
    server.run()
