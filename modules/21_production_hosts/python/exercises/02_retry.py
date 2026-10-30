"""Retry once only when local policy marks a read safe and there is a transport failure.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/21_production_hosts/python/exercises/02_retry.py
Capture the related server: uv run python scripts/tier5.py --module 21 --capture
Expected: Starter extension checks fail until implemented.
"""


def solve(safe_read: bool, transport_error: bool, attempts: int):
    return False


def main() -> None:
    print("Run scripts/check_exercise.py --module 21 --exercise 2")


if __name__ == "__main__":
    main()
