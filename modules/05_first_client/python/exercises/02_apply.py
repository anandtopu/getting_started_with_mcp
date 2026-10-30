"""Distinguish protocol errors, tool failures, and successful responses.
Run: uv run python modules/05_first_client/python/exercises/02_apply.py
Check: uv run python scripts/check_exercise.py --module 5 --exercise 2
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(message: dict):
    # YOUR CODE HERE: Distinguish protocol errors, tool failures, and successful responses.
    return "protocol" if "error" in message else "success"


def main() -> None:
    print(solve(*[{"error": {"code": -32601}}]))


if __name__ == "__main__":
    main()
