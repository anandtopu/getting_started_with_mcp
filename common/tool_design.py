"""Read-only API mirror and task-oriented tools over the same synthetic database."""

import json
import sqlite3
from datetime import date, timedelta
from typing import Annotated, Literal

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

from common.data import data_root
from common.notes import READ

TABLES = ("issues", "projects", "users", "comments", "labels")
Mode = Literal["concise", "detailed"]
Limit = Annotated[int, Field(ge=1, le=20)]


def rows(table: str) -> list[dict]:
    if table not in TABLES:
        raise ValueError("Unknown fixture table.")
    db = sqlite3.connect((data_root() / "issues.db").as_uri() + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in db.execute(f"SELECT * FROM {table} ORDER BY id")]
    finally:
        db.close()


def page(items: list[dict], after: int, limit: int) -> dict[str, object]:
    eligible = [item for item in items if item["id"] > after]
    selected = eligible[:limit]
    return {
        "items": selected,
        "next_after": selected[-1]["id"] if len(eligible) > limit else None,
    }


def issue_brief(issue_id: int, mode: Mode = "concise") -> dict[str, object]:
    issue = next((r for r in rows("issues") if r["id"] == issue_id), None)
    if issue is None:
        raise ToolError("Issue not found. Use search_issues and choose an ID from its results.")
    result = {k: issue[k] for k in ("id", "title", "status", "priority")}
    if mode == "detailed":
        result.update(issue)
        result["comments"] = [r["body"] for r in rows("comments") if r["issue_id"] == issue_id]
    return result


def weekly_issues(week_start: str = "2026-07-13") -> list[dict]:
    try:
        start = date.fromisoformat(week_start)
    except ValueError as exc:
        raise ToolError("Use week_start as an ISO date, for example 2026-07-13.") from exc
    stop = start + timedelta(days=7)
    # The fixture calls these work items; 'bug' is a triage scenario, not a stored type.
    return [r for r in rows("issues") if start.isoformat() <= r["created_at"] < stop.isoformat()]


def triage(week_start: str = "2026-07-13") -> dict[str, object]:
    items = weekly_issues(week_start)
    active = [r for r in items if r["status"] != "closed"]
    return {
        "week_start": week_start,
        "total": len(items),
        "active": len(active),
        "high_priority_ids": [r["id"] for r in active if r["priority"] == "high"],
        "fixture_note": "Synthetic work items; no separate bug type is stored.",
    }


def draft_status(week_start: str = "2026-07-13") -> dict[str, object]:
    result = triage(week_start)
    return {
        "draft": f"Week {week_start}: {result['total']} work items; "
        f"{result['active']} active; {len(result['high_priority_ids'])} high priority.",
        "published": False,
        "evidence": result,
    }


def mirror_server() -> MCPServer:
    server = MCPServer("Lumen endpoint mirror", version="6.0")

    def register(table: str):
        async def list_rows(after: int = 0, limit: Limit = 10) -> dict[str, object]:
            return page(rows(table), after, limit)

        async def get_row(row_id: int) -> dict[str, object]:
            result = next((r for r in rows(table) if r["id"] == row_id), None)
            if result is None:
                raise ToolError("Record not found. List records first and choose an existing ID.")
            return result

        async def count_rows() -> dict[str, object]:
            return {"count": len(rows(table))}

        async def fields() -> dict[str, object]:
            return {"fields": list(rows(table)[0])}

        async def find_rows(
            text: Annotated[str, Field(max_length=100)], limit: Limit = 10
        ) -> dict[str, object]:
            found = [r for r in rows(table) if text.casefold() in json.dumps(r).casefold()]
            return page(found, 0, limit)

        for action, fn in zip(
            ("list", "get", "count", "fields", "find"),
            (list_rows, get_row, count_rows, fields, find_rows),
            strict=True,
        ):
            server.add_tool(
                fn,
                name=f"{action}_{table}",
                description=f"{action} {table} records.",
                annotations=READ,
            )

    for table in TABLES:
        register(table)
    return server


def task_server() -> MCPServer:
    server = MCPServer("Lumen task tools", version="6.0")

    @server.tool(annotations=READ)
    async def search_issues(
        query: Annotated[str, Field(max_length=100)] = "",
        after: Annotated[int, Field(ge=0)] = 0,
        limit: Limit = 10,
        mode: Mode = "concise",
    ) -> dict[str, object]:
        """Find items by title. Follow next_after; start concise, then fetch details."""
        found = [r for r in rows("issues") if query.casefold() in r["title"].casefold()]
        result = page(found, after, limit)
        result["items"] = [issue_brief(r["id"], mode) for r in result["items"]]
        return result

    server.add_tool(
        issue_brief,
        description="Read a known issue ID. Choose detailed for comments or ownership.",
        annotations=READ,
    )
    server.add_tool(
        triage,
        name="triage_week",
        description="Summarize seven days of synthetic work items. Specify the ISO start date.",
        annotations=READ,
    )
    server.add_tool(
        draft_status,
        description="Draft a weekly status update from evidence. Returns text; never publishes.",
        annotations=READ,
    )

    @server.tool(annotations=READ)
    async def project_summary(project_id: Annotated[int, Field(ge=1, le=5)]) -> dict[str, object]:
        """Count a project's work items by status without paging through every issue."""
        items = [r for r in rows("issues") if r["project_id"] == project_id]
        return {
            "project_id": project_id,
            "total": len(items),
            "active": sum(r["status"] != "closed" for r in items),
        }

    @server.tool(annotations=READ)
    async def team_load(assignee_id: Annotated[int, Field(ge=1, le=80)]) -> dict[str, object]:
        """Count active work assigned to one synthetic employee; use an existing assignee ID."""
        return {
            "assignee_id": assignee_id,
            "active": sum(
                r["assignee_id"] == assignee_id and r["status"] != "closed" for r in rows("issues")
            ),
        }

    return server
