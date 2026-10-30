"""Workspace v1: isolated in-memory notes, with explicit write confirmation."""

from threading import Lock
from typing import Annotated

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp_types import ToolAnnotations
from pydantic import Field

READ = ToolAnnotations(
    read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False
)
WRITE = ToolAnnotations(
    read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False
)
# Replacing or deleting existing data has destructive potential, even in a fixture.
REPLACE = WRITE.model_copy(update={"destructive_hint": True})


def notes_server() -> MCPServer:
    server = MCPServer("Lumen notes", version="1.0")
    notes = [
        {
            "id": 1,
            "title": "Release handover",
            "body": "Review the release checklist.",
            "tags": ["release"],
        }
    ]
    lock = Lock()

    @server.tool(annotations=READ)
    def search_notes(query: Annotated[str, Field(max_length=100)] = "") -> list[dict]:
        """Find notes whose title or body contains query, ignoring case. Empty query lists all."""
        with lock:
            return [
                dict(n, tags=list(n["tags"]))
                for n in notes
                if query.casefold() in (n["title"] + " " + n["body"]).casefold()
            ]

    @server.tool(annotations=WRITE)
    def create_note(
        title: Annotated[str, Field(min_length=1, max_length=100)],
        body: Annotated[str, Field(min_length=1, max_length=2000)],
        confirmed: bool = False,
    ) -> dict[str, int | str]:
        """Create an ephemeral note only after the user confirms. Restarting clears new notes."""
        if not confirmed:
            raise ToolError("Confirmation required: review the title and body before creating.")
        with lock:
            note = {"id": len(notes) + 1, "title": title, "body": body, "tags": []}
            notes.append(note)
            return {"id": note["id"], "title": title}

    @server.tool(
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        )
    )
    def tag_note(
        note_id: int,
        tag: Annotated[str, Field(min_length=1, max_length=40)],
        confirmed: bool = False,
    ) -> dict[str, int | list[str]]:
        """Add a tag once to an existing note. Confirm the note ID and tag first."""
        if not confirmed:
            raise ToolError("Confirmation required: review the note ID and tag.")
        with lock:
            note = next((n for n in notes if n["id"] == note_id), None)
            if note is None:
                raise ToolError("Note not found: search notes to obtain a valid ID.")
            if tag not in note["tags"]:
                note["tags"].append(tag)
            return {"id": note_id, "tags": list(note["tags"])}

    return server
