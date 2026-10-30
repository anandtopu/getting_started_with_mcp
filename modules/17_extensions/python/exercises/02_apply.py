"""Distinguish a completed tool error from a failed protocol operation.
Run: uv run python modules/17_extensions/python/exercises/02_apply.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(state: dict):
    # YOUR CODE HERE: extend this narrower working baseline.
    return state["status"]


if __name__ == "__main__":
    print(solve(*[{"status": "completed", "result": {"isError": True}}]))
