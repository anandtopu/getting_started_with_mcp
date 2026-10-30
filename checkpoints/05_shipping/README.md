# Tier 5 checkpoint: release rehearsal

Allow 90 minutes. Complete [packaging](../../modules/18_packaging/README.md),
[registry](../../modules/19_registry/README.md), [deployment](../../modules/20_deployment/README.md)
and [Lumen Chat v4](../../modules/21_production_hosts/README.md).

You are ready when a fresh checkout can build inspectable artifacts, validate
metadata, run the secured local stack, show human decisions in the browser, and
remove the services afterward. Publication and cloud accounts are unnecessary.

```text
uv sync --all-extras
npm ci
uv run python scripts/package_lab.py --prepare
uv run python scripts/package_lab.py
uv run python checkpoints/05_shipping/acceptance.py
docker build -f distribution/notes.Dockerfile -t lumen-notes-course:1.0.0 .
uv run python checkpoints/05_shipping/acceptance.py --container
docker compose -f deployment/compose.yaml up --build -d --wait --wait-timeout 120
uv run python scripts/keycloak_check.py --deployed
npm run build:chat
npx playwright install chromium
npm run test:browser
docker compose -f deployment/compose.yaml down --remove-orphans
```

Stop the old `deployment/auth/compose.yaml` lab before starting the full stack.
If you use a named local container context, add `--docker-context <name>` to the
container acceptance command and use that same context for build/Compose.
The scripts print PASS for package launch, module contracts, container protocol,
PKCE/audience/scope step-up and web-host approval through the proxy. Browser tests
cover refusal, approved reads, input, cancellation, App refresh/isolation and mobile
layout. Teardown belongs to the checkpoint even if a preceding check fails.

| Evidence | Points |
|---|---:|
| Wheel/sdist/npm/MCPB inspected; installed launch outside checkout | 20 |
| Identity/version match; explain why registry metadata grants no trust | 15 |
| Authenticated proxy deployment, rejected unauthenticated access | 20 |
| Browser approval, elicitation, Task cancellation and App isolation | 25 |
| Older handshake, changed-definition rejection, no write retry | 10 |
| Teardown, secret-free artifacts and stated scaling/cost limits | 10 |

Target 90/100 with no missing authorization or teardown requirement. If Docker is
unavailable, the default acceptance command still verifies loopback middleware;
record the container gap and complete it on a Docker-capable machine or CI.

Extend it: add a shared durable issue store, a shared limiter, or browser OAuth
login/refresh with per-user identities. Each needs its own negative tests. The
larger Lumen Ops and Chat Pro capstones remain planned for Phase 8.
