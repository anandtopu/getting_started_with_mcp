"""Run: uv run python modules/07_real_data/python/examples/01_issue_crud.py
Expected: server waits for MCP requests. Verify with scripts/tier2.py --module 7.
"""

from common.issues import make_server

if __name__ == "__main__":
    make_server().run()
