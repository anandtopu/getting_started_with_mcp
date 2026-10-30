"""Retry a read, or a write with a server-enforced operation key; a lost response proves no outcome.
Run: uv run python modules/10_streamable_http/python/exercises/03_retry_policy.py
Expected: prints the first fixture result; check all cases with scripts/check_exercise.py.
"""


def solve(operation: str, has_key: bool) -> object:
    # YOUR CODE HERE: implement the boundary cases in the docstring.
    return operation == "read"


if __name__ == "__main__":
    print(solve(*["read", False]))
