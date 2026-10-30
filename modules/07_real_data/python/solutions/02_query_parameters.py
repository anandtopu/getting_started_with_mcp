"""Return SQL and a separate parameter list; never interpolate the title.
Run: uv run python modules/07_real_data/python/solutions/02_query_parameters.py
Expected: prints the first fixture result; check all cases with scripts/check_exercise.py.
"""


def solve(title: str) -> object:
    return ["SELECT id FROM issues WHERE title=?", [title]]


if __name__ == "__main__":
    print(solve(*["Release"]))
