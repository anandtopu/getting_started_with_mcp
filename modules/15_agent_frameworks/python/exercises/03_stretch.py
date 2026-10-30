"""Normalize structured tool results and text JSON without losing the published flag.
Run: uv run python modules/15_agent_frameworks/python/exercises/03_stretch.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(result: dict):
    # YOUR CODE HERE: extend this narrower working baseline.
    return result


if __name__ == "__main__":
    print(solve(*[{"structuredContent": {"published": False}}]))
