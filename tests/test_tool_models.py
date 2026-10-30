"""Exercise provider payloads and history preservation without contacting providers."""

from types import SimpleNamespace as NS

import pytest
from pydantic import SecretStr

from common.config import Settings
from common.tool_formats import ToolReply
from common.tool_models import ProviderToolModel


@pytest.mark.anyio
@pytest.mark.parametrize("provider", ["openai", "anthropic", "gemini", "ollama"])
async def test_native_tool_history_and_response_ids(monkeypatch, provider):
    requests = []
    call = NS(id="call-7", name="notes__search_notes", args={"query": "release"})
    gemini_content = NS(
        role="model",
        parts=[NS(function_call=call, text=None, thought=False, thought_signature=b"signature")],
    )
    openai_output = [
        NS(type="reasoning", id="reason-1"),
        NS(type="function_call", call_id="call-7", name=call.name, arguments='{"query":"release"}'),
    ]
    anthropic_content = [
        NS(type="tool_use", id="call-7", name=call.name, input={"query": "release"})
    ]

    class OllamaMessage:
        content = ""
        tool_calls = [NS(function=NS(name=call.name, arguments={"query": "release"}))]

        def model_dump(self, **kwargs):
            return {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"function": {"name": call.name, "arguments": {"query": "release"}}}
                ],
            }

    async def create(**kwargs):
        requests.append(kwargs.copy())
        if provider == "openai":
            return NS(output=openai_output, output_text="")
        if provider == "anthropic":
            return NS(content=anthropic_content)
        if provider == "gemini":
            return NS(candidates=[NS(content=gemini_content)])
        return NS(message=OllamaMessage())

    class Client:
        def __init__(self, **kwargs):
            self.responses = self.messages = NS(create=create)
            self.models = NS(generate_content=create)
            self.aio = self
            self.chat = create

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

    sdk = NS(AsyncOpenAI=Client, AsyncAnthropic=Client, Client=Client, AsyncClient=Client)
    monkeypatch.setattr("common.tool_models.import_module", lambda name: sdk)
    model = ProviderToolModel(
        Settings(provider=provider, model="offline-fixture", api_key=SecretStr("fake")),
        "Find release notes",
    )
    tools = [{"name": call.name, "description": "Find notes", "inputSchema": {"type": "object"}}]
    turn = await model.turn(tools, [])
    assert turn.calls[0].arguments == {"query": "release"}
    assert turn.calls[0].name == call.name
    await model.turn(tools, [ToolReply(turn.calls[0], "Denied", True)])
    if provider == "openai":
        assert openai_output[0] in model.history
        assert {
            "type": "function_call_output",
            "call_id": "call-7",
            "output": "Denied",
        } in model.history
    elif provider == "anthropic":
        assert model.history[1]["content"] is anthropic_content
        assert model.history[2]["content"][0]["tool_use_id"] == "call-7"
        assert model.history[2]["content"][0]["is_error"] is True
    elif provider == "gemini":
        assert model.history[1] is gemini_content
        assert model.history[2]["parts"][0]["function_response"]["id"] == "call-7"
        assert requests[0]["config"]["automatic_function_calling"] == {"disable": True}
    else:
        assert model.history[2] == {"role": "tool", "tool_name": call.name, "content": "Denied"}


def test_gemini_definition_accepts_current_sdk_json_schema():
    FunctionDeclaration = pytest.importorskip("google.genai.types").FunctionDeclaration
    from common.tool_formats import provider_tools

    tool = {"name": "search", "inputSchema": {"type": "object", "properties": {}}}
    declaration = provider_tools("gemini", [tool])[0]["function_declarations"][0]
    assert FunctionDeclaration(**declaration).parameters_json_schema == tool["inputSchema"]
