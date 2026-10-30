"""Lumen Ops entry point. Loopback by default; container bind is explicit config."""

import os
from pathlib import Path
from urllib.parse import urlsplit

from common.auth_tokens import JWTVerifier
from common.deployment import public_url
from common.ops import make_app


def application():
    issuer = public_url(os.environ["LUMEN_ISSUER"])
    resource = public_url(os.environ["LUMEN_RESOURCE"])
    verifier = JWTVerifier(issuer, resource, os.environ["LUMEN_JWKS_URL"])
    return make_app(
        verifier,
        Path(os.environ.get("LUMEN_TASKS_DB", ".runtime/ops-tasks.db")),
        hosts=[urlsplit(resource).netloc],
        origins=os.environ.get("LUMEN_ORIGINS", "http://localhost:6274").split(","),
    )


def main():
    import uvicorn

    uvicorn.run(
        application(),
        host=os.environ.get("LUMEN_BIND", "127.0.0.1"),
        port=8000,
        access_log=False,
        proxy_headers=False,
    )


if __name__ == "__main__":
    main()
