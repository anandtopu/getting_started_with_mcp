"""Preserve the request ID when constructing a JSON-RPC result.
Run: uv run python modules/01_architecture_wire/python/solutions/01_practice.py
Check: uv run python scripts/check_exercise.py --module 1 --exercise 1 --solution
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(request: dict, result: dict):
    return {"jsonrpc": "2.0", "id": request["id"], "result": result}


def main() -> None:
    print(solve(*[{"id": "read-7"}, {"resultType": "complete"}]))


if __name__ == "__main__":
    main()
