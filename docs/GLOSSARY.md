# MCP glossary

100 terms. Start with Host, Client and Server, then follow the [mental model](MENTAL_MODEL.md).

| Term | Meaning |
|---|---|
| Access token | A credential authorizing limited access; never treat it as ordinary model context. |
| Agent loop | A bounded cycle of model proposals, tool execution, results and another model turn. |
| Annotation | Metadata hint about behavior; it is not a trustworthy permission grant. |
| App bridge | The controlled message channel between the host and an embedded App. |
| Approval | A separate human decision tied to exact arguments and tool meaning. |
| Audience | The intended resource or recipient of a token; verify it exactly. |
| Authorization server | The service that authenticates/consents and issues access tokens. |
| Bearer token | A token usable by whoever possesses it; protect it in transit and storage. |
| Cache scope | Whether cached data can be shared publicly or must stay private to an identity. |
| Cancellation | A request to stop work; it does not prove that no side effect occurred. |
| Capability | A declared protocol feature a peer supports. |
| Client | A protocol component inside a host that talks to one server. |
| Client credentials grant | A token flow for a service identity, without interactive user delegation. |
| Client ID | An OAuth application identifier; not itself a secret. |
| Client ID Metadata Document | An HTTPS document describing an OAuth client under the current registration approach. |
| Compatibility | The ability of two implementations to agree on message behavior. |
| Completion | Suggestions for a prompt argument or resource-template variable; not a model text completion. |
| Content block | One result item, such as text, an image or a resource link. |
| Context window | The input space available to a model for the current inference. |
| CORS | HTTP response rules controlling which browser origins may read cross-origin responses. |
| Cosine similarity | A comparison of vector direction; useful for ranking related concepts. |
| CSP | Content Security Policy: browser rules limiting scripts, connections and framing. |
| Cursor | An opaque continuation value for the next page of results. |
| Deprecated | Still recognized for a transition period, but discouraged for new work. |
| Digest | A content hash used to detect changed bytes; it does not establish a trusted author. |
| Discovery | Reading a peer catalog or capabilities before choosing what to use. |
| Elicitation | A request for user input, such as a confirmation form. |
| Embedding | A numeric representation used to compare semantic similarity. |
| Evaluation | A measured comparison against explicit expected behavior or human criteria. |
| Extension | An explicitly identified addition to the core protocol. |
| Fixture | Controlled synthetic input used to make tests repeatable. |
| FTS5 | SQLite full-text search support used by the knowledge capstone. |
| Gateway | A server that combines fixed upstream servers and adds shared policy. |
| Host | The application that owns the user interface, model conversation and permission decisions. |
| Host header | The HTTP authority requested by the client; validate it to resist rebinding. |
| ID-JAG | An identity assertion exchanged for a resource access token in enterprise authorization. |
| Idempotency | A defined replay behavior that avoids repeating an effect for the same operation. |
| Input response | An accepted, declined or cancelled answer to an embedded input request. |
| Input schema | The allowed argument structure and constraints for a tool. |
| Input-required result | A response asking the client to gather input and retry the operation. |
| Issuer | The trusted identity service that created the token. |
| JSON | A text format for objects, arrays, strings, numbers, booleans and null. |
| JSON Schema | A machine-readable description of valid JSON data. |
| JSON-RPC | A message format describing requests, results, errors and notifications. |
| JWKS | A published set of JSON signing keys from a configured trusted issuer. |
| JWT | JSON Web Token: encoded claims whose signature and claims must be verified. |
| Least privilege | Grant only the operations and data needed for the current purpose. |
| Legacy | Older behavior shown only to help migrate or interoperate with existing systems. |
| LLM | Large Language Model: a model generating text and structured tool proposals. |
| MCP | Model Context Protocol: a shared message contract for connecting AI applications to capabilities and context. |
| MCP App | An extension-defined interactive UI associated with a server tool and resource. |
| Method | The protocol operation name, such as tools/list. |
| Namespace | A prefix separating otherwise identical names from different sources. |
| Notification | A message without a request ID; it receives no response. |
| OAuth | A framework for delegating limited access without sharing the user password. |
| Origin | A browser security identity made from scheme, hostname and port. |
| Output schema | The promised structure of a tool structuredContent result. |
| Pagination | Splitting a large catalog or result into bounded pages. |
| PKCE | A proof binding an authorization code to the client that started the flow. |
| Polling | Checking state repeatedly within a time and request budget. |
| Principal | The verified user or service identity to which policy and ownership apply. |
| Progress token | A request-chosen correlation value for progress notifications. |
| Prompt | A named template that returns messages for a model conversation. |
| Prompt injection | Untrusted content trying to change the assistant or host behavior. |
| Protocol revision | A dated specification version; distinct from a package version. |
| Rate limit | A bounded request allowance over time, usually per verified principal. |
| Redaction | Removing credentials or private values from diagnostics and captures. |
| Refresh token | A credential used to obtain new access tokens under the issuer policy. |
| Registry | A catalog of server metadata; a listing is not a security endorsement. |
| Request | A message with a method and ID that expects a correlated response. |
| Request ID | A value used to match an answer to the request that caused it. |
| Request state | Opaque server-owned retry data; protect it against tampering and replay. |
| Resource | Addressable content that a client can read by URI. |
| Resource server | The service receiving tokens before exposing protected operations. |
| Resource template | A URI pattern with variables, such as wiki://{space}/{page}. |
| Response | A result or error carrying the ID of its request. |
| Root | A client-declared filesystem boundary hint; enforcement still belongs to the server. |
| Sampling | A deprecated capability asking a host model to generate content; see the migration guide. |
| Sandbox | An enforced execution boundary that limits access, not simply a label on code. |
| Scope | A named permission granted by an authorization server, such as issues:read. |
| SDK | Software Development Kit: code that implements reusable protocol mechanics. |
| SEP | Spec Enhancement Proposal: a documented proposal reviewed through MCP governance. |
| Server | A program exposing tools, resources or prompts through MCP. |
| Server Card | Experimental discovery metadata describing a server and candidate endpoints. |
| Skill | A discoverable instruction bundle; discovering it does not authorize activation. |
| stderr | The separate diagnostic stream; a safe place for local server logs. |
| stdio | Standard input/output pipes connecting a host to a local child process. |
| Streamable HTTP | The current HTTP transport for MCP requests and streamed responses. |
| Structured content | Machine-readable result data, useful alongside human-readable text. |
| Subscription | A filtered channel delivering changes while its listener is active. |
| Task | An extension-defined handle for work whose state can be polled and updated. |
| Timeout | A deadline after which the caller stops waiting; the outcome may be uncertain. |
| Token | A model text unit; distinguish this from an OAuth access token. |
| Tool | A named operation with a description and an input schema that a client can call. |
| Tool calling | A model proposing a named operation and arguments for the host to evaluate. |
| Trace | A linked record of operations and timings for diagnosis. |
| Transport | The mechanism carrying protocol messages between peers. |
| TTL | Time to live: how long a cached value or task may remain usable. |
| URI | Uniform Resource Identifier: a name for content, not necessarily a downloadable web address. |
| URL | A locator specifying how and where to access a resource. |
