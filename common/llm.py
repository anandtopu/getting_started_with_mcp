"""One-shot model generation for foundation lessons; no implicit tool execution.

Run: uv run python scripts/check_env.py. Module 06 builds conversation and tool
conversion on top of these provider clients. Tests use FakeModel without keys.
"""

from collections import deque
from importlib import import_module

from common.config import HELP, Settings, load_settings


class FakeModel:
    def __init__(self, replies: list[str] | None = None):
        self.replies = deque(replies or ["Lumen fixture response: no model was contacted."])
        self.prompts: list[str] = []

    async def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if not self.replies:
            raise RuntimeError("Fake model replies exhausted; supply another test fixture.")
        return self.replies.popleft()


class ProviderModel:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def generate(self, prompt: str) -> str:
        s = self.settings
        try:
            sdk = import_module({"gemini": "google.genai"}.get(s.provider, s.provider))
        except ImportError:
            raise RuntimeError(f"Install model helpers with uv sync --extra host. {HELP}") from None
        try:
            if s.provider == "openai":
                async with sdk.AsyncOpenAI(
                    api_key=s.api_key.get_secret_value(), timeout=s.timeout, max_retries=0
                ) as client:
                    result = await client.responses.create(
                        model=s.model, input=prompt, max_output_tokens=s.max_tokens
                    )
                    return result.output_text
            if s.provider == "anthropic":
                async with sdk.AsyncAnthropic(
                    api_key=s.api_key.get_secret_value(), timeout=s.timeout, max_retries=0
                ) as client:
                    result = await client.messages.create(
                        model=s.model,
                        max_tokens=s.max_tokens,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    return "".join(block.text for block in result.content if block.type == "text")
            if s.provider == "gemini":
                async with sdk.Client(
                    api_key=s.api_key.get_secret_value(),
                    http_options={"timeout": int(s.timeout * 1000)},
                ).aio as client:
                    result = await client.models.generate_content(
                        model=s.model, contents=prompt, config={"max_output_tokens": s.max_tokens}
                    )
                    return result.text or ""
            async with sdk.AsyncClient(host=s.ollama_host, timeout=s.timeout) as client:
                result = await client.chat(
                    model=s.model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"num_predict": s.max_tokens},
                )
                return result.message.content or ""
        except Exception:
            # Provider exceptions can contain request bodies or credentials.
            raise RuntimeError(f"Model request failed for {s.provider}. {HELP}") from None


def create_model(settings: Settings | None = None) -> FakeModel | ProviderModel:
    settings = settings or load_settings()
    return FakeModel() if settings.provider == "fake" else ProviderModel(settings)


def create_tool_model(prompt: str, settings: Settings | None = None, turns=None):
    """Module 06's explicit tool loop uses the same configuration boundary."""
    from common.tool_formats import ToolCall, Turn
    from common.tool_models import ProviderToolModel, ScriptedModel

    settings = settings or load_settings()
    if settings.provider == "fake":
        return ScriptedModel(
            turns
            or [
                Turn(calls=[ToolCall("read-1", "notes__search_notes", {"query": "release"})]),
                Turn("Fixture completed: inspect the returned release note; no LLM was contacted."),
            ]
        )
    return ProviderToolModel(settings, prompt)
