"""Run: uv run python modules/07_real_data/python/examples/02_readonly_analytics.py
Expected: server waits for MCP requests. Verify with scripts/tier2.py --module 7.
"""

from common.analytics import make_server

if __name__ == "__main__":
    make_server().run()
