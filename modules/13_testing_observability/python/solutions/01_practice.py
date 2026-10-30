"""Accept only JSON-RPC object lines on protocol stdout, not arbitrary JSON or debug text.
Run: uv run python modules/13_testing_observability/python/solutions/01_practice.py
Expected: print one baseline result; run the shared exercise checker for all cases.
"""


def solve(lines: list[str]):
    import json

    try:
        values = [json.loads(line) for line in lines]
        return all(isinstance(value, dict) and value.get("jsonrpc") == "2.0" for value in values)
    except ValueError:
        return False


if __name__ == "__main__":
    print(solve(*[['{"jsonrpc":"2.0","id":1,"result":{}}']]))
