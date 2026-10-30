"""Return a bounded page and its next ID only when additional records exist.
Run: uv run python modules/14_tool_design/python/solutions/02_apply.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(items: list, after: int, limit: int):
    eligible = [item for item in items if item["id"] > after]
    selected = eligible[:limit]
    return {"items": selected, "next_after": selected[-1]["id"] if len(eligible) > limit else None}


if __name__ == "__main__":
    print(solve(*[[{"id": 1}, {"id": 2}, {"id": 3}], 0, 2]))
