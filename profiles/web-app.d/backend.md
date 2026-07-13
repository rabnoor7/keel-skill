# Backend conventions — FastAPI, dockerized

Default backend. Applies to **new** code; on existing projects, precedence rules
(`references/memory.md`) decide — conform to what's there.

## Stack

- **FastAPI** + **uvicorn**, async.
- **SQLAlchemy 2.x** (typed, `Mapped[...]`) + **Alembic** for migrations.
- **Pydantic v2** for request/response schemas and settings.
- **pytest** + **httpx** AsyncClient for API tests.
- Dependency management: `pyproject.toml` (uv or pip-tools). Always **dockerized** — the
  backend runs in a container in dev, test, and prod (`references/docker.md`).

Verify current versions and idioms with web search before scaffolding; these move.

## Layout

```
backend/
  app/
    main.py            FastAPI app factory, router registration
    config.py          Pydantic Settings (env-driven; see auth contract below)
    db/
      session.py       engine + session dependency
      base.py          declarative Base
    models/            SQLAlchemy models, one module per aggregate
    schemas/           Pydantic request/response models
    api/
      deps.py          shared dependencies (get_db, get_current_user)
      routes/          one router module per resource
    services/          business logic — routes stay thin, call services
    auth/              the auth contract + providers (see database.md)
  alembic/             migrations
  tests/               pytest; mirrors app/ structure
  pyproject.toml
  Dockerfile
```

## Conventions (the DRY rules)

- **Routes are thin.** A route validates input, calls a service, shapes the response. Business
  logic lives in `services/`, never inline in a route. This is what lets the same logic be
  reused and unit-tested without HTTP.
- **One schema per direction.** Separate Pydantic models for create / update / read. Don't
  reuse the ORM model as the response shape — it leaks columns and couples API to storage.
- **Dependencies for cross-cutting concerns** (db session, current user, pagination). If two
  routes copy the same setup, it belongs in a dependency.
- **Settings come from the environment**, typed via Pydantic Settings. No literals for URLs,
  secrets, or the auth-provider switch. Local values in `.env` (gitignored); never commit
  secrets.
- **Errors are explicit.** Raise typed exceptions in services; translate to HTTP at the edge
  with an exception handler, not scattered `HTTPException` deep in logic.
- **Type everything.** Full type hints; the schemas and models are the contract.

## Assumptions worth stating in code review

When reading existing backend code, the hidden assumption is usually the bug. Name it before
trusting it: does this query return what's expected when the table is empty? Is this list
actually ordered, or assumed ordered? Is this dependency really injected in tests, or hitting
the real DB? Flag these rather than glossing past them.
