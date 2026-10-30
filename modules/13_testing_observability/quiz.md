# Quiz

### 1. What does an in-memory test skip?

<details>
<summary>Answer</summary>

Serialization, subprocess lifetime, HTTP middleware, OAuth, and emitted protocol bytes. Add wire and transport tests.

</details>

### 2. Why is valid JSON not enough for stdout?

<details>
<summary>Answer</summary>

Every line must be a protocol message with the expected envelope. A JSON debug object is still protocol corruption.

</details>

### 3. Which values may the call snapshot normalize?

<details>
<summary>Answer</summary>

Only its documented exclusions: capture timing, request IDs and metadata such as trace context. Tool names, arguments, result content, errors and structured outputs stay comparable.

</details>

### 4. What connects client and server spans?

<details>
<summary>Answer</summary>

A shared trace ID with the server span parented through propagated trace context. Install an exporter to retain the SDK spans.

</details>

### 5. Does 30/30 prove an LLM selects tools well?

<details>
<summary>Answer</summary>

No. This fixture has only issue-read requests, and the baseline is deterministic. Evaluate real models, varied tasks, arguments, errors and adverse prompts separately.

</details>

### 6. Why report concurrency with latency?

<details>
<summary>Answer</summary>

A latency number depends on load, machine, connection setup and measurement method. The lab measures complete short client operations, including discovery.

</details>

### 7. Where do logs belong?

<details>
<summary>Answer</summary>

stderr or an explicitly configured telemetry exporter. Never stdout for a stdio server; never raw credentials or tool bodies in audit logs.

</details>
