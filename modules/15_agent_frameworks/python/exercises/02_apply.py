"""Reject remote endpoints with HTTP, credentials, a query, or a fragment.
Run: uv run python modules/15_agent_frameworks/python/exercises/02_apply.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(url: str):
    # YOUR CODE HERE: extend this narrower working baseline.
    return url.startswith("http")


if __name__ == "__main__":
    print(solve(*["https://mcp.lumen.example/mcp"]))
