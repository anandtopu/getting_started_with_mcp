"""Reject a missing capability object or a different protocol revision.
Run: uv run python modules/01_architecture_wire/python/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py --module 1 --exercise 3 --solution
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(meta: dict):
    return meta.get("io.modelcontextprotocol/protocolVersion") == "2026-07-28" and isinstance(
        meta.get("io.modelcontextprotocol/clientCapabilities"), dict
    )


def main() -> None:
    print(solve(*[{"io.modelcontextprotocol/protocolVersion": "2026-07-28"}]))


if __name__ == "__main__":
    main()
