"""Run a secured Chat read; use --keycloak for the Compose identity provider.

Run: uv run python modules/11_authorization/python/examples/03_local_auth.py
Expected: PASS with the measured checks below.
"""

import argparse
import asyncio

from common.oauth_client import chat
from scripts.auth_lab import auth_stack, fixture_provider


async def main(keycloak: bool) -> None:
    if keycloak:
        print(await chat("http://127.0.0.1:8001/mcp", "http://127.0.0.1:8080/realms/lumen"))
    else:
        async with auth_stack() as authority:
            auth, _ = fixture_provider(authority)
            print(await chat(authority.resource, authority.issuer, auth))
    print("PASS secured Chat read")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keycloak", action="store_true")
    asyncio.run(main(parser.parse_args().keycloak))
