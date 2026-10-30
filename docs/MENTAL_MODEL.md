# MCP on one page

MCP connects an application to capabilities and context. The **host** owns the conversation and permission decisions; a **client** is its protocol connection to a **server**. The server can be a local program or a remote service. The model sees descriptions and results, not a grant of authority.

```mermaid
flowchart TB
  U[Person] --> H[Host: UI, model, approvals]
  H --> C1[Client for notes]
  H --> C2[Client for operations]
  C1 -->|stdio pipes| S1[Local server]
  C2 -->|Streamable HTTP| S2[Remote server]
  AS[Authorization server] -->|Audience-bound token| C2
  S2 -->|Verify identity and scope| P[Policy boundary]
  S1 --> F[Tools / Resources / Prompts]
  P --> F
  F --> D[Allowed data and operations]
  E[Extensions: Tasks, Apps, Skills] -. negotiated capability .-> F
  R[Registry and Server Cards] -. discovery candidates .-> H
  D -->|Untrusted evidence| H
  H -->|Review exact proposed action| U
```

**Choose the primitive.** A tool performs a bounded operation. A resource exposes addressable content. A prompt supplies a reusable conversation template. Completion suggests argument values. Catalogs are paginated and can change; refetch them before relying on old meaning.

**Read the exchange.** A request has a JSON-RPC ID and method; its response repeats the ID. A notification has no ID. Revision 2026-07-28 carries protocol and client capability metadata on each request. `server/discover` reports support; it does not create an implicit protocol session. A tool may finish, return an error, ask for input and retry, or return an extension-defined Task handle.

**Keep trust explicit.** A tool description, annotation, skill, registry listing or model proposal cannot authorize execution. The host obtains approval; the server independently checks identity, scope and input. A content digest detects changes, not a trustworthy author. An App runs behind a browser boundary with only its allowed bridge calls.

[Protocol examples](PROTOCOL_GUIDE.md) · [Design choices](CHOOSING_THE_RIGHT_DESIGN.md) · [Security checklist](SECURITY_CHECKLIST.md) · [Glossary](GLOSSARY.md)
