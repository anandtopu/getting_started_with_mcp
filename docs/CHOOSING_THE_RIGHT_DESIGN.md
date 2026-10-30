# Choose the smallest useful MCP design

Start with the user action and its trust boundary. Each choice below has a runnable example; combine primitives when a workflow needs more than one.

## Tool, resource or prompt?

```mermaid
flowchart TD
 A[What does the caller need?] --> B{Perform an operation or parameterized search?}
 B -->|Yes| T[Tool: search_knowledge]
 B -->|No| C{Read content at a stable URI?}
 C -->|Yes| R[Resource: knowledge://notes/release.md]
 C -->|No| P[Prompt: summarize_note]
 T --> X[Link results to source resources]
```

The [knowledge server](../capstones/01_personal_knowledge/README.md) uses all three: search finds candidates, resources expose sources, and prompts guide a grounded summary. A prompt still contains data that the host reviews before adding to model context.

## stdio or Streamable HTTP?

```mermaid
flowchart TD
 A[Who starts and uses the server?] --> B{One local host can own a child process?}
 B -->|Yes| S[stdio: simplest local boundary]
 B -->|No| H[Streamable HTTP: shared remote service]
 H --> O[OAuth, audience validation, HTTPS, Origin and rate controls]
 S --> P[Absolute paths, minimal environment, protocol-only stdout]
```

Use [notes packaging](../modules/18_packaging/README.md) for local installs and [Ops](../capstones/04_lumen_ops/README.md) for remote access. HTTP adds deployment and identity responsibilities; localhost alone is not user authentication.

## One server or a gateway?

```mermaid
flowchart TD
 A[Several capability domains] --> B{Same owners, permissions and lifecycle?}
 B -->|Yes| S[One cohesive server]
 B -->|No| M[Separate upstream servers]
 M --> C{Need one catalog and central per-user policy?}
 C -->|Yes| G[Gateway with fixed routes and audit]
 C -->|No| H[Host connects to several clients]
```

The [gateway](../capstones/03_lumen_gateway/README.md) filters discovery and rechecks every call. Keep upstream credentials separate and define partial-failure behavior. Namespacing prevents collisions; it does not provide authorization.

## MCP or plain function calling?

```mermaid
flowchart TD
 A[Need a model to propose operations] --> B{Only one application owns the implementation?}
 B -->|Yes| C{Need reuse across independent hosts?}
 C -->|No| F[Plain function calling may be enough]
 C -->|Yes| M[Publish an MCP boundary]
 B -->|No| M
 M --> D[Versioned discovery, schemas, transports and policy]
 F --> P[Still validate arguments and obtain approval]
```

MCP standardizes the external boundary; it does not replace the model's tool-calling format. [Module 06](../modules/06_building_a_host/README.md) converts MCP definitions into provider formats and keeps model proposals separate from execution.
