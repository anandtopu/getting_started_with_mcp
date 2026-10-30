"""Clamp requested pages to 1–50 rows.
Run: uv run python modules/07_real_data/python/exercises/01_page_limit.py
Expected: prints the first fixture result; check all cases with scripts/check_exercise.py.
"""


def solve(requested: int) -> object:
    # YOUR CODE HERE: Clamp requested pages to 1–50 rows.
    return min(50, requested)


if __name__ == "__main__":
    print(solve(*[0]))
