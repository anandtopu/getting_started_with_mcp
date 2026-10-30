"""Namespace a safe tool name; reject separators that could impersonate an alias.
Run: uv run python modules/16_composition/python/solutions/01_practice.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(alias: str, name: str):
    import re

    if not all(
        re.fullmatch(r"[a-z][a-z0-9_]*", value) and "__" not in value for value in [alias, name]
    ):
        return None
    value = alias + "__" + name
    return value if len(value) <= 64 else None


if __name__ == "__main__":
    print(solve(*["issues", "read_issue"]))
