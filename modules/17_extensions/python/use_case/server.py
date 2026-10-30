"""Lumen module 17 server.
Run: uv run python modules/17_extensions/python/use_case/server.py
Inspect: use the Inspector command in this module's README.
Expected: JSON-RPC stdout only. Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

from common.config import ROOT
from common.extensions import extension_server


def main():
    extension_server(ROOT / ".runtime/module17_tasks.db").run()


if __name__ == "__main__":
    main()
