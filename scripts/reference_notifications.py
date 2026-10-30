"""Current-schema logging reference for the protocol guide (deprecated optional feature).
Run through scripts/phase8.py --capture. Application lessons use stderr/OTel.
"""

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp_types import LoggingMessageNotification, LoggingMessageNotificationParams

from common.notes import READ

server = MCPServer("Lumen notification reference")


@server.tool(annotations=READ)
async def inspect_logging(ctx: Context) -> str:
    """Emit one synthetic diagnostic when the client explicitly requests log-level info."""
    if ctx.request_context.meta and ctx.request_context.meta.get(
        "io.modelcontextprotocol/logLevel"
    ):
        await ctx.request_context.session.send_notification(
            LoggingMessageNotification(
                params=LoggingMessageNotificationParams(
                    level="info", logger="lumen.reference", data="Synthetic reference diagnostic"
                )
            ),
            related_request_id=ctx.request_context.request_id,
        )
    return "Use stderr or OpenTelemetry in new applications."


if __name__ == "__main__":
    server.run()
