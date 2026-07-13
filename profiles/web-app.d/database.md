# Database & auth — Postgres everywhere, one auth contract

## Postgres everywhere — no SQLite

Local, test, and prod all run **Postgres**. Local and test Postgres come up via
docker-compose (`references/docker.md`); prod is Supabase Postgres. SQLite is deliberately
**not** used — it was traded away so that local mirrors prod exactly: same engine, same SQL
dialect, RLS available locally, and tests that run against the real database behavior rather
than an approximation. If a project ever proposes SQLite "just for speed", flag the trade:
faster tests, but they stop exercising real Postgres behavior.

## ORM & migrations

- **SQLAlchemy 2.x** (typed) as the ORM, against Postgres in every environment.
- **Alembic** for migrations. Every schema change is a migration; never hand-edit the DB.
- Tests run against an **ephemeral Postgres** (a docker-compose service, or a per-run
  container) with migrations applied, then torn down. Defined in `references/docker.md`.

## The auth contract — the load-bearing part

Production uses **Supabase for auth**; local uses **plain email/password**. The only way that
split stays safe (instead of the two quietly diverging) is to make the app depend on an
**abstraction**, never on Supabase directly.

Define an interface the app talks to:

```python
# app/auth/contract.py
class AuthProvider(Protocol):
    async def current_user(self, request) -> User | None: ...
    async def sign_up(self, email: str, password: str) -> User: ...
    async def sign_in(self, email: str, password: str) -> Session: ...
```

Two implementations behind it, selected by an env var (Pydantic Settings):

- **LocalEmailPasswordProvider** — own `users` table, hashed passwords (passlib/bcrypt),
  issues your own session/JWT. Used in dev and test.
- **SupabaseProvider** — verifies Supabase-issued JWTs / delegates to Supabase Auth. Used in
  prod.

The `get_current_user` dependency depends on the **contract**, so routes and services can't
tell which provider is active. Swapping is a config flip; nothing downstream changes.

## Authorization: backend code by default

Default: **enforce "who can do what" in your FastAPI service layer**, in code. This keeps
authorization fully exercised by the Postgres-backed tests and independent of the auth
provider.

## RLS: optional, per project, not the default

Postgres **Row-Level Security** is now *available* (local runs Postgres, so it can be mirrored
in tests) — but it is **not** the default, because it adds real complexity: policies live in
SQL/migrations, must be tested explicitly, and split the authorization story between code and
database. Offer it only when a project wants defense-in-depth, and if chosen:

- Policies are defined in Alembic migrations and version-controlled.
- The test database applies the same policies, and tests assert them directly (a user cannot
  read another user's rows), since this is exactly the rule that silently breaks if only
  enforced in one place.

Record whichever choice is made as an ADR (`docs/decisions/`).

## By cases: where could an auth bug be?

When auth misbehaves, enumerate before guessing: (A) the provider selection (wrong env in this
environment?), (B) the contract implementation (token verified correctly?), (C) the
authorization check (right rule, wrong place?), (D) RLS policy if enabled. Rule each out in
turn rather than asserting the cause.
