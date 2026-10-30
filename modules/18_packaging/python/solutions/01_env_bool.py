"""Accept only true/false, ignoring case; return None for invalid settings.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/18_packaging/python/solutions/01_env_bool.py
Capture the related server: uv run python scripts/tier5.py --module 18 --capture
Expected: All contract cases pass.
"""


def solve(value: str):
    return {"true": True, "false": False}.get(value.lower())


def main() -> None:
    print("Run scripts/check_exercise.py --module 18 --exercise 1 --solution")


if __name__ == "__main__":
    main()
