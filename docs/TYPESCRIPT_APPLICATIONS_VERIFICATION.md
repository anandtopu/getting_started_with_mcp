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
- Docker Desktop's Linux engine is unavailable locally. Actual Keycloak/container acceptance is delegated to the new required `typescript-applications` CI job, not inferred from fixture tests.

## CI status

Pending publication and execution for this implementation. The existing historical 28-job result belongs to commit `723eb3b`; it is not evidence for these changes. The new workflow adds one required native application job.

No paid model service, vendor account, public package or production cloud deployment is required by this acceptance. The MCPB/Zod advisory R-010 remains a separate mitigated build-tool issue.
