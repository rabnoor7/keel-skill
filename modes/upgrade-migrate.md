# Mode: upgrade-migrate (deps, infra, schema, data)

Covers bumping dependencies, changing infrastructure (e.g. picking/changing the cloud target),
and schema/data migrations. The shared risk is **breaking working behavior**, so the map is
about blast radius and reversibility.

## In DISCUSS

1. **Rehydrate**; read current versions/config from `pyproject.toml`, `package.json`,
   compose files, and `docs/architecture.md`.
2. **Research the target** with web search — breaking changes, migration guides, deprecations
   for the specific version jump. Don't upgrade from memory; these notes are exactly what
   training data gets wrong.
3. **Map the blast radius.** What depends on the thing changing? Which call sites, which
   behaviors, which tests. State it before touching anything.
4. **Plan reversibility.** For schema/data migrations: is the Alembic migration reversible
   (`downgrade` works)? Is there a backup/rollback for prod data? Surface this — irreversible
   data migrations are the dangerous ones.

## On the build gate → BUILD

- **Dependency bumps:** one meaningful upgrade at a time where feasible, so a regression is
  attributable. Run the existing test suite after each.
- **Infra changes:** keep local-first working; the cloud target is recorded in
  `docs/architecture.md`, not hardcoded. Confirm `docker compose up` still works.
- **Schema/data migrations:** Alembic migration with a tested `downgrade`. Apply to the test
  DB first. Never hand-edit the database.

## On "complete" → TEST

The existing suite must still pass (that's the point of having it). Add tests for any new
behavior the upgrade enables or changes. Save definitions to `docs/testing.md`. Record an ADR
for the upgrade decision and journal it with a `friction:` line, noting any breaking changes
handled so the next upgrade is easier.
