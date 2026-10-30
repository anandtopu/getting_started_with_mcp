"""Synthetic client-credentials and enterprise ID-JAG exchange fixtures.

The actual official SDK providers drive discovery/token exchange. The enterprise
IdP login is deliberately a local signed-assertion fixture, not a vendor SSO claim.
"""

import base64
import json
import secrets
import time
from urllib.parse import parse_qs

import httpx2 as httpx
import jwt
from mcp import Client
from mcp.client.auth.extensions.client_credentials import ClientCredentialsOAuthProvider
from mcp.client.auth.extensions.identity_assertion import IdentityAssertionOAuthProvider
from mcp.client.streamable_http import streamable_http_client
from starlette.responses import JSONResponse

from common.auth_fixture import Authority
from common.auth_tokens import JWTVerifier
from common.oauth_client import MemoryStorage
from common.protocol import SPEC_REVISION
from common.secured_issues import make_app
from scripts.auth_lab import running_app
from scripts.http_lab import CaptureTransport

JWT_GRANT = "urn:ietf:params:oauth:grant-type:jwt-bearer"


class MachineAuthority(Authority):
    def __init__(self):
        super().__init__("", "")
        self.secret = secrets.token_urlsafe(32)
        self.idp = Authority("https://idp.lumen.example", "")
        self.used: set[str] = set()
        self.exchanges = 0

    async def metadata(self, request):
        response = json.loads((await super().metadata(request)).body)
        response.update(
            grant_types_supported=["client_credentials", JWT_GRANT],
            token_endpoint_auth_methods_supported=["client_secret_post", "client_secret_basic"],
        )
        return JSONResponse(response)

    async def assertion(self, audience, resource):
        return self.idp.token(
            "issues:read",
            aud=audience,
            resource=resource,
            jti=secrets.token_urlsafe(16),
            sub="synthetic-employee",
        )

    async def exchange(self, request):
        body = await request.body()
        if len(body) > 16000:
            return JSONResponse({"error": "invalid_request"}, status_code=400)
        pairs = parse_qs(body.decode())
        if any(len(v) != 1 for v in pairs.values()):
            return JSONResponse({"error": "invalid_request"}, status_code=400)
        data = {k: v[0] for k, v in pairs.items()}
        authorization = request.headers.get("authorization", "")
        if authorization.startswith("Basic "):
            try:
                client_id, secret = (
                    base64.b64decode(authorization[6:], validate=True).decode().split(":", 1)
                )
            except (ValueError, UnicodeError):
                return JSONResponse({"error": "invalid_client"}, status_code=401)
            if "client_id" in data or "client_secret" in data:
                return JSONResponse({"error": "invalid_request"}, status_code=400)
            data.update(client_id=client_id, client_secret=secret)
        valid = data.get("client_id") == "lumen-machine" and secrets.compare_digest(
            data.get("client_secret", ""), self.secret
        )
        valid = (
            valid
            and data.get("resource") == self.resource
            and data.get("scope", "issues:read") == "issues:read"
        )
        subject = "lumen-machine"
        if data.get("grant_type") == JWT_GRANT:
            try:
                claims = jwt.decode(
                    data.get("assertion", ""),
                    self.idp.key.public_key(),
                    algorithms=["RS256"],
                    issuer=self.idp.issuer,
                    audience=self.issuer,
                    options={"require": ["exp", "iat", "sub", "jti", "resource"]},
                )
                valid = (
                    valid and claims["resource"] == self.resource and claims["jti"] not in self.used
                )
                valid = valid and claims.get("scope") == "issues:read"
                if valid:
                    self.used.add(claims["jti"])
                    subject = claims["sub"]
            except jwt.PyJWTError:
                valid = False
        elif data.get("grant_type") != "client_credentials":
            valid = False
        if not valid:
            return JSONResponse({"error": "invalid_grant"}, status_code=400)
        self.exchanges += 1
        return JSONResponse(
            {
                "access_token": self.token("issues:read", sub=subject, azp="lumen-machine"),
                "token_type": "Bearer",
                "expires_in": 120,
                "scope": "issues:read",
            },
            headers={"Cache-Control": "no-store"},
        )


async def run(enterprise=False, capture=None):
    authority = MachineAuthority()

    def issuer(url):
        authority.issuer = url
        return authority.app()

    async with running_app(issuer):

        def resource(url):
            authority.resource = url + "/mcp"
            return make_app(
                JWTVerifier(
                    authority.issuer, authority.resource, authority.issuer + "/jwks", authority.jwks
                )
            )

        async with running_app(resource):
            storage = MemoryStorage(authority.issuer)
            storage.info = None
            kwargs = dict(
                server_url=authority.resource,
                storage=storage,
                client_id="lumen-machine",
                client_secret=authority.secret,
                issuer=authority.issuer,
                scope="issues:read",
                token_endpoint_auth_method="client_secret_post",
            )
            provider = (
                IdentityAssertionOAuthProvider(**kwargs, assertion_provider=authority.assertion)
                if enterprise
                else ClientCredentialsOAuthProvider(**kwargs)
            )
            transport = CaptureTransport(capture)
            transport.secrets += (authority.secret,)
            async with httpx.AsyncClient(auth=provider, transport=transport, timeout=10) as http:
                async with Client(
                    streamable_http_client(authority.resource, http_client=http), mode=SPEC_REVISION
                ) as client:
                    assert not (await client.call_tool("read_issue", {"issue_id": 1})).is_error
                    assert not (await client.call_tool("read_issue", {"issue_id": 2})).is_error
            assert authority.exchanges == 1
            assert storage.tokens and storage.tokens.expires_in > 0
    return {
        "flow": "enterprise ID-JAG leg 2" if enterprise else "client credentials",
        "token_exchanges": authority.exchanges,
        "verified_at": int(time.time()),
        "vendor_sso_tested": False,
    }
