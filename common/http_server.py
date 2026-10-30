"""Current MCP over loopback ASGI, with explicit browser and host boundaries."""

import re
from contextlib import asynccontextmanager
from typing import Annotated

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.server.transport_security import TransportSecuritySettings
from mcp_types import ResourceLink
from pydantic import Field
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response

from common.analytics import register_analytics
from common.issues import IssueStore, register_issues
from common.notes import REPLACE
from common.protocol import SPEC_REVISION
from common.reports import register_reports


class CurrentHTTP:
    """Keep this teaching endpoint on the pinned current protocol only."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope["headers"])
            if not re.fullmatch(
                rb"(?:127\.0\.0\.1|localhost):[0-9]{1,5}", headers.get(b"host", b"")
            ):
                await Response(status_code=421)(scope, receive, send)
                return
            if headers.get(b"origin") not in (None, b"http://localhost:3000"):
                await Response(status_code=403)(scope, receive, send)
                return
            if scope["method"] not in {"POST", "OPTIONS"}:
                await Response(status_code=405)(scope, receive, send)
                return
            if (
                scope["method"] == "POST"
                and headers.get(b"mcp-protocol-version") != SPEC_REVISION.encode()
            ):
                await JSONResponse(
                    {"error": "Use MCP-Protocol-Version " + SPEC_REVISION}, status_code=400
                )(scope, receive, send)
                return
        await self.app(scope, receive, send)


def make_app(json_response: bool = False):
    """One application-owned store survives individual HTTP requests.

    A real multi-worker deployment needs shared durable storage, shared receipt
    records and a cross-worker notification bus. This lab runs one worker.
    """
    state = {}

    @asynccontextmanager
    async def request_lifespan(server: MCPServer):
        yield state

    server = MCPServer("Lumen remote workspace", lifespan=request_lifespan)
    register_issues(server)
    register_analytics(server)
    register_reports(server)

    @server.tool()
    def route_region(
        region: Annotated[str, Field(json_schema_extra={"x-mcp-header": "Region"})],
    ) -> dict:
        """Echo a header-bound routing label; this is not proof of tenant identity."""
        return {"region": region}

    @server.resource("wiki://{space}/{page}")
    async def wiki_page(space: str, page: str) -> str:
        from common.data import data_root, safe_path

        if space not in {"engineering", "product", "hr", "onboarding", "incident_postmortems"}:
            raise ValueError("Unknown wiki space")
        return safe_path(data_root(), f"wiki/{space}/{page}.md").read_text(encoding="utf-8")

    @server.tool()
    async def find_page(space: str = "engineering", page: str = "page-01") -> ResourceLink:
        """Find an existing remote wiki page."""
        await wiki_page(space, page)
        return ResourceLink(
            type="resource_link", name=page, uri=f"wiki://{space}/{page}", mime_type="text/markdown"
        )

    @server.tool(annotations=REPLACE)
    async def publish_review(text: str, ctx: Context, confirmed: bool = False) -> dict:
        """Publish an ephemeral review notification for reconnect demonstrations."""
        if not confirmed:
            raise ValueError("Human confirmation required")
        state["review"] = text[:500]
        await ctx.notify_resource_updated("workspace://review")
        return {"updated": True}

    @server.resource("workspace://review")
    def review() -> str:
        return state.get("review", "No review yet")

    app = server.streamable_http_app(
        json_response=json_response,
        transport_security=TransportSecuritySettings(
            allowed_hosts=["127.0.0.1:*", "localhost:*"], allowed_origins=["http://localhost:3000"]
        ),
        max_request_body_size=64000,
    )
    sdk_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(application):
        store = IssueStore()
        state.update(issues=store, active_reports=0)
        try:
            async with sdk_lifespan(application):
                yield
        finally:
            store.close()

    app.router.lifespan_context = lifespan
    return CurrentHTTP(
        CORSMiddleware(
            app,
            allow_origins=["http://localhost:3000"],
            allow_methods=["POST"],
            allow_headers=[
                "Content-Type",
                "MCP-Protocol-Version",
                "Mcp-Method",
                "Mcp-Name",
                "Mcp-Param-Region",
            ],
            expose_headers=["MCP-Protocol-Version"],
        )
    )


def serve() -> None:
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    uvicorn.run(make_app(args.json), host="127.0.0.1", port=args.port, access_log=False)
