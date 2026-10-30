# Definition of done

Verification date: **2026-10-30**. Scope: the delivered local course and its CI. The [post-build review](reviews/2026-10-30-review-summary.md) supersedes blanket completeness claims below. [Measured evidence and limits](PHASE_8_VERIFICATION.md) identify the tested versions and optional integrations.

## Requested release gates

- [x] Default cached `uv sync --offline --frozen` and offline Python tests pass without API keys. TypeScript tests pass. Fresh dependency installation needs network.
- [x] Ruff check/format, TypeScript compiler and ESLint pass.
- [x] Final CI matrix: all 28 required jobs passed, covering Python 3.12–3.14 and Node 24/26 on Windows/Linux, plus macOS Python 3.12 and four native SDKs on Windows/Linux. See the linked run in the verification record.
- [x] Every advertised primitive is listed by Inspector or an equivalent client check. Native SDK contracts cover tools/resources/prompts; the explicit audit fixture has a separate stdio regression.
- [x] Repository-wide subprocess tests enforce protocol-only stdout; the TypeScript launcher also runs outside the checkout.
- [x] The source audit rejects banned legacy imports; MCP deprecation warnings are test errors. Labeled older-protocol interoperability is retained deliberately.
- [x] Local HTTP defaults to 127.0.0.1, checks Origin/Host and validates audience on authorized routes. Container-wide binding is explicit and exposed through a loopback proxy.
- [x] Mutating tools require confirmation and appropriate annotations; regression tests reject missing approval, stale decisions and insufficient scope. The deliberately unsafe audit fixtures are labeled and require explicit lab mode.
- [x] All modules and bonuses include the required teaching sections, examples/use cases, three exercises with solutions, quizzes and tests. B1 adds native TypeScript counterparts with documented API limits.
- [x] Feature-map links resolve; local and external link sweeps report zero failures.
- [ ] A first-time human GUI setup in under ten minutes was not timed. The prerequisite-ready CI cold checkout/install/Inspector path is tested; download speed and host account setup remain variable.
- [x] Complete files and runnable reference code are delivered. Intentional exercise stubs are labeled and have independent checkers; no production placeholder is presented as implemented behavior.

## Phase 8 deliverables

- [x] Four bonus modules: TypeScript companions for every module, Go/C#/Rust/Java SDKs, specification workflow, current extensions.
- [x] Five capstones: stories, acceptance, distinct Mermaid architecture, runnable policy starter, reference runtime, tests, evaluated cases, security checklist, rubric and extension ideas.
- [x] Reference docs: mental model, all 24 taught current methods/notifications, four design flowcharts, four-host setup matrix, security, 100-term glossary, troubleshooting and migration.
- [x] Six one-page PDF cheatsheets, editable content and reproducible generator; rendered and visually checked.

## Remaining original-prompt parity

- [ ] B1's complete native application parity: the combined OAuth gateway/deployment and full Chat Pro web backend use shared Python infrastructure. Native TS protocols, providers, data, input, OAuth clients, quality, packaging, Registry, Tasks and App bridge have runnable cases. See the [explicit coverage matrix](../modules/bonus/B1_typescript_track/README.md#coverage-and-runtime-boundaries). A small native tool-review UI is not equivalent to the full production-host lesson.

## Optional integrations outside the tested release

- [ ] Live model measurements, external vendor SSO and a production multi-user deployment require learner credentials and additional evaluation.
- [ ] Public Registry/package publication, cloud deployment and third-party desktop GUI installation were not performed.

Java's stable SDK uses the labeled older-revision path. TypeScript Tasks uses official framing with a bounded receiver because the pinned high-level validator lacks task-result support. Knowledge semantic search uses a small explicit concept encoder. These choices are explained at their teaching points, with runnable evidence.
