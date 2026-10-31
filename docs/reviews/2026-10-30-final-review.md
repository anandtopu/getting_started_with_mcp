# Final original-prompt review and action plan

Date: 2026-10-30. Reviewed baseline: `4a03e3b3050ed11d29fcb5b48edbbe1469f54608`.
Original prompt SHA-256: `e05f61c45b2023c6923e34fa5f757fe5671df9228ab113df1da13be4489aa39c`.

## Verdict

**Follow-up:** F-001 through F-004 have been implemented in the
[fix verification record](../FINAL_REVIEW_FIXES_VERIFICATION.md), which tracks
current test/CI status. The review below preserves the original `4a03e3b`
findings. E-001 through E-003 still require separate acceptance evidence.

**Gaps remain; a strict “all requirements complete” sign-off is not justified.**
The course is runnable, structurally complete, and has a clean npm audit and
passing full CI. The earlier native OAuth gateway/Chat Pro application gap and
the MCPB/Zod and glob/minimatch advisories are resolved. This review found one
reproducible packaging correctness defect, two remaining TypeScript lesson
completeness gaps, and stale lesson wording. Three requested outcomes also lack
executed acceptance evidence.

No P0/P1 finding was identified in this scoped review. That is not a claim that
every implementation or third-party dependency has undergone an exhaustive
security audit. See the [per-file pass](2026-10-30-final-per-file.md) and
[integration pass](2026-10-30-final-integration.md) for scope and evidence.

## Fix queue

| ID | Priority | Owner | Finding and evidence | Action and acceptance |
|---|---|---|---|---|
| F-001 | P2 | Packaging | [scripts/mcpb.mjs](../../scripts/mcpb.mjs), line 42, treats any relative path beginning with `..` as outside the source. `source/..inside/bundle.mcpb` is inside the source but passes. A temporary fixture reproduced this; ordinary `source/bundle.mcpb` was correctly rejected. Existing coverage at [scripts/mcpb.test.mjs](../../scripts/mcpb.test.mjs), line 69, tests only the ordinary name. | Check path components: outside means `rel === '..'`, `rel.startsWith('..' + sep)`, or an absolute relative result for another volume. Reject all other destinations. Add nested `..inside`/`..cache` and ordinary nested-output negatives; retain an actual sibling-directory positive. Verify no output is written for rejected cases. |
| F-002 | P2 | TypeScript lesson 14 | [common/typescript/tool_design.ts](../../common/typescript/tool_design.ts), lines 72–90, evaluates six predetermined direct calls. It has no model/host evaluation route. Python's [common/tool_evaluation.py](../../common/tool_evaluation.py), lines 29–56, supports a provider-backed `live` route. This falls short of the original B1 full-lesson and cross-language behavior promises, even though deterministic retrieval is honestly labeled. | Add an opt-in native model/host evaluation using the same cases and budgets, exposing completion, calls and timing. Keep default tests offline with model fixtures and test both routes through injected provider responses. Document the native live command; do not require a paid call in CI. |
| F-003 | P2 | TypeScript lesson 18 | [common/typescript/advanced_lessons.ts](../../common/typescript/advanced_lessons.ts), lines 128–131, checks read-only tools, a package version string and two fields in the source manifest. The [TypeScript walkthrough](../../modules/18_packaging/typescript/README.md), lines 45–49, runs only those checks. It never builds, validates or installs the artifact being taught. The real shared packaging pipeline works and is tested elsewhere; this is a lesson/acceptance gap, not absence of npm/MCPB distribution. | Wire the TypeScript lesson to the existing native build/packer, build into a temporary staging directory, inspect the resulting tarball/bundle and launch its server outside the checkout. Make its test assert actual packaged contents and MCP calls rather than only `status: PASS`. |
| F-004 | P3 | Course documentation | API tables still say “B1 counterpart planned” or “Full TS counterpart planned in B1”: [module 07](../../modules/07_real_data/README.md), lines 169–170; [module 09](../../modules/09_elicitation_sampling_roots/README.md), line 203; [module 14](../../modules/14_tool_design/README.md), line 141; [module 15](../../modules/15_agent_frameworks/README.md), lines 142–143. | Replace stale future-tense labels with actual native APIs/links or precise language-specific limitations. Do not invent a native equivalent for a Python-only framework. Extend the teaching check to catch stale delivery-status wording. |

F-001 affects an unusual staging layout; the existing course builders place
their output outside the staging directory and still pass. Its impact is
accidentally including earlier generated bundles in later builds, violating
the packer's documented output boundary. This review does not establish an
arbitrary-file-write or runtime authorization exploit.

## Outstanding acceptance evidence

These are separate from the implementation fixes. The original prompt explicitly
requested the outcomes; existing documentation is candid about not claiming them.

| ID | Prompt requirement | Current evidence | Completion criterion |
|---|---|---|---|
| E-001 | Section 12: clone to first Inspector server in under ten minutes; module 00: use the reference server in two hosts | [Definition of done](../DEFINITION_OF_DONE.md), line 17, says no first-time human timing was recorded. [Host setup](../HOST_SETUP.md) confirms config formats but not executed third-party GUI sessions. | Record a first-time learner run with prerequisites and elapsed time, plus successful reference-server calls from two named host versions. Desktop bundle GUI installation can be included in this manual verification. |
| E-002 | Module 18: package the notes server and publish it to TestPyPI | [Module 18](../../modules/18_packaging/README.md), lines 174–178, provides a learner-controlled publication procedure. Local artifacts and isolated installs pass, but no uploaded release is claimed. | Publish reviewed artifacts under an authorized namespace, then record the release URL, version/digests and a successful install-and-call from that release. Registry publication is explicitly optional in module 19; TestPyPI publication is a requested module 18 outcome, not the same requirement. |
| E-003 | Module 14: measure LLM task completion before and after the redesign | The Python live evaluator exists, but [the lesson](../../modules/14_tool_design/README.md), lines 57 and 175, and [Phase 8 evidence](../PHASE_8_VERIFICATION.md), line 43, distinguish fixture checks from unmeasured model accuracy. | Run a controlled comparison with an identified local or hosted model, fixed cases/budgets and repeated trials; save per-case outcomes and limitations. An improvement is not required or presumed; an actual measurement is. |

No live model calls, account-based uploads, cloud deployment or third-party GUI
actions were performed for this review. Public Registry publication, vendor SSO,
and a public multi-user cloud deployment remain optional or beyond the stated
local teaching scope; they are not newly discovered implementation blockers.

## Requirement coverage

| Original area | Review result |
|---|---|
| Public repository identity | GitHub reports PUBLIC, named `getting_started_with_mcp`. |
| Current protocol and SDK approach | The official spec URL still redirects to 2026-07-28. Its changelog was re-read. Verified SDK substitutions and labeled legacy compatibility remain documented. |
| Course structure | 22 modules, four bonuses, five capstones, six one-page PDF sheets. Release/teaching/link gates pass. |
| Examples and exercises | Main modules contain 67 numbered Python examples and 66 TypeScript examples; each language has 66 exercises and 66 solutions. Every main-module use-case entry point exists. All inspected Python example headers include run and expected-output metadata. Presence is not proof of semantic parity: F-002/F-003 remain. |
| Executable inventory | 49 servers plus 184 scripts, 233 total, covered by the recent CI inventory checks. |
| Security and application follow-ups | Native OAuth gateway and full Chat Pro are implemented with actual browser/deployment acceptance; reviewed boundary code and existing regressions remain intact. |
| Dependency advisories | Fresh `npm audit --json` returns an empty vulnerabilities map and zero in all severity counts. Scoped overrides and the stricter CI gate remain in place. |
| Packaging | Wheel/npm/MCPB builds and isolated launches pass in CI; output-path edge case F-001 and TypeScript lesson gap F-003 remain. |
| Beginner and external outcomes | E-001/E-002/E-003 remain unverified. |

## Validation performed

- Re-read the original prompt and current completion/follow-up records.
- Re-ran `scripts/check_course.py --release`: passed, including PDF page counts
  and local links. Ran `scripts/check_links.py --external`: **zero failures**.
- Re-ran the targeted repository/foundation suite excluding the expensive full
  subprocess inventory: **15 passed, one Windows symlink-permission skip**.
- Independently inventoried both language tracks and Python example headers:
  no structural/header gaps in the checked fields.
- Ran TypeScript module 14 example 03 and module 18 example 03: both report PASS;
  source tracing establishes their narrower behavior described above.
- Reproduced F-001 in a temporary directory: the first accepted inside-output
  build contained two files; repeating it contained three, including the previous
  bundle. Removed the temporary fixture afterward.
- Rechecked [the latest full CI run](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41163625829):
  **29 required jobs passed** on `d13a210`; manual external-link job skipped.
  Changes from that tested revision to review baseline `4a03e3b` are documentation
  only. The full suites were not redundantly rerun in this review.
- Recent full-suite evidence: Linux native **159 passed**; Windows native **158
  passed, one skipped**; local Python **249 passed, one skipped**. These are prior
  execution results, not new full-suite runs performed during this review.

## Sign-off rule

Fix and verify F-001 through F-004 before calling the delivered implementation
and lessons complete. Close E-001 through E-003, or explicitly accept them as
unverified exceptions, before claiming literal completion of the entire original
prompt. Green CI alone does not establish these missing behaviors or outcomes.

Primary references rechecked: [current specification](https://modelcontextprotocol.io/specification),
[full revision changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog).
