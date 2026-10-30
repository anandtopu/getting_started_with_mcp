"""Encode Unicode, edge whitespace, controls, and sentinel-shaped text as UTF-8 base64.
Run: uv run python modules/10_streamable_http/python/solutions/02_header_encoding.py
Expected: prints the first fixture result; check all cases with scripts/check_exercise.py.
"""

import base64


def solve(value: str) -> object:
    safe = value == value.strip() and all(32 <= ord(c) <= 126 for c in value)
    sentinel = value.startswith("=?base64?") and value.endswith("?=")
    return (
        value
        if safe and not sentinel
        else "=?base64?" + base64.b64encode(value.encode()).decode() + "?="
    )


if __name__ == "__main__":
    print(solve(*["east"]))
