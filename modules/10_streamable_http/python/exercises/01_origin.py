"""Accept absent Origin or exactly the configured browser origin.
Run: uv run python modules/10_streamable_http/python/exercises/01_origin.py
Expected: prints the first fixture result; check all cases with scripts/check_exercise.py.
"""


def solve(origin: str | None) -> object:
    # YOUR CODE HERE: Accept absent Origin or exactly the configured browser origin.
    return origin == "http://localhost:3000"


if __name__ == "__main__":
    print(solve(*[None]))
