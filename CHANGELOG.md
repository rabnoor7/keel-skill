# Changelog

All notable changes to keel. Versions follow semver; `docs.py --version` reports the installed version.

## [1.1.0] — unreleased (in development)

### Fixed
- **ADR numbering corruption**: a date-named journal draft in `.keel/pending/` (e.g. `2026-07-14-*.md`)
  was parsed as an ADR number, so the next ADR landed as `2027-*.md`. Date-shaped names are now excluded.
- **DOCS INVENTORY scope**: root-level docs (`README.md`, `CLAUDE.md`, `AGENTS.md`, read-first manuals)
  were silently skipped on non-canonical repos, breaking the "nothing silently skipped" promise. A shallow
  root sweep now surfaces them.
- **`read --all`** was a declared no-op; it now dumps `[other]` docs too.
- **`.keel/` gitignore guarantee**: private state is now added to `.gitignore` on the first state write,
  not only in `init` (sessions that never ran `init` could accidentally commit `.keel/`).
- **Windows**: `import fcntl` crashed every command on Windows. The import is now guarded — whiteboard
  posts degrade to unlocked appends on Windows; everything else works. `run` uses `platform.node()`.

### Added
- **Layout resolution** — anchor falls back `docs/architecture.md → README.md → CLAUDE.md → AGENTS.md`;
  decisions/journal auto-detect `adr/`, `docs/rfcs/`, `rfcs/`; `.keel/layout` overrides; `docs.py layout`.
- **DOCS INVENTORY** block in rehydrate — every doc surfaced and tagged; nothing silently skipped.
- **`docs.py feedback`** — log friction about keel itself to a central per-user corpus
  (`~/.claude/keel/feedback.jsonl`, local-only) for improving keel.
- **`docs.py --version`** + `VERSION` file + this changelog.
- **Rehydrate severity split** — BLOCKING (contradictions, open escalations, failed audits) exits 1;
  ADVISORY (stale hashes, pending drafts, hygiene) is surfaced without blocking; consolidated
  CORRECTIVE ACTIONS footer lists every issue with its exact fix command.
- **Prototype commands under evaluation** (shapes may change before release): `run` (resumable
  work-ledger), `sink` (offline capture-inbox), `stance` (standing freeze/modes), `escalate`
  (blocked-on-user checkpoint), `ask` (evidence-gated ask ledger).

## [1.0.0] — 2026-07-13

Initial public release: rehydrate/hydrate loop, three-tier memory (docs/ + project memory + global
prefs), contradiction/staleness/hygiene checks, build contract gate, verify audit ratchet, profiles
(web-app · data-pipeline · automation · cli-tool · ml), multi-agent whiteboard + claims, one-time intro.
