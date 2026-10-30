"""Validate known wiki segments before assembling a URI; return None for unknown pages.
Run: uv run python modules/03_resources/python/solutions/01_practice.py
Check: uv run python scripts/check_exercise.py --module 3 --exercise 1 --solution
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(space: str, page: str):
    from common.wiki import SPACES

    return (
        f"wiki://{space}/{page}"
        if space in SPACES and page in {f"page-{i:02d}" for i in range(1, 9)}
        else None
    )


def main() -> None:
    print(solve(*["engineering", "page-01"]))


if __name__ == "__main__":
    main()
