"""Approve only the exact configured backend URL.
Run: uv run python modules/12_security/python/exercises/01_practice.py
Expected: print one baseline result; run the shared exercise checker for all cases.
"""


def solve(url: str):
    # YOUR CODE HERE: extend this deliberately narrower baseline.
    return url.startswith("https://api.lumen.example")


if __name__ == "__main__":
    print(solve(*["https://api.lumen.example/projects"]))
