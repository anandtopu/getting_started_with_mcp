# Tier 5 / Shipping

Install, deploy, operate and recover. [Printable one-page PDF](05_tier_5.pdf).

## Packages

- Build wheel/sdist, npm package and MCPB bundle from reviewed source. Inspect archive contents.
- Launch installed packages outside the checkout; test uvx/npx and environment configuration.
- Publication is separate from local packaging and requires the learner account.

## Registry

- Validate server.json against the pinned official schema and match package identity/version.
- Verify namespace ownership before publishing. Registry metadata is discovery, not endorsement.
- Review candidate endpoints and dependencies before installation or credential disclosure.

## Remote operations

- Use HTTPS externally, exact public resource URLs and configured trusted key endpoints.
- Separate health/readiness from protected data; limit rates, bytes, runtime and costs.
- Single-worker teaching state must become shared durable state before scaling out.

## Production host

- Bound connection attempts and calls. Retry only locally allowlisted reads; reconcile uncertain writes.
- Refetch changed catalogs and revoke stale approvals.
- Keep provider credentials server-side; isolate App frames and enforce their tool allowlist.

## Run and teardown

- uv run python scripts/package_lab.py --prepare
- npm run build:chat; npm run test:browser
- Use the documented Docker Compose stack; stop it afterward. Remove persistent volumes only intentionally.

## Checkpoint

- Prove installed launches, OAuth rejection, host approval/decline, Tasks and App isolation.
- Finish Ops and Chat Pro capstones; review docs/DEFINITION_OF_DONE.md.

[Full protocol guide](../docs/PROTOCOL_GUIDE.md) · [Learning path](../LEARNING_PATH.md)
