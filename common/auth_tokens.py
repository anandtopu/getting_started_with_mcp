"""JWT verification: trust configured keys/issuer, never URLs supplied by a token."""

import json
import time

import httpx2 as httpx
import jwt
from mcp.server.auth.provider import AccessToken


class JWTVerifier:
    """RS256 only; fetch a bounded JWKS from a configured issuer endpoint."""

    def __init__(self, issuer: str, resource: str, jwks_url: str, keys: dict | None = None):
        self.issuer, self.resource, self.jwks_url = issuer, resource, jwks_url
        self.keys = keys
        self.loaded = time.monotonic() if keys else 0.0

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            if len(token) > 16000:
                return None
            if self.keys is None or time.monotonic() - self.loaded > 60:
                async with httpx.AsyncClient(timeout=3, follow_redirects=False) as http:
                    async with http.stream("GET", self.jwks_url) as response:
                        response.raise_for_status()
                        body = b""
                        async for chunk in response.aiter_bytes():
                            body += chunk
                            if len(body) > 64000:
                                return None
                        self.keys = json.loads(body)
                        self.loaded = time.monotonic()
            header = jwt.get_unverified_header(token)
            key = next(k for k in self.keys["keys"] if k["kid"] == header.get("kid"))
            claims = jwt.decode(
                token,
                jwt.PyJWK.from_dict(key).key,
                algorithms=["RS256"],
                issuer=self.issuer,
                audience=self.resource,
                options={"require": ["iss", "aud", "sub", "exp", "iat"]},
            )
            scopes = claims.get("scope", "")
            client_id = claims.get("azp", claims.get("client_id"))
            if not isinstance(scopes, str) or not isinstance(client_id, str):
                return None
            return AccessToken(
                token=token,
                client_id=client_id,
                scopes=scopes.split(),
                expires_at=claims["exp"],
                resource=self.resource,
                subject=claims["sub"],
                claims={"iss": claims["iss"]},
            )
        except (jwt.PyJWTError, ValueError, KeyError, TypeError, StopIteration, httpx.HTTPError):
            return None
