"""Require read permission, then require write permission for a changing tool.
Run: uv run python modules/16_composition/python/solutions/02_apply.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(read_only: bool, scopes: list[str]):
    return "workspace:read" in scopes and (read_only or "workspace:write" in scopes)


if __name__ == "__main__":
    print(solve(*[True, ["workspace:read"]]))
