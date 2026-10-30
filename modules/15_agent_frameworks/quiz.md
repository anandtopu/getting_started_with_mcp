# Module 15 quiz

## 1. What remains MCP when the framework changes?

<details>
<summary>Answer</summary>

Discovery, schemas, requests and results between the client and the same server.

</details>

## 2. Why isolate Strands and ADK?

<details>
<summary>Answer</summary>

Their declared SDK or telemetry constraints conflict with the main environment.

</details>

## 3. Is FastMCP the official Python SDK?

<details>
<summary>Answer</summary>

No. It is a third-party framework used internally by two client adapters here.

</details>

## 4. Which examples perform complete framework orchestration?

<details>
<summary>Answer</summary>

OpenAI Agents, LangGraph and Pydantic AI; the other adapters have separately described validation levels.

</details>

## 5. Why does a hosted connector need a reachable HTTPS URL?

<details>
<summary>Answer</summary>

The provider is the client and cannot access your machine through your localhost address.

</details>

## 6. What should happen to an approval request?

<details>
<summary>Answer</summary>

Show its exact operation and arguments for a trusted human decision; do not silently approve.

</details>

## 7. Why can a framework test pass without a key?

<details>
<summary>Answer</summary>

Its model fixture is deterministic while tool discovery and execution still use real MCP.

</details>
