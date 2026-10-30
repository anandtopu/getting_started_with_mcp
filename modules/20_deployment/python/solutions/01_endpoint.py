"""Accept HTTPS public URLs or exact loopback HTTP, rejecting credentials/query/fragment.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/20_deployment/python/solutions/01_endpoint.py
Capture the related server: uv run python scripts/tier5.py --module 20 --capture
Expected: All contract cases pass.
"""


def solve(value: str):
    from urllib.parse import urlsplit

    url = urlsplit(value)
    return (
        bool(url.hostname)
        and not (url.username or url.password or url.query or url.fragment)
        and (
            url.scheme == "https"
            or (url.scheme == "http" and url.hostname in {"localhost", "127.0.0.1"})
        )
    )


def main() -> None:
    print("Run scripts/check_exercise.py --module 20 --exercise 1 --solution")


if __name__ == "__main__":
    main()
