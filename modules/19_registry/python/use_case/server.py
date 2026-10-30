"""Host demo server; stdout is reserved for JSON-RPC.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/19_registry/python/use_case/server.py
Capture the related server: uv run python scripts/tier5.py --module 19 --capture
Expected: JSON-RPC only (launch from a host)
"""

from common.distributed_notes import main

if __name__ == "__main__":
    main()
