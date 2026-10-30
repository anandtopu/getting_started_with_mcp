"""Invalidate only the updated URI; preserve unrelated cached values.
Run: uv run python modules/03_resources/python/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py --module 3 --exercise 3 --solution
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(cache: dict, changed_uri: str):
    return {uri: value for uri, value in cache.items() if uri != changed_uri}


def main() -> None:
    print(solve(*[{"wiki://index": "index", "lumen://bulletin": "old"}, "lumen://bulletin"]))


if __name__ == "__main__":
    main()
