# Lumen notes course package

<!-- mcp-name: io.github.anandtopu/lumen-notes -->

Synthetic, ephemeral notes over stdio. This educational package is built and
smoke-tested locally; it has not been uploaded to TestPyPI or PyPI.

`lumen-notes` starts the server. `LUMEN_NOTES_READ_ONLY=true` is the default;
set it to `false` to expose create/tag tools that still require explicit
confirmation. New notes disappear on restart. There are no secrets or file reads.

The source is maintained in the course's common notes module and included by the
build. To publish your own copy, choose a package name you control, build from
the repository, review the artifacts and use the Module 18 publishing instructions.
