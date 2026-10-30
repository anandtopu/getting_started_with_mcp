"""Filter relative filenames, rejecting absolute paths, parent segments, and backslash traversal.
Run: uv run python modules/00_setup/python/solutions/02_apply.py
Check: uv run python scripts/check_exercise.py --module 0 --exercise 2 --solution
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(names: list[str]):
    from pathlib import PurePosixPath, PureWindowsPath

    return [
        name
        for name in names
        if not PurePosixPath(name).is_absolute()
        and not PureWindowsPath(name).drive
        and ".." not in name.replace("\\", "/").split("/")
        and not name.startswith("\\")
    ]


def main() -> None:
    print(solve(*[["notes/a.md", "../secret", "C:/secret", "/tmp/x", "..\\secret"]]))


if __name__ == "__main__":
    main()
