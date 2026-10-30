"""Assess a risky third-party metadata fixture without installing anything.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/19_registry/python/examples/03_review.py
Capture the related server: uv run python scripts/tier5.py --module 19 --capture
Expected: four review flags; automatic_install_allowed False
"""

from common.registry import review_candidate


def main() -> None:
    # KEY IDEA: a registry listing is a starting point for source/permission review.
    result = review_candidate({"version": "latest", "permissions": ["home"], "installScript": True})
    print(result)
    assert not result["automatic_install_allowed"] and len(result["flags"]) == 4


if __name__ == "__main__":
    main()
