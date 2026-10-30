"""Identify a valid method notification without treating errors as notifications.
Run: uv run python modules/01_architecture_wire/python/exercises/02_apply.py
Check: uv run python scripts/check_exercise.py --module 1 --exercise 2
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(message: dict):
    # YOUR CODE HERE: Identify a valid method notification without treating errors as notifications.
    return "id" not in message


def main() -> None:
    print(solve(*[{"jsonrpc": "2.0", "method": "ping"}]))


if __name__ == "__main__":
    main()
