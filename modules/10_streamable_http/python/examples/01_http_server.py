"""Run: uv run python modules/10_streamable_http/python/examples/01_http_server.py
Expected: server waits for MCP requests. Verify with scripts/tier2.py --module 10.
"""

from common.http_server import serve

if __name__ == "__main__":
    serve()
