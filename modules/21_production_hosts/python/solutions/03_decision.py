"""Accept a decision only for the current unexpired unanswered question ID.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/21_production_hosts/python/solutions/03_decision.py
Capture the related server: uv run python scripts/tier5.py --module 21 --capture
Expected: All contract cases pass.
"""


def solve(current: str, received: str, expired: bool, answered: bool):
    return bool(current) and current == received and not expired and not answered


def main() -> None:
    print("Run scripts/check_exercise.py --module 21 --exercise 3 --solution")


if __name__ == "__main__":
    main()
