# Memory model

Three tiers, split by lifecycle, not one file — a single file means every session edits the same lines and
either collides or drifts stale in place.

## The tiers

- **Committed `docs/`** — version-controlled, travels with the repo, source of truth once the session ends:
  `architecture.md` (the REHYDRATION ANCHOR — first thing read, summarizes the rest), `data-model.md`
  (entities/schema/contracts, or the profile's equivalent), `decisions/` (`NNNN-title.md`, one ADR per
  decision, append-only, supersede-aware), `journal/` (`YYYY-MM-DD-slug.md`, dated narrative, append-only).
- **Project memory** — uncommitted, per-machine: session scratch plus the **pending queue**,
  decisions/corrections captured the instant they happen, before they've earned a place in `docs/`.
- **Global `~/` prefs** — cross-project taste, outlives any one repo. Every write is *proposed and
  confirmed*, never silent — it changes behavior on every future project. `docs.py prefs --show` / `--append`.

## The fixes — this is the part that makes it reliable

"Write it to a file" decays the same way the model's own context does: corrections strand, anchors go
stale, the same lesson gets restated in five places until none are trusted. Each fix closes one decay path,
enforced by `docs.py` — not by remembering to be careful.

**(a) Promotion path.** A correction that supersedes an ADR MUST become a superseding ADR — `docs.py
supersede <n> --title "..." --from <file>` — never stranded in project memory or a journal line. Stranded =
invisible to `rehydrate`: the next session reads the old ADR, believes it, rebuilds on a reversed decision.

**(b) Contradictions first.** `rehydrate` loads all three tiers, then runs `docs.py contradictions` — a
deterministic cross-tier claim diff — surfacing conflicts before anything else. You never act on tier 1
while tier 2 quietly disagrees with it.

**(c) Derived freshness.** The anchor's currency is computed — `docs.py` hashes/mtimes `architecture.md`
against the slots it summarizes, reporting "N edits behind" — never a hand-bumped `Last updated:` date. A
hand-bumped date is a lie generator: trivial to forget, confidently wrong once it is.

**(d) Single-source.** One lesson, one authoritative home; every other mention links to it instead of
restating it. Restatements drift apart, and then nobody knows which copy is real.

**(e) Continuous durability.** Decisions/corrections enter the pending queue the moment they happen, not
batched for later; `docs.py hydrate` drains it. An active session ending with an empty journal is a
detectable anomaly, not a quiet default.

**(f) No-clobber guard.** Every write to a durable file carries the hash it was last read at; `docs.py`
refuses the write if the on-disk hash has since moved and asks you to merge — otherwise two parallel
sessions touching `docs/` just clobber each other.

**(g) Queryable, prunable logs.** `decisions/` and `journal/` are append-only and grow forever unless
managed. `docs.py search <query>` finds without loading everything into context; `docs.py supersede <n>`
retires a stale decision (marks it + writes the replacement) while keeping the original discoverable.

## Formats

ADR — `docs/decisions/NNNN-title.md`, supersede-aware:
```
# 0008 — <title>
Date: YYYY-MM-DD
Status: accepted | superseded-by-0011
Supersedes: 0006          # omit if net-new
## Context
## Decision
## Rejected
```

Journal — `docs/journal/YYYY-MM-DD-slug.md`, dated, points at canonical files instead of restating them
(rule d), plus a one-line friction note:
```
# YYYY-MM-DD — <what happened>
What changed: ... (see decisions/0008, data-model.md#x)
friction: one line — where the skill itself helped or got in the way
```

## The line to keep in view

Writing a directive down is not the same as following it. Enforcement is a fixed home for the fact, a
`docs.py` check that flags violations of it, and that check running inside `rehydrate` every session,
unconditionally — not the sentence you wrote.
