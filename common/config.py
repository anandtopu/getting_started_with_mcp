"""Read explicit configuration without printing credentials."""

import os
from pathlib import Path
from typing import Literal

from dotenv import dotenv_values
from pydantic import BaseModel, Field, SecretStr

ROOT = Path(__file__).resolve().parents[1]
HELP = "Run uv run python scripts/check_env.py for setup help."


class Settings(BaseModel):
    provider: Literal["fake", "anthropic", "openai", "gemini", "ollama"] = "fake"
    model: str = "fixture"
    api_key: SecretStr = Field(default_factory=lambda: SecretStr(""))
    ollama_host: str = "http://127.0.0.1:11434"
    timeout: float = Field(default=30, gt=0, le=300)
    max_tokens: int = Field(default=512, ge=1, le=8192)


def load_settings(env_file: Path | None = None) -> Settings:
    """Environment overrides the repository .env; never mutate os.environ."""
    values = {**dotenv_values(env_file or ROOT / ".env"), **os.environ}
    provider = values.get("LLM_PROVIDER", "fake")
    key_name = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
    }.get(provider, "")
    settings = Settings(
        provider=provider,
        model=values.get("LLM_MODEL", "fixture"),
        api_key=values.get(key_name) or "",
        ollama_host=values.get("OLLAMA_HOST", "http://127.0.0.1:11434"),
        timeout=values.get("LLM_TIMEOUT_SECONDS", 30),
        max_tokens=values.get("LLM_MAX_TOKENS", 512),
    )
    if settings.provider != "fake" and settings.model == "fixture":
        raise ValueError(f"Set LLM_MODEL for the selected provider. {HELP}")
    if key_name and not settings.api_key.get_secret_value():
        raise ValueError(f"Set {key_name} in your environment or .env. {HELP}")
    return settings
