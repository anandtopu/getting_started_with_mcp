"""Tasks and Apps attached to one official-SDK server; plain clients get text."""

from contextlib import asynccontextmanager
from pathlib import Path

from mcp.server import MCPServer
from mcp.server.apps import Apps, ResourceCsp, ResourcePermissions

from common.config import ROOT
from common.notes import READ
from common.report_tasks import ReportTasks, report
from common.tool_design import rows

APP_URI = "ui://lumen/analytics.html"


def analytics_apps() -> Apps:
    apps = Apps()
    html = (ROOT / "modules/17_extensions/ui/dashboard.html").read_text(encoding="utf-8")
    apps.add_html_resource(
        APP_URI,
        html,
        csp=ResourceCsp(
            connect_domains=[], resource_domains=[], frame_domains=[], base_uri_domains=[]
        ),
        permissions=ResourcePermissions(),
    )

    @apps.tool(resource_uri=APP_URI, annotations=READ)
    async def analytics_dashboard() -> dict[str, object]:
        """Show synthetic work-item counts as text and, in a supporting host, an interactive
        dashboard.
        """
        items = rows("issues")
        return {
            "total": len(items),
            "counts": [
                {"status": s, "count": sum(r["status"] == s for r in items)}
                for s in ("open", "in_progress", "closed")
            ],
        }

    return apps


def extension_server(path: Path, principal=lambda: "local-learner") -> MCPServer:
    tasks = ReportTasks(path, principal)

    @asynccontextmanager
    async def lifespan(server):
        try:
            yield {}
        finally:
            await tasks.close()

    server = MCPServer(
        "Lumen report and dashboard", extensions=[tasks, analytics_apps()], lifespan=lifespan
    )

    @server.tool(annotations=READ)
    async def quarterly_report(quarter: str = "Q1", ask_details: bool = False) -> dict[str, object]:
        """Generate a simulated report. Task-aware clients can request a details choice."""
        return report(quarter)

    return server
