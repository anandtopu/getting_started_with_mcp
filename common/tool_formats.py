"""Translate a deliberately bounded JSON Schema subset into provider tool definitions."""

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class Turn:
    text: str = ""
    calls: list[ToolCall] = field(default_factory=list)


@dataclass
class ToolReply:
    call: ToolCall
    text: str
    error: bool = False


def provider_tools(provider: str, tools: list[dict]) -> list[dict]:
    """MCP inputSchema becomes parameters or input_schema; it never grants permission."""
    output = []
    for tool in tools:
        schema = deepcopy(tool["inputSchema"])
        common = {"name": tool["name"], "description": tool.get("description", "")}
        if provider == "anthropic":
            output.append({**common, "input_schema": schema})
        elif provider == "openai":
            output.append({"type": "function", **common, "parameters": schema, "strict": False})
        elif provider == "gemini":
            output.append({**common, "parameters_json_schema": schema})
        elif provider == "ollama":
            output.append({"type": "function", "function": {**common, "parameters": schema}})
        else:
            raise ValueError("Choose anthropic, openai, gemini or ollama.")
    return [{"function_declarations": output}] if provider == "gemini" else output
