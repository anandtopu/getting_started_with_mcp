"""Project an issue into concise or detailed output; never include unknown secret fields.
Run: uv run python modules/14_tool_design/python/solutions/01_practice.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(issue: dict, mode: str):
    keys = ["id", "title", "status"]
    if mode == "detailed":
        keys += ["priority", "assignee_id"]
    return {key: issue[key] for key in keys if key in issue}


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
