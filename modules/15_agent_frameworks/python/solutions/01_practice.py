"""Allow only the two reviewed read tools; wildcard names must not grant access.
Run: uv run python modules/15_agent_frameworks/python/solutions/01_practice.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(name: str):
    return name in {"triage_week", "draft_status"}


if __name__ == "__main__":
    print(solve(*["triage_week"]))
