"""Reject changed issue lists and expired continuations; assume one-use storage is separate.
Run: uv run python modules/09_elicitation_sampling_roots/python/exercises/03_retry_binding.py
Expected: prints the first fixture result; check all cases with scripts/check_exercise.py.
"""


def solve(original: list[int], retried: list[int], now: float, expires: float) -> object:
    # YOUR CODE HERE: implement the boundary cases in the docstring.
    return original == retried


if __name__ == "__main__":
    print(solve(*[[1, 2], [1, 2], 9, 10]))
