"""Distinguish protocol errors, tool failures, and successful responses.
Run: uv run python modules/05_first_client/python/solutions/02_apply.py
Check: uv run python scripts/check_exercise.py --module 5 --exercise 2 --solution
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(message: dict):
    return (
        "protocol"
        if "error" in message
        else "tool"
        if message.get("result", {}).get("isError")
        else "success"
    )


def main() -> None:
    print(solve(*[{"error": {"code": -32601}}]))


if __name__ == "__main__":
    main()
