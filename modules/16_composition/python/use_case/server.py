"""Lumen module 16 server.
Run: uv run python modules/16_composition/python/use_case/server.py
Inspect: use the Inspector command in this module's README.
Expected: JSON-RPC stdout only. Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

from common.config import ROOT
from common.gateway import gateway_server


def main():
    server, _, _ = gateway_server(ROOT / ".runtime/module16_tasks.db")
    server.run()


if __name__ == "__main__":
    main()
