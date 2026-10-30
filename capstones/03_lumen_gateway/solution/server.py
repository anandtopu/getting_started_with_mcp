"""Lumen Gateway: protocol-only stdio. Inspect with the MCP Inspector CLI."""

from pathlib import Path
from tempfile import TemporaryDirectory

from common.gateway import gateway_server

_temporary = TemporaryDirectory(prefix="lumen-gateway-demo-")
server, _, _ = gateway_server(Path(_temporary.name) / "tasks.db")

if __name__ == "__main__":
    server.run()
