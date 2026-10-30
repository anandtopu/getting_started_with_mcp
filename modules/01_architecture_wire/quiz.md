# Module 01 quiz

1. Why must a response repeat an ID?

<details><summary>Answer</summary>

To correlate it with the request, even if replies arrive out of order.

</details>

2. Does a notification receive a result?

<details><summary>Answer</summary>

No. It has no request ID and no response.

</details>

3. What does -32700 mean?

<details><summary>Answer</summary>

The input was not valid JSON.

</details>

4. Does stateless mean servers cannot store notes?

<details><summary>Answer</summary>

No. It removes implicit protocol-session assumptions; application state remains explicit.

</details>

5. Why can the proxy not pretty-print the forwarded bytes?

<details><summary>Answer</summary>

That would change the transport. Only the separate captured copy is decoded and formatted.

</details>
