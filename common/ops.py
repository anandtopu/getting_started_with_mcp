"""Capstone: authenticated issues, form retries, durable Tasks and an analytics App."""

from contextlib import asynccontextmanager
from pathlib import Path

from mcp.server import MCPServer
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.settings import AuthSettings
from mcp.server.transport_security import TransportSecuritySettings

from common.deployment import Operations
from common.elicitation import input_lifespan, register_input
from common.extensions import analytics_apps
from common.issues import register_issues
from common.notes import READ
from common.report_tasks import ReportTasks, report
from common.secured_issues import WRITES, ScopeGate


def make_server(path: Path, verifier=None):
    def principal():
        token = get_access_token()
        return token.subject if token else "local-learner"

    tasks = ReportTasks(path, principal=principal)

    @asynccontextmanager
    async def lifespan(server):
        try:
            async with input_lifespan(server) as state:
                yield state
        finally:
            await tasks.close()

    server = MCPServer(
        "Lumen Ops",
        version="1.0",
        lifespan=lifespan,
        extensions=[tasks, analytics_apps()],
        token_verifier=verifier,
        auth=AuthSettings(
            issuer_url=verifier.issuer,
            resource_server_url=verifier.resource,
            required_scopes=["issues:read"],
            validate_token_resource=True,
        )
        if verifier
        else None,
    )
    register_issues(server)
    register_input(server)

    @server.tool(annotations=READ)
    def quarterly_report(quarter: str = "Q1", ask_details: bool = False) -> dict[str, object]:
        """Compute a synthetic report, optionally as a durable Task with a detail choice."""
        return report(quarter)

    return server


def make_app(verifier, path: Path, *, hosts=None, origins=None):
    server = make_server(path, verifier)
    app = server.streamable_http_app(
        json_response=True,
        max_request_body_size=64000,
        transport_security=TransportSecuritySettings(
            allowed_hosts=hosts or ["127.0.0.1:*", "localhost:*"],
            allowed_origins=origins or ["http://localhost:6274"],
        ),
    )
    gate = ScopeGate(
        app,
        verifier,
        hosts=hosts,
        origins=origins,
        write_tools=WRITES | {"bulk_close", "export_report"},
    )
    return Operations(gate, verifier)
