"""Read-only triage tools shared by all six frameworks.

Run: uv run python modules/15_agent_frameworks/python/use_case/server.py
Inspect: use the Inspector command in this module's README.
Expected: six tools on the protocol stream; no ordinary stdout logging.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

from common.tool_design import task_server


def main():
    task_server().run()


if __name__ == "__main__":
    main()
