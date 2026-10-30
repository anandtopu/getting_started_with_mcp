"""Provider conversation adapters. Native assistant turns preserve call IDs and signatures."""

import json
from collections import deque
from importlib import import_module

from common.config import HELP, Settings
from common.tool_formats import ToolCall, ToolReply, Turn, provider_tools


class ScriptedModel:
    def __init__(self, turns: list[Turn]):
        self.turns = deque(turns)
        self.results: list[list[ToolReply]] = []

    async def turn(self, tools: list[dict], results: list[ToolReply]) -> Turn:
        self.results.append(results)
        if not self.turns:
            raise RuntimeError("Fake conversation exhausted.")
        return self.turns.popleft()


class ProviderToolModel:
    def __init__(self, settings: Settings, prompt: str):
        self.settings = settings
        self.history = [{"role": "user", "content": prompt}]
        if settings.provider == "gemini":
            self.history = [{"role": "user", "parts": [{"text": prompt}]}]

    async def turn(self, tools: list[dict], results: list[ToolReply]) -> Turn:
        s = self.settings
        try:
            sdk = import_module({"gemini": "google.genai"}.get(s.provider, s.provider))
            definitions = provider_tools(s.provider, tools)
            if s.provider == "openai":
                self.history.extend(
                    {"type": "function_call_output", "call_id": r.call.id, "output": r.text}
                    for r in results
                )
                async with sdk.AsyncOpenAI(
                    api_key=s.api_key.get_secret_value(), timeout=s.timeout, max_retries=0
                ) as client:
                    result = await client.responses.create(
                        model=s.model,
                        input=self.history,
                        tools=definitions,
                        max_output_tokens=s.max_tokens,
                    )
                self.history.extend(result.output)  # Keep reasoning items, too.
                calls = [
                    ToolCall(b.call_id, b.name, json.loads(b.arguments))
                    for b in result.output
                    if b.type == "function_call"
                ]
                return Turn(result.output_text, calls)
            if s.provider == "anthropic":
                if results:
                    self.history.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": r.call.id,
                                    "content": r.text,
                                    "is_error": r.error,
                                }
                                for r in results
                            ],
                        }
                    )
                async with sdk.AsyncAnthropic(
                    api_key=s.api_key.get_secret_value(), timeout=s.timeout, max_retries=0
                ) as client:
                    result = await client.messages.create(
                        model=s.model,
                        messages=self.history,
                        tools=definitions,
                        max_tokens=s.max_tokens,
                    )
                self.history.append({"role": "assistant", "content": result.content})
                return Turn(
                    "".join(b.text for b in result.content if b.type == "text"),
                    [
                        ToolCall(b.id, b.name, b.input)
                        for b in result.content
                        if b.type == "tool_use"
                    ],
                )
            if s.provider == "gemini":
                if results:
                    self.history.append(
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "function_response": {
                                        "id": r.call.id,
                                        "name": r.call.name,
                                        "response": {"result": r.text, "is_error": r.error},
                                    }
                                }
                                for r in results
                            ],
                        }
                    )
                async with sdk.Client(
                    api_key=s.api_key.get_secret_value(),
                    http_options={"timeout": int(s.timeout * 1000)},
                ).aio as client:
                    result = await client.models.generate_content(
                        model=s.model,
                        contents=self.history,
                        config={
                            "tools": definitions,
                            "max_output_tokens": s.max_tokens,
                            "automatic_function_calling": {"disable": True},
                        },
                    )
                content = result.candidates[0].content
                self.history.append(content)  # Preserve every native part/thought signature.
                calls = [
                    ToolCall(
                        p.function_call.id, p.function_call.name, dict(p.function_call.args or {})
                    )
                    for p in content.parts
                    if p.function_call
                ]
                return Turn(
                    "".join(p.text for p in content.parts if p.text and not p.thought), calls
                )
            self.history.extend(
                {"role": "tool", "tool_name": r.call.name, "content": r.text} for r in results
            )
            async with sdk.AsyncClient(host=s.ollama_host, timeout=s.timeout) as client:
                result = await client.chat(
                    model=s.model,
                    messages=self.history,
                    tools=definitions,
                    options={"num_predict": s.max_tokens},
                )
            self.history.append(result.message.model_dump(exclude_none=True))
            return Turn(
                result.message.content or "",
                [
                    ToolCall(
                        f"ollama-{len(self.history)}-{i}",
                        c.function.name,
                        dict(c.function.arguments),
                    )
                    for i, c in enumerate(result.message.tool_calls or [])
                ],
            )
        except ImportError:
            raise RuntimeError(f"Run uv sync --extra host. {HELP}") from None
        except Exception:
            raise RuntimeError(f"Tool model request failed for {s.provider}. {HELP}") from None
