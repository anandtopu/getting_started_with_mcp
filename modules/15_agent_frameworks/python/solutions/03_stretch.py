"""Normalize structured tool results and text JSON without losing the published flag.
Run: uv run python modules/15_agent_frameworks/python/solutions/03_stretch.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(result: dict):
    if "structuredContent" in result:
        return result["structuredContent"]
    import json

    return json.loads(result["content"][0]["text"])


if __name__ == "__main__":
    print(solve(*[{"structuredContent": {"published": False}}]))
