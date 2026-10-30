"""Check audience, expiry and scopes AFTER signature verification.
Run: uv run python modules/11_authorization/python/solutions/03_stretch.py
Expected: print one baseline result; run the shared exercise checker for all cases.
"""


def solve(claims: dict, resource: str, now: int, required: list[str]):
    audience = claims.get("aud", [])
    audience = [audience] if isinstance(audience, str) else audience
    return (
        resource in audience
        and claims.get("exp", 0) > now
        and set(required) <= set(claims.get("scope", "").split())
    )


if __name__ == "__main__":
    print(solve(*[{"aud": "mcp", "exp": 20, "scope": "read write"}, "mcp", 10, ["read"]]))
