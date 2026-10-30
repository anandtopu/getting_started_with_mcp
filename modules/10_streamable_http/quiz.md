# Module 10 quiz

1. What does each POST carry?

<details><summary>Answer</summary>

One JSON-RPC request with per-request metadata and matching HTTP headers.

</details>

2. How does the client detect JSON versus SSE?

<details><summary>Answer</summary>

It inspects the response Content-Type and supports both.

</details>

3. Does CORS authenticate a client?

<details><summary>Answer</summary>

No. It governs browser access; identity requires authentication.

</details>

4. Can a routing header establish tenant identity?

<details><summary>Answer</summary>

No. It is client input even when it matches the body.

</details>

5. What happens after a subscription disconnect?

<details><summary>Answer</summary>

Reissue the subscription and refetch current state; missed events are not replayed.

</details>

6. Where does durable state belong?

<details><summary>Answer</summary>

Outside per-request factories, in shared storage for a multi-worker deployment.

</details>

7. What prevents duplicate inserts after an uncertain response?

<details><summary>Answer</summary>

A stable operation key enforced atomically with the write.

</details>
