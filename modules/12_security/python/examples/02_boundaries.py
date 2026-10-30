"""Reject URL/command injection and use a fixed backend operation.

Run: uv run python modules/12_security/python/examples/02_boundaries.py
Expected: PASS with the measured checks below.
"""

from common.defenses import command, destination, run_health


def main() -> None:
    for url in [
        "http://169.254.169.254/latest/meta-data",
        "https://api.lumen.example@evil.example/projects",
        "https://api.lumen.example/projects?next=http://localhost",
    ]:
        try:
            destination(url)
        except PermissionError:
            pass
        else:
            raise AssertionError("Unsafe destination accepted")
    for value in ["health; whoami", "health && echo injected", "../health"]:
        try:
            command(value)
        except PermissionError:
            pass
        else:
            raise AssertionError("Unsafe command accepted")
    assert run_health("health") == "synthetic backend healthy"
    print("PASS fixed destination and shell-free command boundary")


if __name__ == "__main__":
    main()
