# Troubleshooting

Start with `uv run python scripts/check_env.py`. Run commands at the repository root. Preserve a redacted capture, exact versions and the failing command before changing configuration.

## Server does not appear in the host

**Symptom:** `Connection closed / server failed to start`.

**Fix:** Run the exact configured command in a terminal. Use an absolute executable and checkout path, regenerate host configs, and inspect stderr. Verify the host trusts/enables the server.

## Logs corrupt stdio

**Symptom:** `Unexpected token / invalid JSON / connection closed`.

**Fix:** Remove print statements from the server protocol stream. Send diagnostics to stderr. Run scripts/run_all_examples.py; wiretap reports non_json_bytes for contamination.

## Windows cannot find a launcher

**Symptom:** `'uvx' is not recognized / spawn npx ENOENT`.

**Fix:** Install uv and Node, restart the host so it inherits the new PATH, then run scripts/check_env.py. Use the resolved executable in generated configs. Do not add shell quoting inside individual JSON arguments.

## Paths and quoting

**Symptom:** `FileNotFoundError / ERR_MODULE_NOT_FOUND`.

**Fix:** Use one JSON array item per argument. Prefer forward slashes or escaped backslashes in Windows JSON. The launch_ts.cjs helper resolves dependencies from the checkout, independent of host cwd.

## Different protocol revisions

**Symptom:** `Unsupported protocol version / -32022`.

**Fix:** Inspect supported revisions. Use the explicit current client for course servers, or the labeled compatibility mode for an older peer. Do not change only a header while retaining old message shapes.

## Copied v1 imports

**Symptom:** `ModuleNotFoundError`.

**Fix:** Recreate the environment with uv sync and follow the current imports in the migration guide. The import text and old/new pair appear only there.

## Origin or browser CORS failure

**Symptom:** `403 / Invalid Origin / blocked by CORS policy`.

**Fix:** Match the configured exact scheme, host and port. Do not use a wildcard with credentials. CORS response permissions and server Origin validation are separate checks.

## OAuth discovery fails

**Symptom:** `IssuerMismatchError / invalid_resource / 401`.

**Fix:** Compare the configured issuer with its metadata issuer exactly. Verify the advertised token endpoint, trusted key endpoint and resource URL. Follow the protected-resource metadata challenge rather than guessing discovery paths.

## Wrong token audience

**Symptom:** `401 Unauthorized`.

**Fix:** Acquire a token whose aud is this MCP resource. Tokens for the issuer, another API, or another port must fail. Do not forward the incoming token to upstream services.

## The model never calls a tool

**Symptom:** `Text answer with no tool call`.

**Fix:** First list tools with a plain SDK client. Enable the host tools, use a precise request, and check descriptions/provider conversion. Use the fake-model test to isolate plumbing. A real model is allowed to answer without a tool.

## Notebook event loop conflict

**Symptom:** `asyncio.run() cannot be called from a running event loop`.

**Fix:** In Jupyter use await your_async_function() in a cell. In a standalone script use asyncio.run(main()). Do not patch or nest event loops to hide ownership errors.

## HTTP metadata mismatch

**Symptom:** `-32020: mcp-method header does not match the request body`.

**Fix:** Use the official transport, which derives headers from the request. For raw tests set Mcp-Method and Mcp-Name consistently with the body; do not trust routing headers for authorization.

## Approval expired or changed

**Symptom:** `Unknown, changed or expired review / Tool changed; review again`.

**Fix:** Rediscover, show the current definition and exact arguments, and obtain a new user decision. Never reuse a consumed ticket.

## TypeScript task handle rejected

**Symptom:** `Invalid tools/call result`.

**Fix:** Read B1 module 17: SDK 2.4.0 has no current Task-result hook. The bounded transport-level receiver is tested against the released Tasks shape; legacy task types are not a substitute.

## Native compiler missing

**Symptom:** `go, dotnet, cargo or mvn not found`.

**Fix:** Install only the toolchain for the optional B2 language you selected. Follow B2 VERSIONS.md. Main Python/TypeScript tests do not require native compilers.

## Package not found offline

**Symptom:** `No solution found when resolving / package not cached`.

**Fix:** Run the documented --prepare build once with network access. Installed offline smoke tests then use the existing cache. Fresh installation is distinct from offline execution.

[Host setup](HOST_SETUP.md) · [Migration](MIGRATING_FROM_OLDER_VERSIONS.md) · [Protocol guide](PROTOCOL_GUIDE.md)
