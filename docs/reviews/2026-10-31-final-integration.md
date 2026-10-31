# Final follow-up review — pass 2: integration

Historical baseline evidence. The [module 14 follow-up](../MODULE_14_PARITY_VERIFICATION.md)
records the R-101/R-102 fixes and their current validation status.

Baseline: `639e043`. See the [action plan](2026-10-31-final-review.md) and
[per-file findings](2026-10-31-final-per-file.md).

## Boundary traces

| Flow | Result |
|---|---|
| Original prompt sections 8/10 → Python and TypeScript module 14 → host loop → grading | Both implementations now run a real host loop with the same six issue IDs and four-turn/four-call limits. Their final-answer predicates differ: R-101 is reproducible without any live measurement. |
| Module 14 CLI → `.env`/provider settings → missing configuration | With `LLM_PROVIDER=fake`, `--live` contacts no provider and exits 1, but exceptions reach the terminal with traces. R-102 concerns presentation/recovery guidance, not silent network use. |
| Bundle destination → canonical parent → relative path check → archive creation | Correct component-boundary check; inside-output regressions pass. Prior F-001 remains closed. |
| Module 18 native examples → build → package → inspect → install/extract → empty working directory → MCP call | Actual effects replace prior metadata-only assertions. Both npm and MCPB paths pass. Prior F-003 remains closed. |
| Native gateway/Chat Pro → shared browser assets → OAuth/Keycloak/upstreams → browser/deployment CI | The tested code is unchanged since passing CI. Required native application and shipping jobs passed; no additional application gap identified in this review scope. |
| Teaching tables → source APIs → release/link gates | Earlier stale counterpart wording is gone, links resolve, and language-specific framework limits are explicit. No separate new documentation-content finding was established. Completion records should incorporate R-101/R-102 when they are fixed. |
| Source revision → CI → evidence-only commit | CI tested `b0b1301c07d2bc4484d690a71090ab9dc625aa4a`. Baseline `639e043` changes only `DEFINITION_OF_DONE.md` and `FINAL_REVIEW_FIXES_VERIFICATION.md` after that revision. All 29 required jobs passed; optional manual external-links job skipped. |

## R-101 replay evidence

For issue 1, replayed the actual fixture ID/status with no model service. Both
catalogs produced the same discrepancy:

| Model behavior | Python completed | TypeScript completed |
|---|---:|---:|
| Correct exact JSON answer, no tool call | 1 of 1 | 0 of 1 |
| Successful tool call, correct ID/status, extra `extra: true` property | 0 of 1 | 1 of 1 |

The first case demonstrates missing evidence enforcement in Python. The second
demonstrates different answer-shape enforcement. The outcome does not depend on
provider quality, credentials, or the three outstanding acceptance items.
Existing native tests explicitly reject no-tool answers but do not establish
the same behavior in Python or require exact answer keys in TypeScript.

## R-102 replay evidence

Ran both example-03 entry points with `--live`, setting `LLM_PROVIDER=fake` and
`LLM_MODEL=fixture` in subprocess environments. Both returned exit code 1.
TypeScript printed `Error: Choose a live LLM_PROVIDER and LLM_MODEL first...`
followed by source/module stack frames. Python printed `Traceback (most recent
call last)` and ended with `ValueError: Choose a real LLM_PROVIDER and LLM_MODEL
for --live.` The TypeScript exception text contains environment-check guidance,
but its CLI still prints a trace; the Python exception lacks that guidance.

## Unchanged acceptance boundaries

E-001: timed first-time setup and two third-party GUI host runs.
E-002: actual TestPyPI publication and install from that release.
E-003: controlled live-model comparison with recorded model/settings/results.

No accounts were used for publication, GUI acceptance, or real model calls.
CI and deterministic fixtures do not prove these outcomes.
