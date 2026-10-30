"""Reusable SDK contract check, with no model or network dependency."""

from mcp import Client


async def check_foundation(server) -> dict[str, int]:
    async with Client(server, raise_exceptions=True) as client:
        tools = await client.list_tools()
        assert any(tool.name == "dataset_counts" for tool in tools.tools)
        assert (await client.list_resources()).resources
        assert (await client.list_prompts()).prompts
        result = await client.call_tool("dataset_counts", {})
        assert not result.is_error
        assert result.structured_content == {"employees": 80, "issues": 400}
        return result.structured_content
