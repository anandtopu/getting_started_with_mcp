"""Distinguish a completed tool error from a failed protocol operation.
Run: uv run python modules/17_extensions/python/solutions/02_apply.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(state: dict):
    status = state["status"]
    if status == "completed":
        return "tool_error" if state["result"].get("isError") else "success"
    return status


if __name__ == "__main__":
    print(solve(*[{"status": "completed", "result": {"isError": True}}]))
