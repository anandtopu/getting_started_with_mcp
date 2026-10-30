"""Inspectable remote-MCP request bodies; external execution requires explicit opt-in."""

import ipaddress
import os
from urllib.parse import urlsplit

from common.frameworks import ALLOWED, PROMPT


def remote_url(url: str, live=False) -> str:
    parts = urlsplit(url)
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username
        or parts.password
        or parts.fragment
        or parts.query
    ):
        raise ValueError(
            "Use a reviewed HTTPS MCP endpoint without credentials, query or fragment."
        )
    if parts.hostname == "localhost" or parts.hostname.endswith(".localhost"):
        raise ValueError("A provider cannot reach your localhost MCP server.")
    try:
        address = ipaddress.ip_address(parts.hostname)
    except ValueError:
        address = None
    if address and not address.is_global:
        raise ValueError("Remote MCP requires a provider-reachable public endpoint.")
    if live and parts.hostname.endswith(".example"):
        raise ValueError("Replace the illustrative .example address before --live.")
    return url


def request_body(provider: str, model: str, url: str, token: str = "") -> dict:
    url = remote_url(url)
    names = sorted(ALLOWED)
    if provider == "openai":
        tool = {
            "type": "mcp",
            "server_label": "lumen",
            "server_url": url,
            "allowed_tools": names,
            "require_approval": "always",
        }
        if token:
            tool["authorization"] = token
        return {"model": model, "input": PROMPT, "tools": [tool], "max_output_tokens": 512}
    if provider == "anthropic":
        server = {"type": "url", "name": "lumen", "url": url}
        if token:
            server["authorization_token"] = token
        return {
            "model": model,
            "max_tokens": 512,
            "messages": [{"role": "user", "content": PROMPT}],
            "mcp_servers": [server],
            "tools": [
                {
                    "type": "mcp_toolset",
                    "mcp_server_name": "lumen",
                    "default_config": {"enabled": False},
                    "configs": {name: {"enabled": True} for name in names},
                }
            ],
        }
    if provider == "gemini":
        tool = {
            "type": "mcp_server",
            "name": "lumen",
            "url": url,
            "allowed_tools": [{"tools": names}],
        }
        if token:
            tool["headers"] = {"Authorization": "Bearer " + token}
        return {
            "model": model,
            "input": PROMPT,
            "tools": [tool],
            "generation_config": {"max_output_tokens": 512},
        }
    raise ValueError("Remote-MCP request examples support openai, anthropic or gemini.")


async def execute_remote(settings, url: str) -> dict:
    """Use the same Settings/provider selection as common.llm; never log credentials."""
    import httpx2 as httpx

    remote_url(url, live=True)
    provider = settings.provider
    body = request_body(provider, settings.model, url, os.environ.get("LUMEN_MCP_TOKEN", ""))
    key = settings.api_key.get_secret_value()
    endpoints = {
        "openai": "https://api.openai.com/v1/responses",
        "anthropic": "https://api.anthropic.com/v1/messages",
        "gemini": "https://generativelanguage.googleapis.com/v1beta/interactions",
    }
    headers = {
        "openai": {"Authorization": "Bearer " + key},
        "anthropic": {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "anthropic-beta": "mcp-client-2026-09-15",
        },
        "gemini": {"x-goog-api-key": key},
    }[provider]
    try:
        async with httpx.AsyncClient(timeout=settings.timeout, follow_redirects=False) as client:
            response = await client.post(endpoints[provider], headers=headers, json=body)
            response.raise_for_status()
            data = response.json()
    except Exception:
        raise RuntimeError(
            "Remote model request failed. Check endpoint reachability, model access "
            "and credentials; no automatic retry was made."
        ) from None
    return {
        "id": data.get("id"),
        "types": [
            item.get("type")
            for item in data.get("output", data.get("content", data.get("steps", [])))
        ],
        "approval_note": "Approval requests are not automatically accepted.",
    }
