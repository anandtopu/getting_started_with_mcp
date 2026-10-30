# Phase 7 verification — 2026-10-30

Target: MCP 2026-07-28, Python SDK 2.3.0, TypeScript SDK 2.4.0.
Modules 18–21 include twelve examples, four finite use cases, twelve starter/solution
pairs, four seven-question quizzes, sixteen external-host configs and five actual
wire captures (including a legacy handshake). Phase 8 remains incomplete.

## Sources and pins

| Component | Pin / source | Evidence |
|---|---|---|
| Python package backend | Hatchling 1.33.0; [uv packaging](https://docs.astral.sh/uv/guides/package/) | Wheel/sdist built; sdist rebuilt outside checkout |
| MCPB | CLI 2.1.2, manifest 0.3; [manifest](https://github.com/modelcontextprotocol/mcpb/blob/main/MANIFEST.md) | Official CLI validate/pack and ZIP inventory |
| Registry publisher | v1.8.7; [release](https://github.com/modelcontextprotocol/registry/releases/tag/v1.8.7) | Release checksum checked; executable version/help and official online validation passed |
| Registry schema | 2025-12-11; [official schema](https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json) | Vendored schema and identity/version validation |
| Registry API | [reference](https://github.com/modelcontextprotocol/registry/blob/main/docs/reference/api/official-registry-api.md) | Offline two-page HTTP fixture; bounded opt-in live reader |
| Browser tests | Playwright 1.64.1, Chromium 156.0.8078.4 | Real approvals, input, Tasks and App isolation tests |
| Proxy | NGINX 1.30.6-alpine3.24; [official image](https://hub.docker.com/_/nginx) | Pinned Compose configuration |
| Identity | Keycloak 26.8.1 | Existing Phase 5 PKCE/resource/scope flow extended through proxy/web host |

The official `mcp-publisher validate distribution/registry/server.json` returned
`server.json is valid`. This validation did not publish metadata or prove that the
proposed npm artifact has been released.

## Local evidence

The Python wheel and npm tarball launch through uvx/npm exec from a temporary
directory outside the checkout. Offline installation passes after an explicit
dependency preparation step. The uv cache and interpreter are passed explicitly,
because a child stdio environment on Windows does not inherit every host setting.

The four module runners pass and record actual stdio/HTTP messages. Legacy mode
negotiates 2025-11-25 with the current SDK's real compatibility transport. This is
not a test against a separately installed historical SDK or vendor host.

The focused shipping tests cover archive secrecy/traversal, sdist independence,
metadata identity, registry cursor cycles, public URL policy, limiter bounds,
config rejection, actual reconnect, full-definition approval invalidation,
read-only retry policy, one-use decisions, CSRF/Origin/Host and concurrent session
capacity. Browser tests passed on Windows and screenshots were visually inspected
at desktop and mobile sizes. App tests prove parent DOM access and external fetch
are blocked, then exercise the allowed refresh and bridge teardown.

Docker CLI is installed locally but its Linux engine is not running. The shipping
CI job builds the notes image, exercises it with an MCP client, builds the full
Keycloak/issues/NGINX stack, runs real OAuth plus web-host approval through the
proxy, and tears down in an always-run step. Final CI outcomes are recorded below
after the implementation run completes.

## Scope and limitations

- No TestPyPI/npm/registry upload, real identity login, paid cloud deployment or
  live model request was performed. These remain explicit learner choices.
- MCPB CLI validation is tested; Claude Desktop bundle installation and the four
  external host GUIs are not claimed as tested. Existing host-format documentation
  remains the basis for generated configs.
- Cloud hosting options were checked against official [AWS](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html),
  [Google](https://docs.cloud.google.com/run/docs/host-mcp-servers) and
  [Microsoft](https://learn.microsoft.com/en-us/azure/container-apps/mcp-overview)
  documentation. Protocol compatibility and actual cost need deployment-specific validation.
- The web host is local/single-user. It accepts trusted configured HTTP endpoints
  and server-side bearer tokens, but provides no browser OAuth login/refresh or
  public multi-tenant session service. SQLite, sessions, rate limits and Task state
  are process-local; scale-out and restart durability require further work.
- The MCPB build CLI depends on Zod 3, which currently has an upstream npm advisory
  for oversized constrained collections. Runtime bundles use patched Zod 4.6.7.
  The build accepts only this repository's reviewed manifest, uses a deadline and
  a bounded Node heap; do not use it as an upload service for arbitrary manifests.
  The transitive tmp advisory is addressed by the root override. Do not force Zod 4
  into a Zod 3 converter and claim compatibility without testing.

The release gate intentionally continues to fail until Phase 8 bonuses, capstones
and final reference material are delivered.
