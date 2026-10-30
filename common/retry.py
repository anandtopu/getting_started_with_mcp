"""Short-lived, one-use continuations bound to the exact tool arguments."""

import json
import secrets
import time
from dataclasses import dataclass

from mcp.server.mcpserver.exceptions import ToolError


@dataclass
class Pending:
    binding: str
    expires: float
    approved: bool = False


class RetryLedger:
    def __init__(self, ttl: float = 60) -> None:
        self.ttl = ttl
        self.pending: dict[str, Pending] = {}

    def issue(self, tool: str, arguments: dict) -> str:
        self.pending = {k: v for k, v in self.pending.items() if v.expires > time.monotonic()}
        if len(self.pending) >= 100:
            raise ToolError("Too many pending requests; wait for existing requests to expire.")
        token = secrets.token_urlsafe(24)
        self.pending[token] = Pending(
            json.dumps([tool, arguments], sort_keys=True), time.monotonic() + self.ttl
        )
        return token

    def take(self, token: str, tool: str, arguments: dict) -> Pending:
        pending = self.pending.pop(token, None)
        if pending is None or pending.expires <= time.monotonic():
            raise ToolError("Request expired or was already used; start again.")
        if pending.binding != json.dumps([tool, arguments], sort_keys=True):
            raise ToolError("Arguments changed; start a new confirmation.")
        return pending
