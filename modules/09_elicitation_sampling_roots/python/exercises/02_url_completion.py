"""A URL accept must also have a completed out-of-band grant.
Run: uv run python modules/09_elicitation_sampling_roots/python/exercises/02_url_completion.py
Expected: prints the first fixture result; check all cases with scripts/check_exercise.py.
"""


def solve(action: str, completed: bool) -> object:
    # YOUR CODE HERE: A URL accept must also have a completed out-of-band grant.
    return action == "accept"


if __name__ == "__main__":
    print(solve(*["accept", True]))
