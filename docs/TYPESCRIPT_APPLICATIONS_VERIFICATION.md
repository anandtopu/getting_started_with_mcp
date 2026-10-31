# Native application parity verification

Date: 2026-10-30. Follow-up to [R-009](reviews/2026-10-30-action-register.md).

## Implemented boundaries

| Boundary | Implementation | Executed acceptance |
|---|---|---|
| OAuth → native gateway | Pinned JWKS/issuer/audience, expiry, per-request identity, private catalogs, scope step-up, throttling and redacted audit | Native HTTP integration with actual SDK clients, signatures and concurrent reader/writer calls |
| Gateway → upstreams | Five native stdio processes, fixed profiles, stripped environment, SDK transport and bounded internal REST | Catalogs for all five, real issue read, approved note write and internal project lookup |
| Browser → host | Loopback Host/Origin, CSRF, bounded sessions, private server settings | Forged Host/Origin, cross-session CSRF/decisions/App URLs and replay rejection |
| Model → execution | Portable schema validation, human review, fresh catalog fingerprint, bounded history/results | Provider HTTP exchange, model confirmation rejected, changed-definition rejection and late-response cancellation |
| Human → ordinary input | Separate scalar form decision and validation | Chromium bulk-close scenario; invalid and declined answers |
| Host → Tasks | Native SQLite receiver, owner-bound official-transport peer, polling, input and cancel | Chromium completion and cancellation; durable receiver regressions |
| Host → App | MCP resource read, official browser bridge, opaque sandbox, exact refresh allowlist | Chromium refresh, parent-document denial, network denial; backend tool-call rejection |
| Connection → lifecycle | Partial-start cleanup, disconnect, read-only retry, refresh/reconnect, explicit legacy handshake | Native session, reconnect and legacy tests; existing ownership regressions |

## Local results

- All three shared Chromium scenarios pass against the native backend.
- Eight new native application/security integration tests pass, including the gateway with five child processes.
- The complete TypeScript compiler, ESLint and Vitest run passes: 132 tests in 32 files, including the legacy regression.
- Python regression suite: 249 passed, one skipped because the local Windows account cannot create symlinks (250 collected). This includes all manifest-driven standalone examples.
- Ruff lint/format, release inventory/teaching/local-link checks, and native Compose configuration validation pass.
- Docker Desktop's Linux engine is unavailable locally. Actual Keycloak/container acceptance is delegated to the new required `typescript-applications` CI job, not inferred from fixture tests.

## CI status

Implementation commit `1adcc06` and corrections through `2eb17e98c81cf9ca2479b840e03284de2822c203` are published. **[All 29 required CI jobs passed](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41155958759)** on that exact implementation. The optional manual external-link job was skipped. The [native application job](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41155958759/job/124402681257) passed all three browser scenarios and the real Keycloak/container acceptance without setting up Python.

The matrix covers Node 24/26 on Windows/Linux, Python 3.12–3.14 on Windows/Linux plus macOS 3.12, all four native SDK tracks, frameworks, Inspector, packaging, browser isolation and both deployment stacks. The completed Linux Python 3.13 log confirms 250 Python tests and all 233 delivered examples. R-009 is closed; the final documentation commit records these results without changing the tested application code.

The first deployment run exposed a browser callback-capture problem; acceptance now uses a real loopback HTTP listener. The next run completed PKCE and token verification, then exposed the SDK selecting every advertised scope when the initial challenge omitted its minimum scope. The resource now explicitly challenges for `workspace:read`; writes retain a separate step-up challenge. The provider also retains issuer-bound discovery state across callbacks. The following run completed OAuth and the deployed Chat Pro call, but its final text selector matched two elements; an exact selector was verified locally in Chromium. Local regressions cover the minimal challenge. These repairs are recorded rather than describing the initial CI attempts as successful.

No paid model service, vendor account, public package or production cloud deployment is required by this acceptance. At this commit, MCPB/Zod advisory R-010 remained mitigated; the later [packaging follow-up](PACKAGING_ADVISORY_VERIFICATION.md) removes the affected dependency.
