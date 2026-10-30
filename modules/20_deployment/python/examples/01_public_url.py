"""Separate local development URLs from public TLS endpoints.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/20_deployment/python/examples/01_public_url.py
Capture the related server: uv run python scripts/tier5.py --module 20 --capture
Expected: Public endpoints require HTTPS; HTTP is loopback-only.
"""

from common.deployment import public_url


def main() -> None:
    print(public_url("https://issues.example/mcp"))
    # KEY IDEA: local HTTP is an explicit loopback exception.
    try:
        public_url("http://issues.example/mcp")
    except ValueError as error:
        print(error)


if __name__ == "__main__":
    main()
