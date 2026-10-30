"""Allow a reviewed installation only when identity, source and requested permissions are
approved and an exact version is pinned.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/19_registry/python/exercises/03_install_policy.py
Capture the related server: uv run python scripts/tier5.py --module 19 --capture
Expected: Starter extension checks fail until implemented.
"""


def solve(review: dict):
    return False


def main() -> None:
    print("Run scripts/check_exercise.py --module 19 --exercise 3")


if __name__ == "__main__":
    main()
