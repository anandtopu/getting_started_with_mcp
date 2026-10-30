"""Project an issue into concise or detailed output; never include unknown secret fields.
Run: uv run python modules/14_tool_design/python/exercises/01_practice.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(issue: dict, mode: str):
    # YOUR CODE HERE: extend this narrower working baseline.
    return issue.copy()


if __name__ == "__main__":
    print(
        solve(
            *[
                {
                    "id": 1,
                    "title": "Release",
                    "status": "open",
                    "priority": "high",
                    "secret": "omit",
                },
                "concise",
            ]
        )
    )
