# Module 07 quiz

1. Why is confirmation not sufficient SQL protection?

<details><summary>Answer</summary>

It expresses user intent; parameter binding separately prevents data from becoming SQL syntax.

</details>

2. Why fetch one extra row?

<details><summary>Answer</summary>

It establishes whether another page exists without returning the extra row.

</details>

3. Does read-only mode bound CPU?

<details><summary>Answer</summary>

No. The progress-handler deadline separately bounds execution.

</details>

4. What survives a restart?

<details><summary>Answer</summary>

Only committed source fixtures; the disposable copy and receipt table are reset.

</details>

5. Can a missing response justify a new operation key?

<details><summary>Answer</summary>

No. Reuse the original key to avoid a duplicate insert.

</details>

6. Does the local mock use the internet?

<details><summary>Answer</summary>

No. ASGITransport sends HTTP requests directly to the local FastAPI application.

</details>
