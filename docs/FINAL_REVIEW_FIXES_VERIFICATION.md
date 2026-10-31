# Final review implementation fixes

Date: 2026-10-30. Follow-up to the [original-prompt review](reviews/2026-10-30-final-review.md)
of baseline `4a03e3b`.

## Changes and acceptance

| Finding | Delivered change | Regression evidence |
|---|---|---|
| F-001: bundle output containment | The packer distinguishes the parent component `..` from contained directory names such as `..inside`. | Reject ordinary/nested and two-dot-prefixed contained destinations before writing; accept actual sibling destinations. Existing deterministic ZIP, manifest and private-path checks remain. |
| F-002: TypeScript module 14 | Both catalogs now run through the native host; the CLI exposes `--live` and `--limit`. Reports include completion, tool calls, timing and per-case results with identical four-turn/four-call budgets. | Offline evidence comes from real MCP results. Injected provider responses exercise the live adapter/host path, both catalogs, limits, malformed answers, failed requests, guessed answers and budget exhaustion. |
| F-003: TypeScript module 18 | Native examples build the self-contained CLI, pack and inspect npm/MCPB artifacts, install/extract them, and call the resulting servers from an empty directory outside the checkout. | The tests check actual inventories/bytes, installed command launch, read-only discovery and the returned release note. Temporary staging avoids shared build-output races. |
| F-004: stale documentation | Modules 07, 09, 14 and 15 name implemented APIs and distinguish Python-only Pydantic AI. Module 14/18 native walkthroughs describe the actual commands and results. | The release teaching check rejects obsolete counterpart-planning wording. |

The three review reports preserve the evidence and line references from their
original baseline; this record tracks the subsequent fixes.

## Validation

- Focused native regressions passed, including real package builds and launches.
- Release structure and local-link checks passed. Ruff check/format passed.
- Fresh npm audit: **zero vulnerabilities**; dependency versions and overrides are unchanged.
- Full native checks passed: TypeScript compiler, ESLint and **170 tests**, with
  one existing Windows symlink skip (171 collected across 35 files).
- Full Python suite and the required CI matrix: in progress. Final results and
  the exact tested revision will be recorded after completion.

## Remaining acceptance evidence

These fixes close the four implementation/documentation findings. They do not
claim the separate E-001/E-002/E-003 outcomes from the review: a timed first-time
learner setup and two third-party GUI hosts, a TestPyPI upload, or a controlled
live-model quality measurement. The live evaluator is implemented and tested
with provider fixtures; those fixtures are not a measurement of a real model.
