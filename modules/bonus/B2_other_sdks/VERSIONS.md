# Native SDK verification — 2026-10-30

| Language | SDK pin | Official tier | Tested revision | Build |
|---|---|---|---|---|
| Go | github.com/modelcontextprotocol/go-sdk v1.8.0 | 1 | 2026-07-28 | Go 1.26; go.mod/go.sum |
| C# | ModelContextProtocol 2.3.0 | 1 | 2026-07-28 | .NET 10; packages.lock.json |
| Rust | rmcp 3.8.0 | 1 | 2026-07-28 | Rust 1.96+; Cargo.lock |
| Java | io.modelcontextprotocol.sdk:mcp 2.1.0 | 2 | **Legacy 2025-11-25** | JDK 17+; Maven pinned dependencies |

Sources: [official inventory](https://modelcontextprotocol.io/docs/sdk), [Go release](https://github.com/modelcontextprotocol/go-sdk/releases/tag/v1.8.0), [C# release](https://github.com/modelcontextprotocol/csharp-sdk/releases/tag/v2.3.0), [Rust release](https://github.com/modelcontextprotocol/rust-sdk/releases/tag/rmcp-v3.8.0), [Java release](https://github.com/modelcontextprotocol/java-sdk/releases/tag/v2.1.0).

Kotlin is official Tier 3; this lesson selects Java for the Java-or-Kotlin option. Official status does not imply current-revision support. Java's current stable line is intentionally an interoperability lesson, not a current-protocol implementation. See [migration](../../../docs/MIGRATING_FROM_OLDER_VERSIONS.md).

Run each `scripts/native_sdks.py --language NAME --build --capture` command from the root. Dependency downloads happen during build. The subsequent protocol contract is offline and uses one disposable child process. C# requires the SDK, not just the runtime. `go test` is an additional native in-memory client example; the shared Python client is the third example for C#, Java and Rust.
