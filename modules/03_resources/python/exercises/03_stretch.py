"""Invalidate only the updated URI; preserve unrelated cached values.
Run: uv run python modules/03_resources/python/exercises/03_stretch.py
Check: uv run python scripts/check_exercise.py --module 3 --exercise 3
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(cache: dict, changed_uri: str):
    # YOUR CODE HERE: Invalidate only the updated URI; preserve unrelated cached values.
    return dict(cache)


def main() -> None:
    print(solve(*[{"wiki://index": "index", "lumen://bulletin": "old"}, "lumen://bulletin"]))


if __name__ == "__main__":
    main()
