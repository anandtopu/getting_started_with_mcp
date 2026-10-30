"""Validate the actual server.json against the vendored official schema.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/19_registry/python/examples/01_metadata.py
Capture the related server: uv run python scripts/tier5.py --module 19 --capture
Expected: io.github.anandtopu/lumen-notes anandtopu 1.0.0
"""

from common.registry import namespace_owner, validate_metadata


def main() -> None:
    document = validate_metadata()
    # KEY IDEA: local schema validation does not prove namespace ownership.
    print(document["name"], namespace_owner(document["name"]), document["version"])


if __name__ == "__main__":
    main()
