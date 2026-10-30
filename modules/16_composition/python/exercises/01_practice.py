"""Namespace a safe tool name; reject separators that could impersonate an alias.
Run: uv run python modules/16_composition/python/exercises/01_practice.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(alias: str, name: str):
    # YOUR CODE HERE: extend this narrower working baseline.
    return alias + "__" + name


if __name__ == "__main__":
    print(solve(*["issues", "read_issue"]))
