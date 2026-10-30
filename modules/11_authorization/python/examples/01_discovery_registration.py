"""Read live protected-resource metadata; compare reviewed client registrations.

Run: uv run python modules/11_authorization/python/examples/01_discovery_registration.py
Expected: PASS with the measured checks below.
"""

import asyncio

import httpx2 as httpx

from common.registration import registration_choice, validate_document
from scripts.auth_lab import auth_stack


async def main() -> None:
    url = "https://client.lumen.example/oauth/client.json"
    document = {
        "client_id": url,
        "redirect_uris": ["http://127.0.0.1:8765/callback"],
        "token_endpoint_auth_method": "none",
    }
    validate_document(url, document)
    assert registration_choice(None, True, url) == url
    assert registration_choice("lumen-chat", True, url) == "lumen-chat"
    async with auth_stack() as authority:
        async with httpx.AsyncClient(timeout=5) as http:
            prm = (
                await http.get(
                    authority.resource.replace("/mcp", "")
                    + "/.well-known/oauth-protected-resource/mcp"
                )
            ).json()
            metadata = (
                await http.get(authority.issuer + "/.well-known/oauth-authorization-server")
            ).json()
            assert prm["resource"] == authority.resource
            assert prm["authorization_servers"] == [metadata["issuer"]]
            assert "S256" in metadata["code_challenge_methods_supported"]
    print("PASS metadata discovery; reviewed CIMD document; pre-registration priority")


if __name__ == "__main__":
    asyncio.run(main())
