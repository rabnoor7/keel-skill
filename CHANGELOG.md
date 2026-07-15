# Changelog

All notable changes to keel. Versions follow semver; `docs.py --version` reports the installed version.

## [1.2.0] — 2026-07-15

### Added
- **Outcome decomposition** — bring a big fuzzy OUTCOME ("build my personal brand", "reach 1000 people")
  and keel decomposes it into aligned CHECKPOINTS instead of diving into execution. `docs.py outcome set/show/clear
  "<north star>"` · `checkpoint add "<layer>"` · `checkpoint status <n> reached|active|undecided` ·
  `checkpoint choice <n> --text "..." [--to-decision "<title>"]` (promote a pivotal choice to a searchable
  ADR). The shape lives in a committed, hand-editable `docs/roadmap.md`; rehydrate surfaces a ROADMAP block
  (north star · statuses · "you are here" · next undecided checkpoint).
- **Decompose-before-execute gate** — an outcome with zero checkpoints is a BLOCKING state in both
  `rehydrate` AND `contract check`, so a build cannot skip decomposition even under "just build it" pressure
  (fixes a real session where keel executed on a fuzzy brand goal instead of breaking it down first). `outcome clear` archives the roadmap and lifts the block if an outcome is abandoned.
- **Tier-relative orchestration** (`route lead --model <you>`) — keel now derives the manager/worker
  topology from YOUR lead model instead of hardcoding one: orchestration + intelligence + verification stay
  on the lead; grunt/bulk-research delegates DOWN to Sonnet; a judge (Opus when the lead is above Opus, else
  the lead) verifies worker output. Sonnet-lead = solo (verify your own). SKILL.md §5 makes this a required
  reflex before a swarm; `contract check` prints a non-blocking cost hint naming grunt-shaped items to
  delegate. **UX-invisible**: fully dormant unless a lead is declared (proven byte-identical rehydrate for
  non-adopters) — same outcome quality, lower token cost.
- **`general` profile** + broadened identity — keel now covers goal-shaped, not-only-code projects
  (personal brand, outreach, content, launch), not just software. SKILL.md gains an Outcome-Decomposition
  loop step (§0a); the install intro and README reflect the wider scope.

### Compatibility
- **Purely additive.** The outcome feature is dormant unless `docs.py outcome set` is run (no
  `docs/roadmap.md` → zero new behavior). Verified: `rehydrate` byte-identical to 1.1.0 across 8 corpus
  repos; round-trip writes byte-identical; existing 23-turn conversational flow 23/23; a user who never
  touches `outcome`/`checkpoint` sees no change.

## [1.1.0] — 2026-07-15

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
- **Lost concurrent updates**: `asks.md`/`escalations.jsonl` read-modify-rewrites could clobber each
  other (measured: 30 of 80 parallel updates lost). Now lock-guarded + atomically replaced (81/81).
- **Drafted decisions skipped their `DECISIONS.md` pointer** at landing, and log recognition switched
  off after the first one-per-file ADR landed — both found by a 23-turn conversational dogfood; a
  present `DECISIONS.md` is now honored unconditionally and pointers append at landing.
- **Same-day journal ordering**: multiple entries on one date sorted alphabetically, so the "newest
  journal" line could lie; mtime now breaks same-day ties.
- **`coverage`** treated bracketed transcript artifacts as ground-truth points; now filtered.

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
- **Standing state**: `stance` (freeze / confirm-memory; survives sessions), `escalate` (durable
  BLOCKED-ON-USER checkpoints; resolving promotes the answer to an ADR), `ask` (evidence-gated ask
  ledger, committed + hand-editable at `docs/asks.md`, loud at 3+ raises).
- **Long-job durability**: `run` (append-only per-item work ledger; exact resume; parked after 7 idle
  days, never auto-deleted), `sink` (durable capture inbox; hash-dedup import; un-merged captures are
  unclearable rehydrate debt).
- **Recall & integrity**: `match` (already-decided detection at orient, stemmed + title-boosted),
  single-file decision logs (`docs/DECISIONS.md`) read as first-class ADRs with pointers appended for
  new decisions, honest digests (`[SUPERSEDED]` tags, `(+N older)`), anchor pointer-rot check,
  `orphans` (dangling-reference check, advisory in rehydrate).
- **Quality gates**: `preserve` (edit-not-regenerate unit diff), `accept` (typed definition-of-done
  registry), `coverage` (every point of an external source addressed), `critique` (assumptions /
  research / alternatives gate on big plans, latest-per-claim), `smoke` (sample go/no-go before
  expensive runs), `livetest` (human live-test lane; `verify done` blocked until the user's verdict),
  `route` (task-class → model policy, advisory, known-crude keyword matching).
- **Multi-worktree**: `handoff` — append-only channel in the git common dir, shared by all worktrees
  of a repo (same-machine); surfaced in rehydrate.
- **Rehydrate render**: severity-dynamic — data-at-risk/integrity advisories always fully detailed;
  housekeeping collapses to one named line past 5 total; CORRECTIVE ACTIONS footer always complete;
  `rehydrate --full` shows everything.
- **Doctrine**: decompose-large-scope-all-the-way-down (experiment-first, scenario questions);
  steelman-every-option; consult stance/escalations at three fixed points; model never self-certifies
  a livetest.

## [1.0.0] — 2026-07-13

Initial public release: rehydrate/hydrate loop, three-tier memory (docs/ + project memory + global
prefs), contradiction/staleness/hygiene checks, build contract gate, verify audit ratchet, profiles
(web-app · data-pipeline · automation · cli-tool · ml), multi-agent whiteboard + claims, one-time intro.
