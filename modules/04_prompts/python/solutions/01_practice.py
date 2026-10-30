"""Filter wiki spaces by a case-sensitive prefix.
Run: uv run python modules/04_prompts/python/solutions/01_practice.py
Check: uv run python scripts/check_exercise.py --module 4 --exercise 1 --solution
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(prefix: str):
    from common.wiki import SPACES

    return [space for space in SPACES if space.startswith(prefix)]


def main() -> None:
    print(solve(*["eng"]))


if __name__ == "__main__":
    main()
