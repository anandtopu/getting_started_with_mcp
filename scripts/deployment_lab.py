"""Exercise production middleware over real loopback HTTP with the synthetic issuer.
Run: uv run python scripts/deployment_lab.py
Compose/Keycloak is separately exercised by scripts/keycloak_check.py --deployed.
"""

import asyncio

import httpx2 as httpx
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

from common.auth_fixture import Authority
from common.auth_tokens import JWTVerifier
from common.connections import discover
from common.deployment import Operations
from common.protocol import SPEC_REVISION
from common.secured_issues import make_app
from scripts.auth_lab import running_app
from scripts.http_lab import CaptureTransport


async def run(capture=None):
    authority = Authority("", "")

    def issuer(url):
        authority.issuer = url
        return authority.app()

    async with running_app(issuer):

        def resource(url):
            authority.resource = url + "/mcp"
            verifier = JWTVerifier(
                authority.issuer, authority.resource, authority.issuer + "/jwks", authority.jwks
            )
            return Operations(make_app(verifier), verifier)

        async with running_app(resource) as url:
            async with httpx.AsyncClient(timeout=5) as http:
                assert (await http.get(url + "/healthz")).status_code == 200
                denied = await http.post(
                    url + "/mcp", headers={"MCP-Protocol-Version": SPEC_REVISION}, json={}
                )
                assert denied.status_code == 401
            async with httpx.AsyncClient(
                transport=CaptureTransport(capture),
                timeout=10,
                headers={"Authorization": "Bearer " + authority.token()},
            ) as http:
                async with Client(
                    streamable_http_client(url + "/mcp", http_client=http), mode=SPEC_REVISION
                ) as client:
                    await discover(client)
                    assert (await client.list_tools()).tools
                    result = await client.call_tool("read_issue", {"issue_id": 1})
                    assert not result.is_error
    print("PASS health, unauthorized rejection, authenticated issue read")


if __name__ == "__main__":
    asyncio.run(run())
