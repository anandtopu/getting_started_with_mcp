# Tier 1 checkpoint: Lumen Chat v1

Build and explain one host connected to **your notes server**, **your wiki server**,
and the **official filesystem reference server** restricted to `data/files`.

From the repository root:

```text
uv sync
npm ci
uv run python modules/06_building_a_host/python/use_case/main.py --demo
```

The deterministic fixture performs exactly these reviewed actions:

1. Search notes for `release`.
2. Find `wiki://engineering/page-01`.
3. List the reference server's allowed directories.
4. Create the in-memory note `Reviewed handover`, with body `Check the wiki.`

It prints each requested name and argument dictionary, then ends with:

```text
Fixture complete: checked three servers and created one approved ephemeral note.
read-1: complete
read-2: complete
read-3: complete
write-1: complete
```

`--demo` approves only these exact fixture actions and always uses fake model
turns. It does not grant arbitrary approval. Notes reset when the process closes;
committed files are unchanged. Run without `--demo` for individual interactive
approval decisions. Configure a real provider through `.env` only if desired;
default fake mode performs one notes search and a fixture response.

## Show that you understand the mechanism

- Trace a `tools/list` request and its schema into one provider's tool definition.
- Explain the difference between a provider call ID and an MCP JSON-RPC ID.
- Show where the host rejects an unknown tool and invalid arguments.
- Deny a proposed write and prove the notes list did not change.
- Explain why a model cannot supply its own `confirmed` flag.
- Explain why a readOnlyHint alone cannot authorize a call.
- Read a resource link, retrieve a prompt, and explain who selected each primitive.
- Follow an empty pagination page and stop at the terminal cursor.
- Open a resource listener before a write and refetch after invalidation.
- Explain what fake tests prove and what requires a live model/host check.

## Acceptance checks

```text
uv run pytest
npm run check
uv run python scripts/tier1.py
uv run python scripts/check_course.py
```

The checked-in [notes](wire/notes.jsonl), [wiki](wire/wiki.jsonl), and
[filesystem](wire/files.jsonl) captures preserve the real server interactions.
Provider histories use offline fixtures in the tests. No credentials are needed.

You are ready for Tier 2 when you can recreate the loop without a framework,
explain a failed request from its JSON, and demonstrate that a denied write does
not run. Continue with modules 07–10 in the [learning path](../../LEARNING_PATH.md)
when the next phase is delivered.
