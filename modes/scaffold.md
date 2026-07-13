# Mode: scaffold (new project from nothing)

The only mode that runs the **full design survey** (SKILL.md Section 4) from scratch — nothing
exists, so every choice is open.

## In DISCUSS

Walk the survey conversationally: problem & scope → data model → API surface → auth/authz →
frontend routes & components → infra. Pin vague terms to concrete meaning. As each choice
lands, record it (`scripts/docs.py decision` / `write`). Do not scaffold anything yet — wait
for the build gate.

End DISCUSS with a clear shared map: the user should be able to see the entire skeleton (which
entities, which endpoints, which pages, which provider) before a single file exists.

## On the build gate → BUILD

1. `python ${CLAUDE_SKILL_DIR}/scripts/docs.py init` — create the `docs/` skeleton and gitignore `.claude/state/`.
2. Write the durable docs from the agreed map (`architecture.md`, `data-model.md`, `api.md`,
   `conventions.md`).
3. Scaffold in dependency order so each layer can be verified before the next:
   monorepo layout → docker-compose + Postgres → backend (models → migrations → schemas →
   services → routes → auth contract with local provider) → frontend (API client → query
   layer → pages → components).
4. Confirm `docker compose up` brings the stack up locally before declaring the scaffold done.

Verify current scaffolding commands (create-next-app flags, shadcn init, Alembic init) with
web search — defaults change.

## On "complete" → TEST

Follow SKILL.md Section 5: agree scenarios, auto-write+run API tests against Postgres, define
frontend tests for the user to run, save all definitions to `docs/testing.md`. Journal the
scaffold with a `friction:` line.
