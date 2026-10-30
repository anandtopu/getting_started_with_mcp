"""Named, bounded SQL queries; resource pages for larger read-only results."""

import json
import sqlite3
import time
from datetime import date

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp_types import ResourceLink, TextContent

from common.data import readonly_database
from common.notes import READ


def usage_page(start: str = "2025-08-01", offset: int = 0, limit: int = 10) -> dict:
    try:
        date.fromisoformat(start)
    except ValueError:
        raise ToolError("Use an ISO date such as 2025-08-01.") from None
    if not 0 <= offset <= 365 or not 1 <= limit <= 50:
        raise ToolError("Offset must be 0–365 and limit 1–50.")
    with readonly_database("analytics.db") as db:
        deadline = time.monotonic() + 0.1
        db.set_progress_handler(lambda: int(time.monotonic() >= deadline), 100)
        try:
            rows = db.execute(
                "SELECT * FROM daily_usage WHERE day>=? ORDER BY day LIMIT ? OFFSET ?",
                (start, limit + 1, offset),
            ).fetchall()
        except sqlite3.OperationalError:
            raise ToolError("Query budget exceeded; narrow the date range.") from None
        finally:
            db.set_progress_handler(None, 0)
    more = len(rows) > limit
    return {
        "rows": [dict(row) for row in rows[:limit]],
        "truncated": more,
        "next_offset": offset + limit if more else None,
    }


def register_analytics(server: MCPServer) -> None:
    @server.tool(annotations=READ)
    def analytics_page(
        start: str = "2025-08-01", offset: int = 0, limit: int = 10
    ) -> list[TextContent | ResourceLink]:
        """Read a bounded daily-usage page; follow its link for the next page."""
        page = usage_page(start, offset, limit)
        content = [TextContent(type="text", text=json.dumps(page))]
        if page["next_offset"] is not None:
            content.append(
                ResourceLink(
                    type="resource_link",
                    name="Next usage page",
                    uri=f"analytics://usage/{start}/{page['next_offset']}/{limit}",
                    mime_type="application/json",
                )
            )
        return content

    @server.resource("analytics://usage/{start}/{offset}/{limit}")
    def usage_resource(start: str, offset: int, limit: int) -> str:
        return json.dumps(usage_page(start, offset, limit))


def make_server() -> MCPServer:
    server = MCPServer("Lumen analytics")
    register_analytics(server)
    return server
