# Final follow-up review — pass 1: per-file analysis

Historical baseline evidence. The [module 14 follow-up](../MODULE_14_PARITY_VERIFICATION.md)
records the R-101/R-102 fixes, passing full CI and closure of both findings.

Date: 2026-10-31 (America/Chicago). Baseline: `639e04355087b6816e113cd887cc562f18095fe1`.
Original prompt SHA-256: `e05f61c45b2023c6923e34fa5f757fe5671df9228ab113df1da13be4489aa39c`.
See the [action plan and verdict](2026-10-31-final-review.md).

## Scope

Reconciled the original requirements, the previous review and its implementation
fixes. Read the changed packaging/evaluation/lesson files, their tests, the native
host and provider adapters, the release and Inspector checks, protocol-guide
generator, feature map, B1 runtime boundaries, application verification records,
host setup, and selected capstone/package documentation. The unchanged full
application/deployment matrix is supported by the verified CI run on `b0b1301`.
Generated captures, PDFs, vendored schemas and third-party libraries were checked
through their existing validation/provenance rather than rereviewed line by line.

## Findings

| ID | Severity | File and line | Finding | Impact | Recommended fix |
|---|---|---|---|---|---|
| R-101 | P2 | [Python evaluator](../../common/tool_evaluation.py), lines 61–64; [TypeScript evaluator](../../common/typescript/tool_design.ts), line 104 | Completion criteria differ. Python accepts an exact correct answer with zero tool calls, whereas TypeScript rejects it. Python rejects an answer with an extra property, whereas TypeScript accepts it after a tool call. | Identical model behavior produces opposite completion scores in the two tracks. This violates the prompt's behavioral-parity requirement and can mislead the later live comparison. | Define one grading contract for both implementations. Require actual successful tool evidence and agree on exact answer shape; apply the same deterministic replay cases to both languages. Update the completion record after verification. |
| R-102 | P3 | [TypeScript evaluation entry point](../../modules/14_tool_design/typescript/examples/03_evaluation.ts), line 13; [Python entry point](../../modules/14_tool_design/python/examples/03_measure_change.py), lines 23/34 | Missing live-model configuration escapes the CLI as an unhandled exception. Both commands print a stack trace; the Python message also omits the environment-check command. | The normal beginner setup failure does not meet section 10's explicit friendly-error requirement. | Catch expected configuration/usage failures at each CLI boundary, print concise setup guidance pointing to `uv run python scripts/check_env.py`, and exit nonzero without a trace. Add subprocess assertions with the provider explicitly set to `fake`. |

## Reviewed files without a new actionable finding

| Surface | Evidence |
|---|---|
| `scripts/mcpb.mjs`, `scripts/mcpb.test.mjs` | Parent-component containment now rejects `..inside` and nested contained destinations while permitting real siblings. Deterministic archive/schema/private-path regressions pass. |
| `scripts/build_notes.mjs`, `scripts/notes_packaging.mjs`, declaration and module 18 tests | Native build, exact inventories, installed-byte comparisons, isolated npm command launch, inspected bundle extraction, actual MCP discovery/call and cleanup are implemented. |
| `common/typescript/advanced_host.ts`, `llm.ts`, evaluator tests | Four-call/four-turn evaluation limits and real provider-adapter routing exist. Provider fixtures verify native behavior; R-101 is the missing cross-language contract, not absence of the native live route. |
| Module 07/09/14/15 API tables and module 14/18 TypeScript walkthroughs | Prior future-tense counterpart labels are removed. Native APIs and Python-only Pydantic AI are described. Command/output documentation matches the successful paths inspected. |
| `scripts/check_course.py`, `tests/test_repository.py`, Inspector inventory, protocol guide | Delivered files, required teaching sections, example inventory, real captures and required method references have executable gates. Those structural gates do not test the two new findings. |
| Feature map, B1 boundaries, application/capstone guides and verification records | Implemented native OAuth/Chat Pro and packaging paths are documented; shared tooling and runtime limitations are explicit. Historical phase counts are dated evidence, not new runtime requirements. |

## Validation

Fresh focused native tests: **39 passed, one existing Windows symlink skip**.
Release/teaching/local-link validation passed. External-link sweep: **zero failures**.
Offline probes reproduced R-101 in both catalogs and R-102 in both CLIs without
network/model calls. Python regression results and CI evidence are recorded in
the [action plan](2026-10-31-final-review.md).

## Open questions

None is needed to fix R-101/R-102. The separate E-001/E-002/E-003 acceptance
items remain unverified. This scoped review is not an exhaustive security audit.
