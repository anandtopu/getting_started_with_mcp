# Lumen security checklist — Tiers 3–4

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

## Tier 4 server additions

| Family / module | Boundary | Enforcement and evidence |
|---|---|---|
| Mirror and task tools / 14–15 | Read-only synthetic database | Fixed tables, bounded pages/queries, no publishing; invalid-input tests |
| Gateway / 16 | Fixed trusted upstreams; verified HTTP subject and resource audience | Read/write scopes checked at execution; catalog cache partitions by subject/scopes/policy; rate and principal limits; logs omit arguments/results; failure/context-isolation tests |
| Tasks and App / 17 (also Gateway) | Local SQLite task owner; host-controlled App sandbox | Owner-bound random handles, TTL/quota, exact form response validation, cancellation; empty network/frame CSP and no HTML insertion; terminal and bridge tests |

The stdio gateway assumes one trusted OS user. HTTP has separate authentication.
Upstream clients use their own service identity; incoming auth context is cleared
and bearer tokens are not forwarded. Local in-memory upstreams share one synthetic
workspace, so this is not tenant-separated data storage. Apps metadata requests
host enforcement; desktop sandbox behavior requires the manual host check.

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

## Phase 7 shipping boundaries

- [x] Inspect wheel/sdist/npm/MCPB for private files and escaping paths; rebuild sdist without checkout sources.
- [x] Keep registry discovery read-only; match package identity/version; never auto-install a listing.
- [x] Bind local Compose ports to loopback, retain public issuer/audience through proxy, bound body/rate/memory/PIDs.
- [x] Revalidate full tool definition after human approval; never automatically retry writes with unknown outcomes.
- [x] Bind one-use answers to a session/question, validate Host/Origin/CSRF and cap sessions.
- [x] Isolate App with opaque-origin iframe/CSP and exact refresh allowlist; test parent DOM/network denial.
- [x] Keep model keys and upstream tokens server-side; use a trusted config file for destinations.
- [ ] Public multi-user deployment, shared durable state and real user login are outside this local teaching host; see [limitations](PHASE_7_VERIFICATION.md).

## Phase 8 additions

- [x] Knowledge index snapshots only bounded Markdown files under its root; queries use parameters and quoted FTS tokens.
- [x] The second audit fixture requires explicit lab mode; repaired paths deny private records and unapproved publication.
- [x] Ops verifies audience, issuer, signature, expiry and scope; authenticated principal owns each durable Task.
- [x] Form retry state and host approval are bound to the exact reviewed request; tickets expire and are consumed once.
- [x] Native Tasks persist owner/state and deny cross-owner access; declined input cancels pending work.
- [x] Skills bytes are checked against manifest digest/size; discovery does not activate instructions.
- [x] Server Card schema and endpoint policy reject untrusted targets; validation never connects to a card's URL.
- [x] Local machine/enterprise fixtures reject wrong resource, bad assertion and replay; published captures redact credentials.

Evidence: [Python regressions](../tests/test_phase8.py), [TypeScript regressions](../common/typescript/phase8.test.ts), [five project checklists](../capstones/README.md). Multi-worker recovery, live identity-provider federation and real production incident response remain deployment-specific work.

## Post-build review corrections

- Security catalog checks explicitly bypass SDK TTL caching immediately before dispatch. Ordinary discovery caching must never weaken a reviewed-definition check.
- The native browser ticket retains its original fingerprint through the execution-time approval callback; a second discovery cannot silently change what was approved.
- Replacement and deletion use `destructiveHint=true`, including bulletin updates. Additive creation/tagging remains separately annotated. All mutations still require explicit approval.
- Native model schemas exclude host-only confirmation; invalid or self-approved proposals fail before human review.
- Failed/cancelled connection startup cleans up before ownership transfers to the host.
- The vulnerable MCPB CLI/Zod 3 dependency has been removed. Both packaging paths use the pinned official MCPB 0.3 JSON Schema with Ajv and a bounded fflate ZIP packer. The helper rejects symlinks, escaping/private/dependency paths and missing entry points; it caps manifests at 64 KB, archive input at 64 MiB, entries at 512 and depth at 16. Build subprocesses retain the 256 MB heap and 120-second deadline. See [packaging evidence](PACKAGING_ADVISORY_VERIFICATION.md).
- Patched minimatch/glob overrides resolve the remaining moderate findings. Compatibility and cancellation regressions cover their consumers. Required CI reports all audit findings without exclusions and fails for any rated low or higher. See [dependency audit evidence and override maintenance](DEPENDENCY_AUDIT_VERIFICATION.md).

[Regressions and remaining limits](reviews/2026-10-30-review-summary.md).
