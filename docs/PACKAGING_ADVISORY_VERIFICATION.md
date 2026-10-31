# MCPB packaging advisory follow-up

Date: 2026-10-30. Baseline: `1586a96`.

This record describes the packaging implementation at `1224c45`. The later
[dependency audit follow-up](DEPENDENCY_AUDIT_VERIFICATION.md) resolves the 13
moderate findings recorded below and strengthens the CI audit gate to all severities.

R-010 is resolved in the repository by removing `@anthropic-ai/mcpb@2.1.2`
and its nested Zod 3.25.76. The latest upstream CLI still requires Zod 3;
[GHSA-mrhx-c7xc-m3w5](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5)
is fixed in Zod 4.6.6. No incompatible major-version override is used.

Both build paths now invoke `scripts/mcpb.mjs`, a native Node helper with only
`validate` and `pack` operations. It uses Ajv 8.20.0, ajv-formats 3.0.1 and
fflate 0.8.3. The official MCPB 0.3 schema is vendored unchanged with its
MIT license, source version and SHA-256; see [provenance and supported scope](../distribution/mcpb/schema/README.md).
The resulting artifact is a standard ZIP with its manifest at the root.
The Notes build-cache digest includes the helper and schema.

Regression coverage checks both manifests, schema provenance, strict validation
and URI/email formats, deterministic archives, extracted execution, invalid CLI
exit status, missing/escaping entry points, private/dependency paths, symlinks,
byte/entry/depth limits and the locked dependency tree. Windows skips the
symlink test because unprivileged symlink creation is not generally available;
Linux CI exercises it. Both package smoke checks launch real MCP servers from
the built artifacts outside the checkout, including the extracted Notes bundle.

The required TypeScript CI matrix runs `npm audit --audit-level=high` in
addition to the compiler, lint and regression suite. A fresh audit after the
replacement reports **zero high or critical findings** and no affected Zod or
MCPB node. It still reports **13 moderate dependency nodes** in ESLint,
typescript-eslint and the filesystem reference server's glob/minimatch trees.
These are separate from R-010; this change does not claim an entirely clean audit.

Local validation: compiler and ESLint passed; 153 native tests passed with one
Windows symlink skip. Both packaging commands passed with dependency preparation
and again using cached dependencies: Notes wheel/npm/extracted MCPB and Knowledge
wheel/extracted MCPB all completed real MCP calls outside the checkout. Ruff
check/format and the release/local-link checker passed. The full Python suite
passed **249 tests**, with one Windows symlink-permission skip and the existing
LangChain beta API warning.

[GitHub CI passed all 29 required jobs](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41161721989)
on implementation commit `1224c4581eb15cef11cc8edea96276f137a26640`, without repair
or rerun. The optional manual external-link job was skipped. The Node 24/26
Windows/Linux matrix passed the audit gate and native checks; Linux ran all
**154 tests**, including symlink rejection, while Windows skipped that one
test. The shipping job passed both package checks with preparation and again
from cached dependencies, all three browser scenarios, container shipping and
OAuth deployment. Native Chat Pro browser/gateway deployment, Python 3.12–3.14
Windows/Linux plus macOS 3.12, course examples/checkpoints, framework adapters,
Inspector, isolation, ops deployment and four other SDKs also passed.

Desktop GUI installation remains a manual host-specific check. No public
package publication or desktop install is performed by this build helper.
