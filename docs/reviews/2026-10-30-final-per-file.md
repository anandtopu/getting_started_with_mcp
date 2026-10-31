# Final review — pass 1: per-file analysis

Historical baseline evidence. See the [follow-up fixes and validation](../FINAL_REVIEW_FIXES_VERIFICATION.md)
for the current status of F-001 through F-004.

Baseline: `4a03e3b`. Findings and acceptance actions are in the
[final review/action plan](2026-10-30-final-review.md).

## Scope

This pass reviewed the original request, course-wide structural contracts,
selected lesson/runtime boundaries, and the recent application/dependency/package
follow-ups. It is not a line-by-line rereview of every module, native SDK example,
generated capture, vendored schema or third-party library. Generated contents
were checked through the release inventory, existing tests and provenance.
Individual entries below specify the inspected responsibility, not an assertion
that the entire file is defect-free.

## Findings and file evidence

| File | Inspected responsibility | Result |
|---|---|---|
| [README.md](../../README.md) | Public course identity, quick start and follow-up status | Public repository confirmed; human timing remains E-001. |
| [LEARNING_PATH.md](../../LEARNING_PATH.md) | Five tiers, checkpoints, three-/six-week schedules | Present; existing release evidence retained. |
| [pyproject.toml](../../pyproject.toml) | Supported Python versions, dependency groups, test markers and warning policy | Python 3.12–3.14; default fixtures; MCP deprecations treated as errors. |
| [package.json](../../package.json) and lockfile | Runtime versions, native checks, security overrides | Reviewed pins remain; current audit is clean. |
| [.github/workflows/ci.yml](../../.github/workflows/ci.yml) | Matrix and actual application/package/deployment gates | Latest 29 required jobs passed. External link gate is manual; freshly executed locally. |
| [scripts/check_course.py](../../scripts/check_course.py) | Teaching metadata, counts, capstones, PDFs and coverage | Passes. Structural checks do not detect semantic lesson gaps F-002/F-003 or stale table wording F-004. |
| [tests/test_repository.py](../../tests/test_repository.py) | Source bans, protocol output, inventory, release and capture checks | Targeted tests passed; full inventory supported by recent full CI. |
| [tests/test_foundation.py](../../tests/test_foundation.py) | Foundation/data/config/security contracts | Targeted tests passed; one local Windows symlink skip. |
| [scripts/check_links.py](../../scripts/check_links.py) | Markdown file and external URL checking | Local/external checks passed. Checker results are not a universal guarantee about every URL embedded in arbitrary code or every anchor. |
| [scripts/protocol_guide.py](../../scripts/protocol_guide.py) | Explicit core/extension coverage and capture-derived guide | Existing 24-method/notification coverage gate passes; changelog rechecked. |
| [docs/HOST_SETUP.md](../HOST_SETUP.md) | Four host formats and support evidence boundaries | Config/documentation verification is explicit; actual GUI/timing acceptance remains E-001. |
| [common/typescript/gateway_http.ts](../../common/typescript/gateway_http.ts) | Pinned issuer/audience/JWKS, scoped identity, stripped bearer boundary | Existing native deployment/security acceptance retained; no new issue identified in inspected boundaries. |
| [common/typescript/chat_pro.ts](../../common/typescript/chat_pro.ts) | Human decisions, fresh definitions, cancellation, bounded state | Existing browser/security acceptance retained; no new issue identified in inspected boundaries. |
| [deployment/typescript/compose.yaml](../../deployment/typescript/compose.yaml) | Bindings, readiness, unprivileged service configuration | Actual CI deployment passes; no public production-host claim inferred. |
| [common/tool_evaluation.py](../../common/tool_evaluation.py), lines 29–56 | Fixture/live evaluation dispatch and budgets | Live route exists in Python; committed live-result evidence remains E-003. |
| [common/typescript/tool_design.ts](../../common/typescript/tool_design.ts), lines 72–90 | Native 25-versus-six evaluation | F-002: predetermined direct retrieval only; no matching live host/model route. |
| [common/typescript/advanced_lessons.ts](../../common/typescript/advanced_lessons.ts), lines 100–131 | Actual module 14/18 example behavior | F-002/F-003: direct retrieval and source metadata assertions are narrower than full lesson parity. |
| [module 14 TypeScript example](../../modules/14_tool_design/typescript/examples/03_evaluation.ts) and [tests](../../modules/14_tool_design/typescript/tests/module.test.ts) | Learner entry point and acceptance | Example passes; tests repeat the narrower helper contract. |
| [module 18 TypeScript walkthrough](../../modules/18_packaging/typescript/README.md), lines 45–49, [example](../../modules/18_packaging/typescript/examples/03_bundle.ts), and [tests](../../modules/18_packaging/typescript/tests/module.test.ts) | Packaging lesson entry points and acceptance | F-003: no built-artifact operation through these entry points. |
| [scripts/build_notes.mjs](../../scripts/build_notes.mjs) | Native bundled executable and license inventory | Actual native build helper exists and can be reused to repair the lesson. |
| [scripts/mcpb.mjs](../../scripts/mcpb.mjs), line 42 | Output/source containment | F-001: `startsWith('..')` confuses an ordinary descendant name with a parent path component. Reproduced. |
| [scripts/mcpb.test.mjs](../../scripts/mcpb.test.mjs), line 69 | Containment regression cases | Tests an ordinary inside path; misses `..inside` descendants. |
| [scripts/dependencies.test.mjs](../../scripts/dependencies.test.mjs) | Override compatibility, cancellation and locked-version tests | Actual consumer tests and CI clean-audit evidence retained; no suppressed advisories. |
| [module 07 README](../../modules/07_real_data/README.md), lines 169–170; [module 09 README](../../modules/09_elicitation_sampling_roots/README.md), line 203; [module 14 README](../../modules/14_tool_design/README.md), line 141; [module 15 README](../../modules/15_agent_frameworks/README.md), lines 142–143 | Python/TypeScript API tables | F-004: stale “planned” wording; distinguish implemented APIs from Python-only frameworks. |
| [module 18 README](../../modules/18_packaging/README.md), lines 174–178 | Publication procedure | E-002: TestPyPI rehearsal described, not executed. |
| Main module directories and Python example headers | Counts, use cases, run/expected metadata | 22 modules; 67 Python/66 TypeScript examples; 66 exercises/solutions per language; use cases exist; checked header fields present. |
| Capstone 01/04/05 READMEs and completion records | Acceptance, reference composition and declared limits | Deliverables present; reduced semantic encoder and local single-user deployment limits are disclosed. Model-quality evidence is not inferred from fixture tests. |

## Validation and limits

Fresh structural, targeted-test, audit, external-link and containment-probe
results are recorded in the action plan. Existing full CI validates unchanged
runtime code but does not eliminate the reproduced edge case or prove absent
lesson behaviors. No remediation was performed as part of this review.
