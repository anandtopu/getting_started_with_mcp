# Verification notes

## Post-build prompt review — October 30, 2026

[Review findings, completed validation and explicit gaps](reviews/2026-10-30-review-summary.md) supersede unqualified completion language in historical phase records. The current spec index and full 2026-07-28 changelog were rechecked. Native additions use verified installed SDK APIs, four provider HTTP contracts, and pinned `@opentelemetry/api` 1.10.0 plus `@opentelemetry/sdk-trace` 3.0.0. The latter replaces the older split trace packages; the lesson uses explicit host spans. The exact lockfile is the reproducible record.

[Post-review CI](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41135048577) passed all 28 required jobs on `723eb3b`, with no repair or rerun. CI logs confirm 250 Python tests and 233 standalone examples; TypeScript has 124 tests, Inspector covers 78 advertised catalogs, and browser acceptance has three scenarios. The local external-link sweep found zero failures.

The subsequent [native application implementation and acceptance record](TYPESCRIPT_APPLICATIONS_VERIFICATION.md) addresses the B1 gateway/Chat Pro parity finding. The [packaging follow-up](PACKAGING_ADVISORY_VERIFICATION.md) removes the MCPB/Zod build dependency that caused R-010. No paid model call or public package publication was performed.

The native parity follow-up is complete: [all 29 required CI jobs passed](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41155958759) on `2eb17e9`. It includes 132 TypeScript tests, the same three browser scenarios against the native backend, and actual Keycloak PKCE/scope-step-up acceptance for the Node gateway and its five native upstream processes. R-009 is closed; the linked record documents CI repairs and local platform limits.

The packaging follow-up is complete: [all 29 required CI jobs passed](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41161721989) on `1224c45`, without repair or rerun. R-010 is closed by removing the vulnerable MCPB/Zod dependency. The native suite now has 154 tests (one Windows-only skip), both MCPB bundles launch outside the checkout, and the high/critical audit gate passes. The [packaging record](PACKAGING_ADVISORY_VERIFICATION.md) distinguishes the 13 separate moderate dependency findings from the resolved advisory.

## Phase 8 — complete course, October 30, 2026

Course 1.0.0 adds the full TypeScript route, four native SDKs, five capstones and final references. [Phase 8 evidence and explicit limits](PHASE_8_VERIFICATION.md) supersede delivery-status statements in historical sections below. [Native pins](../modules/bonus/B2_other_sdks/VERSIONS.md) distinguish Java compatibility from current-revision support. TypeScript uses Agents SDK 0.21.0, LangGraph 1.5.3 and LangChain core 1.3.2 with deterministic model fixtures. PDF regeneration pins ReportLab 5.1.0 in the optional docs group.

Substitutions: the installed Python machine providers take singular `scope`; TypeScript StreamableHTTPClientTransport is exported from the main client package; high-level TS task-result validation requires the documented raw-receiver fallback. [B4](../modules/bonus/B4_whats_new/README.md) records current extension maturity and Server Card prototype caveats; [host setup](HOST_SETUP.md) records the four checked configuration formats.

## Phase 6 — Tier 4, October 30, 2026

Course 0.6.0 retains MCP 2026-07-28, official Python SDK 2.3.0 and TypeScript
SDK 2.4.0. MCP Apps uses `@modelcontextprotocol/ext-apps==2.0.4`, bundled with
esbuild 0.28.2. The official Python SDK provides extension hooks and Apps; its
installed release has no Tasks receiver. The teaching receiver implements the
[released Tasks schema](https://github.com/modelcontextprotocol/ext-tasks/blob/main/schema/2026-07-28/schema.ts)
through those hooks, with `tasks/get`, `tasks/update` and `tasks/cancel`.

The [official inventory](https://modelcontextprotocol.io/extensions/overview)
lists Tasks as Beta, to Core, and Apps as Stable. These maturity labels are
separate from the released revision's frozen wire format. This course does not
teach the older `tasks/result`/`tasks/list` generation as current protocol.

### Dependencies and compatibility

[Framework versions and APIs](../frameworks/README.md) include OpenAI Agents
0.24.0, LangGraph 1.2.18/LangChain 1.4.7, Strands 1.62.0, Pydantic AI 2.63.0,
Google ADK 2.13.0 and Claude Agent SDK 0.2.175. Independent uv locks isolate
Strands' MCP <2.2 requirement and ADK's telemetry <=1.44 requirement. The main
server keeps SDK 2.3.0 and OpenTelemetry 1.45.2. Current LangChain MCPAdapter
(beta) replaces the requested legacy adapter package, which requires MCP <2.
Third-party FastMCP is an internal client dependency, not the course server API.

Remote API request constructors follow official
[OpenAI Responses](https://developers.openai.com/api/docs/guides/tools-connectors-mcp),
[Anthropic MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector)
and [Gemini Interactions](https://ai.google.dev/gemini-api/docs/function-calling)
documentation. Their tool definitions are checked against installed SDK schemas;
Gemini's allowlist uses configuration objects containing tool names. Explicit
`--live` calls require a reviewed public HTTPS endpoint and model credentials.
No live provider calls were made. OpenAI approval requests are not auto-approved.

### Local evidence

- Full Windows Python 3.12 suite: 169 passed, one symlink-permission skip; the
  subsequent provider-schema and completed-tool-error regressions are recorded
  with publication results below. All 107 delivered entry points passed.
- TypeScript compiler, ESLint and 36 tests passed, including the official App
  bridge handshake, tool data, refresh allowlist and teardown.
- Three actual framework runtimes complete the same two-tool workflow without
  model keys. Strands and ADK invoke real tools from isolated environments;
  Claude's bundled CLI establishes its real MCP connection without a model query.
- The redesigned catalog exposes six tools versus 25. The deterministic runner
  completes six of six read cases in each catalog. This measures plumbing and
  catalog size, not a model accuracy improvement or billed token usage.
- Gateway tests cover subject/scope-separated caches, runtime revocation, schema
  validation, per-principal rate limits, upstream failure isolation and cleared
  incoming context. A real loopback OAuth/PKCE test checks audience and Origin.
- Tasks persist handles before returning them, scope reads to owners, resume
  working jobs after restart, validate input responses, expire results and cancel
  pending jobs. The SQLite receiver supports one process, not distributed workers.
- Actual stdio captures include catalog/extension metadata, task handles, polling,
  input updates, completion, cancellation and the complete bundled App resource.
- [Host matrix](PHASE_6_HOST_MATRIX.md) distinguishes documented support from
  tested behavior. No desktop rendering, browser sandbox enforcement, production
  multi-tenant deployment or paid-model quality result is claimed.

### Phase 6 publication

Implementation commit `f5d1fc2e63e40a2a4e262a9fa7441bcf279540df` passed
[all 18 required CI jobs](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41088110387):
seven Python jobs (Linux/Windows 3.12–3.14 and macOS 3.12), four TypeScript jobs
(Linux/Windows Node 24 and 26), four isolated Strands/ADK jobs (Linux/Windows),
Inspector, Keycloak and container isolation. The optional external-link job was
skipped.

- Linux Python 3.13 reports **172 tests passed**, **107 delivered examples**
  checked (29 servers, 78 scripts), and the Tier 4 checkpoint passed. All seven
  Python jobs passed the same course/example/checkpoint workflow.
- TypeScript reports **36 tests passed**, including the official App bridge.
- Native Strands and ADK adapters passed from their isolated locks on both OSes.
  Inspector passed every delivered server, including the four Tier 4 entry points.
- Final local focused tests: **17 passed** after strict report-argument validation
  and provider-schema checks were added. The full local diagnostic rerun passed
  170 tests with one Windows symlink-permission skip before the final tool-error
  regression; the final implementation's complete suite is established by CI.
- The local Tier 4 checkpoint, refreshed actual captures, and isolated ADK/Strands
  checks passed. Ruff, formatting and local course/link validation passed.
- Desktop rendering and sandbox enforcement, paid model runs, and production
  deployment remain the explicit manual/live boundaries documented above.

This documentation-only publication records the tested implementation without
changing it. Modules 18–21, bonus tracks and capstones remain planned.


## Phase 5 — Tier 3, October 30, 2026

Modules 11–13 retain MCP **2026-07-28**, Python SDK **2.3.0**, and the existing
TypeScript **2.4.0** companions. Course package version: **0.5.0**. The previously
locked PyJWT/cryptography and OpenTelemetry extras supply auth and tracing.

### Implementation and local evidence

- Real loopback HTTP tests exercise the SDK OAuth client, metadata discovery,
  S256 PKCE, state/issuer binding, one-use codes, resource indicators, scope
  step-up, and token signature/audience/expiry checks. Resource-server tests
  use SDK bearer middleware plus a body-derived write scope gate.
- Keycloak **26.8.1** remains the preferred identity provider, with an imported
  pre-registered public client and resource-indicator configuration. A separate
  synthetic authority supports offline failure tests; it has no real login.
  [Keycloak's MCP guide](https://www.keycloak.org/securing-apps/mcp-authz-server)
  documents the experimental resource-indicator and CIMD features.
- Security tests reproduce the fake salary leak and verify the repair, detect
  catalog changes, reject injected host routes, constrain URL/command choices,
  and check minimal audit records. A dedicated container configuration runs the
  repaired server unprivileged, read-only and without a network.
- The SDK trace example verifies shared trace IDs and error spans. Actual stdio
  captures include trace context. Semantic wire snapshots preserve call inputs
  and result/error payloads while excluding IDs, timing and metadata.
- The bounded load example completed 20 requests at concurrency 4 with no errors.
  Latencies include discovery and connection setup and are not a capacity claim.
  The deterministic evaluation scores 30/30 homogeneous issue-read fixtures;
  a bad selector scores 0/30. An explicit `--live` mode evaluates real model
  proposals without executing them; it has not been run against a live provider.
- Local Windows/Python 3.12 focused checks: **32 passed**. TypeScript compiler,
  ESLint and **35 tests** passed. Ruff, formatting, local links, lesson structure
  and the Tier 3 checkpoint passed. The separate loopback-cookie boundary
  regression also passed. Full-suite supported-OS evidence appears below.
- Docker CLI is installed locally, but its configured daemon is unavailable.
  Keycloak/container runtime validation therefore runs in dedicated Linux CI.
  No host GUI, browser-login UI, external collector or paid model call is claimed.
  The previously documented Windows Inspector HTTP shutdown issue remains a
  limitation; Linux Inspector tests authenticated and ordinary HTTP.

### Phase 5 publication

Implementation commit `60fe1526f8b96b79b20dab15c93160113087d417` passed
[all 14 required CI jobs](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41072129372):
seven Python jobs (Windows/Linux 3.12–3.14 and macOS 3.12), four TypeScript jobs
(Windows/Linux Node 24 and 26), Inspector, Keycloak, and container isolation.
The optional external-link job was skipped.

- Linux Python 3.12 reports **143 tests passed**, **86 delivered examples**
  checked (25 servers and 61 scripts), and the Tier 3 acceptance checkpoint
  passed. TypeScript reports **35 tests passed**.
- The real Keycloak run passed discovery, PKCE, resource audience validation,
  SDK scope step-up and a confirmed write. The realm explicitly includes the
  subject mapper required by strict token validation. Its headless browser
  cookie policy permits Secure cookies only at the exact local fixture origin,
  `http://127.0.0.1:8080`; a regression test rejects other hosts and ports.
- The repaired server passed inside an unprivileged, read-only container with
  networking disabled. The image uses `python:3.12.13-slim-bookworm` and installs
  pinned `uv==0.13.6`. Linux Inspector passed the delivered server inventory,
  including the authenticated Module 11 server.
- GUI host login, an external telemetry collector, and the optional live-model
  evaluation remain manual checks. Subsequent documentation-only publication
  records this CI result without changing the tested implementation.

## Phase 4 — Tier 2, October 30, 2026

Modules 07–10 use the same pinned **MCP 2026-07-28**, **Python SDK 2.3.0**,
and **TypeScript SDK 2.4.0**. The course package version is **0.4.0**. No SDK
or framework migration was needed; the previously locked HTTP extra supplies
FastAPI, Starlette, and Uvicorn. The npm lock adds the Module 10 workspace.

### Implementation evidence

- Issues use an in-memory SQLite backup of a read-only fixture, parameterized
  statements, explicit transactions, validated input, and confirmed writes.
  Receipt records prevent duplicate insertion and survive deletion; IDs are
  not reused during the application lifetime. Analytics has fixed SQL, bound
  parameters, row limits, an execution deadline, and resource pagination links.
- Lifespan owns the connection. Database handlers are async so the SDK does not
  dispatch a shared SQLite connection onto a worker thread. Reports check
  progress, cancellation, cleanup, and completion. The quarter is explicitly a
  simulated report label, not a date filter.
- Elicitation uses input-required results and retries. Clients advertise form
  and URL support. The server verifies exact arguments, strict input, expiry,
  one-use state, and actual out-of-band URL completion. The local grant ledger
  assumes one OS user; remote principal binding belongs to authorization work.
  Human response time is outside each bounded network request.
- Lumen Chat v2 runs the existing explicit model/tool loop with a separate human
  input adapter. Fake fixtures approve only published exact actions. Live
  provider helpers are unchanged; optional file generation requires separate
  consent and a configured canonical path boundary.
- Python ASGI and TypeScript HTTP are tested through real loopback requests.
  Tests cover JSON and SSE, mirrored method/name/custom headers, Unicode header
  encoding, Host/Origin rejection, CORS, progress cancellation, subscription
  reissue/refetch, and duplicate writes. TypeScript shares its database and event
  bus outside the per-request factory. Multi-worker persistence is explained,
  not claimed as deployed.
- Current captures live in the four module wire folders. Historical sampling
  and roots traffic is generated by the isolated fake fixture embedded only in
  the [migration guide](MIGRATING_FROM_OLDER_VERSIONS.md). No live model was called.

Primary references checked: [input retries](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/mrtr),
[elicitation capabilities](https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation),
[HTTP and header binding](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http),
[Python header parameters](https://py.sdk.modelcontextprotocol.io/advanced/header-parameters/),
and [Open-Meteo parameters](https://open-meteo.com/en/docs). Installed SDK sources
were checked against these references. Host formats were rechecked using the
sources in [host setup](HOST_SETUP.md).

### Local validation

- Windows Python 3.12: **109 passed, 1 skipped** in the full suite; the skip is the
  OS account's symlink-creation permission. After the final receipt and capture
  changes, **39 targeted tests passed**.
- TypeScript: type checking, ESLint, and **35 tests passed** on Node 24.18.
  All three Module 10 TypeScript exercise solutions pass their shared contracts.
- Ruff, formatting, course completeness, local links, Tier 2 capture scenarios,
  and the historical fake capture pass. The manifest contains **71 runnable
  examples**: 22 servers and 49 scripts, exercised by the repository smoke test.
- Inspector 2.13 lists the stdio services locally. Its HTTP CLI crashes on this
  Windows/Node 24 installation with a libuv closing-handle assertion. Both HTTP
  servers pass the independent SDK harness, and Linux Inspector CI passes for
  both implementations. The local Windows Inspector crash remains documented.
- No live provider calls, external weather request, third-party host GUI session,
  or public HTTP deployment was performed. These are not implied by offline tests.

### CI result

[Phase 4 CI run](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41017169749)
passed all **12 required jobs** for implementation commit
`333d03a2a6e09d553ac6e37ba035c8bd6972dda7`:

- Seven Python jobs: Windows/Linux 3.12–3.14, plus macOS 3.12.
- Four TypeScript jobs: Windows/Linux Node 24 and 26.
- Linux Inspector: every manifest server, including both HTTP implementations,
  plus the isolated security fixture and filesystem reference server.

CI logs confirm **110 Python tests**, **35 TypeScript tests**, **71 runnable
examples**, and both Tier 1 and Tier 2 scenarios passing. CI's Windows account can
create symlinks, so its suite has no local-account skip. External link checks are
manual-only and were skipped on this push; local links passed. A subsequent
documentation-only commit records this evidence and aligns lesson time estimates.
Phase 4 is complete; modules 11–21 and later-phase material remain planned.

## Phase 3 — Tier 1, October 30, 2026

Modules 00–06 target the same **2026-07-28** revision and locked Python SDK
**2.3.0** / split TypeScript SDK **2.4.0**. The added official filesystem
reference package is pinned to **2.1.0**, verified against its npm metadata and
[maintained source](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem).
No framework dependency was introduced. JSON Schema validation moved from the
development group into runtime dependencies because the host validates tool calls.

### APIs checked and substitutions made

- Python uses `MCPServer`, `mcp_types`, typed tool/resource/prompt decorators,
  `Context` notifications, `Client.listen`, and completion references. Sources:
  [subscriptions](https://py.sdk.modelcontextprotocol.io/handlers/subscriptions/),
  [completions](https://py.sdk.modelcontextprotocol.io/servers/completions/), and
  the installed 2.3.0 API signatures and implementations.
- High-level Python prompts must return `UserMessage` from
  `mcp.server.mcpserver.prompts.base`, or supported message dictionaries.
  Returning a wire `PromptMessage` object caused stringification. Regression
  tests and Python/TypeScript parity checks now verify embedded resource blocks.
- Expected Python tool failures raise `ToolError`, so the user receives actionable
  text. Arbitrary exceptions are masked by the SDK; expected failures should not
  be implemented as accidental crashes.
- A Python client pinned with `mode="2026-07-28"` skips discovery. The explicit
  helper calls `session.send_discover` and adopts the validated `DiscoverResult`
  before inspecting capability flags. This is a discovery request, not a session
  handshake. Both SDK tracks exercise it in current-revision captures.
- TypeScript uses `serveStdio`, `z.object`, `completable`, literal notification
  method names, and `versionNegotiation`. Its resource server explicitly declares
  `resources.subscribe`; otherwise a resource update filter is not honored.
  These APIs were checked in the installed 2.4.0 declarations and runtime source.
- Inspector **2.13.0** defaults ad-hoc connections to an older mode. The smoke
  runner passes **`--protocol-era modern`**, verified in CLI help and source.
  All 13 delivered server entry points pass the applicable list operations.
- The low-level pagination server uses the public v2 runner metadata parameter
  described in the [migration guide](MIGRATING_FROM_OLDER_VERSIONS.md). Its real
  capture demonstrates an empty intermediate page and a terminal cursor.

### Provider and host verification

All models are still configured through `common/llm.py` and `.env`; fake mode is
the default. Offline adapter tests verify tool envelopes, result IDs, denial
results, native OpenAI/Anthropic history, Gemini thought-signature preservation,
disabled automatic execution, and Ollama tool messages. Sources checked:

- [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling)
- [Anthropic tool-call handling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls)
- [Gemini Generate Content function calling](https://ai.google.dev/gemini-api/docs/generate-content/function-calling)
- [Gemini thought signatures](https://ai.google.dev/gemini-api/docs/generate-content/thought-signatures)
- [Ollama tool calling](https://github.com/ollama/ollama/blob/main/docs/capabilities/tool-calling.mdx)

Gemini's supported Generate Content interface is retained for consistency with
the existing helper; Google now labels those documentation pages Legacy relative
to its Interactions API. This is a provider API designation, not an MCP revision.
Live provider behavior, account permissions, model availability and cost are not
certified by the offline fixtures.

[Host setup](HOST_SETUP.md) records four official configuration formats and their
verification limits. Configs are generated with this machine's absolute paths and
must be regenerated in another checkout. No interactive third-party host UI or
live model call was performed. Learners verify the module 00 two-host chat step.

### Local evidence

- Seven module scenarios pass through actual stdio processes; **20 captures**
  include requests, responses, errors, acknowledgements and change notifications.
- The runner inventories **13 server entry points and 34 executable scripts**.
  It includes both language tracks and the three-server fake Chat checkpoint.
- **79 Python tests passed, one Windows symlink-permission skip**, in the final
  local suite; **33 TypeScript tests passed**. Ruff, formatting, TypeScript
  compilation, ESLint, local links and delivered-course checks pass.
- The Python/TypeScript parity tests compare note state, rich content bytes and
  embedded prompt messages, rather than merely checking that processes start.
- The notification CLI's explicit `--watch-once --confirm-demo-write` path passes
  in both languages and prints the refetched bulletin. Denial does not update it.
- A full external-link sweep is not claimed. The release coverage gate still
  intentionally fails because later tiers are planned.

### Published Phase 3 and CI

Implementation commit `01f462b4f0fba2c0492674318d15bbf0f6ac6a08` passed
[the complete Phase 3 CI run](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41011844541).
All seven Python jobs passed (Windows/Linux 3.12–3.14 and macOS 3.12), all four
TypeScript jobs passed (Windows/Linux Node 24/26), and Inspector passed.
Linux Python 3.14 ran **80 tests with no skips**, including the symlink boundary
case. Every Python job also ran the full example runner and seven Tier 1 scenarios.
The external-link job is intentionally manual and was skipped. The final
documentation-only commit records these results without rerunning unchanged code.

---

Checked: **October 29, 2026, America/Chicago**. Phase 1 records source verification, not installation or runtime certification.

## Specification baseline

The [stable specification entry point](https://modelcontextprotocol.io/specification) resolves to **2026-07-28**. Read the complete [Key Changes page](https://modelcontextprotocol.io/specification/2026-07-28/changelog), including minor changes, deprecated features, schema and governance updates.

Key changes affecting this course: self-contained requests carry version/capability metadata; discovery replaces connection setup. Subscription streams replace previous subscription operations. Results identify completion versus further input. Retry exchanges carry requested input. Tasks move into an extension. HTTP uses method/name headers; response-stream recovery requires a new request. Cache hints accompany eligible results. Schemas allow richer JSON Schema and structured content. Authorization binds credentials to issuers and validates returned issuer information. Roots, sampling, protocol logging, the older HTTP transport and dynamic registration are deprecated. Revised error allocation and feature lifecycle rules also matter. These changes determine the current track; historical behavior belongs in the migration guide.

Read the [schema](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/schema/2026-07-28/schema.ts) alongside the prose when implementing. Do not confuse SDK convenience methods with protocol methods.

## Verified release candidates

Versions below were read directly from PyPI JSON metadata and npm registry `latest` metadata. Links identify the exact inspected release. Proposed Python ranges permit patch updates within the selected minor; npm uses tilde ranges. Exact resolved versions go into lockfiles. Date-versioned reference servers and the MCP types companion are exact pins. Compatibility among all rows has **not** been resolved yet.

| Python package | Observed version | Proposed requirement | Role | Source |
|---|---|---|---|---|
| `mcp[cli]` | 2.3.0 | `mcp[cli]>=2.3.0,<2.4.0` | core | [PyPI](https://pypi.org/pypi/mcp/2.3.0/json) |
| `mcp-types` | 2.3.0 | `mcp-types==2.3.0` | core: exact SDK companion | [PyPI](https://pypi.org/pypi/mcp-types/2.3.0/json) |
| `httpx2` | 2.16.0 | `httpx2>=2.16.0,<2.17.0` | core HTTP | [PyPI](https://pypi.org/pypi/httpx2/2.16.0/json) |
| `pydantic` | 2.14.2 | `pydantic>=2.14.2,<2.15.0` | core | [PyPI](https://pypi.org/pypi/pydantic/2.14.2/json) |
| `python-dotenv` | 1.2.4 | `python-dotenv>=1.2.4,<1.3.0` | core | [PyPI](https://pypi.org/pypi/python-dotenv/1.2.4/json) |
| `jsonschema` | 4.26.0 | `jsonschema>=4.26.0,<4.27.0` | dev/contracts | [PyPI](https://pypi.org/pypi/jsonschema/4.26.0/json) |
| `rich` | 15.0.0 | `rich>=15.0.0,<15.1.0` | core output | [PyPI](https://pypi.org/pypi/rich/15.0.0/json) |
| `httpx` | 0.28.1 | `httpx>=0.28.1,<0.29.0` | optional provider/REST compatibility | [PyPI](https://pypi.org/pypi/httpx/0.28.1/json) |
| `starlette` | 1.10.0 | `starlette>=1.10.0,<1.11.0` | HTTP | [PyPI](https://pypi.org/pypi/starlette/1.10.0/json) |
| `fastapi` | 0.162.0 | `fastapi>=0.162.0,<0.163.0` | HTTP and web host | [PyPI](https://pypi.org/pypi/fastapi/0.162.0/json) |
| `uvicorn` | 0.54.0 | `uvicorn>=0.54.0,<0.55.0` | HTTP | [PyPI](https://pypi.org/pypi/uvicorn/0.54.0/json) |
| `aiosqlite` | 0.22.1 | `aiosqlite>=0.22.1,<0.23.0` | data | [PyPI](https://pypi.org/pypi/aiosqlite/0.22.1/json) |
| `pypdf` | 6.21.4 | `pypdf>=6.21.4,<6.22.0` | data | [PyPI](https://pypi.org/pypi/pypdf/6.21.4/json) |
| `anthropic` | 2.3.0 | `anthropic>=2.3.0,<2.4.0` | host | [PyPI](https://pypi.org/pypi/anthropic/2.3.0/json) |
| `openai` | 3.41.0 | `openai>=3.41.0,<3.42.0` | host | [PyPI](https://pypi.org/pypi/openai/3.41.0/json) |
| `google-genai` | 2.34.0 | `google-genai>=2.34.0,<2.35.0` | host | [PyPI](https://pypi.org/pypi/google-genai/2.34.0/json) |
| `ollama` | 0.6.3 | `ollama>=0.6.3,<0.7.0` | host | [PyPI](https://pypi.org/pypi/ollama/0.6.3/json) |
| `pyjwt[crypto]` | 2.15.1 | `pyjwt[crypto]>=2.15.1,<2.16.0` | auth | [PyPI](https://pypi.org/pypi/pyjwt/2.15.1/json) |
| `opentelemetry-sdk` | 1.45.2 | `opentelemetry-sdk>=1.45.2,<1.46.0` | observability | [PyPI](https://pypi.org/pypi/opentelemetry-sdk/1.45.2/json) |
| `opentelemetry-exporter-otlp` | 1.45.2 | `opentelemetry-exporter-otlp>=1.45.2,<1.46.0` | observability | [PyPI](https://pypi.org/pypi/opentelemetry-exporter-otlp/1.45.2/json) |
| `openai-agents` | 0.24.0 | `openai-agents>=0.24.0,<0.25.0` | frameworks | [PyPI](https://pypi.org/pypi/openai-agents/0.24.0/json) |
| `langchain-mcp-adapters` | 0.3.2 | `langchain-mcp-adapters>=0.3.2,<0.4.0` | frameworks | [PyPI](https://pypi.org/pypi/langchain-mcp-adapters/0.3.2/json) |
| `langgraph` | 1.2.18 | `langgraph>=1.2.18,<1.3.0` | frameworks | [PyPI](https://pypi.org/pypi/langgraph/1.2.18/json) |
| `strands-agents` | 1.62.0 | `strands-agents>=1.62.0,<1.63.0` | frameworks | [PyPI](https://pypi.org/pypi/strands-agents/1.62.0/json) |
| `pydantic-ai` | 2.63.0 | `pydantic-ai>=2.63.0,<2.64.0` | frameworks | [PyPI](https://pypi.org/pypi/pydantic-ai/2.63.0/json) |
| `google-adk` | 2.13.0 | `google-adk>=2.13.0,<2.14.0` | frameworks | [PyPI](https://pypi.org/pypi/google-adk/2.13.0/json) |
| `claude-agent-sdk` | 0.2.175 | `claude-agent-sdk>=0.2.175,<0.3.0` | frameworks | [PyPI](https://pypi.org/pypi/claude-agent-sdk/0.2.175/json) |
| `pytest` | 9.2.0 | `pytest>=9.2.0,<9.3.0` | dev | [PyPI](https://pypi.org/pypi/pytest/9.2.0/json) |
| `anyio` | 4.15.1 | `anyio>=4.15.1,<4.16.0` | core/tests | [PyPI](https://pypi.org/pypi/anyio/4.15.1/json) |
| `ruff` | 0.17.3 | `ruff>=0.17.3,<0.18.0` | dev | [PyPI](https://pypi.org/pypi/ruff/0.17.3/json) |
| `pre-commit` | 4.7.0 | `pre-commit>=4.7.0,<4.8.0` | dev | [PyPI](https://pypi.org/pypi/pre-commit/4.7.0/json) |
| `uv` | 0.13.6 | `uv>=0.13.6,<0.14.0` | installer | [PyPI](https://pypi.org/pypi/uv/0.13.6/json) |
| `mcp-server-fetch` | 2026.10.28 | `mcp-server-fetch==2026.10.28` | reference candidate | [PyPI](https://pypi.org/pypi/mcp-server-fetch/2026.10.28/json) |
| `mcp-server-git` | 2026.10.28 | `mcp-server-git==2026.10.28` | reference candidate | [PyPI](https://pypi.org/pypi/mcp-server-git/2026.10.28/json) |
| `mcp-server-time` | 2026.10.28 | `mcp-server-time==2026.10.28` | reference candidate | [PyPI](https://pypi.org/pypi/mcp-server-time/2026.10.28/json) |

| npm package | Observed version | Proposed range | Source |
|---|---|---|---|
| `@modelcontextprotocol/server` | 2.4.0 | `~2.4.0` | [npm registry](https://registry.npmjs.org/@modelcontextprotocol/server/2.4.0) |
| `@modelcontextprotocol/client` | 2.4.0 | `~2.4.0` | [npm registry](https://registry.npmjs.org/@modelcontextprotocol/client/2.4.0) |
| `@modelcontextprotocol/core` | 2.4.0 | `~2.4.0` | [npm registry](https://registry.npmjs.org/@modelcontextprotocol/core/2.4.0) |
| `@modelcontextprotocol/node` | 2.1.2 | `~2.1.2` | [npm registry](https://registry.npmjs.org/@modelcontextprotocol/node/2.1.2) |
| `@modelcontextprotocol/inspector` | 2.13.0 | `~2.13.0` | [npm registry](https://registry.npmjs.org/@modelcontextprotocol/inspector/2.13.0) |
| `@modelcontextprotocol/ext-apps` | 2.0.4 | `~2.0.4` | [npm registry](https://registry.npmjs.org/@modelcontextprotocol/ext-apps/2.0.4) |
| `@modelcontextprotocol/server-filesystem` | 2.1.0 | `~2.1.0` | [npm registry](https://registry.npmjs.org/@modelcontextprotocol/server-filesystem/2.1.0) |
| `@modelcontextprotocol/server-memory` | 2.0.1 | `~2.0.1` | [npm registry](https://registry.npmjs.org/@modelcontextprotocol/server-memory/2.0.1) |
| `zod` | 4.6.7 | `~4.6.7` | [npm registry](https://registry.npmjs.org/zod/4.6.7) |
| `tsx` | 4.23.15 | `~4.23.15` | [npm registry](https://registry.npmjs.org/tsx/4.23.15) |
| `vitest` | 5.0.5 | `~5.0.5` | [npm registry](https://registry.npmjs.org/vitest/5.0.5) |
| `typescript` | 7.0.2 | `~7.0.2` | [npm registry](https://registry.npmjs.org/typescript/7.0.2) |
| `eslint` | 10.13.0 | `~10.13.0` | [npm registry](https://registry.npmjs.org/eslint/10.13.0) |
| `typescript-eslint` | 8.72.1 | `~8.72.1` | [npm registry](https://registry.npmjs.org/typescript-eslint/8.72.1) |
| `@eslint/js` | 10.0.1 | `~10.0.1` | [npm registry](https://registry.npmjs.org/@eslint/js/10.0.1) |
| `@types/node` | 26.6.6 | `~26.6.6` | [npm registry](https://registry.npmjs.org/@types/node/26.6.6) |

The requested `@modelcontextprotocol/sdk` is published at **1.32.2**, but the [official repository](https://github.com/modelcontextprotocol/typescript-sdk) identifies it as the v1 maintenance line. The stable current-spec implementation uses `@modelcontextprotocol/server` and `@modelcontextprotocol/client` instead. This is a deliberate package substitution, following the request to use confirmed current alternatives. [v2 migration guide](https://ts.sdk.modelcontextprotocol.io/v2/migration/upgrade-to-v2).

Node **26.13.0** is the observed current LTS release (Lithium); Node 24 is also an LTS line. Recommend 26 and test both 24 and 26. [Release schedule](https://nodejs.org/en/about/previous-releases), [release metadata](https://nodejs.org/dist/index.json).

The SDK's top-level Python metadata permits 3.10+, but its current HTTP dependency requires 3.11+. Recommend 3.12; propose CI for 3.12–3.14, and verify all selected extras before making a support promise. Framework packages are optional and may need independent environments. Latest releases alone do not establish mutual compatibility.

## Confirmed APIs and intentional substitutions

| Area | Confirmed documentation evidence | Implementation decision |
|---|---|---|
| Python server | [Python SDK](https://py.sdk.modelcontextprotocol.io/) documents `from mcp.server import MCPServer` | Use v2 server and decorators |
| Python client | [Client guide](https://py.sdk.modelcontextprotocol.io/client/) documents `Client` | Same client abstraction for transport and in-memory tests |
| In-memory tests | [Testing guide](https://py.sdk.modelcontextprotocol.io/get-started/testing/) documents `Client(server, raise_exceptions=True)` | Offline unit tests; separate transport tests prove serialization |
| HTTP library and models | [Migration guide](https://py.sdk.modelcontextprotocol.io/migration/) moves HTTP integration to `httpx2` and models to `mcp_types` | Avoid importing compatibility aliases |
| Run configuration | [Running servers](https://py.sdk.modelcontextprotocol.io/run/) and migration guide place transport settings on run operations | Verify exact method signatures from the installed release |
| TypeScript | [Official SDK README](https://github.com/modelcontextprotocol/typescript-sdk) shows `McpServer`, `registerTool`, and stdio exports in split packages | Use v2 imports and Zod 4 |
| Inspector automation | [CLI guide](https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector/cli) documents CLI methods for tools/resources/templates/prompts | Pin Inspector; use CLI for independent smoke calls |
| Deprecated client features | [Sampling and roots guide](https://py.sdk.modelcontextprotocol.io/handlers/sampling-and-roots/) | Explain compatibility; use explicit directories and provider calls for new applications |

The `mcp` 2.3.0 registry metadata confirms the `cli` extra and `mcp-types==2.3.0` dependency. Some documentation examples still use old model import aliases; the migration guide takes precedence until release-specific imports are tested. No unsupported signatures are invented in Phase 1.

## Extension inventory

The [official extension index](https://modelcontextprotocol.io/extensions/overview) currently lists these six extensions. Distinguish extension maturity from the core specification's stable status. Snapshot the exact extension revision/commit before implementation, especially for Beta extensions.

| Extension | Listed stage | Course location | Primary source |
|---|---|---|---|
| MCP Apps | Stable | 17, 21, Ops and Chat Pro | [Apps](https://modelcontextprotocol.io/extensions/apps/overview) |
| Tasks | Beta, intended for Core | 17, 21, Ops | [Tasks](https://modelcontextprotocol.io/extensions/tasks/overview) |
| Skills over MCP | Beta | B4 | [Skills](https://modelcontextprotocol.io/extensions/skills/overview) |
| Server Cards | Beta | 19, B4 | [Server Cards](https://modelcontextprotocol.io/seps/2127-mcp-server-cards) |
| OAuth Client Credentials | Stable | 11/B4 | [Client credentials](https://modelcontextprotocol.io/extensions/auth/oauth-client-credentials) |
| Enterprise-Managed Authorization | Stable | 11/B4 | [Enterprise authorization](https://modelcontextprotocol.io/extensions/auth/enterprise-managed-authorization) |

The extension index specifies capability advertisement per request and server discovery for the current revision. Its guidance supersedes stale initialization wording on the general specification overview.

## Verification still required

- Resolve and install the proposed dependency sets, then confirm exact APIs against each pinned release. Check TypeScript/ESLint peer compatibility and Python framework dependency conflicts.
- Check and test four host configurations: Claude Desktop, Claude Code, VS Code and Cursor. No host support matrix has been certified.
- Confirm every framework integration and remote model API feature before module 15. A published package version is not proof of current-protocol compatibility.
- Verify hosted low-cost model IDs and an Ollama model before writing `.env.example`; do not infer availability from SDK versions.
- Verify Keycloak image version, authorization-server configuration and compatibility with Client ID Metadata Documents. If necessary, use documented pre-registration for the local provider and teach metadata documents separately.
- Confirm OpenTelemetry semantic-convention status, exporter compatibility, and trace-context fields before module 13; do not label draft conventions stable.
- Check repository maintenance and inspect reference-server tools before using the fetch/git/time/filesystem/memory candidates. Recent registry releases are evidence of publication, not a security assessment.
- Verify desktop bundle format and supported hosts; registry publisher/version/schema; cloud deployment offerings; official SDK status for Go/C#/Java/Kotlin/Rust.
- Pin extension revisions and app integration APIs before module 17/B4.
- Run all code, capture actual exchanges and exercise host UIs in implementation phases.

## Phase 1 checks performed

Read the supplied request and inspected the empty workspace. Read the full stable changelog. Checked primary SDK documentation and migration guides, the Inspector CLI documentation, extension inventory, runtime releases and package registries. Registry access succeeded after using the available external-network execution path.

No application code, tests, linters, installs, Inspector sessions, wire captures, CI jobs or GitHub publication were run. There are no implementation pass claims in this document.

## Phase 2 implementation evidence

The paragraph above describes Phase 1 only. Phase 2 adds runnable foundation code, committed data, real lockfiles and validation.

### Dependency resolution

Python resolution succeeded for the core and all four optional extras (host, HTTP, auth and observability), including 88 installed dependencies on Python 3.12.13. `uv.lock` is the exact resolved record. Framework dependencies remain deferred until module 15 so they cannot silently constrain the core environment.

The first npm resolution correctly rejected TypeScript 7.0.2: `typescript-eslint` 8.72.1 declares a compiler peer range below 6.1. The implementation uses **TypeScript 6.0.3**, verified from the [npm registry](https://registry.npmjs.org/typescript/6.0.3), with the previously checked ESLint versions. No force/legacy-peer override was used. The npm lock contains the successful resolution; installation reported no known vulnerabilities. Hatchling **1.33.0** was verified from [PyPI](https://pypi.org/pypi/hatchling/1.33.0/json) and pinned to its minor range for builds.

### API and model verification

Installed-code inspection confirmed `MCPServer.run`, `tool`, `resource`, `Client`, `StdioServerParameters`, the current revision selector, and `mcp_types.ToolAnnotations` snake-case fields. In-memory and actual subprocess tests exercise these APIs. The foundation server advertises read-only, non-destructive, idempotent, closed-world behavior.

The provider helper currently provides bounded one-shot text generation and a deterministic fake. Module 06 will add tool conversion and multi-turn orchestration. Offline doubles exercise all four provider branches and cleanup; installed-SDK signature checks cover the public API calls. Ollama uses its public async context manager. No paid model request has been made.

The `.env.example` suggestions were checked against provider catalogs on October 29, 2026:

| Provider | Suggested model | Source |
|---|---|---|
| OpenAI | `gpt-6-luna` | [Model page](https://developers.openai.com/api/docs/models/gpt-6-luna) |
| Anthropic | `claude-haiku-5-5` | [Model overview](https://platform.claude.com/docs/en/models/overview) |
| Gemini | `gemini-3.5-flash-lite` | [Model catalog](https://ai.google.dev/gemini-api/docs/models) |
| Ollama | `qwen3:4b` | [Model library](https://ollama.com/library/qwen3) |

These are catalog checks, not proof of account access or local model availability. No model ID is hard-coded into the provider helper; the default is the offline fake.

### Local validation

- Python 3.12.13, Node 24.18.0, npm 11.16.0, uv 0.12.18 on Windows.
- 24 Python tests passed; one symlink test skipped because the account cannot create symlinks. Linux CI must exercise that case.
- Five TypeScript tests passed; compiler, ESLint, ruff and formatting checks passed.
- SDK in-memory tools/resources/prompts checks and real stdio smoke run passed.
- Inspector CLI tools/resources/prompts checks passed, and both wheel and source distribution builds succeeded. The isolated synthetic lab also passes an Inspector tools listing.
- Actual current-revision wire traffic is saved in `docs/wire/foundation_server.jsonl`. The proxy preserves protocol bytes, handles EOF/failure/timeout and redacts capture copies. Captures do not claim to observe HTTP, which arrives in a later tier.
- Data counts, references, PDF text extraction, integrity hashes and repeated regeneration are tested. The generator explicitly closes SQLite connections after committing; Windows exposed and verified that fix.
- Local Markdown links and delivered-file checks passed. The release coverage gate intentionally fails until all 22 modules exist.

No live provider call, complete host UI test, cloud deployment or external-link sweep has been performed. Phase 2 does not claim later module coverage.

### Published repository and CI

Published [anandtopu/getting_started_with_mcp](https://github.com/anandtopu/getting_started_with_mcp). Implementation commit `ed0ba217967394ac2a8ce1bafadb00621b028012` passed [the complete CI run](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41005633590): seven Python jobs (Windows/Linux on 3.12–3.14 and macOS on 3.12), four TypeScript jobs (Windows/Linux on Node 24/26), and Inspector. The external-link job is intentionally manual and was skipped.

Linux Python 3.12 ran **25 tests with no skips**, including the symlink boundary test. Each matrix job sets `UV_PYTHON` explicitly so the checkout's recommended `.python-version` cannot silently change its interpreter. The subsequent documentation-only commit records these outcomes without rerunning the unchanged implementation.

## Phase 7

See [Phase 7 evidence and limitations](PHASE_7_VERIFICATION.md) for packages, registry publisher, deployment and the browser host.
