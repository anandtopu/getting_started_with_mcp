"""Run: uv run python modules/07_real_data/python/examples/03_rest_wrapper.py
Expected: server waits for MCP requests. Verify with scripts/tier2.py --module 7.
"""

from common.rest import make_server

if __name__ == "__main__":
    make_server().run()
