"""Approve only if the exact full definition fingerprint is unchanged.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/21_production_hosts/python/solutions/01_catalog.py
Capture the related server: uv run python scripts/tier5.py --module 21 --capture
Expected: All contract cases pass.
"""


def solve(reviewed: str, current: str | None):
    return bool(reviewed) and reviewed == current


def main() -> None:
    print("Run scripts/check_exercise.py --module 21 --exercise 1 --solution")


if __name__ == "__main__":
    main()
