"""Stop at the deadline; progress never extends the absolute budget.
Run: uv run python modules/08_server_utilities/python/exercises/03_deadlines.py
Expected: prints the first fixture result; check all cases with scripts/check_exercise.py.
"""


def solve(now: float, deadline: float) -> object:
    # YOUR CODE HERE: Stop at the deadline; progress never extends the absolute budget.
    return now <= deadline


if __name__ == "__main__":
    print(solve(*[1.0, 2.0]))
