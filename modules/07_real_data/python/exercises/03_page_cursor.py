"""Return the next offset only when the fetched extra row proves more data exists.
Run: uv run python modules/07_real_data/python/exercises/03_page_cursor.py
Expected: prints the first fixture result; check all cases with scripts/check_exercise.py.
"""


def solve(offset: int, limit: int, fetched: int) -> object:
    # YOUR CODE HERE: implement the boundary cases in the docstring.
    return offset + limit


if __name__ == "__main__":
    print(solve(*[0, 10, 11]))
