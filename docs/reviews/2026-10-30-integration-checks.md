# Cross-file integration checks

Date: 2026-10-30. This pass follows the per-file analysis and tracks data, authority and lifetime across components.

## Flow checks

| Flow | Producer → consumer | Result / evidence | Limit |
|---|---|---|---|
| Human review → fresh discovery → execution | `defenses.catalog` / native CourseHost → cached SDK Client → tool handler | Real server advertises 60-second TTL, changes after review; regression asserts zero execution | Remote changes after the final network check still require server-side authorization; no atomic remote attestation claimed |
| Browser ticket → dispatch approval | native web ticket fingerprint → CourseHost approve callback → refreshed catalog | Catalog changes between preliminary check and dispatch; API returns failure and handler stays uncalled | Local single-user browser service |
| Startup → ownership → cancellation | Python worker/context and native connectPromise → host/web cleanup | Timeout/cancel/start failure and close-during-connect release resources | External process/OS failures remain operational concerns |
| Annotation → host discovery | replace/delete functions → Python and TS catalogs → actual captures | Destructive labels match effects in both languages | Annotations are hints, not authorization grants |
| Model → schema → user → MCP → model | native provider adapters → portable schema → CourseHost → real notes server | Four HTTP doubles preserve native history and tool IDs; malformed/self-approved input fails before review | No live model selection/quality evidence |
| Raw bytes → protocol | SDK-free native server/client → newline JSON → IDs and current envelopes | Count=80, unsupported methods/revisions and bad argument arrays rejected; Inspector lists actual tool | Deliberately small teaching peer |
| SQL page → resource URI → next page | named read-only analytics query → resource_link → ResourceTemplate | Actual SQLite rows and next-page read; invalid date/limit denied | Fixed 365-row fixture bounds native query computation |
| MCP input answer → browser consent | native URL result → independent local portal POST → one-use retry | Accept alone fails; forged Origin denied; real page approval succeeds; grant consumed | Fixture simulates browser interaction; human must consent in real integration |
| Discovery → PKCE → token use | native TS OAuth provider/transport → local issuer/resource | Wrong issuer denied; authenticated read succeeds; missing write scope denied | Python starts the synthetic issuer/resource; no vendor SSO claim |
| Trace/load/evaluation → teaching claim | explicit native OTel spans + actual HTTP clients + fixture dataset | Parent/child IDs and error status checked; ten requests measured; deterministic score labeled | No automatic TS SDK tracing or LLM accuracy inference |
| Design → measured comparison | native 25-tool mirror and six-tool workflow → six retrieval cases | Same data and expected ID/status; catalog characters and concise/detail lengths measured | Retrieval benchmark does not show LLM preference |
| Metadata → package identity → connection decision | Registry JSON Schema → npm manifest → explicit policy | Invalid metadata/version and repeated cursor rejected; no auto-install | Publishing optional; namespaces not verified by schema alone |
| Packaging → installed launch | source → wheel/npm/MCPB → child outside checkout | Notes wheel/npm/extracted bundle and knowledge wheel/bundle launch outside checkout | [R-010 replacement and evidence](../PACKAGING_ADVISORY_VERIFICATION.md); desktop GUI installation remains manual |
| Teaching index → inventory → CI | README commands + FEATURE_MAP → examples.json → pytest/Inspector | Numbered examples must be registered; duplicate/missing entries fail release check | Structural checks cannot establish pedagogical depth by themselves |
| B1 index → native application behavior | native OAuth gateway → five stdio services; native Chat Pro → shared browser assets | Follow-up implementation, local browser/security acceptance and real deployment CI passed | [Native application record](../TYPESCRIPT_APPLICATIONS_VERIFICATION.md) |

## Contract checks

| Contract | Producer | Consumer | Status / invariant |
|---|---|---|---|
| Tool definition fingerprint | Fresh `tools/list` result | Review ticket and final callback | Exact approved schema/description/annotations preserved; refresh bypasses TTL cache |
| Host-only confirmation | Human approve callback | Mutating MCP handler | Removed from model schema; model-supplied field rejected; host adds it only after approval |
| Provider correlation | Provider function call ID | Provider tool-result payload | Same ID and native assistant blocks survive across turns; repeated IDs denied |
| Replacing/deleting data | Annotation constants | Host catalog/UX | readOnlyHint=false, destructiveHint=true |
| Continuation ownership | Server-created requestState/grant | Retried arguments/inputResponses | Opaque, bounded, exact binding and one-use consumption |
| Cursor termination | resources/list or Registry pages | Bounded iterator | Follow empty page with nextCursor; reject repeat/oversize and budget exhaustion |
| Protocol stdout | Server entry point | SDK/Inspector/wiretap | Every captured message is JSON-RPC; diagnostics remain stderr |
| Spec revision | Explicit client mode | Server request envelope | Current revision retained; labeled legacy paths remain isolated |
| Dependency advisory | Official MCPB 0.3 JSON Schema, Ajv and fflate | Both build scripts | Vulnerable CLI/Zod 3 removed; bounded manifest/archive inputs, 256MB child heap, 120-second deadline; dependency regression and CI audit gate |

## Integration findings

R-001 and R-002 are cross-file authorization defects: a correct-looking comparison was weakened by SDK cache behavior or by an approval callback that lost the original fingerprint. R-003 is an ownership-transfer defect. Their regressions exercise the actual SDK/HTTP/lifetime boundaries rather than copying the implementation logic. R-009 is closed by native application implementations, equivalent browser acceptance and real deployment CI; its separate record preserves the evidence and repairs.
