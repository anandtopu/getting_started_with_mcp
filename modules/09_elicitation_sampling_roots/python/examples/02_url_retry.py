"""Run: uv run python modules/09_elicitation_sampling_roots/python/examples/02_url_retry.py
Expected: an input_required round, then an approved synthetic operation.
This fixed demo approves only the published fixture action.
"""

import asyncio

import httpx2 as httpx
from mcp_types import ElicitResult, InputRequiredResult

from scripts.tier1 import script_client


async def main() -> None:
    async with script_client(
        "modules/09_elicitation_sampling_roots/python/use_case/server.py", interactive=True
    ) as client:
        arguments = {}
        first = await client.session.call_tool(
            "export_report", arguments, allow_input_required=True
        )
        assert isinstance(first, InputRequiredResult)
        print("input_required: user action needed")
        # A separate browser action completes the approval; an MCP accept is insufficient.
        async with httpx.AsyncClient() as browser:
            response = await browser.post(first.input_requests["decision"].params.url)
            response.raise_for_status()
        result = await client.session.call_tool(
            "export_report",
            arguments,
            input_responses={"decision": ElicitResult(action="accept", content=None)},
            request_state=first.request_state,
            allow_input_required=True,
        )
        assert not result.is_error
        print(result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
