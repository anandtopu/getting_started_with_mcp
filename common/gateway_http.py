"""Authenticated loopback deployment of the teaching gateway."""

from contextlib import asynccontextmanager
from pathlib import Path

from mcp.server.transport_security import TransportSecuritySettings
from starlette.middleware.cors import CORSMiddleware

from common.gateway import gateway_server
from common.secured_issues import ScopeGate


def make_app(verifier, path: Path):
    server, gateway, tasks = gateway_server(path, verifier=verifier)
    app = server.streamable_http_app(
        json_response=True,
        max_request_body_size=64000,
        transport_security=TransportSecuritySettings(
            allowed_hosts=["127.0.0.1:*", "localhost:*"], allowed_origins=["http://localhost:6274"]
        ),
    )
    sdk_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(application):
        try:
            async with gateway.lifetime(), sdk_lifespan(application):
                yield
        finally:
            await tasks.close()

    app.router.lifespan_context = lifespan
    # ScopeGate provides the existing bounded-body/Host/Origin boundary. Namespaced
    # writes are authorized by Gateway.call against the verified token's scopes.
    return ScopeGate(
        CORSMiddleware(
            app,
            allow_origins=["http://localhost:6274"],
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
    )
