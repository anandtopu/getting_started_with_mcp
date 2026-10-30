"""A small durable receiver for the released 2026-07-28 Tasks extension.

The official Python SDK supplies extension hooks but no Tasks implementation.
SQLite owns state; workers resume on polling after a process restart. This is
a single-process teaching receiver, not a distributed queue.
"""

import asyncio
import json
import secrets
import sqlite3
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from mcp.client.extension import ClientExtension, ResultClaim
from mcp.server.extension import Extension, MethodBinding
from mcp.server.mcpserver.server import require_client_extension
from mcp.shared.exceptions import MCPError
from mcp_types import CallToolResult, Request, RequestParams, Result
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from common.tool_design import rows

TASKS = "io.modelcontextprotocol/tasks"
ACK = {"resultType": "complete"}
TERMINAL = {"completed", "failed", "cancelled"}


def stamp() -> str:
    return datetime.now(UTC).isoformat()


class ReportArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    quarter: Literal["Q1", "Q2", "Q3", "Q4"] = "Q1"
    ask_details: bool = False


class TaskParams(RequestParams):
    task_id: str = Field(alias="taskId", min_length=1, max_length=100)


class UpdateParams(TaskParams):
    input_responses: dict = Field(alias="inputResponses")


class TaskRequest(Request[TaskParams, str]):
    name_param = "taskId"


class UpdateRequest(Request[UpdateParams, str]):
    name_param = "taskId"


class TaskResult(Result):
    model_config = ConfigDict(extra="allow")


class TaskHandle(Result):
    result_type: Literal["task"] = Field(default="task", alias="resultType")
    task_id: str = Field(alias="taskId")
    status: Literal["working", "input_required", "completed", "failed", "cancelled"]
    created_at: str = Field(alias="createdAt")
    last_updated_at: str = Field(alias="lastUpdatedAt")
    ttl_ms: int | None = Field(alias="ttlMs")
    poll_interval_ms: int = Field(default=25, alias="pollIntervalMs")


def report(quarter: str, detailed: bool = False) -> dict:
    items = rows("issues")
    result = {
        "quarter": quarter,
        "scope": "all fixture issues (simulated report)",
        "total": len(items),
    }
    if detailed:
        result["counts"] = {
            s: sum(r["status"] == s for r in items) for s in ("open", "in_progress", "closed")
        }
    return {
        "resultType": "complete",
        "content": [{"type": "text", "text": json.dumps(result)}],
        "structuredContent": result,
        "isError": False,
    }


class ReportTasks(Extension):
    identifier = TASKS

    def __init__(self, path: Path, principal=lambda: "local-learner", ttl_ms: int = 300_000):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY, owner TEXT, "
            "expires REAL, body TEXT, args TEXT, detailed INTEGER)"
        )
        self.db.commit()
        self.principal, self.ttl_ms = principal, ttl_ms
        self.workers: dict[str, asyncio.Task] = {}

    def methods(self):
        return [
            MethodBinding("tasks/get", TaskParams, self.get),
            MethodBinding("tasks/update", UpdateParams, self.update),
            MethodBinding("tasks/cancel", TaskParams, self.cancel),
        ]

    def save(self, task: dict):
        task["lastUpdatedAt"] = stamp()
        with self.db:
            self.db.execute(
                "UPDATE tasks SET body=? WHERE id=?", (json.dumps(task), task["taskId"])
            )

    def load(self, task_id: str, owner: str) -> dict:
        row = self.db.execute(
            "SELECT owner,expires,body FROM tasks WHERE id=?", (task_id,)
        ).fetchone()
        if row is None or row[0] != owner or row[1] <= time.time():
            raise MCPError(code=-32602, message="Unknown or expired task.")
        return json.loads(row[2])

    async def intercept_tool_call(self, params, ctx, call_next):
        if params.name != "quarterly_report":
            return await call_next(ctx)
        try:
            args = ReportArgs.model_validate(params.arguments or {})
        except ValidationError as exc:
            raise MCPError(-32602, "Use quarter Q1–Q4 and a boolean ask_details.") from exc
        capabilities = ctx.session.client_capabilities
        if not capabilities or TASKS not in (capabilities.extensions or {}):
            if args.ask_details:
                require_client_extension(ctx, TASKS)
            return report(args.quarter)
        if args.ask_details and not (capabilities.elicitation and capabilities.elicitation.form):
            # An empty form capability is represented by a model, not a bool.
            if not capabilities.elicitation or capabilities.elicitation.form is None:
                raise MCPError(
                    code=-32602,
                    message="Advertise form elicitation before requesting report input.",
                )
        owner = self.principal()
        with self.db:
            self.db.execute("DELETE FROM tasks WHERE expires<=?", (time.time(),))
        if self.db.execute("SELECT count(*) FROM tasks").fetchone()[0] >= 100:
            raise MCPError(code=-32603, message="Task capacity reached; retry after expiry.")
        task = {
            "taskId": secrets.token_urlsafe(24),
            "status": "working",
            "createdAt": stamp(),
            "lastUpdatedAt": stamp(),
            "ttlMs": self.ttl_ms,
            "pollIntervalMs": 25,
        }
        # KEY IDEA: commit the handle before telling the client it exists.
        with self.db:
            self.db.execute(
                "INSERT INTO tasks VALUES(?,?,?,?,?,NULL)",
                (
                    task["taskId"],
                    owner,
                    time.time() + self.ttl_ms / 1000,
                    json.dumps(task),
                    args.model_dump_json(),
                ),
            )
        self.start(task["taskId"], owner)
        return {"resultType": "task", **task}

    def start(self, task_id: str, owner: str):
        worker = self.workers.get(task_id)
        if worker is None or worker.done():
            self.workers[task_id] = asyncio.create_task(self.work(task_id, owner))
            self.workers[task_id].add_done_callback(
                lambda done: (
                    self.workers.pop(task_id, None) if self.workers.get(task_id) is done else None
                )
            )

    async def work(self, task_id: str, owner: str):
        await asyncio.sleep(0.03)
        try:
            task = self.load(task_id, owner)
            if task["status"] != "working":
                return
            raw, detailed = self.db.execute(
                "SELECT args,detailed FROM tasks WHERE id=?", (task_id,)
            ).fetchone()
            args = ReportArgs.model_validate_json(raw)
            if args.ask_details and detailed is None:
                task.update(
                    status="input_required",
                    inputRequests={
                        "details-1": {
                            "method": "elicitation/create",
                            "params": {
                                "mode": "form",
                                "message": "Include counts by status in this synthetic report?",
                                "requestedSchema": {
                                    "type": "object",
                                    "properties": {"include_details": {"type": "boolean"}},
                                    "required": ["include_details"],
                                    "additionalProperties": False,
                                },
                            },
                        }
                    },
                )
            else:
                task.update(status="completed", result=report(args.quarter, bool(detailed)))
            self.save(task)
        except MCPError:
            return  # Expired work is deliberately abandoned.
        except Exception:
            task = self.load(task_id, owner)
            task.update(
                status="failed", error={"code": -32603, "message": "Report computation failed."}
            )
            self.save(task)

    async def get(self, ctx, params):
        require_client_extension(ctx, TASKS)
        task = self.load(params.task_id, self.principal())
        if task["status"] == "working":
            self.start(params.task_id, self.principal())
        return {**ACK, **task}

    async def update(self, ctx, params):
        require_client_extension(ctx, TASKS)
        task = self.load(params.task_id, self.principal())
        if task["status"] != "input_required" or "details-1" not in params.input_responses:
            return ACK.copy()
        response = params.input_responses["details-1"]
        if not isinstance(response, dict) or response.get("action") not in {
            "accept",
            "decline",
            "cancel",
        }:
            raise MCPError(code=-32602, message="Respond with accept, decline or cancel.")
        if response["action"] != "accept":
            task.update(status="cancelled")
        else:
            content = response.get("content", {})
            if (
                not isinstance(content, dict)
                or set(content) != {"include_details"}
                or type(content["include_details"]) is not bool
            ):
                raise MCPError(code=-32602, message="include_details must be a boolean.")
            with self.db:
                self.db.execute(
                    "UPDATE tasks SET detailed=? WHERE id=?",
                    (int(content["include_details"]), params.task_id),
                )
            task.update(status="working")
        task.pop("inputRequests", None)
        self.save(task)
        if task["status"] == "working":
            self.start(params.task_id, self.principal())
        return ACK.copy()

    async def cancel(self, ctx, params):
        require_client_extension(ctx, TASKS)
        task = self.load(params.task_id, self.principal())
        if task["status"] not in TERMINAL:
            task.update(status="cancelled")
            task.pop("inputRequests", None)
            self.save(task)
        return ACK.copy()

    async def close(self):
        for worker in self.workers.values():
            worker.cancel()
        await asyncio.gather(*self.workers.values(), return_exceptions=True)
        self.db.close()


async def task_request(session, method: str, task_id: str, **kwargs) -> dict:
    cls = UpdateRequest if method == "tasks/update" else TaskRequest
    result = await session.send_request(
        cls(method=method, params={"taskId": task_id, **kwargs}), TaskResult
    )
    return result.model_dump(mode="json", by_alias=True, exclude_none=True)


class TasksClient(ClientExtension):
    identifier = TASKS

    def __init__(self, approve=None):
        self.approve = approve

    def claims(self):
        return [ResultClaim(result_type="task", model=TaskHandle, resolve=self.resolve)]

    async def resolve(self, handle, ctx):
        async with asyncio.timeout(10):
            answered = set()
            while True:
                state = await task_request(ctx.session, "tasks/get", handle.task_id)
                status = state["status"]
                if status == "completed":
                    return CallToolResult.model_validate(state["result"])
                if status in {"failed", "cancelled"}:
                    raise RuntimeError(f"Report task {status}.")
                if status == "input_required":
                    for key, request in state["inputRequests"].items():
                        if key not in answered:
                            response = (
                                await self.approve(request)
                                if self.approve
                                else {"action": "decline"}
                            )
                            await task_request(
                                ctx.session,
                                "tasks/update",
                                handle.task_id,
                                inputResponses={key: response},
                            )
                            answered.add(key)
                await asyncio.sleep(max(0.01, min(state.get("pollIntervalMs", 25) / 1000, 1)))
