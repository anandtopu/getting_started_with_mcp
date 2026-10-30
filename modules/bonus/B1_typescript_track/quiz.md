# B1 quiz

1. Does a TypeScript type validate a remote JSON object?

<details><summary>Answer</summary>

No. Runtime schema validation is still required.
</details>

2. Why pin the protocol separately from SDK version?

<details><summary>Answer</summary>

SDK and protocol releases have different version numbers and compatibility.
</details>

3. Can a model set confirmed=true to authorize a write?

<details><summary>Answer</summary>

No. The host owns the approval decision and injects confirmation only after review.
</details>

4. Why does the Tasks lesson use a raw peer?

<details><summary>Answer</summary>

The installed SDK has no current task-result hook; its transport remains usable.
</details>

5. Does a passing fake-model test prove model accuracy?

<details><summary>Answer</summary>

No. It proves the integration path and policy.
</details>

6. Should a failed write be retried automatically?

<details><summary>Answer</summary>

No. An uncertain write needs reconciliation or an explicit idempotency contract.
</details>