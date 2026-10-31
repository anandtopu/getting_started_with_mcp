# Original-prompt review

Date: 2026-10-30. Reviewer: Codex. Baseline: `main` at `19736c9`.
Original user-supplied build prompt SHA-256: `e05f61c45b2023c6923e34fa5f757fe5671df9228ab113df1da13be4489aa39c`.

## Status

The scoped per-file pass and cross-file integration pass are complete. Security and teaching defects found in those passes have concrete fixes and regressions. The follow-up [native application implementation](../TYPESCRIPT_APPLICATIONS_VERIFICATION.md) addresses R-009 with complete Node backends and passing local browser/security tests; its deployment CI is pending. R-010 remains a mitigated upstream build-tool advisory. Live publication, cloud/vendor accounts and first-time human setup timing remain the previously documented external checks.

| Area | Status | Evidence |
|---|---|---|
| Per-file pass | Complete for listed review scope | [Individual files](2026-10-30-per-file-analysis.md); this is not a line-by-line audit of every generated fixture or dependency |
| Integration pass | Complete for listed flows | [Contracts and flows](2026-10-30-integration-checks.md) |
| Fix validation | Local checks and all 28 required CI jobs passed | Implementation commit `723eb3b`; completed results below |
| Native application follow-up | Implemented; deployment CI pending | [Native application evidence](../TYPESCRIPT_APPLICATIONS_VERIFICATION.md) supersedes the earlier R-009 implementation gap |

## Findings

| ID | Severity | Status | Owner area | Finding | Evidence | Action | Validation |
|---|---|---|---|---|---|---|---|
| R-001 | P1 | Fixed | Catalog authorization | SDK TTL caching allowed a stale tool definition to survive a security recheck. | common/defenses.py; common/gateway.py; common/typescript/advanced_host.ts; common/typescript/production_host.ts | Force a network refresh at review/dispatch; keep only the explicit outer discovery cache. | Real SDK TTL=60000 regressions change semantics after review and assert zero calls. |
| R-002 | P1 | Fixed | Browser approvals | The TS web shell could compare the saved definition, then silently approve a newer definition inside CourseHost. | common/typescript/web_host.ts | Bind the execution-time approval callback to the original one-use ticket fingerprint. | Adversarial browser/API regression changes the catalog between both checks; zero calls. |
| R-003 | P1 | Fixed | Connection lifetime | Python startup cancellation/timeout could leave the worker alive; TS multi-child startup and close-during-start needed explicit ownership cleanup. | common/production_host.py; common/typescript/production_host.ts; common/typescript/web_host.ts | Close failed workers before ownership transfer; settle all child starts; await in-flight starts on close. | Timeout, cancellation, failed web startup and real close-during-connect regressions. |
| R-004 | P1 | Fixed | Mutation annotations | Replace/delete operations advertised destructiveHint=false, understating their effects to hosts. | common/notes.py; common/issues.py; common/wiki.py; common/elicitation.py; common/http_server.py; common/audit_lab.py; native counterparts | Use a distinct replacement annotation; retain additive annotations for create/tag operations. | Catalog assertions in both languages and regenerated actual wire captures. |
| R-005 | P2 | Fixed | Native lessons | Several TS companion examples asserted metadata or toy results instead of the advertised data/auth/quality/design behavior. | common/typescript/advanced_lessons.ts; raw_client.ts; real_data.ts; utilities.ts; oauth.ts; quality.ts; tool_design.ts; registry.ts; url_input.ts | Add SDK-free wire code, real CRUD/SQL/REST, running cancellation, URL consent, native PKCE, OTel/load/eval, 25-versus-six catalogs and actual Registry schema validation. | Native lesson contracts, HTTP negatives, raw stdio, PKCE issuer/scope denial and new Inspector entries. |
| R-006 | P1 | Fixed | Model boundary | The TS host lacked runtime argument validation; its provider lesson converted definitions without implementing the actual native provider loop. | common/typescript/advanced_host.ts; schemas.ts; llm.ts; chat.ts | Validate bounded portable schemas; hide/reject model confirmation; preserve provider call IDs and native history; require separate approval. | Four provider HTTP fixtures perform actual MCP calls; malformed arguments never reach approval; stdio terminal host completes offline. |
| R-007 | P2 | Fixed | Teaching contract | Module headers omitted outcomes/version metadata, timings diverged from the learning path, early takeaways were orphan quiz answers, and host steps requested nonexistent prompts. | modules/00_setup/README.md through modules/21_production_hosts/README.md; scripts/host_configs.py; LEARNING_PATH.md | Restore explicit outcomes/versions, align timings, rewrite five takeaways, use actual host capabilities and the module 07 server. | Release teaching-contract gate, local links and source/config comparison. |
| R-008 | P2 | Fixed | Coverage gates | The release checker accepted headings without key metadata and did not ensure each numbered example was runnable from the inventory. | scripts/check_course.py; tests/test_repository.py; scripts/examples.json; docs/FEATURE_MAP.md | Check metadata, objective/takeaway counts, duplicate inventory and every numbered example; expand legacy scans to capstones/distribution/TS; link remaining map labels. | Release validation and repository source scans. |
| R-009 | P2 | Implemented; CI pending | B1 application parity | Native OAuth gateway deployment and full Chat Pro backend now replace the Python application dependency. | [Implementation and evidence](../TYPESCRIPT_APPLICATIONS_VERIFICATION.md) | Five native stdio services, OAuth resource boundary and complete browser backend; new required deployment job. | Local browser, provider, security, legacy and native process tests pass; actual Keycloak deployment CI pending. |
| R-010 | P2 | Mitigated; upstream open | Packaging dependency | npm audit reports Zod 3.25.76 under MCPB 2.1.2; no compatible upstream fix is currently offered. | package-lock.json; common/packaging.py; scripts/knowledge_package.py | Retain the documented bounded build-only use on repository-owned manifests; replace or upgrade MCPB after compatible validation. Do not force a Zod 3-to-4 override. | Audit records two affected dependency nodes for one advisory; installed package and bundle validation still pass. |
| R-011 | P2 | Fixed | Test reliability | Thirty simultaneous Vitest workers caused a transform/import timeout in an otherwise passing exercise contract under concurrent local work. | package.json | Limit workers to four; keep the actual test assertions and deadlines. | Complete native suite passes with the bounded worker count. |

## Requirement traceability

| Original requirement | Delivered evidence | Review result |
|---|---|---|
| Sections 2–4: explanations, actual JSON, runnable examples, use cases and exercises | 22 module READMEs; wire manifests; `scripts/examples.json`; `scripts/check_course.py` | Outcomes/metadata/takeaways and executable inventory strengthened; captures regenerated |
| Current spec and confirmed SDK APIs | `docs/VERIFICATION_NOTES.md`, lockfiles, installed SDK signatures | 2026-07-28 remains current; Python 2.3.0 and split TS SDK 2.4.0 retained |
| Protocol-only stdout; no v1 imports | `tests/test_repository.py`, raw server, wiretap, Inspector | Broadened source audit and real child-process exchange checks |
| Provider independence and host loop | `common/llm.py`, `common/tool_models.py`, native `llm.ts`/`chat.ts` | Four native adapters now execute the full tool round trip against fixtures; live quality not inferred |
| Secure defaults | approval, filesystem, SQL, JWT, HTTP and gateway implementations | Fresh catalog checks, approval binding, mutation labels and cleanup repaired |
| Fictional Lumen data and reproducibility | generator/data integrity tests, SQLite fixtures, eval rows | Existing deterministic contracts retained; no real data or credentials introduced |
| Modules 00–21 and five checkpoints | module trees, checkpoint acceptance scripts, feature map | Main track present; original five [TS] tracks present; B1 distinction made explicit |
| Module 14 measured improvement | deterministic and opt-in live evaluation helpers | Measured catalog/retrieval results do not establish LLM task-success improvement without a live run |
| Optional B1 full TS versions | native cases for all 22 modules and native advanced application backends | R-009 follow-up has local acceptance and a new required deployment CI job |
| B2–B4 | native SDK contracts, spec workflow, Skills/auth/Card extensions | Prior native build evidence retained; bonus/capstone exchanges regenerated |
| Five capstones | stories, diagrams, conservative starters, runtimes, tests/eval/rubrics | Real helper composition retained; starter failures are intentional exercises |
| Reference docs and six PDF sheets | protocol guide, glossary/design/host/security/migration/troubleshooting docs; cheatsheets | File/link/page-count gates; 24 current captured methods/notifications regenerated |
| Distribution and operation | wheel/npm/MCPB builds, isolated launches, Docker/Compose and CI | Local package validation repeated; public TestPyPI/Registry/cloud publication remains unperformed |
| Beginner setup under ten minutes | setup checks and four host configs | Not human-timed; existing explicit limitation retained |

## Validation evidence

Completed local checks are listed below. Historical Phase 8 results are not used as evidence for revised code; CI is recorded separately.

| Check | Result |
|---|---|
| Python full suite, including all example entry points | 249 passed, one Windows symlink-permission skip; 233 entry points (49 servers + 184 scripts) exercised |
| TypeScript compiler/lint/tests | Passed; 124 tests across 30 files |
| Tier 1–5 and Phase 8 captures | Passed; actual exchanges regenerated |
| Local release contract and protocol guide | Passed; 24 methods/notifications |
| Installed wheel/npm and MCPB build | Passed; notes uvx/npx plus two knowledge wheel/bundle launches outside checkout |
| Browser acceptance | Three Chromium scenarios passed |
| Inspector inventory | Five new local CLI checks passed; CI verified all 78 advertised catalogs across 49 servers |
| npm audit | Two high-severity dependency nodes, one advisory; R-010 |
| CI for revised implementation | [All 28 required jobs passed](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41135048577) on `723eb3bc6a9c92c84087a1d0be234ef26748e7e3`; manual external-link job skipped |
| Documentation links | Local and external sweeps: zero failures |

## Limits and follow-up

R-009's implementation follow-up is documented separately so the original results below remain attributable to their tested commit. Native OAuth gateway and Chat Pro application processes no longer require Python. R-010 is build-only in this repository: the affected CLI consumes trusted checked-in manifests in a bounded Node process with a subprocess deadline. It is not used by the running MCP servers. This reduces exposure but does not make the advisory disappear.

Manual tests of third-party desktop UIs, real model performance/cost, live vendor SSO, public publication and cloud operation are not claimed. The new CI run verified the complete Python 3.12–3.14 Windows/Linux matrix and macOS 3.12, Node 24/26 on Windows/Linux, native Go/C#/Rust/Java builds on Windows/Linux, framework adapters, Inspector, isolated packages, browser acceptance, container isolation and OAuth/Compose deployments. Completed Linux, macOS and Windows logs report 250 Python tests and all 233 standalone examples passing. The implementation required no CI repair or rerun. This documentation-only record does not change the tested code.

## Primary references checked

[Current spec](https://modelcontextprotocol.io/specification), [2026-07-28 changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog), [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling), [Anthropic tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools), [Gemini functions](https://ai.google.dev/gemini-api/docs/function-calling), [Ollama tools](https://docs.ollama.com/capabilities/tool-calling), [OTel trace SDK](https://github.com/open-telemetry/opentelemetry-js/tree/main/packages/sdk-trace), [Zod advisory](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5). No source text was substituted for runtime verification.
