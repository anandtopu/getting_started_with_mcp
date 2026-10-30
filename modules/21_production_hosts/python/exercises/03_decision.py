"""Accept a decision only for the current unexpired unanswered question ID.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/21_production_hosts/python/exercises/03_decision.py
Capture the related server: uv run python scripts/tier5.py --module 21 --capture
Expected: Starter extension checks fail until implemented.
"""


def solve(current: str, received: str, expired: bool, answered: bool):
    return True


def main() -> None:
    print("Run scripts/check_exercise.py --module 21 --exercise 3")


if __name__ == "__main__":
    main()
