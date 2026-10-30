"""Reject any archive member with traversal, absolute paths, or private environment/git files
(Windows paths included).
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/18_packaging/python/solutions/03_inventory.py
Capture the related server: uv run python scripts/tier5.py --module 18 --capture
Expected: All contract cases pass.
"""


def solve(names: list[str]):
    from pathlib import PurePosixPath, PureWindowsPath

    for name in names:
        path = PurePosixPath(name.replace("\\", "/"))
        if path.is_absolute() or PureWindowsPath(name).drive or ".." in path.parts:
            return False
        if any(part == ".git" or part == ".env" or part.startswith(".env.") for part in path.parts):
            return False
    return True


def main() -> None:
    print("Run scripts/check_exercise.py --module 18 --exercise 3 --solution")


if __name__ == "__main__":
    main()
