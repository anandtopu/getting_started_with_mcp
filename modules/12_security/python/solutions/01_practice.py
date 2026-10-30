"""Approve only the exact configured backend URL.
Run: uv run python modules/12_security/python/solutions/01_practice.py
Expected: print one baseline result; run the shared exercise checker for all cases.
"""


def solve(url: str):
    return url == "https://api.lumen.example/projects"


if __name__ == "__main__":
    print(solve(*["https://api.lumen.example/projects"]))
