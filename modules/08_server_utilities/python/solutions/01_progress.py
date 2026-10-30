"""Convert completed work to bounded integer percentage, including a zero total.
Run: uv run python modules/08_server_utilities/python/solutions/01_progress.py
Expected: prints the first fixture result; check all cases with scripts/check_exercise.py.
"""


def solve(completed: int, total: int) -> object:
    return 0 if total <= 0 else max(0, min(100, completed * 100 // total))


if __name__ == "__main__":
    print(solve(*[1, 4]))
