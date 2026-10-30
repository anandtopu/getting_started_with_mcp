"""Approve only accept plus a real boolean true; reject strings.
Run: uv run python modules/09_elicitation_sampling_roots/python/solutions/01_form_decision.py
Expected: prints the first fixture result; check all cases with scripts/check_exercise.py.
"""


def solve(action: str, approve: object) -> object:
    return action == "accept" and approve is True


if __name__ == "__main__":
    print(solve(*["accept", True]))
