"""Reject repeated or oversized cursors and stop after three pages; empty cursor means done.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/19_registry/python/solutions/02_cursor.py
Capture the related server: uv run python scripts/tier5.py --module 19 --capture
Expected: All contract cases pass.
"""


def solve(cursor: str | None, seen: list[str], pages: int):
    return (
        "done"
        if not cursor
        else "reject"
        if cursor in seen or len(cursor) > 2000 or pages >= 3
        else "continue"
    )


def main() -> None:
    print("Run scripts/check_exercise.py --module 19 --exercise 2 --solution")


if __name__ == "__main__":
    main()
