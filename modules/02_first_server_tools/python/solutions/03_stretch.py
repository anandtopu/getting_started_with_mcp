"""Add a tag idempotently while preserving insertion order and the original list.
Run: uv run python modules/02_first_server_tools/python/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py --module 2 --exercise 3 --solution
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(tags: list[str], tag: str):
    return list(tags) if tag in tags else [*tags, tag]


def main() -> None:
    print(solve(*[["release"], "release"]))


if __name__ == "__main__":
    main()
