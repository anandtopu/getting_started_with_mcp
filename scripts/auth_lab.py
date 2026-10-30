"""Real loopback HTTP OAuth tests with a synthetic authority, no external service."""

import asyncio
import logging
import re
import socket
from contextlib import asynccontextmanager

import httpx2 as httpx
import uvicorn

from common.auth_fixture import Authority
from common.auth_tokens import JWTVerifier
from common.connections import discover
from common.oauth_client import MemoryStorage, callback_result, chat, provider
from common.protocol import SPEC_REVISION
from common.secured_issues import make_app
from scripts.http_lab import http_client


@asynccontextmanager
async def running_app(factory, port: int = 0):
    sock = socket.socket()
    sock.bind(("127.0.0.1", port))
    sock.listen(128)
    port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    server = uvicorn.Server(uvicorn.Config(factory(url), log_level="error", access_log=False))
    task = asyncio.create_task(server.serve(sockets=[sock]))
    try:
        async with asyncio.timeout(10):
            while not server.started:
                if task.done():
                    await task
                    raise RuntimeError("Loopback server exited before readiness")
                await asyncio.sleep(0.01)
        yield url
    finally:
        server.should_exit = True
        try:
            await asyncio.wait_for(task, 5)
        finally:
            sock.close()


@asynccontextmanager
async def auth_stack():
    # OAuth URLs contain one-use state and consent tickets; never log them.
    logging.getLogger("httpx2").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    authority = Authority("", "")

    def authority_app(url):
        authority.issuer = url
        return authority.app()

    async with running_app(authority_app):

        def resource_app(url):
            authority.resource = url + "/mcp"
            return make_app(
                JWTVerifier(
                    authority.issuer, authority.resource, authority.issuer + "/jwks", authority.jwks
                )
            )

        async with running_app(resource_app):
            yield authority


def fixture_provider(authority):
    result = None
    storage = MemoryStorage(authority.issuer)

    async def consent(url):
        nonlocal result
        # Automated consent is restricted to this synthetic authority by exact origin.
        if not url.startswith(authority.issuer + "/authorize?"):
            raise ValueError("Unexpected fixture authorization endpoint")
        async with httpx.AsyncClient(follow_redirects=False, timeout=5) as browser:
            page = await browser.get(url)
            page.raise_for_status()
            action = re.search(r'action="([^"]+)"', page.text).group(1)
            response = await browser.post(authority.issuer + action)
            assert response.status_code == 302
            result = callback_result(response.headers["location"])

    async def callback():
        return result

    return provider(authority.resource, authority.issuer, storage, consent, callback), storage


def rpc(name="read_issue", arguments=None):
    return dict(
        jsonrpc="2.0",
        id="auth-check",
        method="tools/call",
        params=dict(
            name=name,
            arguments=arguments or {"issue_id": 1},
            _meta={
                "io.modelcontextprotocol/protocolVersion": SPEC_REVISION,
                "io.modelcontextprotocol/clientCapabilities": {},
                "io.modelcontextprotocol/clientInfo": {"name": "auth-lab", "version": "1"},
            },
        ),
    )


async def exercise_auth(authority, capture=None):
    auth, storage = fixture_provider(authority)
    assert (
        await chat(authority.resource, authority.issuer, auth)
        == "Secured Lumen Chat read completed."
    )
    assert storage.tokens and storage.tokens.scope == "issues:read"
    headers = {
        "MCP-Protocol-Version": SPEC_REVISION,
        "Accept": "application/json, text/event-stream",
    }
    # Capture HTTP status failures as well as successful MCP calls. Tokens are redacted.
    async with http_client(authority.resource, capture) as (client, http):
        for token, status in [
            (None, 401),
            ("corrupt", 401),
            (authority.token(aud="https://wrong.example/mcp"), 401),
            (authority.token(iss="https://wrong.example"), 401),
            (authority.token(exp=1), 401),
            (authority.token(""), 403),
        ]:
            extra = {"Authorization": "Bearer " + token} if token else {}
            response = await http.post(authority.resource, json=rpc(), headers={**headers, **extra})
            assert response.status_code == status, response.text
        readonly = {**headers, "Authorization": "Bearer " + storage.tokens.access_token}
        response = await http.post(
            authority.resource,
            json=rpc("delete_issue", {"issue_id": 1, "confirmed": True}),
            headers=readonly,
        )
        assert (
            response.status_code == 403
            and 'scope="issues:read issues:write"' in response.headers["www-authenticate"]
        )
        http.headers["Authorization"] = "Bearer " + authority.token("issues:read issues:write")
        await discover(client)
        assert (await client.list_tools()).tools
        assert not (await client.call_tool("read_issue", {"issue_id": 1})).is_error
        assert (await client.call_tool("delete_issue", {"issue_id": 1})).is_error
        assert not (
            await client.call_tool("delete_issue", {"issue_id": 1, "confirmed": True})
        ).is_error
    print("PASS OAuth: discovery, SDK PKCE, Chat, issuer/audience/expiry/scope, approved write")
