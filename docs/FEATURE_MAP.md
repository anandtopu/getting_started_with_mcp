# Feature map

Phase 1 coverage contract, October 29, 2026. **All implementation entries below are planned, not complete.** A row closes only when its runnable example, use case, captured exchange, exercises/solutions and tests are delivered. Future paths are code text, not dead links. Replace them with relative links as files land.

The map covers the core protocol, official extension inventory, selected SDK facilities, and the requested application curriculum. It does not imply that every SDK implementation detail is a protocol feature. Framework rows name planned integrations; provider-specific primary API references must be verified and added before implementation.

## Path rules

All paths are relative to the repository root. The example column names a basename:
- Python example: `modules/<module>/python/examples/<basename>.py`.
- For modules 02–05 and 10, TypeScript counterpart: `modules/<module>/typescript/examples/<basename>.ts`.
- Other TypeScript counterparts: `modules/bonus/B1_typescript/<module>/examples/<basename>.ts`.
- Use case: `modules/<module>/python/use_case/main.py` (the named scenario in the table), plus the corresponding TypeScript `use_case/main.ts`.
- Every module supplies `python/exercises/01_practice.py`, `02_apply.py`, `03_stretch.py`, matching solutions, and `python/tests/test_module.py`; TypeScript mirrors these.
- Capture: `modules/<module>/wire/<basename>.jsonl`; its manifest records the exact generating command and dependency versions. Exercises and tests reference those files rather than handwritten transcripts.

## Core curriculum allocation

| Module directory | Example basename | Feature coverage | TypeScript location | Lumen use case | Primary reference |
|---|---|---|---|---|---|
| `00_setup` | `01_ecosystem` | Hosts, clients, servers; N × M integrations; limits of the USB-C analogy; specification, SDKs, Inspector, Registry and governance | B1/00_setup | reference_workspace | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/architecture/index) |
| `00_setup` | `02_environment` | Python, uv, Node and npm checks; venv/pip fallback; PowerShell paths; optional models and Docker | B1/00_setup | reference_workspace | [Reference](https://py.sdk.modelcontextprotocol.io/get-started/) |
| `00_setup` | `03_reference_server` | Restricted filesystem reference server; two host configurations; first chat and captured calls | B1/00_setup | reference_workspace | [Reference](https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-local-servers) |
| `01_architecture_wire` | `01_jsonrpc` | Request IDs, responses, notifications, errors; JSON syntax; unsupported methods and malformed input | B1/01_architecture_wire | annotated_inspector_session | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/index) |
| `01_architecture_wire` | `02_raw_server` | SDK-free stdio server; discovery; per-request version, client capabilities and identity; result discriminator; unsupported-version errors | B1/01_architecture_wire | annotated_inspector_session | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/discover) |
| `01_architecture_wire` | `03_wiretap_client` | Raw requests by hand; byte-preserving wiretap; timing and directions; stdio versus HTTP; explicit state handles | B1/01_architecture_wire | annotated_inspector_session | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/index) |
| `02_first_server_tools` | `01_hello_server` | MCPServer; decorator; tools/list and tools/call; type hints, descriptions, titles, JSON Schema, Pydantic validation | Same module | notes | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) |
| `02_first_server_tools` | `02_rich_results` | Text, image, audio, embedded resources and resource links; structured content; output schemas; schema reference/composition limits | Same module | notes | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) |
| `02_first_server_tools` | `03_errors_approval` | Tool errors versus protocol errors; readOnlyHint, destructiveHint, idempotentHint, openWorldHint; approval-bound writes | Same module | notes | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) |
| `03_resources` | `01_static_resources` | resources/list and resources/read; MIME types, text and binary; metadata and annotations | Same module | wiki | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/resources) |
| `03_resources` | `02_resource_templates` | resources/templates/list; URI templates; wiki space/page routing; resource links from tools | Same module | wiki | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/resources) |
| `03_resources` | `03_resource_changes` | subscriptions/listen; resource change notifications; subscription IDs; cache freshness and scope; tool versus resource | Same module | wiki | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/subscriptions) |
| `04_prompts` | `01_prompt_arguments` | prompts/list and prompts/get; arguments; messages; prompt titles/descriptions; slash-command presentation | Same module | incident_release_meeting | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/prompts) |
| `04_prompts` | `02_embedded_context` | Resource embedding; incident summary, release notes and customer meeting context | Same module | incident_release_meeting | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/prompts) |
| `04_prompts` | `03_prompt_completion` | completion/complete; argument context and suggestions; prompt catalog subscriptions | Same module | incident_release_meeting | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/utilities/completion) |
| `05_first_client` | `01_stdio_client` | Client; process transport; discovery; tools/resources/prompts access; cleanup; async prerequisites | Same module | workspace_query | [Reference](https://py.sdk.modelcontextprotocol.io/clients/) |
| `05_first_client` | `02_pages_and_errors` | Cursor pagination; bounded loops; capability checks; protocol and tool error handling | Same module | workspace_query | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/utilities/pagination) |
| `05_first_client` | `03_cli_and_changes` | Command-line client; multiple servers; notification consumption; cache invalidation | Same module | workspace_query | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/subscriptions) |
| `06_building_a_host` | `01_provider_formats` | LLMs, context windows and tool calling; MCP schema conversion for Anthropic/OpenAI/Gemini/Ollama | B1/06_building_a_host | lumen_chat_v1 | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) |
| `06_building_a_host` | `02_manual_host_loop` | Handwritten model/tool/result loop; tool-call IDs; conversation state; fake provider; bounded turns | B1/06_building_a_host | lumen_chat_v1 | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/architecture/index) |
| `06_building_a_host` | `03_routing_and_approval` | Tool namespaces; multi-server routing; user approvals; refusal, malformed arguments and budgets | B1/06_building_a_host | lumen_chat_v1 | [Reference](https://modelcontextprotocol.io/docs/2026-07-28/develop/clients/client-best-practices) |
| `07_real_data` | `01_issue_crud` | Parameterized issue create/read/update/delete; validated input; transaction boundaries and confirmation | B1/07_real_data | issues_analytics | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) |
| `07_real_data` | `02_readonly_analytics` | Read-only SQLite; query allow-list; row and execution limits; truncation, pagination and resource links | B1/07_real_data | issues_analytics | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/resources) |
| `07_real_data` | `03_rest_wrapper` | REST basics; Open-Meteo opt-in; local internal-API mock; HTTP failures; fake transport tests | B1/07_real_data | issues_analytics | [Reference](https://py.sdk.modelcontextprotocol.io/servers/) |
| `08_server_utilities` | `01_context_lifespan` | Request context; dependency injection; startup/shutdown; database connection lifetime | B1/08_server_utilities | quarterly_report | [Reference](https://py.sdk.modelcontextprotocol.io/handlers/lifespan/) |
| `08_server_utilities` | `02_progress_cancel` | Progress tokens and notifications; cancellation; deadlines; report cleanup | B1/08_server_utilities | quarterly_report | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/progress) |
| `08_server_utilities` | `03_pages_completion` | Server-side cursors; argument completions; bounded results; diagnostic alternatives | B1/08_server_utilities | quarterly_report | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/utilities/pagination) |
| `09_elicitation_sampling_roots` | `01_form_retry` | InputRequiredResult; input requests/responses; request state; form accept/decline/cancel; host and server implementations | B1/09_elicitation_sampling_roots | bulk_close_and_summarize | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/mrtr) |
| `09_elicitation_sampling_roots` | `02_url_retry` | URL-mode elicitation; sensitive out-of-band flows; retry outcome; denial and expiry | B1/09_elicitation_sampling_roots | bulk_close_and_summarize | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation) |
| `09_elicitation_sampling_roots` | `03_files_and_model` | Configured directories and canonical paths; direct provider generation; analyze captured Deprecated roots/sampling exchanges | B1/09_elicitation_sampling_roots | bulk_close_and_summarize | [Reference](https://py.sdk.modelcontextprotocol.io/handlers/sampling-and-roots/) |
| `10_streamable_http` | `01_http_server` | ASGI app; loopback binding; HTTP request/response basics; stateless scaling | Same module | remote_workspace | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http) |
| `10_streamable_http` | `02_headers_and_origin` | Origin validation; DNS rebinding; Host allow-list; CORS; method/name headers; x-mcp-header mapping | Same module | remote_workspace | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http) |
| `10_streamable_http` | `03_stream_recovery` | JSON/SSE response bodies; subscription POST streams; disconnect/reissue; duplicate-write safety; remote clients | Same module | remote_workspace | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http) |
| `11_authorization` | `01_discovery_registration` | OAuth roles; protected-resource and authorization-server metadata; Client ID Metadata Documents and pre-registration | B1/11_authorization | secured_issues | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration) |
| `11_authorization` | `02_pkce_and_tokens` | PKCE; resource indicators; issuer binding; audience, expiry, signature and scope checks; insufficient scope | B1/11_authorization | secured_issues | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations) |
| `11_authorization` | `03_local_auth` | Local OAuth provider; scopes issues:read/issues:write; SDK verification; Inspector and Chat authorization | B1/11_authorization | secured_issues | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/index) |
| `12_security` | `01_poisoned_content` | Tool poisoning; result/resource prompt injection; tool shadowing; rug pulls; schema fingerprints | B1/12_security | vulnerable_lab | [Reference](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices) |
| `12_security` | `02_boundaries` | Confused deputy; token forwarding prevention; SSRF; command injection; least privilege; exfiltration | B1/12_security | vulnerable_lab | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations) |
| `12_security` | `03_defense_lab` | Allow-lists; validation; redaction; approvals; audit logs; container isolation; vulnerable-fixture repair | B1/12_security | vulnerable_lab | [Reference](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/local-server-security) |
| `13_testing_observability` | `01_inmemory_contracts` | In-memory SDK tests; fake models; schemas; Python/TypeScript parity; fixtures and wire snapshots | B1/13_testing_observability | workspace_quality_suite | [Reference](https://py.sdk.modelcontextprotocol.io/get-started/testing/) |
| `13_testing_observability` | `02_inspector_stdout` | Inspector CLI/UI; stdout corruption; stderr logs; subprocess smoke tests; exact error reproductions | B1/13_testing_observability | workspace_quality_suite | [Reference](https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector/cli) |
| `13_testing_observability` | `03_traces_load_eval` | OpenTelemetry context; exporter; structured logs; HTTP load; tool-selection evaluation; Deprecated logging comparison | B1/13_testing_observability | workspace_quality_suite | [Reference](https://py.sdk.modelcontextprotocol.io/run/opentelemetry/) |
| `14_tool_design` | `01_api_mirror` | Baseline of 25 endpoint-shaped tools; names/descriptions/parameters; baseline task success | B1/14_tool_design | tool_redesign | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) |
| `14_tool_design` | `02_task_tools` | Six higher-level tools; concise/detailed output; actionable errors; token budgets | B1/14_tool_design | tool_redesign | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) |
| `14_tool_design` | `03_measure_change` | Evaluation dataset; controlled comparison; dynamic tool list changes; deterministic catalog ordering and caching | B1/14_tool_design | tool_redesign | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/utilities/caching) |
| `15_agent_frameworks` | `01_agents_and_langgraph` | OpenAI Agents SDK; LangChain MCP adapters and LangGraph; tools and approval integration | B1/15_agent_frameworks | weekly_bug_triage | [Reference](https://github.com/modelcontextprotocol/python-sdk) |
| `15_agent_frameworks` | `02_strands_and_pydantic` | Strands Agents and Pydantic AI adapters; same task and fake model fixtures | B1/15_agent_frameworks | weekly_bug_triage | [Reference](https://github.com/modelcontextprotocol/python-sdk) |
| `15_agent_frameworks` | `03_adk_and_claude` | Google ADK and Claude Agent SDK; common triage task; framework comparison | B1/15_agent_frameworks | weekly_bug_triage | [Reference](https://github.com/modelcontextprotocol/python-sdk) |
| `15_agent_frameworks` | `04_remote_model_apis` | Major model API remote MCP integrations; feature/version compatibility and approval semantics | B1/15_agent_frameworks | weekly_bug_triage | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http) |
| `16_composition` | `01_server_as_client` | Server consuming upstream servers; connection lifetime; namespacing and discovery | B1/16_composition | lumen_gateway | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/architecture/index) |
| `16_composition` | `02_policy_gateway` | Per-user tool visibility; auth enforcement; rate limits; upstream identity and audit trails | B1/16_composition | lumen_gateway | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/index) |
| `16_composition` | `03_cache_isolation` | Catalog merging; public/private cache partitioning; failure boundaries; split/combine decisions | B1/16_composition | lumen_gateway | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/server/utilities/caching) |
| `17_extensions` | `01_negotiate` | Extension identifiers; capability negotiation; maturity stages; graceful fallback | B1/17_extensions | report_and_dashboard | [Reference](https://modelcontextprotocol.io/extensions/overview) |
| `17_extensions` | `02_report_task` | Task handles; tasks/get polling; tasks/update input; cancellation and terminal states; durable report results | B1/17_extensions | report_and_dashboard | [Reference](https://modelcontextprotocol.io/extensions/tasks/overview) |
| `17_extensions` | `03_analytics_app` | Tool/UI association; UI resources; host bridge; sandbox/CSP; dashboard and verified host matrix | B1/17_extensions | report_and_dashboard | [Reference](https://modelcontextprotocol.io/extensions/apps/overview) |
| `18_packaging` | `01_python_package` | Build wheel/sdist; uvx entry point; environment config; TestPyPI opt-in; compatibility policy | B1/18_packaging | distributable_notes | [Reference](https://py.sdk.modelcontextprotocol.io/) |
| `18_packaging` | `02_npm_docker` | npm CLI and npx; reproducible image; runtime user; secret-free packaging | B1/18_packaging | distributable_notes | [Reference](https://github.com/modelcontextprotocol/typescript-sdk) |
| `18_packaging` | `03_desktop_bundle` | Verified desktop bundle manifest; safe config; host install and rollback; tool versioning | B1/18_packaging | distributable_notes | [Reference](https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-local-servers) |
| `19_registry` | `01_server_metadata` | server.json; publisher schema; package and transport metadata | B1/19_registry | notes_registry | [Reference](https://modelcontextprotocol.io/registry/about) |
| `19_registry` | `02_namespace` | Namespace verification; publisher validation; optional publication; sub-registries | B1/19_registry | notes_registry | [Reference](https://modelcontextprotocol.io/registry/about) |
| `19_registry` | `03_assess_server` | Review source/permissions/version; registry is not a trust guarantee; Server Cards discovery | B1/19_registry | notes_registry | [Reference](https://modelcontextprotocol.io/seps/2127-mcp-server-cards) |
| `20_deployment` | `01_container` | Issues Dockerfile; health checks; runtime config; filesystem and network boundaries | B1/20_deployment | local_secured_stack | [Reference](https://py.sdk.modelcontextprotocol.io/run/) |
| `20_deployment` | `02_compose_proxy` | Local reverse proxy, OAuth provider and server; HTTPS boundary; rate limits and monitoring | B1/20_deployment | local_secured_stack | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/index) |
| `20_deployment` | `03_cloud_lifecycle` | Container/serverless/managed hosting comparison; secrets and costs; teardown and rollback | B1/20_deployment | local_secured_stack | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http) |
| `21_production_hosts` | `01_resilience` | Reconnect; deadlines; capability checks; tool changes; bounded retries; config files | B1/21_production_hosts | lumen_chat_v4 | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning) |
| `21_production_hosts` | `02_approval_ui` | Web chat; selectable provider; trusted approval screen; elicitation and Tasks interfaces | B1/21_production_hosts | lumen_chat_v4 | [Reference](https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation) |
| `21_production_hosts` | `03_apps_compatibility` | MCP Apps host UI; older-revision interoperability through supported SDK layer; request isolation | B1/21_production_hosts | lumen_chat_v4 | [Reference](https://modelcontextprotocol.io/extensions/apps/overview) |

## Additional feature and method obligations

These are explicit subcases within the files above; they must receive named tests and captured examples. Listing them here prevents a broad lesson title from hiding missed protocol behavior.

| Feature or method family | Assigned module/example | Required demonstration |
|---|---|---|
| JSON-RPC parse/invalid request/invalid params/internal errors; request vs notification | 01/01_jsonrpc | Invalid payloads and correct error correlation; no response to notifications |
| Discovery and version mismatch | 01/02_raw_server | Supported versions, server identity/capabilities, unsupported version response |
| Per-request client identity/capabilities and server identity metadata | 01/02_raw_server | Inspect the serialized metadata on real exchanges |
| Complete vs input-required results | 01/02_raw_server; 09/01_form_retry | Client branches on result kind, including compatibility interpretation |
| Required cache fields and private/public partitioning | 03/03_resource_changes; 16/03_cache_isolation | Freshness, expiration, private-user isolation and invalidation |
| Tool catalog change notification | 14/03_measure_change | Invalidate list cache and revalidate pending tool approval |
| Resource list change vs individual resource update | 03/03_resource_changes | Subscribe to each, inspect subscription IDs and read updated content |
| Prompt catalog change notification | 04/03_prompt_completion | Refresh catalog without connection-scoped assumptions |
| Cursor and nextCursor | 05/02_pages_and_errors; 08/03_pages_completion | Empty pages, terminal cursor, invalid cursor and bounded traversal |
| Input/output schema; local references; composition limits | 02/02_rich_results | Valid/invalid structured results and bounded schema evaluation |
| Content annotations, icons/titles and audience hints | 02/02_rich_results; 03/01_static_resources | Preserve content metadata without treating it as authorization |
| Completion context and pagination hints | 04/03_prompt_completion | Prompt/resource arguments, prior context and truncation |
| Progress and cancellation | 08/02_progress_cancel | Correlate request tokens; cleanup after cancel; race with completion |
| Request-scoped vs subscription-scoped notifications | 10/03_stream_recovery | Capture each on the appropriate stream |
| HTTP method/name/custom parameter headers | 10/02_headers_and_origin | Valid headers plus mismatch rejection, without leaking secrets |
| MRTR request state and answers | 09/01_form_retry | Accept, decline, cancel, invalid answer, expiry and repeated request |
| URL elicitation | 09/02_url_retry | Sensitive flow leaves the tool result; retry establishes outcome |
| Authorization discovery | 11/01_discovery_registration | Protected-resource metadata, issuer metadata and resource selection |
| Client registration | 11/01_discovery_registration | Metadata-document validation and local pre-registration alternative |
| Issuer/audience/scope enforcement | 11/02_pkce_and_tokens | Wrong issuer/audience, expired token and insufficient-scope tests |
| Extension fallback | 17/01_negotiate | Missing capability results in a useful plain-text alternative |
| Tasks lifecycle | 17/02_report_task | Creation/handle return, polling, updates, cancellation, completion, failure and expiry; exact methods from pinned extension |
| App lifecycle | 17/03_analytics_app; 21/03_apps_compatibility | Tool association, UI resource load, bridge messages, sandbox enforcement and teardown |
| SDK low-level escape hatch | 01/02_raw_server; 17/01_negotiate | Handwritten mechanism first; SDK-supported extension dispatch next |
| Legacy protocol compatibility | 21/03_apps_compatibility | Current SDK interoperates with an older fixture; exact old syntax remains in migration guide |
| Deprecated roots and sampling | 09/03_files_and_model | Captured exchange analysis plus safe current replacement on client/server sides |
| Deprecated protocol logging | 08/03_pages_completion; 13/03_traces_load_eval | Per-request legacy behavior explained in migration guide; stderr/OTel replacement tested |
| Removed operations and historical transport/registration | docs/MIGRATING_FROM_OLDER_VERSIONS.md | Old/new comparisons only; ban legacy spellings from runnable course code |

For protocol subcases, use the corresponding primary section in the main allocation table and the [schema reference](https://modelcontextprotocol.io/specification/2026-07-28/schema). Legacy and Deprecated are distinct statuses; no new application depends on a deprecated capability.

## Official extensions and bonus examples

| Extension / bonus | Python example path | TypeScript example path | Use case | Primary source |
|---|---|---|---|---|
| Tasks (Beta) | `modules/17_extensions/python/examples/02_report_task.py` | `modules/bonus/B1_typescript/17_extensions/examples/02_report_task.ts` | Durable quarterly reports | [Tasks](https://modelcontextprotocol.io/extensions/tasks/overview) |
| MCP Apps (Stable) | `modules/17_extensions/python/examples/03_analytics_app.py` | `modules/bonus/B1_typescript/17_extensions/examples/03_analytics_app.ts` | Interactive analytics dashboard | [Apps](https://modelcontextprotocol.io/extensions/apps/overview) |
| Skills (Beta) | `modules/bonus/B4_whats_new/python/examples/01_skills.py` | `modules/bonus/B4_whats_new/typescript/examples/01_skills.ts` | Discover and read incident-response instructions and supporting resources | [Skills](https://modelcontextprotocol.io/extensions/skills/overview) |
| Server Cards (Beta) | `modules/bonus/B4_whats_new/python/examples/02_server_cards.py` | `modules/bonus/B4_whats_new/typescript/examples/02_server_cards.ts` | Discover remote workspace metadata | [Server Cards](https://modelcontextprotocol.io/seps/2127-mcp-server-cards) |
| OAuth Client Credentials (Stable) | `modules/bonus/B4_whats_new/python/examples/03_client_credentials.py` | `modules/bonus/B4_whats_new/typescript/examples/03_client_credentials.ts` | Scheduled analytics service identity | [Client credentials](https://modelcontextprotocol.io/extensions/auth/oauth-client-credentials) |
| Enterprise-Managed Authorization (Stable) | `modules/bonus/B4_whats_new/python/examples/04_enterprise_auth.py` | `modules/bonus/B4_whats_new/typescript/examples/04_enterprise_auth.ts` | Centrally managed workspace access | [Enterprise authorization](https://modelcontextprotocol.io/extensions/auth/enterprise-managed-authorization) |
| Other official SDKs | `modules/bonus/B2_other_sdks/` native-language examples; common Python contract runner | Shared TypeScript contract client | Equivalent notes behavior in Go/C#/Java/Kotlin/Rust, subject to stability verification | [Official SDK inventory](https://modelcontextprotocol.io/docs/2026-07-28/sdk) |
| Reading schema and spec | `modules/bonus/B3_spec_contributing/python/examples/01_schema_contract.py` | B1 equivalent contract checker | Find a documentation/schema discrepancy | [Specification](https://modelcontextprotocol.io/specification/2026-07-28) |
| SEPs and governance | `modules/bonus/B3_spec_contributing/python/examples/02_sep_index.py` | B1 equivalent index reader | Trace a feature proposal into a revision | [SEPs](https://modelcontextprotocol.io/seps) |
| Contribution workflow | `modules/bonus/B3_spec_contributing/python/examples/03_conformance_case.py` | B1 equivalent conformance case | Prepare a reproducible local issue fixture | [SDK contribution guide](https://github.com/modelcontextprotocol/python-sdk/blob/main/CONTRIBUTING.md) |

B4 and B3 each include at least three exercises with solutions, quizzes, diagrams, captured protocol use where applicable, and tests. B2 supplies at least three examples per selected native SDK (tool, resource/prompt, client contract) and equivalent learning materials. No unstable SDK is described as stable to meet a language quota.

## Capstone coverage

| Project | Reused modules | Additional acceptance evidence |
|---|---|---|
| Personal Knowledge Server | 02–10, packaging guidance from 18 | Markdown search, deterministic semantic-search fixture, resources/prompts/completions, package/bundle smoke tests |
| Security Audit Lab | 11–13 | Second vulnerable fixture, reproducible findings, patches, negative regression tests |
| Lumen Gateway | 11, 13–17 | Independent users, filtered tools, audit, rate-limit enforcement, upstream failures |
| Lumen Ops | 07–20 | OAuth, confirmed writes, durable reports, App dashboard, evaluations, Docker and registry metadata |
| Lumen Chat Pro | 06, 09–17, 21 | Provider selection, multi-server config, approvals, input UI, Tasks and Apps, reconnect tests |

## Coverage gate

Phase 2's course checker will inventory modules and examples, assert required README sections, enforce exercise/solution counts and validate delivered links. A separate manifest records planned versus delivered status while phases are in progress. Final release permits no planned rows. Cross-reference the pinned schema's methods/notifications against captures; extension methods use their own versioned schemas. Include SDK API checks and feature-specific negative tests. Do not confuse a file existing with a feature being taught and working.
