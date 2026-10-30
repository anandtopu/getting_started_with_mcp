"""Build a deterministic tool-name catalog: distinct names, sorted, with an optional prefix.
Run: uv run python modules/14_tool_design/python/exercises/03_stretch.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(names: list[str], prefix: str):
    # YOUR CODE HERE: extend this narrower working baseline.
    return names


if __name__ == "__main__":
    print(solve(*[["wiki_read", "issue_read", "issue_read"], "issue"]))
