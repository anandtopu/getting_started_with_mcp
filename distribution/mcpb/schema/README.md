# MCPB manifest schema provenance

`manifest-v0.3.schema.json` is copied without changes from
`@anthropic-ai/mcpb@2.1.2/dist/mcpb-manifest-v0.3.schema.json` (MIT;
the upstream license is included here as `LICENSE`).

SHA-256: `3a0ac9d845711a1b9b17dfa5a52f8b60628239d6a86a9db417206a9efc78592d`.

Upstream: <https://github.com/modelcontextprotocol/mcpb>.
Format documentation: <https://github.com/modelcontextprotocol/mcpb/blob/main/MANIFEST.md>.

The course uses this static draft-07 schema with Ajv and `ajv-formats`;
it does not install or execute the upstream CLI. `scripts/mcpb.mjs` additionally
requires `manifest_version: "0.3"`, because the upstream version-presence
refinement is absent from the generated schema, and checks portable entry paths.

This deliberately scoped helper supports only `validate <manifest.json>` and
`pack <staged-directory> <output.mcpb>`. Packing writes a standard ZIP with
`manifest.json` at its root, using fflate (also used by the upstream packer).
It requires an existing output parent outside the source, includes all staged
regular files, rejects symlinks and private/dependency paths, and enforces 64 KB
manifests, 64 MiB total input, 512 entries, and 16 path components. Stage only
the intended distribution files. It does not interpret `.mcpbignore`, install,
unpack, sign, or implement the upstream CLI's optional asset checks.

To update the schema, review the upstream schema and refinements, replace the
schema and attribution together, and run the packaging regression tests plus
both isolated installed-artifact smoke checks. Keep the dependency audit gate;
do not restore the vulnerable CLI or override its Zod major version.
