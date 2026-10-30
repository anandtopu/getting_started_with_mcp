# Module 02 quiz

1. Does a model see a tool’s source code?

<details><summary>Answer</summary>

Normally it sees the name, description and schema, not the implementation.

</details>

2. What does isError mean?

<details><summary>Answer</summary>

The protocol call completed, but tool execution failed; the model can inspect the error.

</details>

3. What does idempotent mean for tag_note?

<details><summary>Answer</summary>

Repeating the same confirmed tag has the same effect as doing it once.

</details>

4. Is readOnlyHint an authorization guarantee?

<details><summary>Answer</summary>

No. It is untrusted descriptive metadata.

</details>

5. Why keep structuredContent and text?

<details><summary>Answer</summary>

Programs can consume structured fields; people and simpler hosts can read the text fallback.

</details>
