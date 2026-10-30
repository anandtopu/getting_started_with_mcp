"""Continue pagination by nextCursor even if the current page is empty.
Run: uv run python modules/05_first_client/python/exercises/01_practice.py
Check: uv run python scripts/check_exercise.py --module 5 --exercise 1
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(page: dict):
    # YOUR CODE HERE: Continue pagination by nextCursor even if the current page is empty.
    return page.get("nextCursor") if page.get("resources") else None


def main() -> None:
    print(solve(*[{"resources": [], "nextCursor": "next"}]))


if __name__ == "__main__":
    main()
