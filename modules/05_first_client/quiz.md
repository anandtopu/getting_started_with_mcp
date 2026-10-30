# Module 05 quiz

1. Does an MCP client require an LLM?

<details><summary>Answer</summary>

No. The CLI is a deterministic client.

</details>

2. When should pagination stop?

<details><summary>Answer</summary>

When nextCursor is absent, even if earlier pages were empty.

</details>

3. What prevents a repeating cursor from hanging the client?

<details><summary>Answer</summary>

A seen-cursor set plus an absolute page budget.

</details>

4. Why use async with or finally?

<details><summary>Answer</summary>

To close pipes and child processes even when an operation fails.

</details>

5. Are tool errors and protocol errors the same?

<details><summary>Answer</summary>

No. A tool may return isError content; a protocol failure uses an error envelope.

</details>
