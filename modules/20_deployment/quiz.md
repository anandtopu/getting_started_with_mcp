# Module 20 quiz

### 1. Does a proxy replace OAuth?

<details><summary>Answer</summary>

No. The resource still validates tokens and scopes.

</details>

### 2. Which audience belongs in the token?

<details><summary>Answer</summary>

The public resource URL, not its Docker service name.

</details>

### 3. Why allow local HTTP?

<details><summary>Answer</summary>

Only loopback ports are published; identities and data are synthetic.

</details>

### 4. Can the SQLite lab scale to five replicas?

<details><summary>Answer</summary>

Not safely. Store, idempotency and limits must first be shared.

</details>

### 5. Does health prove an authorized call works?

<details><summary>Answer</summary>

No. Run the end-to-end authenticated probe.

</details>

### 6. Which fields stay out of metrics?

<details><summary>Answer</summary>

Tokens, authorization codes, arguments and results.

</details>

### 7. Does closing the client stop cloud billing?

<details><summary>Answer</summary>

No. Tear down infrastructure and verify remaining charges.

</details>
