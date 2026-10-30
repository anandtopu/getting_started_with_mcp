"""Claude Agent SDK connection and read-only permissions; model use is opt-in."""

import asyncio

from common.config import load_settings
from common.frameworks import ALLOWED, PROMPT, server_config


def options():
    from claude_agent_sdk import ClaudeAgentOptions

    return ClaudeAgentOptions(
        mcp_servers={"lumen": {"type": "stdio", **server_config()}},
        strict_mcp_config=True,
        tools=[],
        allowed_tools=[f"mcp__lumen__{name}" for name in sorted(ALLOWED)],
        permission_mode="default",
        max_turns=4,
        env={
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
            "DISABLE_TELEMETRY": "1",
            "DISABLE_ERROR_REPORTING": "1",
        },
    )


async def probe(live=False):
    from claude_agent_sdk import ClaudeSDKClient

    config = options()
    if live:
        settings = load_settings()
        if settings.provider != "anthropic":
            raise RuntimeError("Set LLM_PROVIDER=anthropic and LLM_MODEL before --live.")
        config.model = settings.model
        config.env["ANTHROPIC_API_KEY"] = settings.api_key.get_secret_value()
    async with asyncio.timeout(40), ClaudeSDKClient(options=config) as client:
        for _ in range(25):
            status = await client.get_mcp_status()
            servers = status.get("mcpServers", [])
            if servers and all(server["status"] == "connected" for server in servers):
                break
            if any(server["status"] == "failed" for server in servers):
                raise RuntimeError("Claude SDK could not connect to the local server.")
            await asyncio.sleep(0.5)
        else:
            raise RuntimeError("Claude SDK MCP connection did not become ready.")
        if live:
            await client.query(PROMPT)
            messages = []
            async for message in client.receive_response():
                messages.append(type(message).__name__)
            return {"status": status, "message_types": messages}
        return status
