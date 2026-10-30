"""HTTP-only issue service: SDK bearer validation plus operation-specific scope gates."""

import json
import re
from contextlib import asynccontextmanager

from mcp.server import MCPServer
from mcp.server.auth.settings import AuthSettings
from mcp.server.transport_security import TransportSecuritySettings
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response

from common.auth_tokens import JWTVerifier
from common.issues import IssueStore, register_issues
from common.protocol import SPEC_REVISION

WRITES = {"create_issue", "update_issue", "delete_issue"}


class ScopeGate:
    """Inspect the bounded actual body, not spoofable routing headers."""

    def __init__(self, app, verifier, hosts=None, origins=None):
        self.app, self.verifier = app, verifier
        self.hosts = None if hosts is None else {h.encode() for h in hosts}
        self.origins = {o.encode() for o in (origins or ["http://localhost:6274"])}

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope["headers"])
        host = headers.get(b"host", b"")
        valid_host = (
            host in self.hosts
            if self.hosts is not None
            else re.fullmatch(rb"(?:127\.0\.0\.1|localhost):[0-9]{1,5}", host)
        )
        if not valid_host:
            return await Response(status_code=421)(scope, receive, send)
        if headers.get(b"origin") not in {None, *self.origins}:
            return await Response(status_code=403)(scope, receive, send)
        if scope["path"] == "/mcp":
            if scope["method"] == "OPTIONS":
                return await self.app(scope, receive, send)
            if scope["method"] != "POST":
                return await Response(status_code=405)(scope, receive, send)
            if headers.get(b"mcp-protocol-version") != SPEC_REVISION.encode():
                return await Response(status_code=400)(scope, receive, send)
            body = b""
            while True:
                event = await receive()
                if event["type"] == "http.disconnect":
                    return
                body += event.get("body", b"")
                if len(body) > 64000:
                    return await Response(status_code=413)(scope, receive, send)
                if not event.get("more_body"):
                    break
            try:
                message = json.loads(body)
                write = (
                    isinstance(message, dict)
                    and message.get("method") == "tools/call"
                    and isinstance(message.get("params"), dict)
                    and message["params"].get("name") in WRITES
                )
            except (ValueError, TypeError):
                write = False
            bearer = headers.get(b"authorization", b"").decode("latin1")
            token = (
                await self.verifier.verify_token(bearer[7:])
                if bearer.lower().startswith("bearer ")
                else None
            )
            if write and token and "issues:write" not in token.scopes:
                challenge = (
                    'Bearer error="insufficient_scope", scope="issues:read issues:write", '
                    f'resource_metadata="{self.verifier.resource.replace("/mcp", "")}'
                    '/.well-known/oauth-protected-resource/mcp"'
                )
                return await JSONResponse(
                    {"error": "insufficient_scope"},
                    status_code=403,
                    headers={
                        "WWW-Authenticate": challenge,
                        **(
                            {
                                "Access-Control-Allow-Origin": headers[b"origin"].decode(),
                                "Access-Control-Expose-Headers": "WWW-Authenticate",
                                "Vary": "Origin",
                            }
                            if headers.get(b"origin")
                            else {}
                        ),
                    },
                )(scope, receive, send)
            delivered = False

            async def replay():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {"type": "http.request", "body": body, "more_body": False}
                return await receive()

            return await self.app(scope, replay, send)
        await self.app(scope, receive, send)


def make_app(verifier: JWTVerifier, *, hosts=None, origins=None):
    state = {}

    @asynccontextmanager
    async def request_lifespan(server):
        yield state

    server = MCPServer(
        "Lumen secured issues",
        token_verifier=verifier,
        auth=AuthSettings(
            issuer_url=verifier.issuer,
            resource_server_url=verifier.resource,
            required_scopes=["issues:read"],
            validate_token_resource=True,
        ),
        lifespan=request_lifespan,
    )
    register_issues(server)
    app = server.streamable_http_app(
        json_response=True,
        max_request_body_size=64000,
        transport_security=TransportSecuritySettings(
            allowed_hosts=hosts or ["127.0.0.1:*", "localhost:*"],
            allowed_origins=origins or ["http://localhost:6274"],
        ),
    )
    sdk_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(application):
        store = IssueStore()
        state["issues"] = store
        try:
            async with sdk_lifespan(application):
                yield
        finally:
            store.close()

    app.router.lifespan_context = lifespan
    return ScopeGate(
        CORSMiddleware(
            app,
            allow_origins=origins or ["http://localhost:6274"],
            allow_methods=["POST"],
            allow_headers=[
                "Authorization",
                "Content-Type",
                "MCP-Protocol-Version",
                "Mcp-Method",
                "Mcp-Name",
            ],
            expose_headers=["WWW-Authenticate", "MCP-Protocol-Version"],
        ),
        verifier,
        hosts,
        origins,
    )


def serve() -> None:
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--issuer", default="http://127.0.0.1:8080/realms/lumen")
    args = parser.parse_args()
    verifier = JWTVerifier(
        args.issuer,
        f"http://127.0.0.1:{args.port}/mcp",
        args.issuer + "/protocol/openid-connect/certs",
    )
    uvicorn.run(make_app(verifier), host="127.0.0.1", port=args.port, access_log=False)
