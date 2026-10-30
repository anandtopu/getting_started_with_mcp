"""Request-scoped progress, cooperative cancellation and lifespan cleanup."""

import asyncio
import json
import logging
from typing import Literal

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError
from mcp_types import Completion, PromptReference

from common.issues import issue_lifespan, store_from
from common.notes import READ

logger = logging.getLogger("lumen.reports")


def register_reports(server: MCPServer) -> None:
    @server.tool(annotations=READ)
    async def report_status(ctx: Context) -> dict[str, object]:
        """Inspect active report work; useful after cancellation."""
        return {
            "active": ctx.request_context.lifespan_context["active_reports"],
            "issue_count": store_from(ctx).db.execute("SELECT count(*) FROM issues").fetchone()[0],
        }

    @server.tool(annotations=READ)
    async def quarterly_report(
        ctx: Context, quarter: Literal["Q1", "Q2", "Q3", "Q4"] = "Q1", delay: float = 0.02
    ) -> dict[str, object]:
        """Count issues by status, with progress and a bounded cancellable work simulation."""
        if not 0 <= delay <= 1:
            raise ToolError("Delay must be between zero and one second.")
        state = ctx.request_context.lifespan_context
        state["active_reports"] += 1
        try:
            async with asyncio.timeout(5):
                for step in range(4):
                    await asyncio.sleep(delay)
                    await ctx.report_progress(step + 1, 4, f"{quarter}: section {step + 1}")
                rows = (
                    store_from(ctx)
                    .db.execute("SELECT status, count(*) AS count FROM issues GROUP BY status")
                    .fetchall()
                )
                return {
                    "quarter": quarter,
                    "scope": "all fixture issues (simulated report)",
                    "counts": [dict(row) for row in rows],
                }
        finally:
            state["active_reports"] -= 1
            logger.info("Report request finished or cancelled")  # stderr, not protocol stdout

    @server.prompt()
    def report_brief(quarter: str = "Q1") -> str:
        return f"Summarize the {quarter} fixture report; state that dates are simulated."

    @server.completion()
    async def complete(ref, argument, context) -> Completion:
        values = [f"Q{i}" for i in range(1, 5)]
        matches = [v for v in values if v.startswith(argument.value)]
        if not isinstance(ref, PromptReference) or ref.name != "report_brief":
            matches = []
        return Completion(values=matches, total=len(matches), has_more=False)

    @server.resource("report://catalog")
    def catalog() -> str:
        return json.dumps({"quarters": ["Q1", "Q2", "Q3", "Q4"]})


def make_server() -> MCPServer:
    server = MCPServer("Lumen reports", lifespan=issue_lifespan)
    register_reports(server)
    return server
