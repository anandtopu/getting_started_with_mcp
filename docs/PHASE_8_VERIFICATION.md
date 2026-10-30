# Phase 8 verification

Verification date: **2026-10-30**. Target protocol 2026-07-28, Python SDK 2.3.0 and TypeScript SDK 2.4.0. Dependency manifests and lockfiles are authoritative. This record separates local deterministic evidence from optional integrations.

## Reproduce the release checks

```text
uv sync --frozen
npm ci
uv run pytest
uv run ruff check .
uv run ruff format --check .
npm run check
uv run python scripts/check_course.py --release
uv run python scripts/run_all_examples.py
uv run python scripts/inspector_smoke.py
uv run python scripts/phase8.py
```

Default tests require no model keys and make no live model calls. Dependency installation requires network once. The development group includes the optional SDKs used by default tests; minimal deployment installs use `--no-dev` and explicit extras.

## Feature evidence

| Surface | Check and evidence |
|---|---|
| B1 native TypeScript counterparts | 17 additional lesson tracks, 51 finite examples, native host/framework/input/Task/App components; `npm run check` |
| Go 1.8 / C# 2.3 / Rust 3.8 / Java 2.1 SDKs | `uv run python scripts/native_sdks.py --language go --build`; repeat csharp/rust/java. [Version matrix](../modules/bonus/B2_other_sdks/VERSIONS.md) records toolchains and Java legacy limitation |
| Skills and machine authorization | `scripts/phase8.py`; Python/TypeScript Skills interoperability and actual HTTP OAuth exchanges. `scripts/ts_auth.py` tests native TS service and enterprise providers |
| Personal Knowledge packaging | `uv run python scripts/knowledge_package.py --prepare`, then the same command without prepare; wheel and MCPB embedded wheel launch outside checkout |
| Audit, Gateway, Ops, Chat Pro | [Five reference contracts](../scripts/capstones.py); [Python regression tests](../tests/test_phase8.py); [browser tests](../tests/browser/chat.pw.ts) |
| Policy evaluation | `uv run python scripts/check_capstone.py --project 1`; repeat 2–5. Each compares four actual policy decisions with expected cases; starter intentionally fails |
| Reference completeness | [24 captured methods/notifications](protocol_coverage.json), 100 glossary terms, design flows, host matrix, migration and troubleshooting |
| Printable references | `uv run --group docs python scripts/build_cheatsheets.py`; six PDFs asserted one page, rendered for visual inspection |

## Regenerate evidence

`uv run python scripts/phase8.py --capture` refreshes bonus/capstone conversations; `uv run python scripts/protocol_guide.py` rebuilds the reference from actual messages. Native SDK captures use `--capture` on the native runner. Captures use synthetic fixtures and redact credential fields. The capture header records the client runtime; the B2 matrix identifies the native server SDK.

The Ops deployment combines `deployment/compose.yaml` with `capstones/04_lumen_ops/deployment/compose.yaml`. Docker, browser, package-install and native compiler jobs are separate from the offline default suite. CI runs Python 3.12–3.14 on Windows/Linux (plus macOS 3.12), TypeScript on Node 24/26 on Windows/Linux, and the native contracts on Windows/Linux.

## Explicit limits

- No live LLM accuracy, cost or latency claim. Deterministic framework fixtures test routing and plumbing.
- No cloud service, public Registry entry, package-index publication or vendor SSO deployment was created. Registry/Card domains are fictional examples.
- No claim that all four third-party host GUIs support the newest revision or every extension. [Host setup](HOST_SETUP.md) records documented support and manual checks.
- Knowledge semantic ranking uses a five-concept encoder, not a pretrained general embedding model.
- Java's stable SDK uses older-revision interoperability; TS Tasks uses official transport framing around a bounded receiver because the pinned high-level validator lacks task-result support.
- Ops Task storage and limits are single-process teaching infrastructure; multi-worker scheduling/recovery needs additional design.

## Measured release checks

- The full local Python suite passed **238 tests**, with one OS symlink-permission skip. Three later entry-point/resource regressions were added; the final Phase 8 subset passed **10/10**. All seven final Python CI jobs passed the complete **242-test** suite and all **227 examples**.
- TypeScript: **107 tests in 27 files**, with compiler and ESLint passing.
- Standalone example runner: **227 entry points** (45 servers and 182 scripts), all passed.
- Inspector/equivalent: **73 catalog checks across 45 listed servers** passed advertised primitive discovery. The Windows Node Inspector has a reproducible `UV_HANDLE_CLOSING` shutdown crash for HTTP; the runner uses an explicitly identified SDK equivalent only for that specific failure. Linux CI runs the Inspector path directly.
- Four native SDK contracts passed; nine bonus exercise solutions and **20 capstone policy cases** passed.
- Knowledge wheel and MCPB embedded wheel: **two isolated launches outside the checkout** passed, including the nested-note routing fix.
- Real browser acceptance: **three Chromium tests** passed (approvals, input, Tasks, App sandbox, mobile layout and forged requests).
- Ruff check/format, release inventory, local/external links, 24-method coverage and six one-page PDF checks passed. All six PDF renders were visually inspected.
- Ops Docker/OAuth deployment passed in Linux CI. Local Docker was unavailable; its stalled startup command was stopped. No local container success is claimed.

The [final CI run](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41123051680) passed all **28 required jobs** on `40ff40b`, including expanded Inspector coverage for every advertised Phase 8 resource/prompt list. The optional external-link CI job was skipped; the separate local external-link sweep passed. Earlier runs exposed an invalid C# build switch; the corrected runner performs locked restore followed by `build --no-restore` and passes locally and in CI.

Python 3.14 also reports LangSmith warnings for its use of `asyncio.iscoroutinefunction`; the LangChain MCP adapter emits its documented beta warning. These third-party warnings are recorded, not suppressed. Official MCP deprecation warnings remain test errors.
