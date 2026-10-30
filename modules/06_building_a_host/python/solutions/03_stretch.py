"""Ignore model confirmation; inject True only after a trusted human decision, else return None.
Run: uv run python modules/06_building_a_host/python/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py --module 6 --exercise 3 --solution
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(arguments: dict, approved: bool):
    return {**arguments, "confirmed": True} if approved else None


def main() -> None:
    print(solve(*[{"title": "Review", "confirmed": True}, False]))


if __name__ == "__main__":
    main()
