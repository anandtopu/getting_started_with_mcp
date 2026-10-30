"""Validate known wiki segments before assembling a URI; return None for unknown pages.
Run: uv run python modules/03_resources/python/exercises/01_practice.py
Check: uv run python scripts/check_exercise.py --module 3 --exercise 1
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(space: str, page: str):
    # YOUR CODE HERE: Validate wiki segments; return None for unknown pages.
    return f"wiki://{space}/{page}"


def main() -> None:
    print(solve(*["engineering", "page-01"]))


if __name__ == "__main__":
    main()
