"""Second, purely synthetic audit fixture; no filesystem, shell or network access.

The insecure branch demonstrates policy defects over two fixed strings only.
It cannot reach real accounts or files, even when given attacker-controlled input.
"""

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from common.notes import READ, WRITE

FIXTURE = {"public": "Synthetic release checklist", "private": "FAKE salary: 12345"}


def audit_server(*, repaired=True):
    server = MCPServer("Lumen audit lab: repaired" if repaired else "UNSAFE SYNTHETIC LAB")
    bulletin = "Synthetic release pending"

    @server.tool(annotations=READ)
    def read_record(name: str) -> str:
        """Read the public synthetic record. Private fixture data must never be returned."""
        if repaired and name != "public":
            raise ToolError("Record is not available to this principal.")
        return FIXTURE.get(name, "Unknown synthetic record")

    @server.tool(annotations=WRITE)
    def publish_bulletin(text: str, confirmed: bool = False) -> str:
        """Replace an in-memory synthetic bulletin after the user confirms exact text."""
        nonlocal bulletin
        if repaired and not confirmed:
            raise ToolError("Confirmation required for the exact bulletin text.")
        if repaired and not 1 <= len(text) <= 200:
            raise ToolError("Bulletin must contain 1-200 characters.")
        bulletin = text
        return bulletin

    return server
