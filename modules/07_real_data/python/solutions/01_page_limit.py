"""Clamp requested pages to 1–50 rows.
Run: uv run python modules/07_real_data/python/solutions/01_page_limit.py
Expected: prints the first fixture result; check all cases with scripts/check_exercise.py.
"""


def solve(requested: int) -> object:
    return max(1, min(50, requested))


if __name__ == "__main__":
    print(solve(*[0]))
