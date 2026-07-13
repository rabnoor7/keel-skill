# Docker — local-first, dev and test

The Python backend is **always dockerized**, and local-first is the floor: the whole stack
must run on a fresh machine with `docker compose up`. Cloud target (Railway / GCP / AWS / etc.)
is chosen per project and may change — don't bake a specific cloud into the core setup.

## docker-compose (dev)

Services:

- **db** — Postgres (pinned major version). Healthcheck so dependents wait for readiness.
  Volume for persistence in dev.
- **backend** — FastAPI container, depends_on db (healthy), runs uvicorn with reload in dev,
  applies Alembic migrations on start.
- **frontend** — Next.js dev server (optional in compose; many run it on the host with pnpm).

Environment via `.env` (gitignored). The auth-provider switch (`references/database.md`) is an
env var here — local sets the email/password provider.

## Test database

API tests run against a **real Postgres**, not a mock and not SQLite:

- Either a dedicated `db-test` compose service, or an ephemeral Postgres container spun up for
  the test run and torn down after.
- Migrations are applied to the test DB before tests; the DB is reset between runs (fresh
  schema or transaction rollback per test).
- This is why "Postgres everywhere" matters: the tests exercise real dialect and constraints.

## Dockerfile (backend)

- Small base (`python:3.x-slim`), multi-stage if build deps are heavy.
- Install deps as a separate, cached layer before copying app code.
- Non-root user. No secrets baked into the image — they come from the environment at runtime.

## Frontend build

Next.js typically deploys separately (often Vercel or a Node container). For container parity,
a multi-stage Dockerfile (deps → build → run with `next start`) is fine. Decide per project and
record it in `docs/architecture.md`.

## Reductio for "it works on my machine"

If something runs locally but the claim is "Docker is the same", assume the opposite: the
container differs. Then either an env var, a mounted volume, a build-cache staleness, or a
service-start-order race must explain it. Walk those four; one of them is it.
