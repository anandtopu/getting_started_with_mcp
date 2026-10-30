"""Current input_required form and URL retries; all effects follow validation."""

from contextlib import asynccontextmanager

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError
from mcp_types import (
    ElicitRequest,
    ElicitRequestFormParams,
    ElicitRequestURLParams,
    ElicitResult,
    InputRequiredResult,
)
from pydantic import BaseModel, ConfigDict, StrictBool

from common.issues import issue_lifespan, register_issues, store_from
from common.notes import WRITE
from common.portal import approval_portal
from common.retry import RetryLedger


class Confirm(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approve: StrictBool


@asynccontextmanager
async def input_lifespan(server: MCPServer):
    async with issue_lifespan(server) as state:
        state["ledger"] = RetryLedger()
        async with approval_portal(state["ledger"]) as origin:
            state["portal"] = origin
            yield state


def answer(ctx: Context) -> ElicitResult:
    responses = ctx.input_responses or {}
    result = responses.get("decision")
    if set(responses) != {"decision"} or not isinstance(result, ElicitResult):
        raise ToolError("Expected exactly one elicitation response named decision.")
    return result


def require_mode(ctx: Context, mode: str) -> None:
    caps = ctx.client_capabilities
    elicitation = caps.elicitation if caps else None
    if elicitation is None or (mode == "url" and elicitation.url is None):
        raise ToolError(f"Client must advertise {mode} elicitation support.")
    if mode == "form" and elicitation.form is None and elicitation.url is not None:
        raise ToolError("Client must advertise form elicitation support.")


def register_input(server: MCPServer) -> None:
    @server.tool(annotations=WRITE)
    async def bulk_close(
        issue_ids: list[int], ctx: Context
    ) -> dict[str, object] | InputRequiredResult:
        """Ask the user before closing 1-20 distinct issues in a disposable database."""
        if not issue_ids or len(issue_ids) > 20 or len(set(issue_ids)) != len(issue_ids):
            raise ToolError("Choose 1-20 distinct issue IDs.")
        store = store_from(ctx)
        for issue_id in issue_ids:
            store.read(issue_id)
        ledger = ctx.request_context.lifespan_context["ledger"]
        arguments = {"issue_ids": issue_ids}
        if ctx.request_state is None:
            require_mode(ctx, "form")
            token = ledger.issue("bulk_close", arguments)
            return InputRequiredResult(
                request_state=token,
                input_requests={
                    "decision": ElicitRequest(
                        params=ElicitRequestFormParams(
                            message=f"Close these synthetic issues: {issue_ids}?",
                            requested_schema=Confirm.model_json_schema(),
                        )
                    )
                },
            )
        ledger.take(ctx.request_state, "bulk_close", arguments)
        response = answer(ctx)
        if response.action != "accept":
            return {"outcome": response.action, "closed": []}
        try:
            confirmation = Confirm.model_validate(response.content)
        except ValueError:
            raise ToolError("The form requires a boolean approve field.") from None
        return store.bulk_close(issue_ids) if confirmation.approve else {"closed": []}

    @server.tool(annotations=WRITE)
    async def export_report(ctx: Context) -> dict[str, object] | InputRequiredResult:
        """Ask the user to approve a fixture export in a separate local browser page."""
        state = ctx.request_context.lifespan_context
        if ctx.request_state is None:
            require_mode(ctx, "url")
            token = state["ledger"].issue("export_report", {})
            return InputRequiredResult(
                request_state=token,
                input_requests={
                    "decision": ElicitRequest(
                        params=ElicitRequestURLParams(
                            message="Open the local approval page, approve, then return here.",
                            url=f"{state['portal']}/approve/{token}",
                        )
                    )
                },
            )
        pending = state["ledger"].take(ctx.request_state, "export_report", {})
        response = answer(ctx)
        if response.action != "accept":
            return {"outcome": response.action, "exported": False}
        if not pending.approved:
            raise ToolError("The browser approval has not completed; start again.")
        return {"exported": True, "report": "Synthetic Lumen issue report"}


def make_server() -> MCPServer:
    server = MCPServer("Lumen input", lifespan=input_lifespan)
    register_issues(server)
    register_input(server)
    return server
