"""Registration policy for reviewed metadata; retrieval requires a separate SSRF boundary."""

from urllib.parse import urlsplit


def validate_document(client_id: str, document: dict) -> dict:
    url = urlsplit(client_id)
    if (
        url.scheme != "https"
        or not url.hostname
        or url.path in {"", "/"}
        or url.username
        or url.password
        or url.fragment
        or url.query
    ):
        raise ValueError("Client ID must be an HTTPS metadata-document URL")
    if document.get("client_id") != client_id:
        raise ValueError("Document client_id does not match its URL")
    if document.get("token_endpoint_auth_method") != "none":
        raise ValueError("This lesson registers public clients only")
    redirects = document.get("redirect_uris", [])
    if not redirects or any(uri != "http://127.0.0.1:8765/callback" for uri in redirects):
        raise ValueError("Review exact redirect URIs; wildcards are not accepted")
    return document


def registration_choice(preregistered: str | None, supports_cimd: bool, document_url: str) -> str:
    """An existing registration is used first; CIMD enables new relationships."""
    if preregistered:
        return preregistered
    if supports_cimd:
        validate_document(
            document_url,
            {
                "client_id": document_url,
                "token_endpoint_auth_method": "none",
                "redirect_uris": ["http://127.0.0.1:8765/callback"],
            },
        )
        return document_url
    raise ValueError("Pre-register this client; no current automatic registration is available")
