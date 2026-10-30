"""Host demo server; stdout is reserved for JSON-RPC.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/20_deployment/python/use_case/server.py
Capture the related server: uv run python scripts/tier5.py --module 20 --capture
Expected: JSON-RPC only (launch from a host)
"""

from common.secured_issues import serve as main

if __name__ == "__main__":
    main()
