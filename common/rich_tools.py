"""Tool result shapes: validated objects, multimedia, and resource references."""

import base64
import io
import wave

from mcp.server import MCPServer
from mcp_types import (
    Annotations,
    AudioContent,
    EmbeddedResource,
    ImageContent,
    ResourceLink,
    TextResourceContents,
)
from pydantic import BaseModel, Field

from common.notes import READ

PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII="


class ReleaseSummary(BaseModel):
    title: str = Field(description="Human-readable release label")
    open_issues: int = Field(ge=0)


def rich_server() -> MCPServer:
    server = MCPServer("Lumen rich results", version="1.0")

    @server.tool(title="Release summary", annotations=READ)
    def release_summary(open_issues: int = 3) -> ReleaseSummary:
        """Return a structured release summary; negative counts fail output validation."""
        return ReleaseSummary(title="Lumen release review", open_issues=open_issues)

    @server.tool(annotations=READ)
    def review_assets() -> list:
        """Return a tiny preview, silent audio fixture, embedded note and wiki link."""
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(8000)
            audio.writeframes(b"\x00\x00" * 80)
        return [
            ImageContent(
                type="image",
                data=PNG,
                mime_type="image/png",
                annotations=Annotations(audience=["user"], priority=0.5),
            ),
            AudioContent(
                type="audio",
                data=base64.b64encode(buffer.getvalue()).decode(),
                mime_type="audio/wav",
            ),
            EmbeddedResource(
                type="resource",
                resource=TextResourceContents(
                    uri="lumen://review/note",
                    text="Synthetic review fixture.",
                    mime_type="text/plain",
                ),
            ),
            ResourceLink(
                uri="wiki://engineering/page-01",
                name="Release reference",
                mime_type="text/markdown",
            ),
        ]

    return server
