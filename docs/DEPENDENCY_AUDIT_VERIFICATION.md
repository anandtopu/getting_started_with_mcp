# Remaining dependency findings: resolution and verification

Date: 2026-10-30. Baseline: `f11ceb5`.

The 13 moderate npm findings were affected dependency nodes from two advisories,
not 13 independent vulnerabilities:

- [minimatch pattern amplification](https://github.com/advisories/GHSA-g3hv-75wg-m249),
  patched in 11.0.1. The lockfile used 10.2.6.
- [glob traversal continuing after cancellation](https://github.com/advisories/GHSA-3g3m-2fjr-6pw4),
  patched in 14.0.2. The lockfile used 13.0.6.

The dependency tree now resolves minimatch **11.0.3** and glob **14.0.3**.
`npm audit --json` reports **zero vulnerabilities at every severity**. The
required Node CI matrix now runs `npm audit --audit-level=low`, with no omitted
dependency groups or advisory allowlist.

## Compatibility and scope

Current parent releases still request minimatch 10 and glob 13. Updating the
parents alone does not resolve these findings; the audit's suggested ESLint 4
downgrade is not an appropriate fix for this ESLint 10 course. Two explicit
overrides retain the current application and tooling versions:

- `minimatch@>=10 <11` resolves to 11.0.3 for ESLint, its config-array dependency,
  typescript-estree and the filesystem reference server.
- Only `@modelcontextprotocol/server-filesystem@2.1.0` has its glob dependency
  replaced with 14.0.3. Glob 14 itself requests minimatch 11 and path-scurry 3.

These are reviewed major-version overrides, not assumed patch compatibility.
The published minimatch declaration diff removes regex-oriented APIs such as
`makeRe` and `AST`; the installed consumers above use the retained `Minimatch`,
`match` and `minimatch` interfaces. Glob is upgraded together with minimatch so
its traversal code consumes the new matching representation. Their engine
ranges include both Node 24 and 26 used by this repository. The lockfile adds
the upstream `@isaacs/nonrecursive-glob-match` dependency and updates path-scurry
to 3.0.0; application package versions stay unchanged.

## Acceptance

[Dependency regressions](../scripts/dependencies.test.mjs) exercise the actual
consumers: ESLint recursive TypeScript discovery, ignored directories and typed
project-service matching; the reference filesystem MCP server's recursive search,
dotfiles, exclusions and denied access outside its allowed directory; normal
glob traversal and cancellation between a directory read and its callback;
bounded minimatch pattern expansion; and every affected lockfile instance.
The glob regression observes filesystem reads after cancellation rather than
only checking that the promise rejects.

Local compiler, ESLint and native tests passed: **158 tests passed** across
34 files, with the existing Windows symlink skip. The full Python suite passed
**249 tests**, with one Windows symlink-permission skip and the existing LangChain
beta API warning. Ruff check/format, the release contract and local documentation
links passed. The initial focused run caught a
Windows separator assumption in the new test, corrected by normalizing returned
paths before comparison; no runtime behavior was changed for that correction.

The [first CI run](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41163436532)
on `f29fe99` exposed a second fixture portability issue:
Windows runners can use an 8.3 alias for their temporary directory, whereas the
filesystem server correctly returns canonical paths. The fixture now resolves
its temporary root with `realpathSync.native` before making exact relative-path
assertions. The search and allowed-directory assertions remain unchanged.

That superseded run was stopped after publishing the fixture correction.
[The complete corrected CI run passed all 29 required jobs](https://github.com/anandtopu/getting_started_with_mcp/actions/runs/41163625829)
on `d13a210c626fc128094d686352b0355eb17f4640`. The optional manual external-link
job was skipped. All four Node 24/26 Windows/Linux jobs completed clean locked
installs and reported **zero vulnerabilities**. Linux passed all **159 native
tests**; Windows passed 158 with the existing symlink skip.

The full Python 3.12–3.14 Windows/Linux matrix and macOS 3.12 passed, including
the standalone course examples and checkpoints. Inspector, four other SDKs,
framework adapters, isolation, both package build/installed-launch paths,
browser acceptance, native Chat Pro/OAuth deployment and ops deployment also
passed. The corrected run needed no further repair or retry. The dependency
versions did not change during the Windows fixture correction.

## Maintaining the overrides

Keep the exact pins and regression tests until parent releases declare compatible
patched ranges. When removing or updating an override, inspect `npm ls minimatch
glob`, perform a clean locked install, run the dependency regressions and full
native checks, and require a clean audit plus the full CI matrix. Update the
lockfile pin assertions alongside an intentionally reviewed version change.
Do not edit installed dependencies or suppress audit reports.
