"""Run: uv run python modules/08_server_utilities/python/examples/01_context_lifespan.py
Expected: server waits for MCP requests. Verify with scripts/tier2.py --module 8.
"""

from common.reports import make_server

if __name__ == "__main__":
    make_server().run()
