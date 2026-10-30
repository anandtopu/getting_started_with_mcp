"""Advertise supported input modes while defaulting unhandled prompts to denial."""

from mcp_types import ElicitResult


async def decline_unhandled_input(context, params) -> ElicitResult:
    """Manual retry hosts handle input explicitly; automatic fallback never approves."""
    return ElicitResult(action="decline")
