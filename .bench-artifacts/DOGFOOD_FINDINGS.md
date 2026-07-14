# Dogfood findings — 4 independent sessions on real repos (consolidated)

Sessions: faire-lead (canonical), agw-scout-site (alt/README), rag-mcp (partial/single-file-log), portfolio-manager (virgin/root-docs).

## Design decisions — RESOLVED BY EVIDENCE (consensus)
- **D1 new-ADR location → MATCH the project's folder** (unanimous). Guard: if BOTH docs/decisions/ AND adr/ exist, surface the ambiguity, don't silently pick. Requires single-file-log support to be complete.
- **D2 feedback tier → central corpus + gitignored .keel/ mirror; NOT committed to docs/.** 3/4 explicit; the dissent (portfolio) also rejects committed. OVERRULES my earlier "committed friction note" idea — agents argue committed tool-feedback pollutes repo/PRs/blame. REAL bug to fix: ensure `.keel/` is gitignored on first write to it (init isn't always run).
- **D3 auto-capture → near-silent, STAGED AS A DRAFT, fired only on explicit decision/correction signals, batched at hydrate; never mid-build, never per-friction ack** (unanimous). Reuse the existing draft→visible-debt→hydrate substrate.
- **D4 CORRECTIVE ACTIONS block → YES** (unanimous). Consolidate scattered [!] into ONE severity-ordered, individually-approvable block, distinguishing BLOCKING (audit failed / live contradiction) vs ADVISORY (stale hash / drafts to flush).
- **D5 inventory verbosity → split by repo density.** Enrich (first-heading + line-count) when few/loose docs (rag, portfolio); names-only when rich (faire-lead, 3 extras). Resolution: enrich but collapse when many; the deeper fix is SCOPE (below) + fix DECISIONS digest.

## Prototype bugs / gaps found (prioritized)
1. **[CRITICAL] `_next_adr()` ADR-number corruption → "2027".** Globs `.keel/pending/*.md` and parses leading digits; a date-named journal draft `2026-07-14-*.md` reads as ADR 2026 → next=2027. (faire-lead, reproduced)
2. **[HIGH] DOCS INVENTORY scope — "nothing silently skipped" is FALSE on non-canonical repos.** `_doc_inventory()` only scans docs/ + resolved slots + anchor. Silently skips root CLAUDE.md/AGENTS.md (agw) and 14 root manuals (portfolio). Flagship-claim breaker.
3. **[HIGH] Single-file decision logs unsupported.** `docs/DECISIONS.md` with 9 ADRs → "0 ADR"; `layout --set decisions=<file>` still 0 (globs file as dir). No contradiction/supersede on it. (rag-mcp)
4. **[HIGH] `read --all` is a dead no-op flag;** `read` dumps ~3 lines while 1300+ across [other] docs ignored. (rag-mcp)
5. **[HIGH] First ADR on flat-root repo silently scaffolds docs/ tree → split-brain** (anchor at root, decisions nested). No prompt/announcement. (agw)
6. **[MED] `.keel/` not gitignored when init never ran** → feedback mirror + state committable by accident. (agw, rag, portfolio)
7. **[MED] VERIFY STALE fires blocking exit-1 on mtime/hash drift** (false alarm on read-only sessions). Should split FAILED(blocking) vs stamp-stale(advisory). (faire-lead)
8. **[MED] DECISIONS digest hides superseded ADR identity** (blockquote eats title); `decs[-12:]` silently drops older ADRs (contradicts "nothing skipped"). Fix: render `NNNN — title [SUPERSEDED]` + "(+N older)". (faire-lead)
9. **[MED] Anchor fallback too narrow** — misses read-first root docs (`01_*.md`, `market_research/INDEX.md`). (portfolio)
10. **[MED] CLI-vs-prose contradiction** — rehydrate prints "run docs.py init" but SKILL.md forbids init on existing repo. (portfolio)
11. **[MED] profile doesn't compose** despite SKILL.md saying it does (stores one string, overwrites). (rag-mcp)
12. **[MED] anchor content-staleness undetected** — faire-lead anchor points at fullstack-builder path + wrong abs path; mtime check can't catch it. (faire-lead)
13. **[LOW] supersede** writes immediately (no --draft/contract gate), misreports "marked ADR N" when idempotency-skip. (faire-lead)

## Innovation seeds (from dogfood — cross-validate with workflow)
- **ADOPT flow**: point keel at existing docs (root manuals, INDEX.md, single-file logs) instead of scaffolding a blank parallel. Turn "0 docs" into "N existing docs, not yet keel-managed — adopt?"
- **Repo-wide truthful discovery**: shallow `*.md` sweep; earn or drop the "nothing silently skipped" guarantee.
- **"Already decided" detection**: at orient, match the incoming ask against recent ADR titles/status → "this looks settled in ADR 0015 (2026-07-12) — new, or re-run?". The map-before-build payoff.
- **Distinct empty-state verdict** vs "✅ clean".
- **Recognize existing memory conventions**: single-file decision logs, root anchors, index files, CLAUDE/AGENTS.

## What's PROVEN good (keep)
- Round-trip parity (byte-identical writes), layout resolution across classes, anchor fallback mechanics, missing-tier grace (read-only, no refusal, no forced migration), draft→debt→hydrate loop, contract freshness gate, feedback isolation, search.
