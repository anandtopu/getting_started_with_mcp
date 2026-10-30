# Quiz

### 1. Can a tool description authorize its own access?

<details>
<summary>Answer</summary>

No. Treat server descriptions and annotations as untrusted input; access policy lives outside the model and server-supplied text.

</details>

### 2. What does the catalog hash detect?

<details>
<summary>Answer</summary>

Changes in reviewed definitions, including descriptions, schemas and annotations. It cannot detect unchanged definitions backed by malicious implementation code.

</details>

### 3. Why namespace every tool?

<details>
<summary>Answer</summary>

It keeps identical tool names from distinct servers from colliding and lets the host apply server-specific permissions.

</details>

### 4. Does wrapping poisoned text in a label solve injection?

<details>
<summary>Answer</summary>

No. The label is context, while allow-lists, scoped credentials and approval boundaries restrict what a deceived model can actually execute.

</details>

### 5. Why reject a URL with the approved host in its username?

<details>
<summary>Answer</summary>

The actual destination host comes after the @ sign. This lab avoids URL interpretation attacks by accepting one exact configured destination.

</details>

### 6. Can the server trust a user_id in model arguments?

<details>
<summary>Answer</summary>

No. Derive identity from the verified token or, for this local stdio fixture, the launching context.

</details>

### 7. Why not forward an inbound bearer token?

<details>
<summary>Answer</summary>

It was issued for this resource. A downstream service needs independently scoped credentials or an explicit token exchange; passthrough creates a confused deputy.

</details>
