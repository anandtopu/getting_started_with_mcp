"""Lumen Chat v2: keep elicitation and progress outside the language model."""

import asyncio

from mcp_types import InputRequiredResult

from common.host import Host


class InteractiveClient:
    """Adapt a normal Client without changing the v1 host's approval/schema gates."""

    def __init__(self, client, ask, progress):
        self.client, self.ask, self.progress = client, ask, progress

    def __getattr__(self, name):
        return getattr(self.client, name)

    async def call_tool(self, name: str, arguments: dict):
        async def send_round(**kwargs):
            async with asyncio.timeout(15):
                return await self.client.session.call_tool(
                    name,
                    arguments,
                    allow_input_required=True,
                    progress_callback=self.progress,
                    **kwargs,
                )

        result = await send_round()
        for _ in range(3):
            if not isinstance(result, InputRequiredResult):
                return result
            responses = {}
            for key, request in (result.input_requests or {}).items():
                if request.method != "elicitation/create":
                    raise RuntimeError("This host only accepts user elicitation requests.")
                responses[key] = await self.ask(request.params)
            result = await send_round(
                input_responses=responses,
                request_state=result.request_state,
            )
        if isinstance(result, InputRequiredResult):
            raise RuntimeError("Input retry budget exceeded.")
        return result


class HostV2(Host):
    async def call_tool(self, client, name: str, arguments: dict):
        # Network rounds are bounded; the human's deliberation is outside that clock.
        return await client.call_tool(name, arguments)

    def __init__(self, clients: dict, approve, ask, progress):
        super().__init__(
            {name: InteractiveClient(client, ask, progress) for name, client in clients.items()},
            approve,
        )
