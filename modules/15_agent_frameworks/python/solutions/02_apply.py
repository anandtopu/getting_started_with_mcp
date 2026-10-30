"""Reject remote endpoints with HTTP, credentials, a query, or a fragment.
Run: uv run python modules/15_agent_frameworks/python/solutions/02_apply.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(url: str):
    from urllib.parse import urlsplit

    p = urlsplit(url)
    return (
        p.scheme == "https"
        and bool(p.hostname)
        and not any([p.username, p.password, p.query, p.fragment])
    )


if __name__ == "__main__":
    print(solve(*["https://mcp.lumen.example/mcp"]))
