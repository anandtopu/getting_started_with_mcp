"""Small policy helpers; enforce these at the transport/tool boundary."""

from collections.abc import Iterable


def origin_allowed(origin: str | None, allowed: Iterable[str]) -> bool:
    """Non-browser clients may omit Origin. Browser origins must match exactly."""
    return origin is None or origin in frozenset(allowed)
