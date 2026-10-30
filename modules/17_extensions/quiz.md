# Module 17 quiz

## 1. Who decides whether a call becomes a Task?

<details>
<summary>Answer</summary>

The server, after the client advertises support on that request.

</details>

## 2. Is the task handle nested inside task?

<details>
<summary>Answer</summary>

No. The released 2026-07-28 creation result has flat Task fields and resultType task.

</details>

## 3. How does a client supply requested input?

<details>
<summary>Answer</summary>

Send tasks/update with inputResponses keyed by outstanding input request IDs.

</details>

## 4. Does isError true imply failed task status?

<details>
<summary>Answer</summary>

No. A tool-level error is a completed result; failed is for protocol errors.

</details>

## 5. Can cancelling completed work undo its effects?

<details>
<summary>Answer</summary>

No. Cancellation is cooperative and terminal results stay terminal.

</details>

## 6. What connects a tool to its App?

<details>
<summary>Answer</summary>

Tool metadata points to a ui:// resource with the MCP App HTML MIME type.

</details>

## 7. Does advertising CSP make arbitrary HTML safe?

<details>
<summary>Answer</summary>

No. The host must enforce the sandbox, permitted origins and bridge authorization.

</details>
