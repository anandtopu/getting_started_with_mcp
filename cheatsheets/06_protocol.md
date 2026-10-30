# Protocol / 2026-07-28

A compact message and trust reference. [Printable one-page PDF](06_protocol.pdf).

## Envelope

- Request: jsonrpc="2.0", id, method, params. Response: same id with result or error.
- Notification: method and params, no id and no response.
- Client _meta: io.modelcontextprotocol/protocolVersion, clientInfo, clientCapabilities.

## Ten core request methods

- server/discover; tools/list; tools/call
- resources/list; resources/templates/list; resources/read
- prompts/list; prompts/get; completion/complete; subscriptions/listen

## Results and caching

- complete: inspect application outcome, including isError on tool results.
- input_required: collect input, echo protected requestState, retry with inputResponses.
- Cacheable results carry ttlMs and cacheScope. Keep private caches partitioned by identity.

## Notifications

- Progress and cancellation are request-correlated. Subscription acknowledgment starts an event stream.
- Resource update and tool/resource/prompt list-change events invalidate cached state.
- Protocol logging remains deprecated optional vocabulary; prefer stderr or OpenTelemetry.

## Extensions

- Tasks: resultType=task; tasks/get, tasks/update, tasks/cancel.
- Skills: skills/list, skills/get; resources/read verifies bytes; directory reads are optional.
- Apps have a separate UI bridge. OAuth exchanges and Server Cards are HTTP metadata, not new JSON-RPC methods.

## Failures and trust

- -32601 unknown method; -32602 invalid params; -32020 HTTP metadata mismatch; -32021 missing capability; -32022 unsupported revision.
- Descriptions and schemas do not grant permission. Verify identity, scopes, arguments and exact approval independently.
- Full captured examples: docs/PROTOCOL_GUIDE.md.

[Full protocol guide](../docs/PROTOCOL_GUIDE.md) · [Learning path](../LEARNING_PATH.md)
