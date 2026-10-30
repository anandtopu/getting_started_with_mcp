# Lumen security checklist — Tier 3

Filled for the delivered course servers as of 2026-10-30. This is a fixture lab,
not a production certification. Each row names the actual boundary and remaining
limit. The [manifest](../scripts/examples.json) lists every runnable entry point;
multiple examples that use the same factory share the row below.

| Server family / modules | Identity and permitted access | Input / output and approval boundary | Evidence / remaining limit |
|---|---|---|---|
| Foundation / 00 | Launching OS user; synthetic dataset only | Fixed count tool; no writes | Repository smoke and real wire; no remote auth |
| Raw protocol / 01 | Local pipe only | Fixed directory count; malformed envelopes rejected | Raw protocol tests; teaching subset, not general server |
| Notes and rich tools / 02 | Local user; disposable notes | Typed input; host approval before writes; output contracts | Tier 1 validation and idempotency tests; confirmation boolean trusts host |
| Wiki / 03 | Configured synthetic root | Path and symlink confinement, bounded file types; resource text untrusted | Path/permission tests; filesystem TOCTOU not a kernel sandbox |
| Prompts / 04 | Local synthetic customer/wiki data | Fixed templates and validated arguments; embedded resources remain data | Prompt and completion tests; host controls model context |
| Paginated server / 05 | Local fixed resource set | Cursor validation and page budget | Empty/repeated cursor tests |
| Filesystem reference / 06 | Pinned package, `data/files` root only | Host approves every call; namespaced routes | Checkpoint/Inspector; package remains a third-party trust dependency |
| Issues / 07,09 | Disposable SQLite copy, local user | Pydantic bounds, transactions, receipts, confirmation; bulk close uses bound retry state | CRUD/rollback/replay tests; not a multi-tenant service |
| Analytics / 07 | Read-only fixture connection | Named SQL, parameters, row limit and query deadline | Limit/deadline tests; no arbitrary SQL |
| REST wrapper / 07 | Local mock by default; weather opt-in | Fixed API, response bound, timeout, no redirects | Failure tests; live weather not part of offline suite |
| Reports / 08 | Same local issue copy | Cancellation cleanup, bounded work, progress | Progress/cancellation tests; no durable job queue |
| File summarizer / 09 | Configured local root | Path/type/size bounds and explicit consent; fake model default | Root/consent tests; real provider requires separate credentials |
| Approval portal / 09 | One OS user; loopback only | Expiring one-use ticket, exact Host/Origin, browser proof | URL-mode denial/replay tests; not multi-user login |
| Remote workspace / 10, Python + TS | Loopback development endpoint, **no OAuth** | Host/Origin/CORS/header checks, body limits, bounded writes | Tier 2 parity and HTTP tests; never expose this entry point publicly |
| Secured issues / 11 | Verified issuer, RS256 signature, audience, expiry, scopes | Body-derived write scope gate; SDK bearer check; confirmed mutations | Tier 3 HTTP failures + Keycloak integration; single synthetic tenant, in-memory keys/receipts |
| Repaired lab / 12 | Server-bound synthetic principal | Own-employee permission, fixed backend, no outbound token forwarding, minimal audit | Injection/catalog/permission tests + isolated container; no production payroll data |
| Traced notes / 13 | Same boundary as module 02 | JSON stderr exporter excludes raw arguments/results | Snapshot, trace and stdout checks; collector configuration is operator-owned |
| Deliberately vulnerable fixture | Explicit isolated lab only | **Fails** object authorization by design | Regression reproduces leak, then verifies repair; excluded from ordinary host configs |

## Host checklist

- [x] Tools have server namespaces; duplicate/unsafe names fail discovery.
- [x] Host validates arguments and removes model-controlled confirmation fields.
- [x] Exact tool arguments reach the user approval callback before execution.
- [x] ReviewedHost rejects changed catalogs and excludes forbidden routes.
- [x] Poisoned wiki data cannot authorize file/mail/salary routes in the restricted host.
- [x] Network, turn, call, page and output budgets are bounded.
- [x] OAuth tokens stay in connection memory; captures redact Authorization fields.
- [x] HTTP operations test invalid credentials and body/header disagreement.
- [x] Audit/export code excludes request/response payloads and credentials.
- [ ] General prompt injection prevention is **not** claimed: a model can still misread data.
- [ ] Production tenant isolation, durable approvals, key rotation, revocation,
  TLS, rate limits, incident response and independently audited supply chain remain deployment work.

## Review procedure

Run `uv run pytest tests/test_tier1.py tests/test_tier2.py tests/test_tier3.py` and the
[Tier 3 checkpoint](../checkpoints/03_security/README.md). Review package/image pins,
tool definitions and least-privilege host configs. For new server entries, add a row
with identity source, data boundaries, approval policy and a regression proving denial.
Use the Keycloak and container checks for their respective runtime boundaries;
the offline fixture cannot establish interoperability or OS isolation by itself.
