"""Reject repeated or oversized cursors and stop after three pages; empty cursor means done.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/19_registry/python/exercises/02_cursor.py
Capture the related server: uv run python scripts/tier5.py --module 19 --capture
Expected: Starter extension checks fail until implemented.
"""


def solve(cursor: str | None, seen: list[str], pages: int):
    return "continue"


def main() -> None:
    print("Run scripts/check_exercise.py --module 19 --exercise 2")


if __name__ == "__main__":
    main()
