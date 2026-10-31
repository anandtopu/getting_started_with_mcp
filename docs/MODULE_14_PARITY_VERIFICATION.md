# Module 14 grading and configuration follow-up

Date: 2026-10-31 (America/Chicago). **R-101 and R-102 are closed.** These findings
originated in the [final follow-up review](reviews/2026-10-31-final-review.md)
of baseline `639e043`.

## Delivered behavior

**R-101 — shared scoring contract.** Both evaluators require a JSON object with
exactly `id` and `status`, the expected numeric ID and status, at least one tool
call, and no failed calls. JSON `1` and `1.0` represent the same numeric value;
boolean `true` and string `"1"` are rejected. No-tool guesses and extra properties
fail in both tracks. Model/parse failures and exhausted budgets remain failed
cases. The live paths, case list and four-turn/four-call limits are retained.

The [shared fixture](../tests/fixtures/tool_evaluation.json) drives 16 independent
replays through both catalogs in both languages: exact success, numeric notation,
no-tool guess, extra property, boolean/string/wrong ID, wrong status, missing
property, null/array answer, malformed JSON, a tool error followed by correct
evidence, provider failure, call budget and turn budget. Python exercises its
real host with an injected model; TypeScript exercises its provider adapter and
host with injected HTTP responses. No real provider is contacted.

**R-102 — friendly configuration failures.** The evaluators classify expected
configuration/limit errors for their CLI boundaries. The commands print a concise
stderr message, include `scripts/check_env.py`, and exit 1 without a traceback.
Raw validation errors are not echoed because they can contain configuration
values. Unexpected programming errors are not disguised as setup failures.

Subprocess tests in each language cover the fake provider with `--live`, an
unknown provider containing a sentinel value, a missing live model, a missing
hosted-provider key, and an invalid limit. They assert nonzero exit, empty stdout,
setup guidance, no stack trace and no echoed sentinel. Invalid limits also have
direct Python tests, including boolean input.

The module READMEs now document the common scoring rule and setup diagnostics.
The review reports preserve their original baseline findings and link here for
the follow-up status.

## Validation

- Focused Python: **25 passed**; targeted Ruff check/format passed.
- Focused TypeScript/module 14: **32 passed**; TypeScript compilation passed.
- Full native checks: TypeScript compiler, ESLint and **191 tests passed**, with
  one existing Windows symlink skip (192 collected across 35 files).
- Release/teaching/local-link checks passed; npm audit reports **zero vulnerabilities**.
- Full corrected local Python suite: **274 passed, one existing Windows
  symlink-permission skip**; the existing LangChain beta warning remains.
- Tier 4 plus the new evaluation regressions: **42 passed** after updating the
  older diagnostic assertion; Ruff check/format passed.
- [All 29 required CI jobs passed](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41177147316)
  on `52612c5b97e02faae35df8c1fd6d99f139caac93`. Linux Python reports **275 passed**
  and **233 standalone examples** checked. All seven Python jobs, four Node
  24/26 Windows/Linux jobs, application/browser/deployment, packaging, Inspector,
  framework and native SDK checks passed. Linux native tests: **192 passed**;
  Windows native tests: **191 passed, one existing skip**. The optional manual
  external-link job was skipped.

The [initial CI run](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41176718847)
on `f406b51` exposed an older Tier 4 assertion matching the previous `1–6` error
text. The new evaluator tests passed; the older assertion was updated to require
the specific configuration-error class, the new range wording and setup guidance.
The superseded run was stopped. The fresh full matrix above passed. The initial
local suite had already loaded the old assertion; a full local rerun after the
correction also passed. The final documentation-only commit records this evidence
with `[skip ci]`; the CI link identifies the tested code revision.

## Remaining acceptance items

This follow-up does not claim E-001 (timed setup/two GUI hosts), E-002 (TestPyPI
publication), or E-003 (controlled live-model measurement). The new fixtures
validate scoring and error behavior; they are not measurements of model quality.
