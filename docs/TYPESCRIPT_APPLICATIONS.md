# Native OAuth gateway and Chat Pro

The complete application backends run in Node 24 or 26. They reuse the checked-in synthetic data and the language-neutral browser assets; no Python application process is needed. This closes the implementation scope of review finding R-009. The [verification record](TYPESCRIPT_APPLICATIONS_VERIFICATION.md) distinguishes local checks from deployment CI.

## Chat Pro

From the repository root:

```text
npm ci
npm run chat:typescript
```

Open http://127.0.0.1:8768. Keep **Practice** selected for the repeatable no-key workflow. Try the four suggested prompts, approve or decline exact calls, answer the issue-close form, complete or cancel the quarterly-report Task, and refresh the analytics App. The full [backend](../common/typescript/chat_pro.ts) uses the same [browser tests](../tests/browser/chat.pw.ts) as the Python reference.

Choose a live provider only after configuring its key and model in the server environment or repository `.env`. Keys never enter browser storage or API responses. Set `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GEMINI_API_KEY` as appropriate, and enter the model name in the UI. Alternatively use `OPENAI_MODEL`, `ANTHROPIC_MODEL`, `GEMINI_MODEL`, or `OLLAMA_MODEL`; matching `LLM_PROVIDER`/`LLM_MODEL` are a fallback. Ollama uses `OLLAMA_HOST` (default http://127.0.0.1:11434). Provider requests preserve native history and call IDs, have a 60-second network deadline, and stop when the user cancels.

Each browser session owns notes, issues and gateway connections. The gateway combines notes, wiki, issues, analytics and workflow SDK servers. The full host additionally exposes the native durable report receiver and analytics App under its `gateway` alias. Tasks use SQLite at `.runtime/typescript/tasks.db`, with session ownership and expiry. Their separate official-transport peer handles the pinned SDK's missing custom Task-result hook. App HTML is read through MCP, served in an opaque sandbox, denied external connections and restricted to its exact read-only refresh tool.

The host validates model arguments before asking a human, then refreshes and fingerprints the complete catalog again before dispatch. Ordinary input and Task input each require a new one-use decision. A cancelled workflow cannot execute a late model proposal. Requests, models, tools, results, sessions, forms and Task polling have explicit bounds. Reconnect clears displayed Apps and refreshes capabilities; only locally allowlisted reads can retry after a connection failure. Writes are never retried automatically.

## Native OAuth deployment

The [Compose stack](../deployment/typescript/compose.yaml) starts Keycloak, the Node gateway and an nginx reverse proxy. The gateway owns **five separate native stdio child processes**, plus the analytics service's bounded local HTTP fixture. The child environment excludes provider keys and gateway tokens. No upstream receives the caller's bearer token. The public proxy binds only to loopback; the application container has no published port.

```text
docker compose -f deployment/typescript/compose.yaml up --build -d --wait --wait-timeout 180
npx playwright install chromium
npm run test:deployment:typescript
docker compose -f deployment/typescript/compose.yaml down --volumes --remove-orphans
```

Use this stack separately from the Python deployment, which occupies the same ports. The synthetic issuer is http://127.0.0.1:8080/realms/lumen and the protected resource is http://127.0.0.1:8001/mcp. The fixture realm's `learner` / `lumen-local-only` account and `lumen-chat` public client are for this local lab. The acceptance runner uses a real Chromium login, native SDK authorization-code/PKCE, audience verification and scope step-up. It then connects native Chat Pro to the authenticated deployment and completes a reviewed tool call.

The [resource server](../common/typescript/gateway_http.ts) pins issuer, resource and JWKS URL; accepts RS256 signatures with bounded key retrieval/cache/rotation; checks issuer, audience, expiry and not-before; and binds identity to each asynchronous request. `workspace:read` exposes read-only tools. `workspace:write` additionally exposes writes, which still require explicit confirmation. A direct write with insufficient scope returns an OAuth step-up challenge. Catalogs are private with zero TTL, policy is rechecked on dispatch, rate limits apply per subject, and audit records contain only subject, tool and outcome. Unknown JWT key IDs cannot cause an unbounded JWKS refresh storm.

The Node entrypoint accepts operator-owned `LUMEN_ISSUER`, `LUMEN_RESOURCE`, `LUMEN_JWKS_URL`, `PORT` and `LUMEN_BIND`. Container binding is explicitly `0.0.0.0`; normal local binding defaults to `127.0.0.1`. The internal JWKS URL is an operator-pinned back channel, never taken from a token. Configure HTTPS and your own identity service before adapting the lab to a real deployment.

## Reviewed remote configuration

```text
npm run chat:typescript -- --config deployment/typescript/chat.json
```

Obtain a resource-bound token with a trusted OAuth client and place it in `LUMEN_GATEWAY_TOKEN` in the host environment. The example config contains the environment variable's name, never the token. The host supports one to five unique aliases, fixed local profiles and explicitly configured HTTPS or exact-loopback `/mcp` URLs; a model cannot supply commands or URLs. `mode` can be `current`, `auto`, or explicitly `legacy`. Legacy peers use their initialization handshake rather than current `server/discover`.

The remote configuration exposes the deployed gateway's tools. The default local configuration also provides Task and App services; the deployed gateway does not advertise those local extensions. Browser sessions are local and single-user; the shared gateway's synthetic data is workspace-wide. This is a bounded teaching deployment, not a multi-tenant production service. Existing lessons for OAuth URL consent, packaging and other languages retain their separately documented test fixtures.

## Verification

```text
npm run check
npx playwright install chromium
npm run test:browser:typescript
npm run test:deployment:typescript
```

The final command requires the Compose stack. CI's `typescript-applications` job runs the native browser scenarios and actual Keycloak deployment without setting up Python. Existing Node 24/26 Windows/Linux jobs run the unit and integration contracts, including five native child processes. The separate Python browser suite remains available as `npm run test:browser`.
