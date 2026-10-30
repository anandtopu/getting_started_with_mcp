"""Return a configured route only; unknown names must return None.
Run: uv run python modules/06_building_a_host/python/exercises/02_apply.py
Check: uv run python scripts/check_exercise.py --module 6 --exercise 2
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(name: str, routes: dict):
    # YOUR CODE HERE: Return a configured route only; unknown names must return None.
    return name.split("__", 1)


def main() -> None:
    print(solve(*["notes__search", {"notes__search": ["notes", "search"]}]))


if __name__ == "__main__":
    main()
