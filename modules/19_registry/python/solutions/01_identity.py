"""Require matching nonempty registry identity and package mcpName.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/19_registry/python/solutions/01_identity.py
Capture the related server: uv run python scripts/tier5.py --module 19 --capture
Expected: All contract cases pass.
"""


def solve(registry: str, package: str):
    return bool(registry) and registry == package


def main() -> None:
    print("Run scripts/check_exercise.py --module 19 --exercise 1 --solution")


if __name__ == "__main__":
    main()
