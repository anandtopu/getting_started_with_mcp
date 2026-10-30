"""One-use approvals bound to validated tool arguments and a user identity."""

import hashlib
import json
import secrets
import time
from collections.abc import Callable


class Approvals:
    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self.clock = clock
        self.pending: dict[str, tuple[str, float]] = {}

    @staticmethod
    def fingerprint(user: str, tool: str, arguments: dict) -> str:
        value = json.dumps([user, tool, arguments], sort_keys=True, allow_nan=False)
        return hashlib.sha256(value.encode()).hexdigest()

    def grant(
        self, user: str, tool: str, arguments: dict, *, confirmed: bool, ttl: float = 60
    ) -> str:
        if not confirmed or ttl <= 0:
            raise PermissionError("Explicit confirmation is required.")
        self.pending = {k: v for k, v in self.pending.items() if v[1] > self.clock()}
        token = secrets.token_urlsafe(24)
        self.pending[token] = (self.fingerprint(user, tool, arguments), self.clock() + ttl)
        return token

    def consume(self, token: str, user: str, tool: str, arguments: dict) -> None:
        expected, expires = self.pending.pop(token, ("", 0))
        if expires <= self.clock() or expected != self.fingerprint(user, tool, arguments):
            raise PermissionError("Approval is missing, expired, or for another operation.")
