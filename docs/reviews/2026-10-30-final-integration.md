# Final review — pass 2: cross-file integration

Historical baseline evidence. See the [follow-up fixes and validation](../FINAL_REVIEW_FIXES_VERIFICATION.md)
for the current status of F-001 through F-004.

Baseline: `4a03e3b`. See [findings and actions](2026-10-30-final-review.md).

## Boundary traces

| Requirement / flow | Producer → consumer | Evidence and result |
|---|---|---|
| Full TypeScript lesson 14 | Example 03 → `lesson(14,3)` → `designEvaluation()` | Six predetermined calls directly to each MCP catalog. Python example 03 → `evaluate(live, limit)` → `Host`/`create_tool_model` has an additional route. **F-002**; passing helper assertions do not prove equivalent evaluation behavior. |
| Full TypeScript lesson 18 | Three examples → `lesson(18,part)` → in-memory read-only server/source JSON | No build, archive validation or installed server is invoked by these entry points. **F-003**. The separate Python-orchestrated packaging pipeline and native build/packer do work; CI shipping verifies them. |
| Bundle containment | `pack(source,destination)` → canonical parent → `relative` → prefix condition → walk/ZIP/write | `source/..inside/output.mcpb` produces `..inside/output.mcpb`, which passes the prefix condition. **F-001**. A second build can package the earlier output because it now resides under the input tree. No arbitrary-file-write exploit was established. |
| Lesson promises → acceptance | B1 full-track objective → module pages → helper tests | Structural gates establish counts and runnable contracts, not complete behavioral equivalence. F-002/F-003 require tests that observe model-loop and built-artifact effects. |
| Implemented native APIs → teaching tables | Native runtime files → Python module API table | Future-tense “planned” entries remain in four module READMEs. **F-004**; update to actual APIs or explicit language-specific differences. |
| Dependency tree → actual consumers → CI | Scoped minimatch/glob overrides → ESLint/project service/reference server → compatibility and cancellation tests | Fresh audit has zero vulnerabilities; all four Node CI jobs pass. No open dependency advisory was identified. |
| OAuth gateway → upstreams | HTTP token validation → request-local identity → filtered native workspace → stdio services | Prior gap is closed. Current CI exercises real Keycloak, scope step-up, gateway and native upstreams. No new defect found in the scoped boundary inspection. |
| Browser → model → approval → execution | Chat Pro session → provider adapter → one-use human decision → refreshed fingerprint → MCP call | Prior application gap is closed. Same browser scenarios pass against both implementations; this is distinct from the lesson parity findings. |
| Repository → new learner | Public checkout → install → Inspector → two host GUIs | CI cold installs and protocol tests pass, but no first-time human timing/two-host execution record establishes **E-001**. |
| Source → public package | Shared sources → wheel/npm/MCPB → isolated local launch → TestPyPI upload | Local stages pass. Last external stage was not executed: **E-002**. Registry publication is explicitly optional and should not be conflated with this use case. |
| Tool redesign → quality claim | 25 versus six catalogs → deterministic fixtures → optional live model route | Fixture results measure retrieval/catalog behavior, not LLM success. Actual model comparison evidence remains **E-003**. |
| Docs → reachable references | Local Markdown targets + external URL checker | Fresh check reports zero failures. Host capability documentation remains conditional and does not substitute for GUI acceptance. |

## Priority after integration review

F-001 remains P2 because known shipping staging layouts are unaffected and archive
size limits still apply; its promised containment behavior is nonetheless false.
F-002/F-003 remain P2 educational/acceptance gaps rather than failures of the
already implemented native application backends. F-004 is P3 documentation drift.
E-001/E-002/E-003 are unverified requested outcomes, with concrete completion
criteria in the action plan.

The corrected dependency CI run passed all 29 required jobs. Its success is
consistent with these findings: the missing descendant-path case, model route
and lesson artifact actions are not required by the existing assertions, while
manual publication and novice/GUI acceptance are outside the automated run.

## Scope limits

No newly discovered P0/P1 runtime issue was demonstrated. This pass traced the
listed boundaries and compared acceptance evidence to the original prompt; it
did not re-audit every third-party SDK, prove all possible malicious inputs safe,
or perform account-based publication, paid model evaluation or GUI onboarding.
