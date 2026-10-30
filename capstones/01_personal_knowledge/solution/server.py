"""Personal Knowledge Server: protocol-only stdio. Inspect with the MCP Inspector CLI."""

from common.config import ROOT
from common.knowledge import knowledge_server

server = knowledge_server(ROOT / "capstones/01_personal_knowledge/notes")

if __name__ == "__main__":
    server.run()
