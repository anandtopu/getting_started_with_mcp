"""Accept HTTPS public URLs or exact loopback HTTP, rejecting credentials/query/fragment.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/20_deployment/python/exercises/01_endpoint.py
Capture the related server: uv run python scripts/tier5.py --module 20 --capture
Expected: Starter extension checks fail until implemented.
"""


def solve(value: str):
    return False


def main() -> None:
    print("Run scripts/check_exercise.py --module 20 --exercise 1")


if __name__ == "__main__":
    main()
