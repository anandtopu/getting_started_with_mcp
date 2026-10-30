# Module 06 quiz

1. Who executes a model’s tool request?

<details><summary>Answer</summary>

The host, after routing, validation and approval.

</details>

2. Why namespace tool names?

<details><summary>Answer</summary>

Different servers can expose identical names; the host needs an unambiguous route.

</details>

3. May a model supply confirmed=true?

<details><summary>Answer</summary>

No. The host excludes it from the advertised schema and rejects such arguments.

</details>

4. Why preserve a tool-call ID?

<details><summary>Answer</summary>

The provider must pair each returned result with the original tool request.

</details>

5. Does fake mode prove that a real model selects the right tools?

<details><summary>Answer</summary>

No. It proves the host loop deterministically; live model behavior requires an opt-in test.

</details>
