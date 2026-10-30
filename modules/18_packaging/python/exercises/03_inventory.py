"""Reject any archive member with traversal, absolute paths, or private environment/git files
(Windows paths included).
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/18_packaging/python/exercises/03_inventory.py
Capture the related server: uv run python scripts/tier5.py --module 18 --capture
Expected: Starter extension checks fail until implemented.
"""


def solve(names: list[str]):
    return True


def main() -> None:
    print("Run scripts/check_exercise.py --module 18 --exercise 3")


if __name__ == "__main__":
    main()
