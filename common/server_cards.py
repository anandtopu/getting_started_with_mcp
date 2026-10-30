"""Experimental Server Card schema validation plus local connection policy.

The upstream prototype still labels itself experimental. A valid card is a hint,
not permission to connect, fetch icons, install software or trust an OAuth issuer.
"""

import json
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker

from common.config import ROOT

BASE = ROOT / "modules/bonus/B4_whats_new/data"


def validate_card(card: dict, trusted_host: str):
    schema = json.loads((BASE / "server-card.schema.json").read_text())
    Draft202012Validator(
        {**schema, "$ref": "#/$defs/ServerCard"}, format_checker=FormatChecker()
    ).validate(card)
    remotes = card.get("remotes", [])
    if not remotes:
        raise ValueError("Select a card with an explicit remote endpoint.")
    for remote in remotes:
        url = urlsplit(remote["url"])
        if url.scheme != "https" or url.hostname != trusted_host or url.username or url.password:
            raise ValueError("Endpoint requires HTTPS and an explicitly trusted host.")
        if remote.get("headers"):
            raise ValueError(
                "Review header requests separately; never copy credentials from a card."
            )
    return {"name": card["name"], "candidate_count": len(remotes), "connected": False}
