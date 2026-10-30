"""Interoperate with the pinned Compose Keycloak, including SDK scope step-up.

Run after docker compose -f deployment/auth/compose.yaml up -d:
uv run python scripts/keycloak_check.py
Only the fixed synthetic account/issuer is used; never print credentials or tokens.
"""

import asyncio
import html
import logging
import re
import time

import httpx2 as httpx
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

from common.auth_tokens import JWTVerifier
from common.connections import discover
from common.oauth_client import MemoryStorage, callback_result, provider
from common.protocol import SPEC_REVISION
from common.secured_issues import make_app
from scripts.auth_lab import running_app

ISSUER = "http://127.0.0.1:8080/realms/lumen"
RESOURCE = "http://127.0.0.1:8001/mcp"


async def main():
    logging.getLogger("httpx2").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    async with httpx.AsyncClient(timeout=5, follow_redirects=False) as browser:
        deadline = time.monotonic() + 120
        while True:
            try:
                response = await browser.get(ISSUER + "/.well-known/openid-configuration")
                response.raise_for_status()
                metadata = response.json()
                break
            except httpx.HTTPError:
                if time.monotonic() >= deadline:
                    raise RuntimeError(
                        "Keycloak not ready; start the auth Compose service"
                    ) from None
                await asyncio.sleep(1)
        assert metadata["issuer"] == ISSUER
        callback_value = None

        async def redirect(url):
            nonlocal callback_value
            if not url.startswith(ISSUER + "/protocol/openid-connect/auth?"):
                raise ValueError("Unexpected authorization endpoint")
            response = await browser.get(url)
            phase = "authorization request"
            if response.status_code == 200:
                match = re.search(r'<form[^>]+action="([^"]+)"', response.text)
                if not match:
                    raise RuntimeError("Expected Keycloak login form")
                action = html.unescape(match[1])
                if not action.startswith(ISSUER + "/login-actions/"):
                    raise ValueError("Unexpected login form target")
                phase = "login form submission"
                response = await browser.post(
                    action,
                    data={
                        "username": "learner",
                        "password": "lumen-local-only",
                        "credentialId": "",
                    },
                )
            if response.status_code != 302:
                feedback = re.findall(
                    r"<(?:h1|span|p)[^>]*(?:kc-page-title|kc-feedback-text|instruction)[^>]*>(.*?)</",
                    response.text,
                    re.S,
                )
                summary = " ".join(
                    html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in feedback
                )[:300]
                raise RuntimeError(f"Keycloak {phase}: HTTP {response.status_code}; {summary}")
            callback_value = callback_result(response.headers["location"])

        async def callback():
            return callback_value

        verifier = JWTVerifier(ISSUER, RESOURCE, metadata["jwks_uri"])
        async with running_app(lambda _: make_app(verifier), port=8001):
            storage = MemoryStorage(ISSUER)
            auth = provider(RESOURCE, ISSUER, storage, redirect, callback)
            async with httpx.AsyncClient(auth=auth, timeout=10) as http:
                async with Client(
                    streamable_http_client(RESOURCE, http_client=http),
                    mode=SPEC_REVISION,
                    raise_exceptions=False,
                ) as client:
                    await discover(client)
                    assert not (await client.call_tool("read_issue", {"issue_id": 1})).is_error
                    first = await verifier.verify_token(storage.tokens.access_token)
                    assert first and first.scopes == ["issues:read"]
                    result = await client.call_tool(
                        "create_issue",
                        {
                            "issue": {"title": "Keycloak compatibility"},
                            "operation_key": "keycloak-check",
                            "confirmed": True,
                        },
                    )
                    assert not result.is_error
                    stepped = await verifier.verify_token(storage.tokens.access_token)
                    assert stepped and {"issues:read", "issues:write"} <= set(stepped.scopes)
                    # Same verifier must reject a token for a different resource.
                    verifier.resource = "https://different.example/mcp"
                    assert await verifier.verify_token(storage.tokens.access_token) is None
            print("PASS Keycloak: discovery, PKCE, resource audience, SDK scope step-up, write")


if __name__ == "__main__":
    asyncio.run(main())
