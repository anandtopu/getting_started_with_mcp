# Contributing

This course targets beginners. Explain jargon before using it, keep examples focused, and show a real captured exchange for every protocol feature. Read the [plan](docs/PHASE_1_PLAN.md) and [coverage map](docs/FEATURE_MAP.md) before adding a lesson.

Run `uv sync` and `npm install`, then the checks listed in [README.md](README.md). Install local hooks with `uv run pre-commit install`. Use `uv sync --all-extras` for provider-adapter tests. No API keys are required. Live tests must use the `live` marker and are skipped by default.

Use type hints, docstrings with runnable commands, and stderr for stdio diagnostics. Put shared logic in `common/`. Verify imports against the locked SDK; do not copy old tutorials. Any intentional API substitution belongs in verification notes.

Keep fixtures synthetic and deterministic. Never attach real credentials or customer data. When changing generated fixtures, update the generator and run it, then verify the manifest and reproducibility test. Change captured traffic only by running the capture command; inspect it for accidental data disclosure.

A contribution should include the problem, resulting behavior, exact check results, and limitations. Add meaningful regression tests for behavior changes. Examples that require an external service need an offline fixture path. Do not claim a complete module based on file count alone.

Report content errors using the issue template with the module, quoted sentence, and primary source. For a suspected security issue, use the repository's private vulnerability reporting if enabled; otherwise contact the repository owner without posting exploit details or secrets publicly.
