"""Accept only true/false, ignoring case; return None for invalid settings.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/18_packaging/python/exercises/01_env_bool.py
Capture the related server: uv run python scripts/tier5.py --module 18 --capture
Expected: Starter extension checks fail until implemented.
"""


def solve(value: str):
    return None


def main() -> None:
    print("Run scripts/check_exercise.py --module 18 --exercise 1")


if __name__ == "__main__":
    main()
