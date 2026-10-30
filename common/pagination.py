"""A low-level resource catalog with an empty middle page and opaque cursors."""

from mcp.server.lowlevel import Server
from mcp_types import ListResourcesResult, Resource


def paged_server() -> Server:
    async def listing(ctx, params) -> ListResourcesResult:
        cursor = params.cursor if params else None
        if cursor is None:
            return ListResourcesResult(
                resources=[Resource(uri="wiki://index", name="Index")], next_cursor="middle"
            )
        if cursor == "middle":
            return ListResourcesResult(resources=[], next_cursor="last")
        if cursor == "last":
            return ListResourcesResult(
                resources=[Resource(uri="lumen://bulletin", name="Bulletin")]
            )
        raise ValueError("Invalid cursor: restart from the first page.")

    return Server("Lumen paged catalog", version="1.0", on_list_resources=listing)


async def all_resources(client, max_pages: int = 10) -> list:
    cursor, seen, items = None, set(), []
    for _ in range(max_pages):
        result = await client.list_resources(cursor=cursor)
        items.extend(result.resources)
        cursor = result.next_cursor
        if cursor is None:
            return items
        if cursor in seen:
            raise RuntimeError("Repeated cursor: stop instead of looping forever.")
        seen.add(cursor)
    raise RuntimeError("Page budget exceeded.")
