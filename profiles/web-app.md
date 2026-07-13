# Web App — Next.js (Pages Router) + FastAPI + Postgres

Next.js (Pages Router, TypeScript) frontend, dockerized Python FastAPI backend, Postgres always.
Auth is email/password locally and Supabase in prod, both behind one interface — nothing calls
Supabase directly.

## Survey
Ask before building; resolve everything else yourself and state the default.
- **Problem & scope** — what must this feature/app do, and what's explicitly out of scope?
- **Data model** — entities, relationships, ownership; new tables or extending existing ones?
- **API surface** — which resources, which verbs, who calls them (frontend only, or external too)?
- **Auth & authz** — who can do what. Default: enforced in the FastAPI service layer, in code.
  Offer Postgres RLS only as defense-in-depth, per project, never as the default — it splits the
  authorization story across code and SQL. Record the choice as an ADR either way.
- **Frontend routes & components** — new pages or additions to existing ones? Componentise on the
  third repetition, not the first use. No prop-drilling past two levels — reach for a store or a
  query hook past that.
- **Infra** — `docker compose up` is the floor for every project, no exceptions. Cloud target
  (Railway/GCP/AWS/etc.) is chosen per project; never bake one into the core setup.

## Build
- **Thin routes → services → typed schemas.** A route validates input, calls a service, shapes
  the response. Business logic lives in `services/`, never inline in a route. One Pydantic model
  per direction (create/update/read) — never return the ORM model as the response shape.
- **Auth behind one interface.** An `AuthProvider` contract with two implementations (local
  email/password, Supabase), selected by env var. Routes and services depend on the contract,
  never on which provider is active — swapping is a config flip, not a code change.
- **Postgres everywhere** — local, test, and prod; local/test via docker-compose. No SQLite: it
  stops local and tests from exercising real dialect, constraints, and RLS.
- Verify current library idioms (FastAPI, SQLAlchemy, Next.js, TanStack Query, shadcn...) via
  **web search, not memory** — these move fast and training data goes stale.

## Verify
- **Backend: pytest against a real Postgres**, brought up via docker-compose with migrations
  applied first. Auto-run, no permission needed — this is the API's ground truth. Mock nothing
  that touches the database.
- **Frontend: no auto-run harness by default.** Write concrete, numbered check definitions (what
  to click, what should render, what state should change) into `verify/audit.py` or an adjacent
  checklist, and hand them to the user to run — don't claim a UI works because the backend tests
  passed.
- **`docker compose up` must succeed clean** on a fresh checkout — db healthy, backend up,
  migrations applied — before anything counts as done.
- If RLS is enabled, tests assert the policy directly (a user cannot read another user's rows) —
  the exact rule that silently breaks when only enforced in one layer.

## Depth (load as needed)
Full conventions carried intact from the original full-stack builder:
`web-app.d/backend.md` (FastAPI layout, thin-routes→services→schemas) ·
`web-app.d/frontend.md` (Next.js Pages Router, componentisation & DRY rules) ·
`web-app.d/database.md` (Postgres, SQLAlchemy+Alembic, the dual auth-provider contract, RLS tradeoff) ·
`web-app.d/docker.md` (docker-compose dev/test, Dockerfiles). Task-type playbooks
(scaffold / add-feature / debug / upgrade-migrate / refactor) are in `../../modes/`.
