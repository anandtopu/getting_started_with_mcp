"""Registry metadata is an index entry, not a trust decision or installed artifact."""

import json
import re
from urllib.parse import quote

import httpx2 as httpx
from jsonschema import Draft7Validator, FormatChecker

from common.config import ROOT

BASE = ROOT / "distribution/registry"
REGISTRY = "https://registry.modelcontextprotocol.io"


def validate_metadata(document=None):
    document = document or json.loads((BASE / "server.json").read_text())
    schema = json.loads((BASE / "server.schema.json").read_text())
    Draft7Validator(schema, format_checker=FormatChecker()).validate(document)
    if document.get("$schema") != schema["$id"]:
        raise ValueError("Use the pinned registry schema URI.")
    package = json.loads((ROOT / "distribution/npm/package.json").read_text())
    if (
        document["name"] != package["mcpName"]
        or document["packages"][0]["identifier"] != package["name"]
        or document["version"] != package["version"]
    ):
        raise ValueError("Registry identity/version must match the package being published.")
    return document


def namespace_owner(name):
    match = re.fullmatch(r"io\.github\.([A-Za-z0-9-]{1,39})/([a-z0-9-]{1,100})", name)
    if not match:
        raise ValueError("This example uses io.github.<owner>/<server>.")
    return match[1]


def review_candidate(record):
    """Deterministic triage flags; a clean result still needs source/permission review."""
    flags = []
    if record.get("version") in {None, "latest", "*"}:
        flags.append("Pin an immutable version.")
    if not record.get("repository", {}).get("url", "").startswith("https://github.com/"):
        flags.append("Review the publisher and source repository.")
    if record.get("permissions"):
        flags.append("Review each filesystem/network permission before installation.")
    if record.get("installScript"):
        flags.append("Review install scripts before executing them.")
    return {"flags": flags, "automatic_install_allowed": False}


async def list_registry(transport=None, *, live=False):
    if transport is None and not live:
        raise ValueError("Use a fixture transport, or explicitly opt in to the public registry.")
    records, cursor, seen = [], None, set()
    async with httpx.AsyncClient(transport=transport, timeout=10, follow_redirects=False) as client:
        for _ in range(3):
            async with client.stream(
                "GET",
                REGISTRY + "/v0.1/servers",
                params={"limit": 5, **({"cursor": cursor} if cursor else {})},
            ) as response:
                response.raise_for_status()
                body = b""
                async for chunk in response.aiter_bytes():
                    body += chunk
                    if len(body) > 256_000:
                        raise ValueError("Registry page exceeds the response budget.")
                page = json.loads(body)
            records.extend(page.get("servers", []))
            cursor = page.get("metadata", {}).get("nextCursor")
            if not cursor:
                return records
            if cursor in seen or len(cursor) > 2000:
                raise ValueError("Invalid or repeated registry cursor.")
            seen.add(cursor)
    raise ValueError("Registry traversal exceeded three pages.")


def fixture_transport():
    def respond(request):
        assert request.url.host == "registry.modelcontextprotocol.io"
        cursor = request.url.params.get("cursor")
        return httpx.Response(
            200,
            json={
                "servers": [{"server": validate_metadata()}] if not cursor else [],
                "metadata": {"nextCursor": "page-2"} if not cursor else {},
            },
        )

    return httpx.MockTransport(respond)


def version_url(name, version):
    return f"{REGISTRY}/v0.1/servers/{quote(name, safe='')}/versions/{quote(version, safe='')}"
