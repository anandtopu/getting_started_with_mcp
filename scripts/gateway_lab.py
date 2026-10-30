"""Exercise a secured gateway with real loopback OAuth and signed fixture tokens.

Run: uv run python scripts/gateway_lab.py
Expected: PASS OAuth gateway, scope partition, audience and Origin checks.
No real identity or external model service is used.
"""

import asyncio
import logging
import tempfile
from pathlib import Path

import httpx2 as httpx
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

from common.auth_fixture import Authority
from common.auth_tokens import JWTVerifier
from common.connections import discover
from common.gateway_http import make_app
from common.protocol import SPEC_REVISION
from scripts.auth_lab import fixture_provider, rpc, running_app


async def run():
    logging.getLogger("httpx2").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    authority = Authority("", "", {"workspace:read", "workspace:write"})

    def issuer(url):
        authority.issuer = url
        return authority.app()

    with tempfile.TemporaryDirectory() as directory:
        async with running_app(issuer):

            def resource(url):
                authority.resource = url + "/mcp"
                verifier = JWTVerifier(
                    authority.issuer, authority.resource, authority.issuer + "/jwks", authority.jwks
                )
                return make_app(verifier, Path(directory) / "tasks.db")

            async with running_app(resource):
                auth, storage = fixture_provider(authority, "workspace:read")
                async with httpx.AsyncClient(auth=auth, timeout=10) as http:
                    async with Client(
                        streamable_http_client(authority.resource, http_client=http),
                        mode=SPEC_REVISION,
                    ) as client:
                        await discover(client)
                        assert storage.tokens.scope == "workspace:read"
                        names = {t.name for t in (await client.list_tools()).tools}
                        assert (
                            "workflow__triage_week" in names and "notes__create_note" not in names
                        )
                        assert (
                            await client.call_tool("workflow__triage_week", {})
                        ).structured_content["total"] > 0
                headers = {
                    "MCP-Protocol-Version": SPEC_REVISION,
                    "Accept": "application/json, text/event-stream",
                    "Mcp-Method": "tools/call",
                    "Mcp-Name": "workflow__triage_week",
                }
                async with httpx.AsyncClient(timeout=10) as http:
                    for token, expected in [
                        (authority.token("workspace:read", aud="https://wrong.example"), 401),
                        (authority.token("workspace:read"), 200),
                    ]:
                        response = await http.post(
                            authority.resource,
                            headers={**headers, "Authorization": "Bearer " + token},
                            json=rpc("workflow__triage_week", {"week_start": "2026-07-13"}),
                        )
                        assert response.status_code == expected
                    response = await http.post(
                        authority.resource,
                        headers={**headers, "Origin": "https://evil.example"},
                        json=rpc(),
                    )
                    assert response.status_code == 403
    print("PASS OAuth gateway, scope partition, audience and Origin checks")


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
