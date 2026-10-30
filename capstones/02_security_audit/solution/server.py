"""Security Audit Lab: protocol-only stdio. Inspect with the MCP Inspector CLI."""

from common.audit_lab import audit_server

server = audit_server(repaired=True)

if __name__ == "__main__":
    server.run()
