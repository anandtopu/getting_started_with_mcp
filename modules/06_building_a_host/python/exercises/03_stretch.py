"""Ignore model confirmation; inject True only after a trusted human decision, else return None.
Run: uv run python modules/06_building_a_host/python/exercises/03_stretch.py
Check: uv run python scripts/check_exercise.py --module 6 --exercise 3
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(arguments: dict, approved: bool):
    # YOUR CODE HERE: Inject confirmation only after a trusted human decision.
    return dict(arguments)


def main() -> None:
    print(solve(*[{"title": "Review", "confirmed": True}, False]))


if __name__ == "__main__":
    main()
