"""Preserve the request ID when constructing a JSON-RPC result.
Run: uv run python modules/01_architecture_wire/python/exercises/01_practice.py
Check: uv run python scripts/check_exercise.py --module 1 --exercise 1
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(request: dict, result: dict):
    # YOUR CODE HERE: Preserve the request ID when constructing a JSON-RPC result.
    return {"jsonrpc": "2.0", "id": 0, "result": result}


def main() -> None:
    print(solve(*[{"id": "read-7"}, {"resultType": "complete"}]))


if __name__ == "__main__":
    main()
