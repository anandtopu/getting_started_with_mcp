"""Accept only JSON-RPC object lines on protocol stdout, not arbitrary JSON or debug text.
Run: uv run python modules/13_testing_observability/python/exercises/01_practice.py
Expected: print one baseline result; run the shared exercise checker for all cases.
"""


def solve(lines: list[str]):
    # YOUR CODE HERE: extend this deliberately narrower baseline.
    return all(line.startswith("{") for line in lines)


if __name__ == "__main__":
    print(solve(*[['{"jsonrpc":"2.0","id":1,"result":{}}']]))
