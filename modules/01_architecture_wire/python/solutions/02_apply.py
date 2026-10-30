"""Identify a valid method notification without treating errors as notifications.
Run: uv run python modules/01_architecture_wire/python/solutions/02_apply.py
Check: uv run python scripts/check_exercise.py --module 1 --exercise 2 --solution
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(message: dict):
    return (
        message.get("jsonrpc") == "2.0"
        and isinstance(message.get("method"), str)
        and "id" not in message
    )


def main() -> None:
    print(solve(*[{"jsonrpc": "2.0", "method": "ping"}]))


if __name__ == "__main__":
    main()
