# TypeScript 07: Structured tools

Run issue CRUD, read-only analytics pages, resource links and bounded local REST calls. These are the TypeScript counterparts to [Module 07](../README.md). Read that lesson's explanation, diagram and quiz first; this page records language-specific behavior.

## Prerequisites

From the root: `npm ci`. Node 24 or 26 is required. The pinned official MCP SDK is 2.4.0; the protocol is 2026-07-28. No model key is needed.

## Learning objectives

- Execute each case and explain its observable assertion.
- Identify the boundary enforced by the server or host.
- Make a controlled change and demonstrate its failing regression.

## The big idea

Run issue CRUD, read-only analytics pages, resource links and bounded local REST calls. The language changes syntax and library choices; the peer still sees the same JSON-RPC contract. A deterministic fixture is an integration check, not a measured model-quality claim.

## How it works

```mermaid
sequenceDiagram
    participant E as TypeScript example
    participant C as MCP client
    participant S as Lumen server
    E->>C: Configure explicit policy
    C->>S: Discover and call
    S-->>C: Bounded result or error
    C-->>E: Check behavior
```

## On the wire

[Actual TypeScript traffic](../../bonus/B1_typescript_track/wire/notes.jsonl), [form retries](../../bonus/B1_typescript_track/wire/forms.jsonl), and [Tasks](../../bonus/B1_typescript_track/wire/tasks.jsonl) share the current envelope. [Regeneration manifest](../../bonus/B1_typescript_track/wire/manifest.json). Captures are shared by capability, not duplicated to imply a separate capture of an in-memory assertion.

## Key APIs at a glance

| Python | TypeScript | Purpose |
|---|---|---|
| MCPServer | McpServer | Register local behavior |
| Client | Client | Request/validate protocol results |
| Context | ctx.mcpReq | Cancellation, input state and notifications |
| gateway/host helpers | CourseHost, Gateway, Connection | Keep execution policy outside model proposals |

## Walkthrough

- `01_issue_crud.ts`: run `node --import tsx modules/07_real_data/typescript/examples/01_issue_crud.ts`; expect `status: PASS`.
- `02_readonly_analytics.ts`: run `node --import tsx modules/07_real_data/typescript/examples/02_readonly_analytics.ts`; expect `status: PASS`.
- `03_rest_wrapper.ts`: run `node --import tsx modules/07_real_data/typescript/examples/03_rest_wrapper.ts`; expect `status: PASS`.

The executable contracts live in [advanced_lessons.ts](../../../common/typescript/advanced_lessons.ts); follow the module-number branch to the focused implementation it invokes. This avoids copying the same host/security logic into every example.

1. `01_issue_crud.ts` creates, reads, updates and deletes an ephemeral issue. A missing confirmation is rejected; a repeated operation key returns the original creation, and a deleted receipt cannot recreate it.
2. `02_readonly_analytics.ts` queries `analytics.db` using a read-only connection, a fixed parameterized query, ISO date validation and a 1–50 row page. It follows the actual next-page resource link and rejects an excessive limit. This fixture has 365 rows, so work is bounded by its fixed dataset; the Python variant also demonstrates a SQLite instruction deadline for larger databases.
3. `03_rest_wrapper.ts` starts an actual local HTTP API, reads a project through MCP and rejects an invalid ID. Open-Meteo uses a fixed destination and requires explicit `allow_network=true`; default tests use an injected response. HTTP helpers reject redirects, enforce a five-second deadline and cap responses at 64 KB.

Implementations: [real_data.ts](../../../common/typescript/real_data.ts), [remote.ts](../../../common/typescript/remote.ts). Inspect `node --import tsx modules/07_real_data/typescript/analytics_server.ts`; call `analytics_page` with `{"limit":2}`. [Captured analytics request and resource read](../../bonus/B1_typescript_track/wire/analytics.jsonl).

## Try it in a host

Use the [B1 host configs](../../bonus/B1_typescript_track/host_configs/vscode.json), replacing the absolute repository path. Ask "Find release notes." The fixed `notes` profile starts with protocol-only stdout. The `forms` profile asks for a bulletin decision; the `workflow` profile reads and drafts without publishing.

## Real-world use case

Run `node --import tsx modules/07_real_data/typescript/use_case/main.ts`. Expect three passing cases. In a company, keep the same boundary checks while replacing the synthetic data source and setting an explicitly reviewed identity policy.

## Common mistakes

- `Unknown lesson`: use a listed module and part 1–3.
- `User declined`: the host decision was false; do not silently retry a write.
- `Review the current catalog first`: discover and review before executing.
- `Invalid issuer, audience or expiry`: verify the configured resource and issuer; never weaken checks to make a token pass.

## Exercises

Run `node --import tsx scripts/check-ts-extension-exercise.ts 7 1` (or 2/3). Initially it reports a deliberate mismatch; use `--solution` to verify the answer.

1. **Practice — row_limit:** Permit positive integer query limits through 20; reject all other input types. Run exercise 1 against the independent positive and negative cases in `common/typescript/exercise_contracts.ts`.
2. **Apply:** require a nonempty reviewed fingerprint, exact equality with the current fingerprint, and explicit approval. Test a changed catalog and a declined decision.
3. **Stretch:** consume page cursors until `undefined`, count pages, reject repeats and stop at 20 pages. An empty/incomplete sequence is an error. Apply it to discovery before exposing a model catalog.

## Quiz

Use the [module quiz](../quiz.md), then explain which assertions above support your answers. B1's [cross-language quiz](../../bonus/B1_typescript_track/quiz.md) checks API and runtime differences.

## Key takeaways

- The wire contract is language independent.
- Types do not replace runtime validation.
- Capability discovery is separate from approval.
- Finite budgets make failures visible.
- A local fake model cannot measure live model accuracy.

## Go deeper

[Official TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk), [current specification](https://modelcontextprotocol.io/specification/2026-07-28).

## Next

Return to the [full track index](../../bonus/B1_typescript_track/README.md).
