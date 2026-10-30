"""Three real framework runtimes, one read-only MCP server, deterministic models.

Imports are local so foundation lessons do not require the frameworks extra.
The LangChain and Pydantic adapters use third-party FastMCP internally; the
course server itself uses the official SDK.
"""

import json
import sys
from typing import TypedDict

from common.config import ROOT

SERVER = ROOT / "modules/15_agent_frameworks/python/use_case/server.py"
PROMPT = (
    "Triage the synthetic work items for the week starting 2026-07-13 "
    "and draft a status update. Do not publish."
)
ARGS = {"week_start": "2026-07-13"}
ALLOWED = {"triage_week", "draft_status"}


def server_config(path=SERVER) -> dict:
    return {"command": sys.executable, "args": [str(path)], "cwd": str(ROOT)}


async def run_agents(path=SERVER, prefix="") -> str:
    from agents import Agent, RunConfig, Runner
    from agents.items import ModelResponse
    from agents.mcp import MCPServerStdio
    from agents.models.interface import Model
    from agents.usage import Usage
    from openai.types.responses import (
        ResponseFunctionToolCall,
        ResponseOutputMessage,
        ResponseOutputText,
    )

    class FixtureModel(Model):
        def __init__(self):
            self.step = 0

        async def get_response(
            self,
            system_instructions,
            input,
            model_settings,
            tools,
            output_schema,
            handoffs,
            tracing,
            **kwargs,
        ):
            self.step += 1
            if self.step <= 2:
                name = prefix + ("triage_week" if self.step == 1 else "draft_status")
                assert name in {tool.name for tool in tools}
                output = [
                    ResponseFunctionToolCall(
                        id=f"item-{self.step}",
                        call_id=f"call-{self.step}",
                        name=name,
                        arguments=json.dumps(ARGS),
                        type="function_call",
                    )
                ]
            else:
                evidence = [
                    item["output"]
                    for item in input
                    if isinstance(item, dict) and item.get("type") == "function_call_output"
                ]
                if len(evidence) != 2:
                    raise AssertionError("Both MCP tool results must reach the framework model.")
                output = [
                    ResponseOutputMessage(
                        id="answer",
                        role="assistant",
                        status="completed",
                        type="message",
                        content=[
                            ResponseOutputText(
                                type="output_text", text=str(evidence[-1]), annotations=[]
                            )
                        ],
                    )
                ]
            return ModelResponse(output=output, usage=Usage(), response_id=None)

        async def stream_response(self, *args, **kwargs):
            raise RuntimeError("This local fixture uses non-streaming Runner.run.")
            yield  # An async-generator interface, never reached.

    async with MCPServerStdio(
        params=server_config(path),
        name="lumen",
        use_structured_content=True,
        tool_filter={"allowed_tool_names": [prefix + name for name in ALLOWED]},
    ) as server:
        agent = Agent(
            name="Lumen triage", instructions=PROMPT, model=FixtureModel(), mcp_servers=[server]
        )
        result = await Runner.run(
            agent, PROMPT, max_turns=4, run_config=RunConfig(tracing_disabled=True)
        )
        return str(result.final_output)


async def run_langgraph(path=SERVER, prefix="") -> str:
    from langchain.mcp import MCPAdapter
    from langgraph.graph import END, START, StateGraph

    class State(TypedDict):
        triage: str
        draft: str

    config = {"mcpServers": {"lumen": {"transport": "stdio", **server_config(path)}}}
    async with MCPAdapter(config) as adapter:
        tools = {tool.name: tool for tool in await adapter.list_tools()}

        async def triage_node(state):
            return {"triage": str(await tools[prefix + "triage_week"].ainvoke(ARGS))}

        async def draft_node(state):
            if not state["triage"]:
                raise AssertionError("Triage evidence is required before drafting.")
            return {"draft": str(await tools[prefix + "draft_status"].ainvoke(ARGS))}

        # A deterministic graph proves integration, not autonomous model selection.
        graph = StateGraph(State)
        graph.add_node("triage", triage_node)
        graph.add_node("draft", draft_node)
        graph.add_edge(START, "triage")
        graph.add_edge("triage", "draft")
        graph.add_edge("draft", END)
        result = await graph.compile().ainvoke({"triage": "", "draft": ""})
        return result["draft"]


async def run_pydantic(path=SERVER, prefix="") -> str:
    from pydantic_ai import Agent
    from pydantic_ai.mcp import MCPToolset
    from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart, ToolReturnPart
    from pydantic_ai.models.function import FunctionModel

    step = 0

    def fixture(messages, info):
        nonlocal step
        step += 1
        if step <= 2:
            name = prefix + ("triage_week" if step == 1 else "draft_status")
            assert name in {tool.name for tool in info.function_tools}
            return ModelResponse(
                parts=[ToolCallPart(tool_name=name, args=ARGS, tool_call_id=f"call-{step}")]
            )
        evidence = [
            part.content
            for message in messages
            for part in message.parts
            if isinstance(part, ToolReturnPart)
        ]
        assert len(evidence) == 2
        return ModelResponse(parts=[TextPart(content=str(evidence[-1]))])

    config = {"mcpServers": {"lumen": {"transport": "stdio", **server_config(path)}}}
    toolset = MCPToolset(config, prefer_tasks=False).filtered(
        lambda ctx, tool: tool.name in {prefix + n for n in ALLOWED}
    )
    agent = Agent(FunctionModel(fixture), toolsets=[toolset], instructions=PROMPT)
    async with agent:
        result = await agent.run(PROMPT)
    return str(result.output)


async def run_framework(name: str, path=SERVER, prefix="") -> str:
    try:
        runner = {"agents": run_agents, "langgraph": run_langgraph, "pydantic": run_pydantic}[name]
        return await runner(path, prefix)
    except ImportError as exc:
        raise RuntimeError(
            "Install the adapters with uv sync --extra frameworks. "
            "Run scripts/check_env.py for environment help."
        ) from exc
