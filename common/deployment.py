"""Container entry point: exact public authority, bounded per-principal rates, health."""

import os
import time
from collections import Counter, deque
from urllib.parse import urlsplit

from starlette.responses import JSONResponse, Response

from common.auth_tokens import JWTVerifier
from common.secured_issues import make_app


def public_url(value):
    url = urlsplit(value)
    if url.username or url.password or url.query or url.fragment or not url.hostname:
        raise ValueError("Use a public URL without credentials, query or fragment.")
    if url.scheme != "https" and not (
        url.scheme == "http" and url.hostname in {"127.0.0.1", "localhost"}
    ):
        raise ValueError("Public endpoints require HTTPS; HTTP is loopback-only.")
    return value.rstrip("/")


class Operations:
    """Single-worker teaching limits. Use a shared limiter/store before scaling out."""

    def __init__(self, app, verifier, *, limit=120, clock=time.monotonic):
        self.app, self.verifier, self.limit, self.clock = app, verifier, limit, clock
        self.windows, self.counts = {}, Counter()

    def allow(self, principal):
        now = self.clock()
        self.windows = {k: v for k, v in self.windows.items() if v and v[-1] > now - 60}
        if principal not in self.windows and len(self.windows) >= 1000:
            return False
        window = self.windows.setdefault(principal, deque())
        while window and window[0] <= now - 60:
            window.popleft()
        if len(window) >= self.limit:
            return False
        window.append(now)
        return True

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        # Health endpoints expose no data and are network-internal in Compose.
        if scope["path"] in {"/healthz", "/readyz"}:
            return await JSONResponse({"status": "ready"})(scope, receive, send)
        if scope["path"] == "/metrics":
            body = (
                "\n".join(
                    f'lumen_requests_total{{status="{k}"}} {v}'
                    for k, v in sorted(self.counts.items())
                )
                + "\n"
            )
            return await Response(body, media_type="text/plain")(scope, receive, send)
        headers = dict(scope["headers"])
        bearer = headers.get(b"authorization", b"").decode("latin1")
        token = (
            await self.verifier.verify_token(bearer[7:])
            if bearer.lower().startswith("bearer ")
            else None
        )
        if token and not self.allow(token.subject):
            self.counts[429] += 1
            return await JSONResponse(
                {"error": "rate_limited"}, status_code=429, headers={"Retry-After": "60"}
            )(scope, receive, send)

        async def counted(message):
            if message["type"] == "http.response.start":
                self.counts[message["status"]] += 1
            await send(message)

        return await self.app(scope, receive, counted)


def application():
    issuer = public_url(os.environ["LUMEN_ISSUER"])
    resource = public_url(os.environ["LUMEN_RESOURCE"])
    # Configured internal key endpoint is trusted deployment config, never a token's jku.
    verifier = JWTVerifier(issuer, resource, os.environ["LUMEN_JWKS_URL"])
    hosts = [urlsplit(resource).netloc]
    origins = os.environ.get("LUMEN_ORIGINS", "http://localhost:6274").split(",")
    return Operations(make_app(verifier, hosts=hosts, origins=origins), verifier)


def main():
    import uvicorn

    uvicorn.run(
        application(),
        host=os.environ.get("LUMEN_BIND", "127.0.0.1"),
        port=8000,
        access_log=False,
        proxy_headers=False,
    )


if __name__ == "__main__":
    main()
