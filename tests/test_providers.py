"""Exercise all provider branches offline with strict SDK-shaped client doubles."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from common.config import Settings
from common.llm import ProviderModel


@pytest.mark.anyio
@pytest.mark.parametrize("provider", ["openai", "anthropic", "gemini", "ollama"])
async def test_provider_requests_and_cleanup(provider, monkeypatch):
    results = {
        "openai": SimpleNamespace(output_text="fixture answer"),
        "anthropic": SimpleNamespace(content=[SimpleNamespace(type="text", text="fixture answer")]),
        "gemini": SimpleNamespace(text="fixture answer"),
        "ollama": SimpleNamespace(message=SimpleNamespace(content="fixture answer")),
    }
    send = AsyncMock(return_value=results[provider])
    closed = []

    class Client:
        responses = SimpleNamespace(create=send)
        messages = SimpleNamespace(create=send)
        models = SimpleNamespace(generate_content=send)
        chat = send

        def __init__(self, **kwargs):
            self.options = kwargs

        @property
        def aio(self):
            return self

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            closed.append(True)

    sdk = SimpleNamespace(
        AsyncOpenAI=Client, AsyncAnthropic=Client, Client=Client, AsyncClient=Client
    )
    monkeypatch.setattr("common.llm.import_module", lambda _: sdk)
    model = ProviderModel(Settings(provider=provider, model="test-model", api_key="fixture-key"))
    assert await model.generate("Summarize Lumen") == "fixture answer"
    assert closed == [True]
    assert send.call_args.kwargs["model"] == "test-model"
    send.side_effect = RuntimeError("fixture-key private request")
    with pytest.raises(RuntimeError) as error:
        await model.generate("Another request")
    assert "fixture-key" not in str(error.value)
    assert "check_env.py" in str(error.value)
    assert len(closed) == 2


def test_installed_provider_api_signatures():
    """Extras are optional locally; CI installs them to check real public interfaces."""
    import inspect

    openai = pytest.importorskip("openai")
    anthropic = pytest.importorskip("anthropic")
    genai = pytest.importorskip("google.genai")
    ollama = pytest.importorskip("ollama")
    with openai.OpenAI(api_key="fixture") as client:
        assert {"input", "model", "max_output_tokens"} <= set(
            inspect.signature(client.responses.create).parameters
        )
    with anthropic.Anthropic(api_key="fixture") as client:
        assert {"messages", "model", "max_tokens"} <= set(
            inspect.signature(client.messages.create).parameters
        )
    with genai.Client(api_key="fixture") as client:
        assert {"model", "contents", "config"} <= set(
            inspect.signature(client.models.generate_content).parameters
        )
    assert {"model", "messages", "options"} <= set(
        inspect.signature(ollama.AsyncClient.chat).parameters
    )
