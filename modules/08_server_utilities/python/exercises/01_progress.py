"""Convert completed work to bounded integer percentage, including a zero total.
Run: uv run python modules/08_server_utilities/python/exercises/01_progress.py
Expected: prints the first fixture result; check all cases with scripts/check_exercise.py.
"""


def solve(completed: int, total: int) -> object:
    # YOUR CODE HERE: Convert completed work to bounded integer percentage, including a zero total.
    return completed * 100 // total if total else 0


if __name__ == "__main__":
    print(solve(*[1, 4]))
