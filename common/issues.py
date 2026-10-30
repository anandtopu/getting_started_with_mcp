"""Transactional issue tools over a disposable copy of the Lumen fixture."""

import sqlite3
from contextlib import asynccontextmanager
from datetime import date
from typing import Literal

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel, ConfigDict, Field

from common.data import data_root
from common.notes import READ, WRITE


class IssueInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=120)
    project_id: int = Field(default=1, ge=1, le=5)
    priority: Literal["low", "medium", "high"] = "medium"


class IssueStore:
    """Own a copy and its connection; never write to the committed database."""

    def __init__(self) -> None:
        self.db = sqlite3.connect(":memory:")
        source = sqlite3.connect((data_root() / "issues.db").as_uri() + "?mode=ro", uri=True)
        try:
            source.backup(self.db)
        finally:
            source.close()
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("CREATE TABLE receipts(key TEXT PRIMARY KEY, issue_id INTEGER)")
        self.next_id = self.db.execute("SELECT max(id)+1 FROM issues").fetchone()[0]

    def close(self) -> None:
        self.db.close()

    def read(self, issue_id: int) -> dict[str, object]:
        row = self.db.execute("SELECT * FROM issues WHERE id=?", (issue_id,)).fetchone()
        if row is None:
            raise ToolError("Issue not found; choose an existing issue ID.")
        return dict(row)

    def create(self, issue: IssueInput, key: str) -> dict[str, object]:
        if not 1 <= len(key) <= 80:
            raise ToolError("Use an operation key of 1â€“80 characters.")
        with self.db:
            prior = self.db.execute("SELECT issue_id FROM receipts WHERE key=?", (key,)).fetchone()
            if prior:
                result = self.read(prior[0])
                if any(result[k] != v for k, v in issue.model_dump().items()):
                    raise ToolError("Operation key already belongs to different arguments.")
                return result
            row = self.db.execute(
                "INSERT INTO issues(id,project_id,title,status,priority,created_at) "
                "VALUES(?,?,?,?,?,?)",
                (
                    self.next_id,
                    issue.project_id,
                    issue.title,
                    "open",
                    issue.priority,
                    date(2026, 10, 30).isoformat(),
                ),
            )
            self.next_id += 1  # Do not reuse an ID whose receipt survives deletion.
            self.db.execute("INSERT INTO receipts VALUES(?,?)", (key, row.lastrowid))
            return self.read(row.lastrowid)

    def bulk_close(self, ids: list[int]) -> dict[str, object]:
        if not ids or len(ids) > 20 or len(set(ids)) != len(ids):
            raise ToolError("Choose 1â€“20 distinct issue IDs.")
        with self.db:
            for issue_id in ids:
                self.read(issue_id)
                self.db.execute("UPDATE issues SET status='closed' WHERE id=?", (issue_id,))
        return {"closed": ids}


@asynccontextmanager
async def issue_lifespan(server: MCPServer):
    store = IssueStore()
    try:
        yield {"issues": store, "active_reports": 0}
    finally:
        store.close()


def store_from(ctx: Context) -> IssueStore:
    return ctx.request_context.lifespan_context["issues"]


def register_issues(server: MCPServer) -> None:
    @server.tool(annotations=READ)
    async def read_issue(issue_id: int, ctx: Context) -> dict[str, object]:
        """Read one issue by its stable ID."""
        return store_from(ctx).read(issue_id)

    @server.tool(annotations=WRITE)
    async def create_issue(
        issue: IssueInput, operation_key: str, ctx: Context, confirmed: bool = False
    ) -> dict[str, object]:
        """Create an approved issue; reuse the same operation key after an uncertain response."""
        if not confirmed:
            raise ToolError("Confirm this exact write in the host first.")
        return store_from(ctx).create(issue, operation_key)

    @server.tool(annotations=WRITE)
    async def update_issue(
        issue_id: int,
        status: Literal["open", "in_progress", "closed"],
        ctx: Context,
        confirmed: bool = False,
    ) -> dict[str, object]:
        """Change an issue status after confirmation."""
        if not confirmed:
            raise ToolError("Confirm this exact write in the host first.")
        store = store_from(ctx)
        store.read(issue_id)
        with store.db:
            store.db.execute("UPDATE issues SET status=? WHERE id=?", (status, issue_id))
        return store.read(issue_id)

    @server.tool(annotations=WRITE)
    async def delete_issue(
        issue_id: int, ctx: Context, confirmed: bool = False
    ) -> dict[str, object]:
        """Delete an issue and its dependent records in one transaction."""
        if not confirmed:
            raise ToolError("Confirm this exact write in the host first.")
        store = store_from(ctx)
        store.read(issue_id)
        with store.db:
            for table in ("comments", "issue_labels"):
                store.db.execute(f"DELETE FROM {table} WHERE issue_id=?", (issue_id,))
            store.db.execute("DELETE FROM issues WHERE id=?", (issue_id,))
        return {"deleted": issue_id}


def make_server() -> MCPServer:
    server = MCPServer("Lumen issues", lifespan=issue_lifespan)
    register_issues(server)
    return server
