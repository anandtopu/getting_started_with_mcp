"""Use the SDK's PKCE/discovery/issuer checks with a pre-registered public client."""

import asyncio
import getpass
import webbrowser
from urllib.parse import parse_qs, urlsplit

import httpx2 as httpx
from mcp import Client
from mcp.client.auth.oauth2 import OAuthClientProvider
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.auth import AuthorizationCodeResult, OAuthClientInformationFull, OAuthClientMetadata

from common.auth_fixture import CALLBACK
from common.protocol import SPEC_REVISION


class MemoryStorage:
    """Per-connection tokens: deliberately never persisted or printed."""

    def __init__(self, issuer: str):
        self.tokens = None
        self.info = OAuthClientInformationFull(
            client_id="lumen-chat",
            issuer=issuer,
            redirect_uris=[CALLBACK],
            grant_types=["authorization_code"],
            response_types=["code"],
            token_endpoint_auth_method="none",
        )

    async def get_tokens(self):
        return self.tokens

    async def set_tokens(self, tokens):
        self.tokens = tokens

    async def get_client_info(self):
        return self.info

    async def set_client_info(self, info):
        self.info = info


def callback_result(url: str) -> AuthorizationCodeResult:
    parsed = urlsplit(url)
    if f"{parsed.scheme}://{parsed.netloc}{parsed.path}" != CALLBACK or parsed.fragment:
        raise ValueError("Callback must match the registered loopback URL exactly.")
    values = parse_qs(parsed.query)
    if any(len(v) != 1 for v in values.values()) or "error" in values:
        raise ValueError("Authorization denied or ambiguous callback.")
    return AuthorizationCodeResult(
        code=values["code"][0],
        state=values.get("state", [None])[0],
        iss=values.get("iss", [None])[0],
    )


async def browser_redirect(url: str) -> None:
    print("Opening the identity provider. After login, copy the loopback callback URL.")
    webbrowser.open(url)


async def browser_callback() -> AuthorizationCodeResult:
    # No listener is required. The browser shows an unavailable localhost page;
    # its address contains the short-lived code. Never paste it into a chat/log.
    url = await asyncio.to_thread(getpass.getpass, "Callback URL (hidden; kept in memory): ")
    return callback_result(url.strip())


def provider(
    url: str,
    issuer: str,
    storage: MemoryStorage,
    redirect=browser_redirect,
    callback=browser_callback,
    scopes="issues:read",
) -> OAuthClientProvider:
    return OAuthClientProvider(
        server_url=url,
        storage=storage,
        client_metadata=OAuthClientMetadata(
            redirect_uris=[CALLBACK],
            token_endpoint_auth_method="none",
            grant_types=["authorization_code"],
            response_types=["code"],
            scope=scopes,
        ),
        redirect_handler=redirect,
        callback_handler=callback,
    )


async def chat(url: str, issuer: str, auth=None) -> str:
    from common.host import Host
    from common.tool_formats import ToolCall, Turn
    from common.tool_models import ScriptedModel

    auth = auth or provider(url, issuer, MemoryStorage(issuer))
    async with httpx.AsyncClient(auth=auth, timeout=10, follow_redirects=False) as http:
        async with Client(
            streamable_http_client(url, http_client=http),
            mode=SPEC_REVISION,
            raise_exceptions=False,
        ) as client:

            async def approve(name, arguments):
                # This fixed demonstration authorizes only an exact read of issue 1.
                return name == "issues__read_issue" and arguments == {"issue_id": 1}

            model = ScriptedModel(
                [
                    Turn("", [ToolCall("read", "issues__read_issue", {"issue_id": 1})]),
                    Turn("Secured Lumen Chat read completed.", []),
                ]
            )
            host = Host({"issues": client}, approve)
            result = await host.run(model)
            assert host.audit and not host.audit[0].error
            return result
