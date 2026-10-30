# Local Keycloak for Lumen issues

This development realm is synthetic and loopback-only. Keycloak **26.8.1** is pinned;
pre-registration avoids requiring a public HTTPS metadata document for a local client.
The experimental `resource-indicators` feature binds tokens to the exact resource URL.
The imported `lumen-issues` client declares `resource_url`; `lumen-chat` has the audience
mapper and optional read/write scopes. Never reuse these fixture accounts in deployment.

The default `basic` client scope explicitly maps the subject (`sub`) claim. Keycloak
moved this claim into a mapper; omitting it produces tokens our verifier correctly
rejects. Full-scope role access is disabled. The verifier still requires the subject,
signature, issuer, audience and expiry rather than accepting an incomplete token.

From the repository root:

```text
docker compose -f deployment/auth/compose.yaml up -d
uv run python scripts/keycloak_check.py
uv run python modules/11_authorization/python/use_case/server.py
```

The check waits up to 120 seconds for discovery, performs a synthetic browser login
through the SDK, reads an issue, obtains write scope after a 403, and creates one
in-memory issue. It then rejects the token against another audience. It starts its
own resource server on port 8001, so run it **before** the persistent server command.

In a second terminal:

```text
uv run python modules/11_authorization/python/examples/03_local_auth.py --keycloak
```

Sign in as `learner` with the development password `lumen-local-only`. After login,
the browser reaches `http://127.0.0.1:8765/callback` and shows an unavailable page.
Copy its complete address into the waiting terminal. The SDK validates state and
issuer and redeems the one-use code. Do not paste that address into chats or logs.
The browser step is interactive; CI uses only this fixed synthetic account and an
isolated cookie jar. The account is a development convenience, not a password grant.

The HTTP test browser has a cookie policy restricted to `http://127.0.0.1:8080`.
Keycloak treats loopback as a trusted browser context and sets Secure cookies;
Python's default jar would omit them on HTTP and cause `cookie_not_found`.
This test-only exception models the local browser flow, never a remote identity
provider. The SDK's token transport and signature/issuer/audience checks are unchanged.

For Inspector UI or another host, register its **exact** callback URL and use the
pre-registered client ID in its OAuth settings. Host-specific browser flows are
manual checks; the Inspector CI uses a short-lived fixture bearer to check the
authenticated MCP endpoint. Never copy a persistent token into committed JSON.

Admin UI: `http://127.0.0.1:8080`, account `local-admin` / `local-admin-only`.
Stop the local service with `docker compose -f deployment/auth/compose.yaml down`.
Realm state is disposable. Import only affects a new realm; after editing the
realm file, recreate the disposable container before rerunning the compatibility check.

The offline suite uses a separate [synthetic authority](../../common/auth_fixture.py)
with ephemeral RSA keys, one-use expiring codes, PKCE and explicit synthetic consent.
It has no real identity proof and is not a substitute for Keycloak. This keeps CI
failure tests reproducible without weakening the actual provider path.

Keycloak's [MCP guide](https://www.keycloak.org/securing-apps/mcp-authz-server)
documents resource indicators and CIMD as experimental. The lesson uses current
pre-registration; enabling CIMD additionally requires reviewed client policy and
an HTTPS metadata document. No dynamic registration fallback is enabled here.
