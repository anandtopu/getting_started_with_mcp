# Tier 3 checkpoint: secured and tested Lumen workspace

**Time:** 90 minutes. Complete modules 11–13 first. Workspace version 5.

```text
uv sync --frozen --all-extras
npm ci
uv run python checkpoints/03_security/acceptance.py
uv run pytest tests/test_tier3.py
npm run check
```

The acceptance script runs the Tier 2 workspace with its fixed, approved fake-model
conversation, then a separate secured issue connection through the same Chat host
loop. It verifies OAuth failure cases, repair/injection boundaries, traced stdio and
all nine worked exercise contracts. The fixture is local and does not log in a real user.
The complete interactive production host remains a later module.

For provider and container evidence:

```text
docker compose -f deployment/auth/compose.yaml up -d
uv run python scripts/keycloak_check.py
docker compose -f deployment/security/compose.yaml build
uv run python scripts/container_check.py
uv run python scripts/inspector_smoke.py
```

These require Docker or the documented Inspector environment. If unavailable locally,
record that limit and use the corresponding CI result; do not substitute the offline
authority as evidence of Keycloak interoperability. Never run regeneration and snapshot
validation concurrently.

## Self-check

- Explain why an authentic signature is insufficient without audience and issuer checks.
- Show a read token denied a write, then scope step-up with new consent.
- Replay a code and confirm it is rejected; alter the PKCE verifier and confirm rejection.
- Show employee 2's synthetic salary leaking in the vulnerable fixture and denied in the repair.
- Change a pinned tool description and show the host rejects execution before approval.
- Read the poisoned wiki and demonstrate that its requested exfiltration route is unavailable.
- Reproduce the stdout diagnostic and compare a regenerated call snapshot.
- Identify a server error span under the same trace as its client operation.
- Explain why the 30/30 deterministic evaluation does not measure LLM accuracy.
- Review every row of the [filled security checklist](../../docs/SECURITY_CHECKLIST.md),
  including the intentionally vulnerable row and production limitations.

**Pass:** the commands succeed, each denied action has test evidence, and you can
explain the limits without calling the whole workspace production-ready. Tier 4 and
the full Security Audit capstone remain planned.
