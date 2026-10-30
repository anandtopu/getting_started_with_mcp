"""Workspace v2: static and templated resources with opt-in change streams."""

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ResourceNotFoundError, ToolError
from mcp_types import (
    Annotations,
    Completion,
    CompletionArgument,
    CompletionContext,
    PromptReference,
    ResourceTemplateReference,
)

from common.data import data_root, safe_path
from common.notes import READ, REPLACE

SPACES = ["engineering", "product", "hr", "onboarding", "incident_postmortems"]


def wiki_text(space: str, page: str) -> str:
    if space not in SPACES or page not in {f"page-{i:02d}" for i in range(1, 9)}:
        raise ResourceNotFoundError(
            "Unknown wiki page: use a listed space and page-01 through page-08."
        )
    return safe_path(data_root(), f"wiki/{space}/{page}.md").read_text(encoding="utf-8")


def wiki_server() -> MCPServer:
    server = MCPServer("Lumen wiki", version="2.0")
    state = {"text": "Release review at 14:00 UTC", "revision": 1}
    status_enabled = False

    @server.completion()
    async def complete(
        ref: PromptReference | ResourceTemplateReference,
        argument: CompletionArgument,
        context: CompletionContext | None,
    ) -> Completion:
        options = []
        if isinstance(ref, ResourceTemplateReference) and ref.uri == "wiki://{space}/{page}":
            if argument.name == "space":
                options = SPACES
            elif (
                argument.name == "page"
                and context
                and (context.arguments or {}).get("space") in SPACES
            ):
                options = [f"page-{i:02d}" for i in range(1, 9)]
        return Completion(values=[v for v in options if v.startswith(argument.value)])

    @server.resource(
        "wiki://index",
        mime_type="text/plain",
        title="Lumen wiki index",
        annotations=Annotations(audience=["user"], priority=1.0),
    )
    def index() -> str:
        """Available spaces; each contains page-01 through page-08."""
        return ", ".join(SPACES)

    @server.resource("wiki://{space}/{page}", mime_type="text/markdown")
    def page(space: str, page: str) -> str:
        return wiki_text(space, page)

    @server.resource("lumen://contract/1", mime_type="application/pdf")
    def contract() -> bytes:
        return (data_root() / "files/contracts/contract-01.pdf").read_bytes()

    @server.resource("lumen://bulletin", mime_type="text/plain")
    def bulletin() -> str:
        return state["text"]

    @server.tool(annotations=READ)
    def find_page(space: str = "engineering", page: str = "page-01") -> list:
        """Return a wiki resource link after checking that the page exists."""
        from mcp_types import ResourceLink

        wiki_text(space, page)
        return [ResourceLink(uri=f"wiki://{space}/{page}", name=page, mime_type="text/markdown")]

    @server.tool(annotations=REPLACE)
    async def update_bulletin(text: str, ctx: Context, confirmed: bool = False) -> str:
        """Update only the in-memory training bulletin after confirmation; notify subscribers."""
        nonlocal status_enabled
        if not confirmed:
            raise ToolError("Confirmation required: review the bulletin text.")
        if not 1 <= len(text) <= 500:
            raise ToolError("Bulletin text must contain 1 to 500 characters.")
        state["text"] = text
        state["revision"] += 1
        if not status_enabled:

            @server.tool(annotations=READ)
            def bulletin_status() -> str:
                """Read the revision after the bulletin has been reviewed at least once."""
                return f"Bulletin revision {state['revision']}"

            @server.resource("lumen://review-receipt", mime_type="text/plain")
            def review_receipt() -> str:
                return f"Reviewed bulletin revision {state['revision']}"

            status_enabled = True
        # KEY IDEA: the notification means refetch; it does not contain the new content.
        await ctx.notify_resource_updated("lumen://bulletin")
        await ctx.notify_resources_changed()
        await ctx.notify_tools_changed()
        return f"Bulletin revision {state['revision']}"

    return server
