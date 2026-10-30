"""Lumen module 14 server.
Run: uv run python modules/14_tool_design/python/use_case/server.py
Inspect: use the Inspector command in this module's README.
Expected: JSON-RPC stdout only. Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

from common.tool_design import task_server


def main():
    task_server().run()


if __name__ == "__main__":
    main()
