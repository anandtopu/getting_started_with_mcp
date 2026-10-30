"""Loopback-only synthetic OAuth fixture. NOT an identity provider for real users.

No login or persistent secrets: explicit consent means the single synthetic user.
Keycloak in deployment/auth is the course's interoperable identity provider.
"""

import base64
import hashlib
import html
import json
import re
import secrets
import time
from urllib.parse import parse_qs, urlencode

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from starlette.routing import Route

CALLBACK = "http://127.0.0.1:8765/callback"
SCOPES = {"issues:read", "issues:write"}


class Authority:
    def __init__(self, issuer: str, resource: str, scopes=None):
        self.issuer, self.resource = issuer, resource
        self.scopes = set(SCOPES if scopes is None else scopes)
        self.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(self.key.public_key()))
        self.jwks = {"keys": [{**jwk, "kid": "fixture", "use": "sig", "alg": "RS256"}]}
        self.pending: dict = {}
        self.codes: dict = {}

    def token(self, scopes: str = "issues:read", **overrides) -> str:
        now = int(time.time())
        claims = dict(
            iss=self.issuer,
            aud=self.resource,
            sub="lumen-learner",
            azp="lumen-chat",
            iat=now,
            exp=now + 120,
            scope=scopes,
        )
        return jwt.encode(
            {**claims, **overrides}, self.key, algorithm="RS256", headers={"kid": "fixture"}
        )

    async def metadata(self, request: Request):
        return JSONResponse(
            dict(
                issuer=self.issuer,
                authorization_endpoint=self.issuer + "/authorize",
                token_endpoint=self.issuer + "/token",
                jwks_uri=self.issuer + "/jwks",
                response_types_supported=["code"],
                grant_types_supported=["authorization_code"],
                token_endpoint_auth_methods_supported=["none"],
                code_challenge_methods_supported=["S256"],
                scopes_supported=sorted(self.scopes),
                authorization_response_iss_parameter_supported=True,
            )
        )

    async def authorize(self, request: Request):
        query = dict(request.query_params)
        valid = (
            query.get("client_id") == "lumen-chat"
            and query.get("redirect_uri") == CALLBACK
            and query.get("response_type") == "code"
            and query.get("resource") == self.resource
            and query.get("code_challenge_method") == "S256"
            and re.fullmatch(r"[A-Za-z0-9_-]{43}", query.get("code_challenge", ""))
            and set(query.get("scope", "").split()) <= self.scopes
        )
        if not valid:
            return JSONResponse({"error": "invalid_request"}, status_code=400)
        self.pending = {k: v for k, v in self.pending.items() if v[1] > time.time()}
        if len(self.pending) >= 100:
            return Response(status_code=429)
        ticket = secrets.token_urlsafe(24)
        self.pending[ticket] = (query, time.time() + 60)
        return HTMLResponse(
            "<h1>Synthetic OAuth fixture</h1><p>No real account is authenticated.</p>"
            f"<p>Requested scopes: {html.escape(query.get('scope', ''))}</p>"
            f'<form method="post" action="/consent?ticket={ticket}">'
            "<button>Allow this synthetic session</button></form>",
            headers={
                "Cache-Control": "no-store",
                "Referrer-Policy": "no-referrer",
                "Content-Security-Policy": "default-src 'none'; form-action 'self'",
            },
        )

    async def consent(self, request: Request):
        if request.headers.get("origin") not in {None, self.issuer}:
            return Response(status_code=403)
        query, expires = self.pending.pop(request.query_params.get("ticket"), ({}, 0))
        if expires <= time.time():
            return Response(status_code=400)
        self.codes = {k: v for k, v in self.codes.items() if v[1] > time.time()}
        if len(self.codes) >= 100:
            return Response(status_code=429)
        code = secrets.token_urlsafe(24)
        self.codes[code] = (query, time.time() + 60)
        return RedirectResponse(
            CALLBACK
            + "?"
            + urlencode(dict(code=code, state=query.get("state", ""), iss=self.issuer)),
            status_code=302,
        )

    async def exchange(self, request: Request):
        body = await request.body()
        if len(body) > 8000:
            return Response(status_code=413)
        data = {k: v[0] for k, v in parse_qs(body.decode()).items()}
        query, expires = self.codes.pop(data.get("code"), ({}, 0))
        verifier = data.get("code_verifier", "")
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        valid = (
            expires > time.time()
            and data.get("grant_type") == "authorization_code"
            and re.fullmatch(r"[A-Za-z0-9._~-]{43,128}", verifier)
            and secrets.compare_digest(
                challenge.decode().rstrip("="), query.get("code_challenge", "")
            )
            and all(data.get(k) == query.get(k) for k in ("client_id", "redirect_uri", "resource"))
        )
        if not valid:
            return JSONResponse({"error": "invalid_grant"}, status_code=400)
        return JSONResponse(
            dict(
                access_token=self.token(query.get("scope", "")),
                token_type="Bearer",
                expires_in=120,
                scope=query.get("scope", ""),
            ),
            headers={"Cache-Control": "no-store"},
        )

    def app(self):
        async def keys(request):
            return JSONResponse(self.jwks)

        return Starlette(
            routes=[
                Route("/.well-known/oauth-authorization-server", self.metadata),
                Route("/authorize", self.authorize),
                Route("/consent", self.consent, methods=["POST"]),
                Route("/token", self.exchange, methods=["POST"]),
                Route("/jwks", keys),
            ]
        )
