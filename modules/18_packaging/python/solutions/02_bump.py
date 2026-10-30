"""Classify tool changes: removed or newly required inputs need major; additive optional inputs
need minor; docs-only patch.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/18_packaging/python/solutions/02_bump.py
Capture the related server: uv run python scripts/tier5.py --module 18 --capture
Expected: All contract cases pass.
"""


def solve(change: str):
    return (
        "major"
        if change in {"removed", "required"}
        else "minor"
        if change == "optional"
        else "patch"
    )


def main() -> None:
    print("Run scripts/check_exercise.py --module 18 --exercise 2 --solution")


if __name__ == "__main__":
    main()
