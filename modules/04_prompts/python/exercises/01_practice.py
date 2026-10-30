"""Filter wiki spaces by a case-sensitive prefix.
Run: uv run python modules/04_prompts/python/exercises/01_practice.py
Check: uv run python scripts/check_exercise.py --module 4 --exercise 1
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(prefix: str):
    # YOUR CODE HERE: Filter wiki spaces by a case-sensitive prefix.
    from common.wiki import SPACES

    return list(SPACES)


def main() -> None:
    print(solve(*["eng"]))


if __name__ == "__main__":
    main()
