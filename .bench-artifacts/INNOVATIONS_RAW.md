# RAW INNOVATION MATERIAL (salvaged from workflow journal)
themes=12  innovations=36  verdicts_landed=48 (keep=42, kill=6)

## THEMES
1. **Persistent, calibrated permission & autonomy model for non-code and operational actions (incl. user-named modes)** — keel's contract gate is a per-BUILD, ephemeral approval scoped to code/files/schema, with a lightweight lane for 'trivial reversible edits.' This user's loudest, angriest, most-recurring friction is that gate being the wrong shape in BOTH directions. It gates too little: irreversible OPERATIONAL side-effects (real DMs, engaging live convos, launching an expensive multi-hour run, real external edits), destructive ops on protected data zones (RAG/Qdrant/tenets/catalog — 'always ask before purge'), and additive-never-wipe runtime invariants never trip a code-build gate, so the loop acts without asking. And it gates too much: the user grants standing 'cofounder/ownership' authority for whole classes of routine work and resents being re-asked. What's missing is a persistent, per-domain autonomy dial + a judgment-based escalation protocol (escalate when the agent deems it necessary, route through me, confirm what gets written to memory) — and a standing FREEZE/discussion-only state and user-named modes ('sensei', 'partner') that survive interruptions and new sessions and can block even the lightweight lane. This is the single most frequent meta-friction in the corpus.  [repos: faire-lead (brand data-pipeline), knowledge-graph-rag (brain / Graphiti+Qdrant),]  strength=very high
2. **Durable, resumable EXECUTION state & run-lifecycle for long jobs** — keel hydrates durable memory at the END of the loop and its 'unflushed pending queue' tracks un-written DECISIONS — not progress through a multi-item batch. Multi-hour scrapes/enrichments/swarms get interrupted before hydrate ever runs, so hours of fetched data are discarded and 'where you left off' cannot be reconstructed. The need is a persisted work-queue/cursor/ETA (which items done, which pending, current position), continuous flush-as-you-go of BOTH expensive fetched artifacts and decisions during the build phase, resume-after-partial-failure with offline-inbox reconciliation (records captured while backend was down), a per-agent ledger so a halted swarm restarts mid-flight without redoing work, and syncing that durable state across two mirrored machines. This is the most recurring friction in the corpus — 'continue exactly where you left off' spans nearly every long task.  [repos: faire-lead (brand data-pipeline), instagram-enrichment, brand-intelligence-app (]  strength=very high
3. **Clarify/contract gate for NON-BUILD deliverables + durable per-deliverable acceptance specs** — keel's contract gate (map-before-act, scope files/edge-cases/will-not-do) fires ONLY for code/files/schema/migrations. But the bulk of this user's work is knowledge work — research runs, visualizations, audits, emails — which fall in the ungated lightweight lane, so the agent guesses scope and gets angrily rejected ('that's not what I asked'). The need is to extend the clarify/contract discipline to non-build deliverables, AND to store per-deliverable-TYPE acceptance criteria as durable memory enforced before 'done' — e.g. the cofounder visualization must preserve ALL non-trivial info, carry citations/proof-volume, and be EDITED not regenerated. The quality bar currently lives only in the user's head and is re-taught every session.  [repos: cofounder-viz / sales-deck, meeting-audit (sales-agent), faire-lead (research)]  strength=very high
4. **Continuous, layered & data-aware auditing during/after runs (+ data-artifact lifecycle)** — keel's verify is a one-shot, field/spec-level audit fired at the 'done' gate; its anti-fabrication means 'a claim with no source pointer fails.' This user needs auditing that (a) runs continuously and in LAYERS while a long job executes (small per-batch audits + a large overall audit + corrective loops), (b) includes a FABRICATION check aimed at a delegated sub-agent's scraped output ('did sonnet invent this row'), (c) compares an output DATA artifact against a stored prior-run baseline to catch silent under-capture ('if this scrape is smaller than last time, something's wrong'), (d) treats stored data records as untrusted unless they carry a citation + timestamp + cross-validation (a product-quality invariant), (e) gates merge/push on a measurable dataset before/after IMPROVEMENT, and (f) manages the data-artifact lifecycle itself (raw dumps → validated → master CSV → archive, graduating to sqlite/CRUD) — none of which keel's claim-level verify or doc-drift hygiene touches.  [repos: faire-lead (brand data-pipeline), brand-intelligence-app (leads/ads/catalog), in]  strength=high
5. **Verification against external ground truth & human live-testing** — keel's verify is automated, one-directional (every CLAIM must cite a source) and self-marks 'done.' This user's ground truth is reality, and verify needs to run the other way and hand off. Needs: a COVERAGE / reverse-provenance audit ('did the output address every point in this meeting transcript') against external sources; a human-in-the-loop lane that runs automated tests first, then stands the environment up and HANDS OFF to the user for a live real-world test, then ingests their observations — with an explicit ban on self-marking done via self-test; proof-of-intact + a durable edge-case suite exercised before any handoff (e.g. how the KG layer behaves when a tenet is deleted; are all tenets mapped); and verification of RENDERED, VISUAL outcomes (centering, overflow, scroll) that a claim-audit simply cannot observe, leaving the user as the only verifier of every UI regression.  [repos: meeting-audit (sales-agent), cofounder-viz / sales-deck, knowledge-graph-rag (br]  strength=high
6. **Persistent tracking & accountability layer (forward plan/backlog/asks + backward action/scope/blast-radius)** — keel records point DECISIONS (ADRs) and dated journal notes, but has no living status surface — neither forward nor backward. Forward: a phased/layered roadmap tracking each layer's verified-working status and an explicit 'left-out / still-to-build' backlog; parked items with wake-conditions that resurface at the right phase ('raise it when we reach Phase 5'); and a standing ledger of user-facing feature/bug asks that persists until each is VERIFIABLY resolved, with detection when a previously-satisfied ask regresses ('I've asked for this so many times'). Backward: an on-demand action-accountability audit — what did you do vs the scope I authorized (an overreach ledger: 'where did I tell you to stop and what did you implement past that'), a cross-folder/cross-repo BLAST-RADIUS proof that nothing outside the declared scope was touched (sibling folders are git-synced; a stray write corrupts a separate system), and a 'what happened this session and how does it change the decisions I still have to make' recap.  [repos: knowledge-graph-rag (brain / git-synced siblings), brand-intelligence-app (leads]  strength=high
7. **Broaden the memory taxonomy to missing tiers, graph-integrity & the user's REAL substrates** — keel's memory is architecture.md / data-model.md / ADRs / journal — decision & design records it authors itself. This user re-teaches whole categories of memory every session because they have no home: a procedural RUNBOOK tier for hard-won tacit operational knowledge (bot-detection evasion — same-tab reuse, on-screen-visibility requirement — empirically measured rate limits, safe human-like cadence); an empirical FINDINGS/benchmarks tier with provenance (measured limits, free-provider comparisons, 'what these repos give us', gap analyses) so research isn't re-run; a living operational 'DIRECTIVE' runbook that itself needs de-duping as it accretes; SCOPE/generality tags on learnings (instance-specific vs general, to stop over-fitting one meeting's feedback); a persisted teaching/expertise level for a non-technical user on a learning journey; and — critically — recognition that the user's actual anchor-of-truth is a single living agents.md, an Obsidian vault, and a Graphiti knowledge-graph RAG, none of which keel reads or writes as a memory tier. It also lacks a deterministic ORPHAN/dangling-reference check over the memory graph.  [repos: faire-lead (brand data-pipeline), knowledge-graph-rag (agents.md / Obsidian / Gr]  strength=high
8. **Structured adversarial critique of design/proposals — research-grounded, self-initiated, with quality-triggered redo** — keel's 'honesty over agreeableness' and anti-fabrication apply to CODE CLAIMS at the verify gate. This user repeatedly (and angrily) has to manually invoke a red-team pass over DESIGN proposals and plans BEFORE they're presented — 'sensei mode', an extremely-thorough 5-why root-cause, an assumption audit. The needed capability: run structured self-critique of assumptions by default before proposing; GROUND proposals in gathered multi-angle external research, surface the gaps found, and attribute the proposal to that research (bitter complaints when 'no research leveraged / no innovation'); PROACTIVELY spawn fresh, independent adversarial-critique/audit sessions on the agent's own judgment rather than only on command; and trigger an automatic REDO on poor output that carries forward corrective learnings, explores adjacent/opposite angles, and surfaces an approach discovered to be better than the agreed plan.  [repos: meeting-audit (sales-agent), knowledge-graph-rag (brain), faire-lead (brand data]  strength=strong
9. **First-class support for external artifacts as knowledge sources & evaluation corpora** — keel's memory ingests only docs/ADRs/journal that keel itself authors. This user's central knowledge substrate is external meeting transcripts (Fathom), and there is no path to treat them as first-class. Needs: a typed/labeled REGISTRY of external runs so 'which one' is resolvable (sales vs brainstorm vs benchmark; nailed vs failed) — the agent keeps grabbing the wrong near-identical meeting; INGESTION of inline human feedback embedded in a transcript into discrete, durable OUTCOMES/backlog items (instead of the user re-pointing at 'the last meeting' every session); and using the corpus of runs as an EVALUATION/regression set with a persistent, co-developed audit-dimensions RUBRIC that compounds learnings across many runs without over-fitting. The same audit dimensions are re-derived from scratch each session.  [repos: meeting-audit (sales-agent), faire-lead (repos-as-sources research), knowledge-g]  strength=strong
10. **Cost & model-routing as first-class, persistent constraints** — keel has no cost or budget model whatsoever — every gate is about correctness/contract, never spend, and global preferences.md captures engineering conventions but not a task-class-to-model routing policy. This user treats tokens and dollars as a hard constraint and re-states it every session: they want pre-run token/dollar ESTIMATES before committing, cost-conscious ROUTING (cheap 'grunt' models for heavy lifting, the smart model reserved for intelligence work), a spend cap the loop respects (prefer targeted extracts over full re-runs when tokens are low), and after-the-fact accounting of where tokens were wasted. This routing/budget intent should be a durable, enforced preference, not re-explained per session.  [repos: faire-lead (brand data-pipeline), meeting-audit (sales-agent), brand-intelligenc]  strength=strong
11. **Coordination & portability beyond a single flat peer on one machine** — keel's multi-agent support is a flat peer model (whiteboard log + resource-claim locks) on one shared filesystem, and it models a single project's memory. This user operates a richer topology with no keel equivalent: a hierarchical opus 'manager' orchestrating sonnet 'grunt' workers across sessions/worktrees, with cross-session HANDOFF documents (IG-audit-handoff-*.md — memory keel doesn't recognize), a report-up channel, and visibility into pending work living in ANOTHER branched-off worktree; coordination with a HUMAN teammate through git (track where Saurabh is, stay synced on top of his commits, guarantee the branch stays mergeable, understand divergence); and portability operations — extracting a CURATED memory subset into a new repo with an explicit contamination (inclusion/exclusion) boundary, promoting a proven sandbox track wholesale into the canonical docs, and tracing which version of a finalized working artifact is actually live and where its outputs landed.  [repos: faire-lead (brand data-pipeline), instagram-enrichment, knowledge-graph-rag (bra]  strength=strong
12. **Preflight readiness: environment health, external-service liveness & smoke-test go/no-go** — keel's rehydrate checks are read-only and scoped to docs/memory (contradiction, staleness, superseded, pending, hygiene); they never inspect runtime health or external dependencies, and verify only gates 'done' after the fact. This user's work is repeatedly and silently sabotaged by unmodeled preconditions. Needs: runtime-ENVIRONMENT health awareness (Cloudflare WARP / VPN / proxies degrading or blocking the work — the agent was blind until the user diagnosed it); external-SERVICE liveness preflight (every session opens with 're-establish state' — is the Qdrant cluster up, is the MCP connected, are the APIs reachable — this topology lives in no memory tier); and a pre-flight SMOKE-test gate that validates the full pipeline on a tiny sample and requires an explicit go/no-go before committing to an expensive or irreversible long run — exactly the 'quick 1-min test then long run' ritual the user performs by hand every time.  [repos: faire-lead (brand data-pipeline), knowledge-graph-rag (Qdrant / MCP), brand-inte]  strength=medium-strong

## INNOVATIONS (36)

### 1. Source Registry — a typed, content-addressed tier for external artifacts
- **one-liner:** docs.py source: register external transcripts as first-class, typed/verdict-labeled memory, and make "which one" a deterministic resolve that fails loudly instead of grabbing the wrong near-identical meeting.
- **problem:** keel's three memory tiers hold only keel-authored records; the user's actual knowledge substrate — Fathom transcripts — has no home, no type, no identity. So the agent free-text-matches filenames and keeps grabbing the wrong near-identical meeting. 'the last sales type meet (not the brainstorm one)' and 'this is the benchmark - not a benchmark, that's one kinda sales/partnership meeting' are the user hand-disambiguating every session because nothing durable does it.
- **evidence:** 'audit the last sales type meet (not the brainstorm one)'; 'this is the benchmark- not a benchmark because that's one kinda sales/partnership meeting' — the user is manually doing the type-disambiguation that a typed registry + fail-loud resolve would enforce; the reported failure mode is 'the agent keeps grabbing the wrong near-identical meeting'.
- **mechanism:** A new committed tier docs/sources.jsonl. Each record: {label (stable, human), path, type (sales|brainstorm|benchmark|partnership|... user-defined taxonomy), verdict (nailed|failed|mixed|unrated), date, content_hash, fingerprint}. `source add` records the file's content_hash (reusing _hash). `source resolve "<query>"` is the deterministic teeth: it parses type keywords + recency ('last'/'latest') from the query, filters the registry by matched type, and — mirroring the contradiction check's fail-loudly-not-guess stance — exits NON-ZERO listing all candidates when the match is ambiguous (>1 of the same type with no recency disambiguator), instead of silently returning one. rehydrate gains a SOURCES block that lists registered sources by type+verdict and, like _anchor_staleness, recomputes each file's hash to flag DRIFTED (file changed under a registered label) or DANGLING (path now missing) sources. Orient-step behavior change: on 'audit the X meeting', the agent must run `source resolve` before opening any file — resolution is a gate, not a guess.
- **sketch:** Commands:
  docs.py source add <path> --type sales --verdict nailed --label acme-q3 [--date 2026-07-10]
  docs.py source list [--type sales] [--verdict nailed]
  docs.py source verdict acme-q3 failed
  docs.py source resolve "the last sales meet"

`source resolve` output — unambiguous:
  RESOLVED → acme-q3  type=sales verdict=nailed  path=transcripts/acme-2026-07-10.txt
            (hash ok; 1 of 1 sales source)

`source resolve` — ambiguous, exit 1:
  [!!] AMBIGUOUS — 3 sales sources, query has no date/latest disambiguator:
     acme-q3     (nailed)  2026-07-10
     globex-demo (failed)  2026-07-02
     partnership-hive       2026-06-28
     → name a label. NOT guessing. (exit 1)

rehydrate SOURCES block:
  --- SOURCES: 5 registered (2 sales, 1 brainstorm, 1 benchmark, 1 partnership) ---
  [!] DRIFTED: acme-q3 file changed since registered (re-verify verdict).
  [!] DANGLING: globex-demo path missing.

Check logic (rehydrate): for r in load(sources.jsonl): if _hash(read(r.path))!=r.content_hash → drift; if not exists(r.path) → dangling; each increments problems.
- **fit:** Extends the existing 'external artifacts get a source pointer' provenance idea into an actual registered tier those pointers resolve against. Drift detection is _anchor_staleness applied to inputs instead of the anchor; fail-loud resolve is the _contradictions 'resolve before acting, never guess' stance. Committed docs/ because verdicts/types are durable knowledge that must travel with the repo, like decisions/.

### 2. Outcome Ingestion — inline transcript feedback becomes a durable, provenance-bound, idempotent backlog
- **one-liner:** docs.py outcome: turn the 'feedback for the agent' buried at the end of a transcript into discrete durable outcome items, each pinned to a source+offset, ingested idempotently so the user never re-points at 'the last meeting' again.
- **problem:** Human feedback embedded in a transcript ('sidenote... deep feedback for the agent', 'the last part is deep feedback') is high-value and perishable — it lives only in the transcript, so every session the user must re-point the agent at the right meeting and re-extract the same points by hand. keel has a durable pending queue for keel's own decisions but no path to lift externally-authored directives into durable, discrete, trackable work items.
- **evidence:** 'TAKE EACH AND EVERY POINT COVERED TOWARD THE END OF THE MEETING AS AN INDIVIDUAL OUTCOME TO ACHIEVE' (discrete items, not a blob); 'a lot of notes have been specifically made for you mentioned sidenote... The last part of the conversation is deep feedback for the agent' (the feedback is inline in an external artifact and must be lifted out durably rather than re-pointed at each session).
- **mechanism:** A durable ledger docs/outcomes.jsonl. Each outcome: {id, text, source (a registry label from Innovation 1), at (line/timestamp offset), status (open|done|dropped), ts}. Two deterministic teeth: (1) Provenance-required — `outcome add` REJECTS any outcome lacking a resolvable source label + offset, exactly as verify rejects a datum with no source pointer; an outcome can't be a free-floating hallucination, it must point at a spot in a registered transcript. (2) Idempotent ingest — `outcome ingest <label> --span <selector>` hashes the ingested transcript span and records {source, span_hash} in .keel; re-running ingest on the same span is refused with 'already ingested at <ts>, N outcomes — see outcome list --source X', so re-processing the same meeting can't silently duplicate the backlog. The model still does the judgment (reading the transcript, identifying the discrete points); the CLI enforces provenance, idempotency, and durability. rehydrate gains an OPEN OUTCOMES block (like the unflushed-pending block) so the standing backlog from ingested meetings loads every session without the user pointing at anything. `outcome close` requires an --evidence pointer, giving the backlog the same 'done needs proof' teeth as verify done.
- **sketch:** Commands:
  docs.py outcome ingest acme-q3 --span "last-part"   # marks span_hash ingested; refuses re-ingest
  docs.py outcome add --text "open with a sharper discovery question" --source acme-q3 --at 42:15
  docs.py outcome list [--open] [--source acme-q3]
  docs.py outcome close <id> --evidence journal/2026-07-14-discovery.md

add without provenance → exit 1:
  [!] outcome REJECTED — no --source/--at. An outcome with no transcript pointer is unanchored. (exit 1)

re-ingest guard:
  outcome ingest acme-q3: already ingested 2026-07-11 (6 outcomes). Not re-extracting.
     → docs.py outcome list --source acme-q3

rehydrate OPEN OUTCOMES block:
  [!] 4 OPEN OUTCOME(S) from ingested transcripts:
     acme-q3@42:15  open with a sharper discovery question
     acme-q3@48:03  send pricing one-pager within 24h
     → docs.py outcome list --open
- **fit:** The pending queue re-pointed at external inputs: JSONL, surfaced-in-rehydrate, drained by action. Provenance-required reuses verify's anti-fabrication rule. Idempotent-ingest is the deterministic form of 'never re-ask what is recorded' — the standing backlog replaces the user re-pointing at 'the last meeting.' close --evidence mirrors 'done needs a fresh passing check.'

### 3. Audit Rubric + Corpus Regression — a compounding eval set that separates nailed from failed without over-fitting
- **one-liner:** docs.py rubric: a persistent, versioned list of audit dimensions plus a corpus-regression eval that replays the rubric against the nailed/failed labeled runs — so dimensions compound across sessions and a coverage gate + discrimination check enforce 'all aspects, without overfitting.'
- **problem:** The audit dimensions are re-derived from scratch every session — no standing rubric — so learnings don't compound and coverage is whatever the model happens to think of that day. And there's no mechanism to keep the rubric honest across runs: a dimension motivated by one bad meeting can over-fit to it, and a nailed meeting can silently start failing a rubric that drifted too strict. keel's verify ratchet exists for objective data deliverables but nothing extends it to a subjective audit rubric graded against labeled exemplars.
- **evidence:** 'Tell me all the aspects on which you need to audit a conversation... so that all aspects are covered thoroughly without overfitting' (standing rubric + coverage gate + anti-overfit); 'audit of all meets there were 2 other meetings, one was pretty nailed and one it fucked up heavily... compound the learnings' (the nailed/failed pair is exactly a regression pair the rubric must keep classifying right — compounding, not re-deriving).
- **mechanism:** Part A — persistent versioned rubric docs/rubric.md: dimensions with {id, definition, motivating_source}. Supersede-aware like ADRs (retire, don't delete). rehydrate loads it, so a session STARTS from the standing rubric and only proposes ADDITIONS — dimensions never re-derived from zero. `rubric check <audit-output>` is a coverage gate: every active dimension id must be addressed in the audit output or it exits non-zero — deterministic 'all aspects covered thoroughly.' Part B — corpus regression `rubric eval`: this is the ratchet applied to judgment. It treats the registry's verdict-labeled sources (Innovation 1) as a labeled eval set and checks the rubric separates them: every 'nailed' exemplar must PASS the rubric, every 'failed' must FAIL on ≥1 dimension. A nailed exemplar that fails ⇒ rubric drifted too strict (over-fit to a failure); a failed exemplar that passes ⇒ rubric has a gap. The anti-overfit teeth: any dimension that fires on all runs or zero runs across the corpus is flagged as non-discriminating (dead weight / over-fit), the deterministic reading of 'without overfitting.' The model still authors dimension definitions and judges each transcript; the CLI enforces coverage, retirement-not-deletion, and that new/changed dimensions still classify every past labeled run correctly — the rubric can only get sharper without silently breaking on prior exemplars.
- **sketch:** Commands:
  docs.py rubric add --dim next-step-commitment --def "..." --from-run acme-q3
  docs.py rubric list
  docs.py rubric check audit-out.md    # coverage gate — every active dim addressed?
  docs.py rubric eval                  # regression across labeled corpus
  docs.py rubric retire pricing-anchor --reason "over-fit: only fired on globex-demo"

`rubric check` failure → exit 1:
  [!] audit skips 2 active dimensions: [objection-handling, next-step-commitment] (exit 1)

`rubric eval` output:
  RUBRIC EVAL — 6 dims x 3 labeled runs
    acme-q3      (nailed) → PASS ✓
    brainstorm-2 (nailed) → PASS ✓
    globex-demo  (failed) → FAIL on [objection-handling, next-step]  ✓ correctly caught
  VERDICT: separates nailed from failed on 3/3. ✅
  [!] dim 'pricing-anchor' fired on 3/3 (all) — non-discriminating, review.
  [!] dim 'tone' fired on 0/3 — dead/over-fit, review.

Check logic: for each labeled source, coverage of active dims → pass/fail; assert verdict=='nailed' ⇒ pass and 'failed' ⇒ ≥1 dim fails; per-dim fire-rate in {0, all} ⇒ flag.
- **fit:** Directly extends verify's 'every fixed bug becomes a permanent regression assertion' ratchet — here every verdict-labeled run becomes a regression exemplar the rubric must keep classifying, so learnings compound and can't silently regress. The all-or-nothing fire-rate flag is 'model legitimate absence / don't cry wolf' applied to rubric dimensions. Versioned + supersede-aware storage matches decisions/. It's the missing 'verify for subjective audits graded against a corpus,' which keel has no analog for today.

### 4. run — the durable resumable work-ledger (execution cursor)
- **one-liner:** An append-only per-item run ledger that makes 'where did I leave off', ETA, and idempotent resume deterministic — and blocks a clean rehydrate while any run is mid-flight.
- **problem:** keel's only progress-like state is the pending queue, which tracks un-written DECISIONS (ADR/journal kind+title) drained at loop END. It has no concept of a work-item universe, current position, throughput, ETA, resume-set, or per-agent attribution — and multi-hour scrapes/enrichments/swarms get interrupted before hydrate ever runs, so 'continue exactly where you left off' cannot be reconstructed and a fresh rehydrate shows nothing in progress. The invariant 'checkpoint after every unit of work, resume idempotently' is written five times across profiles/data-pipeline.md, profiles/automation.md, references/orchestrate.md and enforced zero times.
- **evidence:** 'CONTINUE EXACTLY WHERE YOU LEFT OFF DO NOT MISS OUT ON ANYTHING' (recurs); 'is it running rn?' / 'how long till it finishes?' / 'contnue, i don't see anything running'; 'lots of agents in swarm stopped mid process... assess what all is left and continue exactly where you left off'; 'how teh fuck will rehydrate work if nothing is written or noted here'. And the invariant already sits inert as prose in profiles/data-pipeline.md:23-24 ('Persist a checkpoint after every unit of work, not at the end') and profiles/automation.md:20 ('A run that dies at item 400 of 1,000 resumes at 400').
- **mechanism:** New EXECUTION-state tier: .keel/runs/<run-id>.jsonl, append-only (one fsync'd line per item = the checkpoint the prose demanded). Line 1 is a MANIFEST record (label, total, item-id universe or count, profile, host, start ts); every subsequent line is an ITEM record (item-id, status done|failed|skip, by=<agent>, ts, optional note). All progress is COMPUTED from replaying the ledger (same pattern as _contradictions/_deliverable_hash — never a hand-maintained counter that lies). A run is OPEN until a close record exists; an open run with pending>0 is a loud rehydrate problem, so a new session literally cannot rehydrate clean without first seeing the cursor. Reuses existing _append_jsonl/_load_jsonl and the rehydrate problems++ pattern.
- **sketch:** docs.py run start --label faire-enrich --items ids.txt   (or --count 1000)  -> RUN r7a3, 0/1000
docs.py run mark r7a3 brand_88231 --status done --by agent-3   (append-only, per item)
docs.py run resume r7a3   -> prints the exact PENDING item-ids (manifest minus done/skip) = idempotent skip-what's-done, feeds straight back into the worker loop
docs.py run status r7a3:
  RUN r7a3 "faire-enrich"  data-pipeline  by laptop
  progress  412/1000 done · 7 failed · 581 pending   (41%)
  position  last item #418 (brand_88231)
  rate      23.4 items/min (last 50)  ->  ETA ~24m
  heartbeat last mark 3m12s ago     [>10m => STALLED, flagged]
  by-agent  agent-1:140 · agent-2:138 · agent-3:134
  failed    [brand_401, brand_559, ...7]  -> run resume replays these
REHYDRATE gains _open_runs(): problems++ and exit 1 when any run has a manifest, no close, pending>0:
  [!] RUN MID-FLIGHT — r7a3 "faire-enrich": 412/1000 done, 581 pending, last mark 3m ago.
      -> resume where it left off: docs.py run resume r7a3   (do NOT restart from 0)
- **fit:** Moves the resumability invariant from five prose restatements into enforced CLI state + an unconditional rehydrate check — exactly what references/memory.md:71-75 says enforcement must be. Append-only like decisions/ and the whiteboard. 'Assume you will forget' — the ledger IS the memory; ETA/position are computed, never hand-bumped (rule c). Per-agent attribution makes a halted swarm restartable from the record, not from re-doing work (references/orchestrate.md manager/worker split).

### 5. sink — offline capture-inbox with idempotent reconcile
- **one-liner:** A durable landing zone where fetched payloads go the instant they're captured, with hash-deduped idempotent import into the master when the backend returns — so fetched data can never be silently disposed.
- **problem:** keel flushes DECISIONS continuously but has no continuous-flush path for the expensive fetched ARTIFACT itself. archive/inputs/ is a static rebuildable-source folder, not a live capture buffer; there is no dedup-by-hash, no offline import, and no check for 'fetched-but-never-landed'. So when the backend/master-CSV is unreachable mid-run, or the end-of-run write never happens, hours of fetched rows evaporate. The rule 'never dispose of fetched data, merge partials' (profiles/data-pipeline.md:28, orchestrate.md:53) has no teeth.
- **evidence:** 'Backend offline — saved 500 ads to the repo inbox... It'll auto-import when the backend is up. It was capturing but then it stopped in the middle' (a hand-rolled version of exactly this, with no primitive behind it); 'FUCKING INTERNALISE THAT WHEVER HOURS OR MINS ARE SPENT TO FETCH DATA DON'T just dispose it... ENTER IT IN THE MASTER CSV'. Matches profiles/automation.md Verify ('captured-count vs true-count') and data-pipeline provenance-per-field.
- **mechanism:** New state .keel/inbox/<stream>.jsonl, append-only. Each record = the fetched payload + a computed content-hash (dedup key) + provenance/source-pointer + intended target (e.g. data/master.csv). 'sink add' is where data goes the moment it's fetched — durable even when the target is down. 'sink import' idempotently reconciles: for each buffered record whose content-hash isn't already in a sidecar index, merge/append into the target and mark reconciled; duplicates are skipped by construction (satisfies 'resume is idempotent, don't double-append'). A non-empty unreconciled stream is a loud rehydrate problem: fetched-but-unlanded data is un-clearable debt, so you cannot rehydrate clean while captured bytes sit outside the master. Composes with run: a worker does run mark <id> done AND sink add <payload> per item — cursor and payload flushed together.
- **sketch:** docs.py sink add --stream ads --target data/master.csv --provenance <url> --from row.json
  -> sink: +1 ads (hash ab12), 500 buffered, target unreachable — held durably
docs.py sink status:
  ads    -> data/master.csv   500 buffered · 0 reconciled · oldest 2h ago · target: DOWN
docs.py sink import --stream ads   (run when backend is back)
  -> 500 buffered -> 483 new merged, 17 already present (hash dup) -> master.csv now 12,340 rows
REHYDRATE gains _unreconciled_sink(): problems++:
  [!] CAPTURE INBOX — 500 record(s) captured while target was unavailable, not yet merged:
      ads -> data/master.csv  (oldest 2h ago)
      -> fetched data at risk of disposal. Reconcile: docs.py sink import --stream ads
- **fit:** Makes 'never dispose fetched data' a deterministic un-clearable flag instead of a plea in prose — the exact enforcement-not-sentence principle of references/memory.md. Content-hash dedup is the anti-double-append guard; provenance pointer per record is the same anti-fabrication stance as verify's provenance check. Extends keel's 'flush continuously, never at the end only' (SKILL.md:91) from decisions to payloads.

### 6. mirror — cross-machine reconcile of execution state
- **one-liner:** Host-stamped, git-carryable, append-only run/sink ledgers that merge conflict-free across two mirrored machines, plus a rehydrate check that refuses to let one machine redo work the other already finished.
- **problem:** .keel/ is gitignored and machine-local, and claim locks are single-host fcntl files — so the run ledger and capture inbox don't travel. Two machines holding 'the literal same faire lead folder' diverge silently: the laptop finishes 400 items, the desktop's fresh session starts from 0 and re-does them, or worse breaks the thesis by overwriting. keel has no cross-host anything.
- **evidence:** 'That desktop also has the literal same faire lead folder... mirror version of this laptop' — two mirrored machines with divergent local state; combined with 'lots of agents in swarm stopped mid process... continue where you left off without breaking the entire thesis' (a halted swarm whose per-agent ledger must survive across the machines running it).
- **mechanism:** Because run/sink records are append-only and KEYED (run-id+item-id, or stream+content-hash) and now HOST-stamped, their union is conflict-free — the same property the whiteboard already relies on (references/orchestrate.md: append-only beats shared-editable). 'mirror enable' moves the ledgers from the gitignored zone into a tracked, mergeable location (docs/execution/*.jsonl) or a configured peer path, and installs a trivial union+dedup merge so git carries them without semantic conflict. 'mirror reconcile' unions the local ledger with the peer snapshot, dedups by key (last-status-per-key wins), and recomputes progress ACROSS both hosts, so run resume's pending-set automatically excludes items the other machine finished. A rehydrate divergence check flags when the peer holds keys the local ledger lacks. Honest limit (stated, per SKILL.md:77-79): keel can't force a git pull or reach the peer itself — it reconciles against whatever peer branch/snapshot is configured and surfaces divergence loudly; the transport is git or a shared folder, keel supplies the conflict-free format + reconcile + check.
- **sketch:** docs.py mirror enable   -> moves .keel/runs + .keel/inbox to docs/execution/ (git-tracked), installs union merge
docs.py mirror reconcile   (after git pull, or against configured peer path)
  -> unioned run r7a3: laptop 412 marks + desktop 137 marks = 470 unique done (79 overlap deduped)
docs.py mirror status:
  MIRROR run r7a3
    this host (laptop):  412 marks
    peer (desktop):      137 marks  [pulled 08:40]
    union:               470 unique items done -> resume set excludes the desktop's 137
REHYDRATE divergence check: problems++ when a configured peer snapshot has keys the local ledger lacks:
  [!] EXECUTION STATE DIVERGED across mirrors — desktop finished 137 items this host doesn't record.
      -> docs.py mirror reconcile before resuming, or you'll re-do the desktop's work.
- **fit:** Conflict-free-by-construction (append-only + keyed union) is the same design keel chose for the whiteboard over a shared-editable file. It carries the no-clobber-across-parallel-writers guarantee (references/memory.md:42-45, rule f) across machines, not just processes. It states its transport limit honestly rather than selling a block it can't enforce — keel's stated stance on gates it can only detect+surface.

### 7. Routing policy tier + `docs.py route` classify/check
- **one-liner:** A durable task-class-to-model routing policy that keel classifies work against deterministically and enforces at the contract gate — so ‘Fable for intelligence, Sonnet for grunt’ is codified once, not re-typed every session.
- **problem:** The user opens nearly every session by re-stating the same routing law ('USE FABLE ONLY FOR THE INTELLIGENT WORK and SONNET SESSIONS FOR ANY HEAVY LIFTING'). keel has no place to record a task-class-to-model policy and no check that a plan honors it. preferences.md holds engineering conventions but not routing. So the intent decays exactly the way memory.md warns about: a directive written in prose that the next session forgets, forcing the human to be the check.
- **evidence:** Direct quotes the user repeats across sessions: 'USE FABLE ONLY FOR THE INTELLIGENT WORK and SONNET SESSIONS FOR ANY HEAVY LIFTING' and 'conserve tokens on non intelligent task and maximise on intelligence'. These are re-explained per session today; memory.md's own thesis ('a fixed home for the fact, a docs.py check that flags violations, running inside rehydrate every session') is exactly the fix pattern this applies to routing. Repos faire-lead and brand-intelligence-app are full of grunt work (40k-row backfills, dedupe) interleaved with genuine intelligence work (entity/schema design), so the class split is real.
- **mechanism:** Add a routing tier and a `route` command family to scripts/docs.py. Policy resolves project-over-global: committed `docs/routing.md` overlays a `~/keel/routing.toml` default (precedence matches keel's existing 'recorded decisions -> user prefs -> defaults' order). A policy row is (task-class -> tier -> model) plus keyword triggers, e.g. grunt: scrape|extract|dedupe|normalize|backfill|migrate|re-run|bulk -> sonnet; intelligence: schema|entities|synthesize|judge|name|architecture|decide -> fable. `route classify "<work-item>"` deterministically maps a contract line to a tier by keyword match. `route check` reads the current contract's per-item routing (the BUILD CONTRACT gains a required tier/model column) plus the session's declared model (`.keel/session`, set by `docs.py session --model fable`) and FLAGS every grunt-class item routed to the premium model, and every intelligence-class item routed to the cheap model. It is wired into rehydrate as one surfaced digest line and into `contract check` so the build-start gate is routing-aware. HONEST LIMIT (keel's own 'don't sell blocks you can't enforce' rule): keel cannot force which model the harness runs, so `route check` is detect+surface — it converts a per-session verbal instruction into a codified policy and a deterministic mismatch flag ('you are running as FABLE but 2 of 5 contract items are grunt — delegate to a Sonnet subagent'), not a hard block.
- **sketch:** $ docs.py route check
ROUTING POLICY (docs/routing.md over ~/keel/routing.toml)
  grunt        -> sonnet   scrape|extract|dedupe|normalize|backfill|migrate|re-run|bulk
  intelligence -> fable    schema|entities|synthesize|judge|name|architecture|decide
SESSION MODEL: fable   (.keel/session)
CONTRACT items (5):
  OK  design lead-scoring entities        intelligence  fable
  X   backfill 40k faire brand rows       grunt         fable   <- premium model on grunt work
  X   dedupe ads table                    grunt         fable   <- delegate to a sonnet subagent
VERDICT: 2 grunt item(s) routed to the premium model -- delegate or justify. (exit 1)

# wiring: /Users/rabnoor.singh/Desktop/keel-skill/scripts/docs.py cmd_contract('check') calls route_check(); SKILL.md section 2 gains a 'routing column' line in the BUILD CONTRACT spec.
- **fit:** Textbook keel: the invariant (routing law) moves out of prose into deterministic CLI state; a check runs in rehydrate every session unconditionally; precedence follows the existing project-over-global order; and it is honest about being detect+surface rather than overselling a block it can't enforce.

### 8. Budget ledger: estimate-gate + persistent cap + conserve mode
- **one-liner:** A `docs.py budget` family that makes a pre-run cost estimate a HARD precondition of the contract gate, a persistent dollar cap the loop reads, and a conserve-mode flag that auto-tightens the build gate to extract-not-re-run when the cap runs low.
- **problem:** The user wants estimates before committing ('you give me the evaluation of token consumption estimates and we can start fast'), hard dollar caps ('budget is $3-4'), and a loop that visibly respects remaining spend ('we are very low on tokens... let's work efficiently'). Today all of this lives in chat and evaporates: no estimate is required before a build, no cap persists across sessions, and 'low on tokens, work efficiently' is a plea with no mechanism behind it. keel's contract gate already gestures at this ('state its rough cost... is a cheaper external tool already doing this?') but nothing codifies or enforces it.
- **evidence:** 'you give me the evaluation of token consumption estimates and we can start fast' -> the estimate-gate makes that estimate a build precondition, not a courtesy. 'budget is $3-4' and '$2 or $5 on gr is not a problem if needed' -> a persistent, adjustable cap with a global default. 'we are very low on tokens so if you need something manually ask me, let's work efficiently' -> exactly conserve mode: below-threshold flips the build gate to extract-not-re-run and tells keel to ask before any fan-out. Applies across all four repos (faire-lead, meeting-audit, brand-intelligence-app, knowledge-graph-rag) since each runs costly pipelines/agents.
- **mechanism:** Add a `budget` command family backed by an append-only `.keel/budget.jsonl` ledger and a persistent `.keel/budget.cap` (default cap sourced from a one-line ~/keel/preferences.md entry so '$3-4' is a standing preference, not re-typed). (1) ESTIMATE-GATE with real teeth: `budget estimate --usd 2.10 --tokens 1.5M --basis "..."` binds an estimate to the current contract hash; `contract check` (the build-START gate in cmd_contract) now HARD-REFUSES with exit 1 if no estimate is attached, or if the estimate exceeds remaining cap — this part is fully enforceable because it gates keel's own contract artifact, so it can't be talked past. (2) PERSISTENT CAP: `budget cap --usd 4` survives across sessions in .keel. (3) CONSERVE MODE: `budget record --usd 0.80 --item "faire scrape"` appends actuals; `budget check` sums spend vs cap and, when remaining crosses a threshold (<25% of cap), sets a persistent conserve flag and exits non-zero. While conserve is on, rehydrate surfaces it every session AND `contract check` additionally requires each build item to declare 'reuse/extract from existing artifact' rather than 'full re-run' — turning keel's existing prose default ('never dispose of costly data; prefer incremental/resumable work') into a budget-triggered gate. HONEST LIMIT: keel can't meter tokens itself; actuals must be recorded by the agent or imported from a harness usage file. The estimate/cap precondition is hard; the spend-vs-cap accounting is as good as the recorded numbers — stated plainly, not oversold.
- **sketch:** $ docs.py budget check
CAP: $4.00   (.keel/budget.cap; default $3-4 from ~/keel/preferences.md)
SPENT: $3.55  across 6 recorded items
REMAINING: $0.45  (11% of cap)
[!] CONSERVE MODE ON -- targeted extracts only; no full re-runs; ask before any fan-out.
    contract check now requires each build item to declare reuse-from-artifact, not re-run.
(exit 1)

$ docs.py contract check          # build-START gate, now cost-aware
contract check: X no budget estimate attached for contract 4f2a91 -- run `budget estimate` first. (exit 1)

# wiring: cmd_contract('check') in /Users/rabnoor.singh/Desktop/keel-skill/scripts/docs.py gains an estimate+cap precondition; cmd_rehydrate adds a CONSERVE/BUDGET digest block next to the existing VERIFY STALE block.
- **fit:** Mirrors keel's verify gate exactly — a precondition enforced by exit code rather than prose ('an exit code is a gate; prose is a suggestion the model can forget under pressure'). The cap is a durable memory-tier fact with a global default; conserve mode upgrades an existing standing default into an enforced check; and the limit (keel can't meter tokens) is disclosed rather than papered over.

### 9. Cost ratchet: `budget reconcile` + waste-pattern guard
- **one-liner:** After-the-fact estimate-vs-actual accounting that runs inside hydrate, plus a durable waste-pattern list that `contract check` matches future plans against — the regression-assertion ratchet applied to spend.
- **problem:** When tokens are burned on the wrong thing the user says so bluntly ('YOU WASTED RESEARCH TOKENS ON THAT ENTIRE RESEARCH'), but that lesson evaporates — nothing records where spend diverged from the estimate, and nothing stops the same waste next week. keel has a powerful pattern for exactly this ('every fixed bug becomes a permanent regression assertion... the audit is a ratchet, it only ever gets stricter') but it is applied only to correctness, never to cost.
- **evidence:** 'YOU WASTED RESEARCH TOKENS ON THAT ENTIRE RESEARCH' is the exact event this captures: reconcile would have flagged the research fan-out as the +300% overrun line, and `waste add` would make 'full research fan-out on already-scraped brands' a pattern the next contract in brand-intelligence-app / knowledge-graph-rag is checked against. It operationalizes the theme's 'after-the-fact accounting of where tokens were wasted' and 'prefer targeted extracts over full re-runs.'
- **mechanism:** Two parts on top of the budget ledger. (1) `budget reconcile` compares the bound estimate against recorded actuals per work-item/task-class, prints a variance table, and names the biggest overrun. It runs automatically inside `hydrate`, so every closed loop lands a one-line cost postmortem into the journal (keel already treats an active session ending without a journal entry as an anomaly). (2) WASTE-PATTERN GUARD: `waste add --pattern "full research fan-out on already-scraped brands" --cost 1.20 --instead "targeted extract from archive/inputs"` appends to a durable, append-only `docs/waste-patterns.md` (committed, travels with the repo; cross-project ones go to global prefs). `contract check` then keyword-matches every new plan against recorded waste patterns and surfaces a warning: 'this plan resembles WASTE-PATTERN #2 ($1.20 wasted 2026-07-10) -> prefer targeted extract.' HONEST LIMIT: like the routing check this is detect+surface (a warning on the contract, not a hard block, since plan text is fuzzy) — but it makes an identified waste a permanent, session-crossing guard instead of a one-time scolding.
- **sketch:** $ docs.py budget reconcile          # also invoked inside `hydrate`
ESTIMATE vs ACTUAL (contract 4f2a91)
  item                     est     actual    delta
  faire scrape             $0.80   $0.75     -6%
  lead research fan-out    $0.40   $1.60    +300%   <- overrun
  TOTAL                    $2.10   $3.55     +69%
biggest waste: lead research fan-out (+$1.20)
  -> record it: docs.py waste add --pattern "..." --cost 1.20 --instead "targeted extract"

$ docs.py contract set --from plan.md && docs.py contract check
[!] plan resembles WASTE-PATTERN #2 ($1.20 wasted 2026-07-10):
    "full research fan-out on already-scraped brands" -> prefer targeted extract from archive/inputs.

# wiring: cmd_hydrate in /Users/rabnoor.singh/Desktop/keel-skill/scripts/docs.py calls budget_reconcile() before draining the queue; cmd_contract('check') adds a waste-pattern scan alongside the routing check.
- **fit:** This is keel's ratchet philosophy ('the audit only ever gets stricter; a later agent can't reintroduce the exact bug you just fixed') extended from correctness to spend: an identified waste becomes a permanent, committed guard. It reuses the append-only + supersede-aware memory discipline, lands its postmortem through the existing continuous-hydrate path, and is honest that the guard is a surfaced warning, not a block.

### 10. handoff — cross-worktree coordination tier (report-up + inbound handoffs)
- **one-liner:** A shared, addressed, append-only handoff/report ledger keyed to the git common dir so it spans worktrees, turning keel's flat one-filesystem peer model into a hierarchical manager/worker channel across sessions and branched-off worktrees.
- **problem:** keel's whiteboard + claim locks live in .keel/ under a single cwd (scripts/docs.py:29-34, STATE=ROOT/.keel). The instant a sonnet grunt works in a separate `git worktree` branched off the manager's tree, the two share no .keel/ — the flat peer model silently breaks and neither can see the other. The user's real handoffs (IG-audit-handoff-2026-07-09.md) are loose files keel doesn't recognize as memory: rehydrate never surfaces them, and there is no from/to, no source-commit, no open/consumed status, and no report-up channel back to the opus manager.
- **evidence:** 'intelligence managed by opus and grunt work by sonnet' / 'fucking tell me what's wrong to report to your opus manager' (the report-up channel); 'check this from the other manager IG-audit-handoff-2026-07-09.md' (unrecognized handoff doc); 'still pending in the other sonnet session in a separate worktree which i branched from here' (pending work in a non-shared worktree, invisible to keel today).
- **mechanism:** A new coordination tier keyed to `git rev-parse --git-common-dir` — the ONE path every linked worktree of a repo agrees on (each worktree's .git file points back to it), which is the deterministic fix for the single-filesystem assumption. `docs.py handoff send/report` writes append-only JSONL records there (reusing the existing _append_jsonl/_load_jsonl helpers): {id, from_role, to_role e.g. manager|grunt, kind: handoff|report, title, body_path, source_sha=`git rev-parse HEAD`, worktree, status: open|acked|consumed}. rehydrate gains a CROSS-WORKTREE panel (same panel+problems+exit-1 pattern as lines 297-334): runs `git worktree list --porcelain`, lists sibling worktrees and their HEADs, prints OPEN handoffs addressed to me, and FLAGS LOUDLY my outbound handoffs still unconsumed and pending work parked in another worktree. `handoff import <file>` ingests an ad-hoc IG-audit-handoff-*.md into the ledger stamped with author role + commit, so keel finally treats that doc as recognized memory.
- **sketch:** $ docs.py handoff send --to grunt --kind handoff \
    --title "IG audit: enrich 485 brand rows" --from-file IG-audit-handoff-2026-07-09.md
handoff#7 -> grunt  source_sha=a1c9f2  worktree=ig-audit  status=open
  (written to <git-common-dir>/keel/coord/ — visible from every worktree of this repo)

$ docs.py handoff report --to manager --re 7 --title "audit done: 3 fields still empty"
report#8 -> manager  re handoff#7  status=open      # the 'report to your opus manager' channel

# folded into rehydrate:
--- CROSS-WORKTREE (git-common-dir coord) ---
worktrees:  main@a1c9f2 (HEAD)  ·  ig-audit@f77b10  ·  brain-extract@0c22d1
[!] 1 OPEN handoff addressed to me (manager):
    #8 report from grunt @f77b10: "audit done: 3 fields still empty"  (re #7)
[!] 1 handoff I emitted is UNCONSUMED: #7 -> grunt (open 4h) — work may be stranded in worktree ig-audit
    -> that worktree's .keel is NOT shared; the git-common-dir coord IS. (exit 1)
- **fit:** Same 'coordination by construction, not by remembering' spirit as whiteboard/claim (references/orchestrate.md:26-37), but lifted off the single-filesystem assumption onto the only anchor all worktrees share. Append-only, addressed, and provenance-stamped with source_sha — no clobber, and no fabrication about who did what against which tree state.

### 11. sync/teammate — deterministic git mergeability guard for a human collaborator
- **one-liner:** Registers a teammate's ref and computes divergence plus a read-only three-way mergeability probe (git merge-tree) that fails loudly in rehydrate the moment your branch stops being cleanly mergeable back to them.
- **problem:** scripts/docs.py has zero git awareness anywhere, yet the user's hardest recurring task is human coordination through git: branch off Saurabh's last update, stay rebased on his commits, and 'make sure is mergeable for saurabh.' Today that is eyeballed. There is no deterministic answer to 'am I ahead/behind, has my fork-point gone stale, and will my work conflict when Saurabh merges it' — precisely the kind of silent drift keel exists to convert into a loud, unmissable check.
- **evidence:** 'create a new branch of saurabh's last update and git pull'; 'Help me get where saurabh reached and stay synced and dev on top... make sure is mergeable for saurabh' — 'understand divergence' and 'guarantee the branch stays mergeable' are exactly a deterministic divergence + merge-tree computation.
- **mechanism:** `docs.py teammate set saurabh <ref>` records the tracked ref in .keel/teammate (mirroring how PROFILE is stored, line 28/548-554). `docs.py sync` computes ground truth, all read-only (map before build): ahead/behind via `git rev-list --left-right --count HEAD...<ref>`; fork-point staleness via `git merge-base --is-ancestor`; and the crucial mergeability probe via `git merge-tree --write-tree <merge-base> <ref>` (git >=2.38; legacy `git merge-tree` as fallback), which performs the 3-way merge in memory and lists conflicting files WITHOUT touching the working tree. rehydrate gains a TEAMMATE SYNC panel and treats 'diverged AND merge-tree reports conflicts' as a loud problem (exit 1) — the git analogue of keel's 'do not build on a superseded ADR': do not build on a base that will not merge back.
- **sketch:** $ docs.py teammate set saurabh saurabh/main
teammate: saurabh -> saurabh/main  (fork-point recorded at merge-base 7fd0aa)

$ docs.py sync
TEAMMATE saurabh (saurabh/main @ e04b71)
  ahead 6  ·  behind 12                 # 6 commits of yours; 12 of theirs you lack
  fork-point staleness: your base 7fd0aa is 12 commits behind their HEAD (rebase to re-sync)
  MERGEABILITY (git merge-tree, read-only, tree untouched):  x 2 files would conflict
     src/pipeline/enrich.py
     docs/data-model.md
  -> resolve now, not at merge time. `git rebase saurabh/main`, then re-run sync.

# in rehydrate:
[!] TEAMMATE saurabh — behind 12 and 2 files would CONFLICT on merge-back.
    -> your branch is NOT currently mergeable for Saurabh. (exit 1)
- **fit:** Honesty over agreeableness applied to git: merge-tree is ground truth, not a guess, and it never mutates the working tree. Converts 'guarantee the branch stays mergeable' from a hope the model must remember into an invariant re-checked every rehydrate — invariants in the deterministic CLI, not in prose.

### 12. compartment — curated extract / promote across an enforced contamination boundary
- **one-liner:** Treats a workstream (the 'brain', the 'ig' track) as a labeled compartment and computes its transitive reference-closure, so you can extract it to a new repo — or promote it into canonical docs — with a deterministic leak report that refuses to carry any reference across the declared boundary.
- **problem:** keel models one project's memory in place (references/memory.md) and has no notion of moving a curated SUBSET with an explicit boundary. The user needs exactly that, twice and in opposite directions: 'tear out the brain repo... no contamination outside what we discussed here to be rehydrated into the new repo,' and its inverse 'merge the ig things into the real docs overall.' Done by hand, extraction strands dangling ADR cross-references (contamination that silently re-imports excluded context) or drops context the moved docs depend on — with no check either way.
- **evidence:** 'this brain repo is the one i want to tear out from here... no contamination outside what we discussed here to be rehydrated into the new repo' (extract with an explicit inclusion/exclusion boundary); 'now that everything works cleanly, merge the ig things into the real docs overall of this folder' (promote a proven sandbox track into canonical docs). Repos named in the theme (knowledge-graph-rag / brain, instagram-enrichment) are the concrete source/target.
- **mechanism:** A compartment = a label on ADRs/journal/memory (front-matter `compartment: brain`, or a path prefix). keel already parses the ADR-reference graph (_ADRREF at line 40, reused by _contradictions/_suspect_decisions) — reuse that exact graph. `docs.py compartment extract brain --to ../new-repo`: (1) inclusion set = docs labeled brain; (2) compute the transitive ADR-reference closure; (3) any reference from an INCLUDED doc to an EXCLUDED doc = a LEAK (contamination); (4) emit a manifest INCLUDED / EXCLUDED / LEAKS and REFUSE to copy while any leak exists — resolve = include the target, or sever the reference — the same gate discipline as verify done (lines 493-501). `docs.py compartment promote ig --into docs/` is the inverse merge with the identical boundary check, so nothing canonical silently pulls in ig-private context and vice-versa.
- **sketch:** $ docs.py compartment extract brain --to ../knowledge-graph-rag
COMPARTMENT brain — reference-closure boundary check
  INCLUDED  9 docs:  decisions/0007,0011,0014 · memory/graph-schema.md · journal/2026-07-0{2,6,9} ...
  EXCLUDED (stay behind):  decisions/0009 (faire-lead pipeline) · memory/ig-scrape.md
  [!!] 2 LEAKS — included docs reference EXCLUDED context (would carry a dangling pointer):
     decisions/0014 -> "supersedes ADR 0009"      (0009 is EXCLUDED)
     memory/graph-schema.md -> "see ig-scrape.md"  (EXCLUDED)
  REFUSING export. Resolve each: include the target, or sever the reference. (exit 1)

$ # after resolving:
$ docs.py compartment extract brain --to ../knowledge-graph-rag
  OK boundary clean — 9 docs + anchor copied to ../knowledge-graph-rag/docs/  (manifest: .keel/extract-brain.json)
- **fit:** The contamination boundary is keel's provenance / anti-fabrication ethic applied to portability: a moved memory subset must carry every source it points to, or the pointer is severed on purpose — nothing travels by accident. Reuses the existing ADR-reference parser and gates the copy exactly as verify gates 'done.' (Adjacent unmet need this leaves open — 'WE FINALISED IT... can't see where the prompt was used or where outputs landed' — is best served later by extending _deliverable_hash into a content-hash provenance ledger; noted, not padded into a weak fourth.)

### 13. critique — the proposal-audit gate (symmetric bookend to verify)
- **one-liner:** A pre-build audit that blocks `contract approve` until the proposal carries a stress-tested assumption ledger, multi-angle research provenance with surfaced gaps, and rejected alternatives — the same provenance-or-fail mechanic verify applies to data, applied to the plan.
- **problem:** keel's rigor is entirely post-build. `verify done` (docs.py:493) refuses to claim done unless a passing audit is bound to the deliverable hash; but `contract approve` (docs.py:436) just flips `approved=True` with zero quality check. So the assumption audit, the research grounding, and the 5-why the user keeps screaming for are pure prose in SKILL.md — forgettable under pressure, exactly the failure mode keel says it guards against. The user has to hand-invoke 'sensei mode' every single time because nothing gates the plan.
- **evidence:** Directly answers 'THERE WAS NO INNOVATION AT ALL FUCKING NO RESEARCH LEVERAGED' (rules 2+3), 'DO AN EXTREMELY THOROUGH 5 WHY ANALYSIS' and 'SOME ASSUMPTIONS WERE DEEPLY WRONG' (rule 1 — untested load-bearing assumptions become a hard fail), and 'find the gaps... propose the real golden phase 2' (rule 3). Verified against baseline: `contract` (docs.py:427-448) has only set/approve/check and performs no rigor audit; no assumption or research ledger exists anywhere in docs.py. Genuinely new.
- **mechanism:** A `critique` command family building a proposal ledger in `.keel/critique/`, bound to the current contract plan's hash (mirroring how verify binds to `_deliverable_hash()`).

Build the ledger incrementally:
- `docs.py critique assume --claim "brand is unique per row" --bearing load|minor --status untested|tested|user-confirmed [--source "file:line|url|query@ts"]`
- `docs.py critique research --angle "pricing models" --source "<pointer>" --finding "..." [--gap "no data on tiered wholesale"]`
- `docs.py critique alt --option "embedding dedup" --rejected-because "latency 4x, marginal recall gain"`

Then `docs.py critique check` runs a deterministic audit that exits non-zero (identical enforcement shape to `verify run`). Check logic — all structural/provenance, never semantic-truth (same honest bargain verify makes):
  1. FAIL if any assumption with bearing=load has status=untested — the direct analog of verify's 'a derived datum with no source pointer fails as fabricated' (references/verify.md:29). A load-bearing untested assumption is a fabricated foundation. This is what forces the assumption audit BY DEFAULT.
  2. FAIL if the research ledger covers < K distinct angles (K from `clarify-depth`, default 3) OR any source lacks a pointer. Zero-grounding = the literal 'no research leveraged' failure.
  3. FAIL if no `--gap` was ever recorded — a proposal that surfaced no gaps across K angles didn't actually look. Forces 'surface the gaps found.'
  4. FAIL if < 2 rejected alternatives — anti first-idea-wins.
Stamp pass/fail + plan-hash to `.keel/critique.stamp`.

Wire the gate: extend `cmd_contract` action `approve` (docs.py:436) to refuse unless `critique.stamp` is pass AND its plan-hash equals the current contract hash — byte-for-byte the guard `verify done` already uses (docs.py:499). Change the plan, critique goes stale, must re-run.
- **sketch:** $ docs.py critique check
CRITIQUE AUDIT — proposal rigor gate (blocks contract approve)
  assumptions:   7 ledgered — 2 load-bearing UNTESTED            ✗
     - "brand names unique per row"   [load, untested]  ← verify or downgrade
     - "CRM export is complete"        [load, untested]
  research:      2 angles (need >=3)                              ✗
                 gaps surfaced: 0 (need >=1)                       ✗
  alternatives:  1 rejected (need >=2)                            ✗
VERDICT: FAIL — 4 gap(s). `contract approve` is blocked. (exit 1)

$ docs.py contract approve
contract approve: ✗ critique.stamp FAILING for this plan — run `critique check`, close the gaps. (exit 1)
- **fit:** Pure keel: 'invariants live in the deterministic CLI, not prose'; extends provenance-as-anti-fabrication from data to plan-claims; it IS 'map before build' given teeth. The honest-limit note (SKILL.md:78) applies verbatim — teeth exist only when the proposal is routed through `critique`, and the checks are structural (counts, pointers), not truth-judging — same deal verify already makes.

### 14. critique charter — independent red-team with a provenance-independence gate
- **one-liner:** Emits a structured red-team brief with a mandatory inversion angle, then requires the contract to carry critique verdicts whose provenance token differs from the proposer's — so a plan cannot be approved on the author's own rationalization, only on independent eyes.
- **problem:** The user demands keel 'spawn fresh sessions for extreme thorough critique' of its OWN judgment, unprompted. But keel's orchestrate doctrine is the opposite: it delegates only grunt work and says 'Never delegate judgment' (orchestrate.md:14). There is no primitive for adversarial critique of the agent's reasoning, and nothing stops the model from grading its own homework — the same rubber-stamp risk verify exists to kill, but for plans instead of deliverables. Self-critique in one session is just rationalization with extra steps.
- **evidence:** Answers 'it's as much your job to spawn fresh sessions for extreme thorough critique... BE THE FUCKING BEST PARTNER' and 'reiterate with a multi facet multi agent web search' (rules 3+4). Baseline check: orchestrate.md only covers manager/worker grunt delegation and explicitly forbids delegating judgment; `whiteboard`/`claim` exist but there is no critique charter, no verdict record, and no independence check anywhere in docs.py. New.
- **mechanism:** Invert the orchestrate rule for exactly one task: critique is the judgment you MUST delegate, because you cannot red-team your own rationalization.

- `docs.py critique charter` emits `.keel/critique/charter.json` = {plan_hash, author_token, angles:[...]} and prints a hand-off brief. It AUTO-INSERTS a required `inversion` angle: 'Assume the recommended option is wrong; make the strongest case for the top rejected alternative from the `alt` ledger.' Author token is read from `KEEL_SESSION` (or `--by`), reusing the provenance-token pattern already in `whiteboard`/`claim --by` (docs.py:521,536).
- A fresh/independent session (spawned by the model or the user) posts: `docs.py critique verdict --by <token> --angle inversion --finding "..." --severity high|med|low [--better-approach "..."]`.
- `critique check` (Innovation 1) gains two more deterministic gates:
  5. Coverage: every chartered angle has >=1 verdict.
  6. Independence: at least one verdict's `--by` token != charter author_token. If all verdicts share the author's token → FAIL 'self-critique does not count.' Independence is thus a mechanical property (distinct provenance), not a vibe — the same way verify makes 'verified' mean an exit code, not agreement.
- If any verdict carries `--better-approach`, check surfaces it and BLOCKS approve until it is disposed (hands to Innovation 3's thesis record) — a discovered-better idea can't be silently buried.
- **sketch:** $ docs.py critique charter
RED-TEAM CHARTER (plan a91c, author sess-000) — hand to a FRESH session:
  angle[1] assumptions   — attack the 2 load-bearing untested assumptions
  angle[2] research-gaps — the ledger surfaced 0 gaps across pricing/catalog; find them
  angle[3] inversion*    — argue the strongest case for the rejected 'embedding dedup'
  (* mandatory; a plan no one argued against is unexamined)

$ docs.py critique verdict --by sess-7f3 --angle inversion --severity high \
    --finding "fuzzy-match dedup silently merges sub-brands" --better-approach "embed dedup"
verdict recorded (sess-7f3) — carries a BETTER-APPROACH; must be disposed before approve.

$ docs.py critique check
  red-team: 3/3 chartered angles covered
     independence: authors {sess-7f3,sess-9a1} != proposer sess-000       ✓
     BETTER-APPROACH (sess-7f3, high): "embed dedup" — UNDISPOSED          ✗
VERDICT: FAIL — 1 undisposed better-approach. (exit 1)
- **fit:** 'Honesty over agreeableness' operationalized: independent provenance stops the model agreeing with itself. Reuses keel's existing provenance-token and append-only-coordination primitives rather than inventing new ones, and it consciously, narrowly overrides 'never delegate judgment' with a stated reason — the kind of recorded, justified deviation keel favors over silent drift.

### 15. redo ratchet — quality-fail opens a redo obligation that must differ along recorded axes
- **one-liner:** A verify-fail or an explicit corrective-learning entry opens a REDO obligation; the re-proposal cannot be approved until it demonstrably cites the learning, adds a named adjacent AND a named opposite angle versus the failed snapshot, and records whether a better-than-agreed approach emerged.
- **problem:** When output is poor, keel just... tries again, with no memory that the last attempt failed and no requirement that the retry actually explore differently. The user's exact complaint: 'after such poor performance this should have been rerun with the corrective learning and deeper in this particular and similar and dissimilar angles,' and 'self correction if any contradictions/thesis deviations found... better than the original.' Baseline has no redo concept at all — a failed proposal and its successor are unlinked, so the retry can silently repeat the same blind spot.
- **evidence:** Answers 'this should have been rerun with the corrective learning and deeper in this particular and similar and dissimilar angles' (rule 4 — a+b) and 'self correction if any contradictions found, any innovative inspirations/thesis deviations found... better than the original' (rule 4 — c, the mandatory thesis-deviation record). Baseline check: docs.py has no `redo` command, no obligation state, and `verify run` (docs.py:485) stamps but opens nothing; contradiction detection (docs.py:180) finds ADR reversals but does not force a differentiated retry. New.
- **mechanism:** Apply keel's core ratchet doctrine ('every fixed bug becomes a permanent assertion', verify.md:84) to proposals: every poor proposal becomes a redo obligation carrying its corrective learning forward.

Deterministic triggers (no vibes):
- `verify run` exiting non-zero auto-opens a redo obligation (it already stamps; add the open).
- `docs.py redo open --learning "assumed brand==row; actually 1:N brand→product, broke dedup" [--for <plan-hash>]` — the model calls this the moment the user reacts negatively. It snapshots the failed plan's hash, its research-angle set, and its chosen approach.
- SOFT signal only (respecting 'don't cry wolf', verify.md:68): a `supersede` retiring an ADR authored in the current session prints a SUSPECT-redo hint — never an auto-hard-open, matching the existing suspect-decisions posture (docs.py:198).

While any redo is OPEN, `critique check` adds requirements computed by diffing the new ledger against the snapshot:
  (a) the corrective-learning id is cited by >=1 new ledger entry (`assume/research --addresses L2`);
  (b) the new research ledger contains >=1 angle NOT in the snapshot (adjacent) AND >=1 entry flagged `--opposite` (dissimilar/inversion) — a set-difference on angle names, fully mechanical;
  (c) a thesis-deviation record exists: `docs.py redo thesis --deviation "embed dedup beats agreed plan"` OR `--none "explored embed+supplier-side; agreed plan stands because recall parity at 1/4 latency"`. The field is mandatory, so 'did anything better than the agreed plan surface?' is answered every redo, not skipped.
`docs.py redo close` (and thus `contract approve`) is refused until (a)(b)(c) pass; close links the new plan-hash to the resolved obligation.
- **sketch:** $ docs.py redo open --learning "assumed brand==row; actually 1:N brand→product (broke dedup)"
redo #2 OPEN (learning L2, snapshot a91c). Re-proposal must: cite L2; add >=1 adjacent
+ >=1 opposite angle vs {pricing,catalog}; record a thesis-deviation.

$ docs.py redo status
REDO #2 (open) — supersedes failed proposal a91c
   L2 cited by new ledger:                    ✗ not yet
   new adjacent angle vs {pricing,catalog}:   ✓ "supplier-side dedup"
   new opposite angle (--opposite):           ✗ none
   thesis-deviation recorded:                 ✗
   → 3 requirement(s) open; `contract approve` blocked. (exit 1)
- **fit:** It is verify's ratchet ('the audit only ever gets stricter') moved to the proposal side: a failure permanently raises the bar for its own retry and carries the specific learning forward, enforced by the CLI rather than by remembering. The soft-SUSPECT trigger honors 'a gate that cries wolf gets ignored' (SKILL.md:88). Closes the loop with Innovations 1+2 on one shared ledger substrate.

### 16. blast-radius — post-hoc scope-containment proof (docs.py scope)
- **one-liner:** Snapshot git state of the working repo plus declared sibling repos at contract-approval, then PROVE at build-end that nothing changed outside the contract's declared file-scope; any write into a git-synced sibling fails loudly with an exit code.
- **problem:** The user's sharpest fear is a stray write corrupting a SEPARATE system: 'do not touch any files... they are running in sync with git, do a thorough reassessment that nothing was changed in our process in other folders' and 'thoroughly read and tell where I asked you to stop and what all actually has been implemented... REACESS EVERYTHING as sensei'. keel's contract declares a file-scope and a will-NOT-do list, but NOTHING checks the actual filesystem against it afterward. Worse: keel already tells the model to 'map the blast radius' in prose (modes/refactor.md, add-feature.md, upgrade-migrate.md) — the exact 'directive in prose the model forgets under pressure' that keel's own philosophy says must live in code. Cross-repo overreach is silent and, on git-synced siblings, destructive.
- **evidence:** 'do not touch any files... they are running in sync with git, do a thorough reassessment that nothing was changed in our process in other folders' and 'tell where I asked you to stop and what all actually has been implemented... REACESS EVERYTHING as sensei'. Confirmed new: grep shows 'blast radius' appears only as prose in modes/*.md and 'scope' only inside verify sync — no snapshot/diff mechanism, no cross-repo check exists in docs.py.
- **mechanism:** Git is the external oracle (keel's veracity cross-check, not self-grading). (1) On `contract approve`, auto-run `scope snapshot`: for the project ROOT and each sibling root, record `git rev-parse HEAD` + a hash of `git status --porcelain -z` + a content hash of every already-dirty file, into .keel/scope-baseline.json. Allow-globs default to the contract's declared 'files' section; sibling roots are auto-detected as sibling directories of ROOT that are their own git repos, overridable via .keel/siblings. (2) `docs.py scope audit` (the blast-radius proof) recomputes current git state and diffs vs baseline, classifying every changed path: (a) inside an allow-glob and in-project = EXPECTED; (b) in-project but outside allow-globs, or matching a will-NOT-do pattern = OVERREACH; (c) ANY delta in a sibling root (HEAD moved OR working-tree differs from baseline) = BLAST-RADIUS BREACH. Exits non-zero on any (b) or (c). (3) rehydrate gains a SCOPE block: if a baseline exists and the audit shows breaches, it fails loudly like contradictions do. Honest-limit (stated, per SKILL.md): this PROVES containment after the fact via git — it cannot PREVENT a raw Write; the user asked for exactly the proof ('reassessment that nothing was changed'), so detect-and-surface is the honest deliverable, not a block it can't enforce.
- **sketch:** $ docs.py contract approve         # auto: scope snapshot (ROOT + siblings ../knowledge-graph-rag, ../brand-intelligence-app)
$ docs.py scope audit
BLAST-RADIUS AUDIT — baseline @ contract-approve 14:02, 41 paths changed since
  REPO                     PATH                          verdict
  faire-lead (this)        pipeline/enrich.py            EXPECTED   (in allow-glob pipeline/**)
  faire-lead (this)        pipeline/score.py            EXPECTED
  faire-lead (this)        cofounder-viz/deck.json      OVERREACH  (outside contract files; will-NOT-do)
  knowledge-graph-rag      graph/store.db               [!!] SIBLING BREACH — git-synced, working tree moved
  brand-intelligence-app   (clean, HEAD unchanged)      contained
VERDICT: ✗ 1 overreach, 1 sibling breach — exit 1. Nothing may be called 'done'.
# clean run:
VERDICT: ✅ contained — 39 changes, all inside declared scope; siblings byte-identical to baseline.
- **fit:** Uses git as an external oracle exactly as verify.md prescribes for veracity ('cross-check against an independent enumeration, not the pipeline that graded itself'). Converts an existing PROSE directive ('map the blast radius') into an exit-code gate — the literal 'invariants live in the deterministic CLI, not prose' tenet. Bookends the contract: contract gates the START of a build by scope, blast-radius gates the END by scope, symmetric with how verify done mirrors the contract. Honest about the raw-Write limit rather than overselling prevention.

### 17. ask ledger — standing user-ask register with verify-bound resolution (docs.py ask)
- **one-liner:** Every user-facing feature/bug ask becomes a tracked entry that can only reach VERIFIED-RESOLVED when bound to a passing named assertion in the verify audit; if that assertion later fails or the deliverable changes un-reverified, the ask auto-flips to REGRESSED and rehydrate surfaces it with its re-raise count.
- **problem:** 'STill i hover info is overflowing... WTH I have asked for this so many times' and 'still seems to be not additive'. The model repeatedly claims an ask resolved; the user repeatedly re-raises it; NOTHING counts the re-raises or binds 'resolved' to a real check. keel records point decisions (ADRs) and dated journal notes, but a user ASK is a different object with a lifecycle keel has no home for: it persists across sessions until VERIFIABLY closed, and it can silently regress. 'I've asked for this so many times' is today an emotion; it should be a deterministic counter the model is forced to see.
- **evidence:** 'STill i hover info is overflowing... WTH I have asked for this so many times' / 'still seems to be not additive'. Confirmed new: no ask/ledger/register concept in docs.py; 'regression' today applies only to fixed-bug assertions inside the audit template, never to standing user requests, and has no re-raise counter or auto-flip.
- **mechanism:** Reuses verify's exit-code ratchet ('every fixed bug becomes a permanent assertion' — an ask resolution IS a user-visible named assertion). (1) `docs.py ask add "<text>"` normalizes to a token set and fuzzy-matches existing open+resolved asks. No match = new entry {id, text, first_raised, raised_count:1, status:OPEN, bind:null}. Match against a RESOLVED entry = increment raised_count, flip to REGRESSED, stamp the re-raise date — making 'asked N times' deterministic. (2) `docs.py ask resolve <id> --bind audit.py::test_hover_additive` binds the ask to a NAMED assertion in the verify audit; status becomes CLAIMED-RESOLVED, never VERIFIED, until `verify run` passes AND that assertion is present in the run. An ask with no bindable check CANNOT be marked resolved — unverifiable asks honestly stay OPEN. (3) Regression detection runs inside rehydrate: for every VERIFIED ask, re-evaluate against the latest verify stamp + deliverable hash; if the audit failed, or the deliverable moved without a fresh passing run, flip to REGRESSED and fail loudly with the raise-count and prior 'resolved' date. This is the exact moment that turns 'WTH I asked for this so many times' into 'ask #7 regressed, raised x4, was green 2026-06-02' — before the user has to notice.
- **sketch:** $ docs.py ask add "hover tooltip overflows the card"
ask: matched RESOLVED #7 (token overlap 0.82) → raised_count 3→4, status VERIFIED→REGRESSED, re-raised 2026-07-14
$ docs.py ask list
ASK LEDGER — 2 open · 1 REGRESSED · 6 verified-resolved
 [!!] #7  hover tooltip overflows       ×4  REGRESSED  bind audit.py::test_hover_additive (FAIL @ 07-14) · green 06-02
 [!]  #12 lead dedup misses aliases     ×2  OPEN       bind (none) — unverifiable, cannot be marked resolved
      #3  CSV export utf-8 mojibake      ×1  VERIFIED   bind audit.py::test_utf8 (pass @ 07-14)
# rehydrate then fails loudly:
[!!] ASK REGRESSED — #7 'hover tooltip overflows' resolved 06-02, bound check now FAILS. Raised 4x. Do not re-close without a green bind.
- **fit:** Directly extends verify.md's ratchet ('the audit only ever gets stricter; one assertion per fixed thing') to user asks, so resolution is an exit code, not agreement. Embodies honesty-over-agreeableness: the model literally cannot claim an ask resolved without a passing bound check, and unverifiable asks are surfaced as still-open rather than quietly dropped. Determinism-first: the raise count and the regression flip are computed in rehydrate (the unconditional every-session gate), never remembered.

### 18. roadmap — phase-status ratchet, left-out backlog, and parked items with wake-conditions (docs.py roadmap / park)
- **one-liner:** A phased roadmap where a phase reaches VERIFIED-WORKING only through a passing bound audit, an explicitly enumerated 'left-out / still-to-build' backlog, and parked items that stay completely silent until a machine-checkable wake-condition (e.g. reaching Phase 5) fires inside rehydrate.
- **problem:** keel has no living FORWARD status surface. Three distinct pains: (1) 'let's redo this step... Phase 5: parked. Won't raise it again until you do' and 'raise it when we reach Phase 5' — a parked idea today either nags every session or vanishes; there is no dormant-until-condition object. (2) 'Implement all the things that you left out' and 'let's take the big build still left and a reaudit before that' — 'left out' work lives only in the model's memory, so it's vague and lossy. (3) A phase the model called 'working' can silently stop working, and there's no ratchet catching that. Plus the recap need: 'help me with exactly what happened in short and how does this effect the decisions I had to make'.
- **evidence:** 'Phase 5: parked. Won't raise it again until you do' / 'raise it when we reach Phase 5' / 'Implement all the things that you left out' / 'let's take the big build still left and a reaudit before that' / 'exactly what happened in short and how does this effect the decisions I had to make'. Confirmed new: no roadmap/phase/park/wake/backlog anywhere in docs.py; ADRs are point decisions with no ordering, status, or wake predicate.
- **mechanism:** Same verify ratchet, applied forward. (1) `docs.py roadmap add "enrich" --phase 3` builds an ordered phase list; status in {planned, building, verified-working, blocked}; current-phase pointer advanced by `docs.py phase advance`. A phase reaches VERIFIED-WORKING only via `docs.py roadmap verify <phase> --bind <assertions>` bound to passing audit checks — it cannot self-declare working. rehydrate re-checks every 'working' phase against the verify stamp/deliverable hash and flags SILENT PHASE REGRESSION (a layer that was working and stopped). (2) `docs.py roadmap backlog add "alias matching" --deferred-from 2` is the enumerable left-out list, so 'implement all the things you left out' resolves to a concrete printed set, not memory. (3) `docs.py park "<item>" --wake-at phase:5` (or `--wake-when verify:<assertion>` / `--wake-when backlog-empty`) stores a dormant item with a MACHINE-CHECKABLE predicate and produces ZERO output until it trips. rehydrate evaluates every parked predicate each session; when current-phase >= 5 the item WAKES loudly — the deterministic form of 'raise it when we reach Phase 5', so it is neither forgotten nor prematurely raised. (4) Recap facet: `docs.py roadmap recap` prints the roadmap diff since the last session (phases advanced, backlog added, ADRs landed, asks flipped) plus the decision-debt it changed — open decisions now UNBLOCKED or BLOCKED by this session — answering 'what happened and how does it change the decisions I still have to make' from computed state, not narration.
- **sketch:** $ docs.py roadmap
ROADMAP — faire-lead pipeline   (current: Phase 3 of 6)
  1 ingest    ✅ verified-working  (bind audit.py::test_ingest, pass 07-02)
  2 dedup     ✅ verified-working  (bind audit.py::test_dedup,  pass 07-09)
  3 enrich    🔨 building          (audit STALE — not covered)
  4 score     ○ planned
  5 export    ○ planned            [1 parked item wakes here]
  6 notify    ○ planned
BACKLOG (left-out, still-to-build): 3
  - alias matching in dedup            (deferred from Phase 2)
  - retry/backoff on enrich API
  - csv-vs-parquet export              (needs decision — blocks Phase 5)
$ docs.py park "revisit response caching" --wake-at phase:5
parked: dormant until current-phase >= 5 (silent until then)
# later, at Phase 5, rehydrate wakes it:
[!] PARKED WOKE — 'revisit response caching' (parked @ Phase 2, wake-at Phase 5; you're now at Phase 5).
[!] SILENT PHASE REGRESSION — Phase 2 'dedup' was verified-working 07-09; bound check now fails.
- **fit:** Extends the verify ratchet to forward layers (a phase can't self-declare working; regressions are caught in rehydrate) exactly as bugs and asks are. Parked wake-conditions are deterministic predicates evaluated in rehydrate, the unconditional every-session gate — so 'don't raise it until Phase 5' becomes an invariant in code, not the model's memory (the core keel tenet). The recap is computed from state diffs, not free-text narration, keeping it honest and non-fabricated.

### 19. substrate — external anchors of truth as first-class, divergence-gated tiers
- **one-liner:** Let the user DECLARE that agents.md / an Obsidian vault / a Graphiti KG is the real anchor-of-truth, then have rehydrate read it and fail loudly when it has drifted out of sync with landed decisions.
- **problem:** keel assumes its own docs/ is the source of truth. This user's actual anchor lives in a single living agents.md, an Obsidian vault, and a Graphiti knowledge-graph RAG — none of which keel reads on rehydrate or knows the freshness of. So every session the user manually asks 'do we have all the latest up to date everything in agents.md about the exact state of things,' and keel eyeballs it instead of computing an answer. Their memory substrate is effectively inverted from keel's assumption: docs/ is secondary, agents.md/Graphiti is primary.
- **evidence:** Direct quotes: 'do we have all the latest up to date everything in agents.md about the exact state of things' and 'I have my own rag and am using graphiti for kg.' Repos: knowledge-graph-rag (agents.md / Obsidian / Graphiti) is literally the user's memory substrate; faire-lead / instagram-enrichment feed it. Baseline gap confirmed by reading docs.py: keel CAN be pointed at custom memory DIRS via .keel/memory-paths + KEEL_MEMORY (_memory_dirs), but it treats them as generic keel-format .md folders to grep — it never treats an external file as the DECLARED anchor-of-truth, never runs a divergence gate against it, and has no concept of sync-debt to a non-file substrate. grep confirms no 'agents.md', 'obsidian', 'graphiti', or 'substrate' anywhere in the skill.
- **mechanism:** A registry of external anchors with per-kind determinism, so 'is my real anchor current' becomes a computed verdict in rehydrate, not a thing the model reads-and-forgets. `docs.py substrate add --path ../knowledge-graph-rag/agents.md --kind anchor` writes .keel/substrate.json {kind: anchor|vault|kg, path/endpoint, synced watermark = last ADR n + ts}. rehydrate gains a SUBSTRATE block: (1) file-backed anchors (agents.md, Obsidian .md) get hash+mtime divergence BOTH directions — 'agents.md is N landed decisions behind (ADR mtimes > its mtime)' and 'agents.md changed since docs/architecture.md — your anchor may be behind your real source' — reusing the existing contradiction extractor extended to the external file; (2) service-backed anchors (Graphiti/RAG, which can't be hashed) get a SYNC-DEBT LEDGER instead: a deterministic count of decisions+findings with ts > the recorded watermark. keel does NOT push to Graphiti/Obsidian (that is the obsidian/graphiti MCP tools' job) — it owns the ledger and surfaces the debt; `docs.py substrate sync --kind kg` records the watermark after the agent pushes. This honors keel's stated 'detect + surface, not prevent' honesty boundary: determinism owns the ledger, the agent owns the I/O.
- **sketch:** docs.py substrate add --path ../knowledge-graph-rag/agents.md --kind anchor
docs.py substrate add --path ~/Obsidian/faire/ --kind vault
docs.py substrate add --endpoint graphiti://faire-lead --kind kg

# rehydrate excerpt:
--- SUBSTRATE (external anchors of truth) ---
  anchor  ../knowledge-graph-rag/agents.md   [!] BEHIND — ADR 0011,0012,0013 landed after it (mtime)
  vault   ~/Obsidian/faire/                    ok (last synced 2026-07-13)
  kg      graphiti://faire-lead               [!] SYNC DEBT — 3 decisions, 2 findings since 2026-06-30
    -> agents.md is your DECLARED anchor; it hasn't absorbed 3 decisions. Update it, then `substrate sync`.
VERDICT: exit 1 (an out-of-date anchor-of-truth is a loud rehydrate failure, like a stale docs/ anchor)
- **fit:** Invariant (anchor currency) lives in the CLI as a computed check, not prose. Precedence-aware: it lets the user's real substrate WIN over keel's docs/ default instead of imposing keel's file layout. Honest about enforcement limits — surfaces sync debt rather than pretending it can write to a remote KG.

### 20. finding + runbook — empirical & procedural memory tiers with provenance-or-reject, shelf-life, and scope tags
- **one-liner:** Two new committed tiers for the categories keel re-teaches every session — measured empirical FINDINGS and tacit procedural RUNBOOKs — each carrying a provenance gate (fabrication = refused), a TTL (a stale measurement fails rehydrate), and a scope tag (instance vs general, to stop overfitting).
- **problem:** The user re-teaches two whole categories of memory every session because keel has no home for either. (1) Empirical findings — measured rate limits, free-provider comparisons, 'what these repos give us,' gap analyses — get re-derived because nothing durably stores a measurement WITH how/when it was measured. (2) Procedural runbooks — hard-won tacit ops knowledge like 'reuse one foreground tab to avoid the human-check,' 'keep the target on-screen,' 'stay under the measured cadence' — don't fit an ADR (a decision) or a journal (dated narrative that scrolls out of the digest). And a living operational directive accretes redundant entries that need de-duping. None of decisions/ or journal/ is the right shape for reusable, expiring, scoped operational knowledge.
- **evidence:** Findings/limits: 'you didn't even define a framework or test the actual rate limit' and 'in 1 hour how many reels would a person watch, we stay under that' (instagram-enrichment; meeting-audit is literally a research-findings repo). Runbook/tacit ops: 'the Verify you are human checkbox — this only comes if you always open a new tab... if you use the same tab you'll never face that problem.' Directive de-dup: 'update the directive in docs, remove useless things that are redundant now.' Scope/anti-overfit: 'i was being just damn specific about review collection from this one meeting, not being general... without overfitting.' Baseline gap: grep confirms no finding/runbook tier, no ttl/shelf/expire, and no scope TAG (scope only means 'out of scope' in the web-app survey); provenance exists only for the deliverable audit, not for a memory tier.
- **mechanism:** New committed tiers docs/findings/ and docs/runbook/ that travel with the repo and load a digest on rehydrate — but the value is the four checks the tier enforces, not the folder. (a) PROVENANCE-OR-REJECT: `docs.py finding` refuses to write without --source + --method (mirrors verify's anti-fabrication rule — a measured value with no 'how measured' is fabricated). (b) SHELF-LIFE / TTL: every finding carries `ttl:`; rehydrate computes age vs ttl and flags EXPIRED findings — this is the deterministic hook that turns 'do we have the latest rate limit' into a computed verdict ('measured 94d ago, ttl 30d -> re-measure before relying'). (c) SCOPE TAG: every finding/runbook record carries `scope: instance:<id> | general`; rehydrate and search render scope inline and refuse to promote an instance-scoped record into a general directive, fencing one meeting's feedback from becoming a global rule. (d) ACCRETION DE-DUP: `docs.py runbook lint` runs shingle-overlap over runbook steps and flags near-duplicates so the living directive gets de-duped deterministically instead of by memory.
- **sketch:** docs.py finding --title "IG reel rate limit" \
  --measure "~200 reels/hr before soft-block" \
  --source "instagram-enrichment run 2026-07-10, n=6 sessions" \
  --method "ramped batch, watched for challenge redirect" \
  --ttl 30d --scope instance:instagram-enrichment
  # missing --source/--method -> `finding: x no provenance — a measured value needs source+method`; exit 1

docs.py runbook add --title "evade IG human-check" --scope general \
  --steps "reuse ONE foreground tab; never open a new/background tab; keep target on-screen; cadence < measured limit"
docs.py runbook lint      # -> "2 overlapping steps in browser-hygiene (0.79 shingle overlap) — de-dupe"

# rehydrate excerpt:
--- FINDINGS: 4 (1 EXPIRED) ---
  [!] IG reel rate limit — measured 94d ago, ttl 30d -> RE-MEASURE (scope: instance:instagram-enrichment)
--- RUNBOOK: 3 procedures --- (runbook lint: 2 overlapping steps in "browser-hygiene")
- **fit:** 'Measure real limits on a small sample before scaling' is a standing keel default — this gives the measurement a durable, expiring, provenance-checked home so it is measured ONCE, not re-guessed or trusted forever. Provenance-reject reuses keel's existing anti-fabrication stance. TTL and scope are structured metadata a deterministic check reads — invariants in code, not prose. De-dup operationalizes memory.md's single-source rule (d), which today is only prose.

### 21. orphans — deterministic dangling-reference / graph-integrity check over the memory graph
- **one-liner:** Resolve every cross-reference in the memory graph (ADR->entity, journal->decisions/NNNN, file#anchor, substrate->repo path), classify each orphan by WHY it dangles, and auto-repair the unambiguous ones — the diagnose-and-fix the user had to demand by hand.
- **problem:** keel's single-source rule says 'every other mention LINKS to its canonical home instead of restating it' (memory.md rule d) — but nothing checks those links still resolve. References rot silently: a journal points at decisions/0008 that got superseded, an ADR cites data-model.md#brand_id that was renamed, agents.md references a repo path that moved. The user had to catch this himself and demand a diagnosis AND ask why keel hadn't fixed it proactively. Graph integrity is asserted in prose and never computed.
- **evidence:** Direct quotes: 'DEEP DIAGNOSE ON WHAT AND WHY ARE THESE ORPHANS' and 'Why did you not update the orphans yourself first' — the user explicitly wanted (a) classification of WHY each reference dangles and (b) proactive auto-repair, neither of which keel offers. Applies across all four repos since journals/ADRs/agents.md cross-link entities and files that move. Baseline gap confirmed: grep finds 'orphan' only in the data-pipeline profile (deliverable foreign keys), never over the memory graph; no dangling-link resolution exists anywhere in docs.py.
- **mechanism:** A pure reference-resolution pass, exit-non-zero, wired into rehydrate. EXTRACT every intra-memory reference: `decisions/NNNN` and `ADR NN`, `data-model.md#anchor`/entity names, relative markdown links `[..](path)`, and (composing with innovation 1) references inside declared substrate files. RESOLVE each: the ADR exists in docs/decisions; the #anchor exists as a heading/entity in its target; the path exists on disk. CLASSIFY each orphan by WHY (the 'deep diagnose' the user asked for): target-deleted | target-renamed (fuzzy nearest match + score) | target-superseded (points at a retired ADR; names the successor) | path-moved. AUTO-REPAIR (the 'why didn't you fix it yourself' part): `docs.py orphans --fix` rewrites the unambiguous cases — a pointer at a superseded ADR becomes its successor; a 1:1 high-confidence rename is updated — and lists ambiguous ones for the user to confirm. Distinct from baseline: contradictions/suspect_decisions only detect supersession CLAIMS via regex; they never resolve a reference TARGET. The data-pipeline profile's 'orphan check' is about foreign keys in the DELIVERABLE data, a different graph entirely.
- **sketch:** docs.py orphans
ORPHANS — 3 dangling reference(s) in the memory graph:
  docs/journal/2026-07-02-...md:4  -> "see decisions/0008"     target-superseded -> successor is 0012   [auto-fixable]
  docs/decisions/0011-...md:9      -> "data-model.md#brand_id" target-renamed -> nearest: brand_key (0.82)  [confirm]
  ../knowledge-graph-rag/agents.md -> "faire-lead/pipeline.py" path-moved -> not found on disk              [confirm]
-> docs.py orphans --fix applies the 1 auto-fixable (0008->0012); re-run for the 2 that need confirmation.
# runs inside rehydrate; any orphan makes the digest exit 1, alongside the stale-anchor / contradiction checks.
- **fit:** Turns memory.md's single-source/linking rule from prose into a computed, loud check — exactly keel's 'invariants live in the CLI, not prose' thesis. The WHY-classifier + auto-repair embodies 'assume you will forget, drift, and rationalize — lean on the checks': the model no longer has to notice orphans or be asked to fix them; the check does both. Composes cleanly with innovation 1 (substrate references are just more edges in the same graph).

### 22. Preflight dependency manifest + liveness board (new committed tier, wired into rehydrate)
- **one-liner:** A committed docs/preflight.yaml declaring each external service with its probe + recovery step, and a docs.py preflight check that runs every probe at session open and fails rehydrate loudly on any required dependency that is down.
- **problem:** Every session opens with a manual 're-establish state' ritual: is the Qdrant cluster up, is the MCP connected, are the APIs reachable? This runtime topology lives in NO memory tier today (docs/ holds architecture/data-model/decisions/journal only), so keel starts blind and the user personally diagnoses 'the cluster was paused' or 'I connected this MCP but haven't used it in a while' every time.
- **evidence:** 'is this on and working?... I had connected this but not used in a while'; 'i restarted the cluster there, it was paused... need to recover this'; the recurring session-open 're-establish state' for Qdrant/MCP/APIs across knowledge-graph-rag and brand-intelligence-app.
- **mechanism:** Add a new COMMITTED memory tier — docs/preflight.yaml — a peer of data-model.md but for runtime dependencies instead of data shape. It declares, once and versioned, each service: id, a probe command, the EXPECTED signal (exit0 / HTTP 200 / body match), who owns it, and a recovery hint. `docs.py preflight` deterministically runs every declared probe and prints a green/red board; a red REQUIRED precondition exits non-zero. It is wired into cmd_rehydrate right after the MEMORY-tiers line, incrementing the existing `problems` counter — so a session cannot rehydrate 'clean' while Qdrant is paused, and the recovery step ('cluster likely PAUSED — resume it, wait ~30s') is surfaced automatically instead of user-diagnosed. Determinism-first: keel never GUESSES health — the user DECLARES the precondition set + expected signals once, that declaration is committed/versioned, and every rehydrate re-runs the same deterministic gate. Anti-fabrication carries over: a probe with no declared `expect` is rejected ('it responded' is not 'it is healthy', exactly like a datum with no source pointer). Hydrate tie-in: when a session discovers a new dependency, it lands into docs/preflight.yaml so the topology accretes into durable memory. Honest limit (same as the contract gate): probes only bind work routed through keel; elsewhere it is detect+surface, not prevent. Solves the external-service-liveness class of the theme.
- **sketch:** docs/preflight.yaml:
  services:
    - id: qdrant
      probe: curl -sf http://localhost:6333/readyz
      expect: exit0
      owner: "Qdrant Cloud (cloud.qdrant.io)"
      recover: "cluster likely PAUSED — resume in console, wait ~30s, re-probe"
      required: true
    - id: mcp-knowledge-graph
      probe: <mcp ping cmd>
      expect: exit0
      recover: "reconnect MCP in settings; 'connected but idle a while' → toggle off/on"
      required: true
    - id: faire-api
      probe: curl -sf -o /dev/null -w '%{http_code}' https://www.faire.com/robots.txt
      expect: "200"
      required: false

$ docs.py preflight
KEEL PREFLIGHT — runtime dependencies (docs/preflight.yaml)
  ✅ qdrant                readyz 200          (12ms)
  ❌ mcp-knowledge-graph   no response
       recover: reconnect the MCP in settings; toggle off/on
  ⚠️  faire-api (optional) 429 throttled
VERDICT: ✗ 1 REQUIRED dependency down — do not start work that needs it. (exit 1)

# rehydrate integration: after 'MEMORY tiers found', a red required probe does problems += 1 and forces the existing sys.exit(1).
- **fit:** Moves an invariant (what must be live) out of the model's head into a declared, versioned artifact + a loud deterministic check — the core keel move. Reuses the exact rehydrate `problems` pattern, the .keel stamp discipline, and the provenance/anti-fabrication stance ('responded' ≠ 'healthy'). Maps the terrain before building.

### 23. Environment baseline fingerprint + drift diff (catches the WARP/VPN/proxy blindness you never declared)
- **one-liner:** docs.py preflight env --record snapshots a known-good egress/network fingerprint; the check re-samples at rehydrate and fails loudly on any drift (WARP now active, egress IP changed, latency 9x, browser no longer foreground) — the undeclared preconditions a manifest can't anticipate.
- **problem:** The manifest in proposal 1 covers what you KNOW to check. The Cloudflare WARP incident is definitionally what you DIDN'T: a proxy/VPN silently activated, intercepted egress, and tanked throughput — and the agent was completely blind until the user diagnosed 'some WARP system was activated... it is causing your internet speed.' A declarative service list would never have caught this, because nobody thought to list it. This is the runtime-environment-health class of the theme.
- **evidence:** 'Some cloudflare WARP system was activated on my machine... It is causing your internet speed. Please check.' (agent blind until user diagnosed); 'if the browser is not actually open on my window, it sometimes triggers a bot test by faire' (an unmodeled env precondition).
- **mechanism:** A differential check, not a declarative one — the runtime analog of keel's existing _anchor_staleness() (recorded snapshot + deterministic diff, fails loudly on drift). `docs.py preflight env --record`, run once when things are known-good (e.g. right after a clean successful run), captures .keel/env-baseline.json: egress IP, http(s)/all_proxy vars, VPN/utun/wg interfaces present, `warp-cli status`, DNS, and a latency baseline to the key hosts (plus browser_foreground on the automation profile). The check re-samples and diffs FIELD BY FIELD, printing only what moved and by how much; any material drift increments rehydrate's `problems` and exits non-zero. keel is not judging 'WARP is bad' via intelligence — it reports 'your egress environment is not the one you last succeeded under' and names the exact fields, turning 'your internet is slow, please check' into a quantified, surfaced precondition at session open. The 9x-latency line and the 'egress IP routed through WARP' line make the invisible visible. Profile-aware: the automation profile adds browser_foreground, so 'if the browser is not actually open it triggers a bot test' becomes a named red flag ('your continuously-used foreground session is gone → expect bot-checks'), straight from that profile's 'one active session, reused' rule. Escape hatch: re-record the baseline if the drift is the new normal, keeping the check honest rather than nagging.
- **sketch:** $ docs.py preflight env --record        # capture known-good
.keel/env-baseline.json ← {egress_ip, proxies, vpn_ifaces, warp, dns, latency_ms{host}, browser_foreground}

$ docs.py preflight env                  # the check (also runs in rehydrate)
KEEL PREFLIGHT ENV — drift vs baseline (recorded 2026-07-10)
  [!] warp:          disconnected → CONNECTED    ← new since baseline
  [!] egress_ip:     73.15.x.x   → 104.28.x.x    ← routed through WARP
  [!] latency faire: 40ms        → 380ms (9.5x)  ← degraded
      proxies: unchanged   vpn_ifaces: unchanged
VERDICT: ⚠️  environment DRIFTED from last known-good — a proxy/VPN is likely
         intercepting egress and will silently degrade or block network work.
         → disable WARP, or `preflight env --record` if this is the new normal. (exit 1)
- **fit:** Transposes _anchor_staleness (recorded artifact + deterministic diff, fail loudly) from docs onto the runtime environment. Determinism lives in the diff against a recorded baseline, not in the live world. Honesty over agreeableness: surfaces a degraded environment instead of grinding blindly. Distinct failure class from proposal 1 (differential vs declarative), so it earns its own mechanism while sharing the same rehydrate board.

### 24. Smoke gate — config-bound go/no-go before expensive or irreversible long runs
- **one-liner:** docs.py smoke arm/run/gate: declare a tiny end-to-end sample bound to the EXACT config the long run will use, run it fanned-out per endpoint/IP, and stamp a go/no-go the launch refuses without — the symmetric before-gate to verify's after-gate, with real teeth for SKILL.md's currently prose-only 'expensive actions are gated' clause.
- **problem:** The user performs this ritual by hand every single time — 'run quick 1-min test that everything is working then start long-running execution' — and keel gives it no enforcement. SKILL.md §2 SAYS 'measure real limits on a small sample before scaling' and 'expensive/out-of-lane actions are gated,' but unlike the contract gate and verify, there is NO artifact backing it: nothing prevents launching an expensive/irreversible run untested, and nothing catches the lethal bait-and-switch where the 1-min test ran on a different config than the launch (smoke on 1 IP, launch on 8 including 2 blocked ones). This is the smoke-test go/no-go class of the theme.
- **evidence:** 'I've turned on vpn in one browser and not in other, run quick 1 min test that everything is working then start long running execution'; 'let's spec a multi-IP build and then run a small test on multi-ip system' — the recurring quick-test-then-long-run ritual, and specifically the multi-IP case where each IP/session is a separate precondition an aggregate test conceals.
- **mechanism:** The exact symmetric analog of verify (verify gates 'done' AFTER via a stamp bound to _deliverable_hash; smoke gates 'GO' BEFORE via a stamp bound to a CONFIG hash), mirroring verify's init/run/done and contract's set/approve/check triad. `docs.py smoke arm` declares the smoke spec: the tiny sample (N + selection), the FULL pipeline it exercises end-to-end, the pass criteria, and — critically — a fingerprint of the config the eventual long run will use (target endpoints / IP set / query / collection / cluster / model). `docs.py smoke run` executes on the sample and, for automation/multi-IP work, fans out PER declared endpoint/IP requiring all-green per-endpoint (never aggregate — aggregate is exactly what hides one dead IP), then stamps .keel/smoke.stamp {result, config_hash, ts}. `docs.py smoke gate` is the go/no-go the expensive launch routes through: it passes only if a fresh smoke exists, PASSED, and its config_hash EQUALS the config about to launch — so you cannot smoke config A and launch config B. If the config drifted (added IPs, switched collection, changed query), the gate fails and names the untested delta. This kills both failure modes in the multi-IP evidence: a per-endpoint precondition that aggregate testing hides, and a config bait-and-switch between the 1-min test and the launch. Determinism-first: the go/no-go becomes a deterministic stamp check (fresh + passed + config-matched), not the model remembering to test first — and it finally gives SKILL.md's expensive-action clause the same CLI teeth the contract gate has (honest same limit: only binds runs routed through keel).
- **sketch:** $ docs.py smoke arm --from smoke_spec.md
.keel/smoke.arm ← {sample_n:5, pipeline:"fetch→embed→upsert→query",
   config:{ips:[ip1,ip2,ip3], collection:"brands_v3", cluster:"qc-prod"}, config_hash:"a91f",
   criteria:["5/5 upserted","recall>0","0 errors PER ip"]}

$ docs.py smoke run
KEEL SMOKE — 5-item pipeline on the LONG-RUN config
  fetch  5/5   ip1 ✅  ip2 ✅  ip3 ❌ (bot-check block page)
  embed  5/5
  upsert 5/5 → qc-prod/brands_v3     query recall 5/5
VERDICT: ✗ ip3 bot-checked on the smoke — the full run WILL block on 1/3 of its IPs.
         Fix or drop ip3, re-arm, re-smoke.  (exit 1)

$ docs.py smoke gate     # the launch refuses without this
smoke gate: ✗ config CHANGED since smoke — smoked {3 ips, brands_v3},
            launching {8 ips, brands_v4}. The 5 new ips + new collection are UNTESTED. (exit 1)
- **fit:** Completes keel's gate symmetry (contract = what to build, verify = is it done, smoke = is it safe to spend) and converts a prose-only invariant into an enforcing artifact — the central keel discipline of moving invariants into deterministic code. Directly realizes the standing default 'measure real limits on a small sample before scaling.' Honesty over agreeableness: reports '1/3 IPs blocked' and blocks the GO rather than launching hopefully.

### 25. Autonomy ledger + operational gate (docs.py autonomy / docs.py gate)
- **one-liner:** A persistent, per-DOMAIN autonomy dial with absolute destructive-op floors, plus a gate that classifies ANY action (operational side-effects included) — not just code writes — and returns proceed/ask/frozen with a non-zero exit.
- **problem:** keel's only gate is cmd_contract: one ephemeral .keel/contract.json holding {plan,hash,ts,approved}, scoped to code/files/schema, fresh for a 3600s window. It is the wrong shape in both directions at once. Too little: a real DM, a live-conversation reply, launching a multi-hour/expensive run, a Qdrant/RAG purge, or a catalog wipe changes no code/file/schema, so the contract gate is silent — the loop acts on irreversible operational side-effects and destructive ops on protected data zones without ever asking. Too much: every routine code build re-opens a fresh contract, so durable 'cofounder' authority the user already granted gets re-requested every session. There is no notion of a domain, an action type, or a persistent permission level anywhere in the CLI.
- **evidence:** 'take explicit permission for me for anything that can touch rag' -> autonomy set rag ask --floor no-purge. 'YOU HAVE DURABLE PERMISSION AS THAT COMES AS PART OF OWNERSHIP AND BEING MY COFOUNDER' -> autonomy set code auto (persistent, never re-asked). 'no purges lets proceed with other things' / 'Catalog never-wipe' / 'it still seems to be not additive' -> floors no-purge/additive-only, absolute regardless of dial. Irreversible operational side-effects (real DMs, engaging live convos, launching an expensive multi-hour run) change no code so today's cmd_contract (docs.py:427-448) is silent on them; a domain like external-dm/expensive-run makes `gate` fire on exactly those with zero file change. Baseline gap: cmd_contract stores only {plan,hash,ts,approved} — no domain, no action-type, no floor, no persistence.
- **mechanism:** Add a persistent per-domain autonomy ledger in .keel/autonomy.json (persists across sessions like profile/contract; consistent with existing state). A domain is a user-named ACTION CLASS, not a file path — e.g. code, rag, catalog, external-dm, expensive-run, live-convo. Each domain carries (a) a dial level and (b) zero or more absolute floors. Levels: frozen | ask (every action asks) | ask-destructive (additive/routine proceeds, destructive/irreversible asks) | auto (full standing autonomy). Floors are invariants NO level can lift: no-purge, additive-only, no-external-send. `docs.py gate <domain> --action "..." [--destructive] [--irreversible] [--external] [--cost N]` classifies the action, consults the domain dial AND its floors, and exits 0 (PROCEED) or 1 (ASK/FROZEN) — the same teeth pattern as `contract check`/`verify run`, so real action-wrappers can call it. A floor match forces ASK even at auto (this is how 'catalog never-wipe' and 'no purges' become enforced rather than remembered). An undeclared domain that is clearly present in the repo (a qdrant/ or rag dir, a declared deliverable) defaults to ASK — fail safe, so a fresh clone that lost .keel/ never fails open. rehydrate gains an AUTONOMY LEDGER block that prints each domain+level+floors and flags undeclared-but-present domains, wiring the dial into the inbound gate every session.
- **sketch:** $ docs.py autonomy set code auto
$ docs.py autonomy set rag ask --floor no-purge
$ docs.py autonomy set catalog ask-destructive --floor additive-only

$ docs.py gate code --action "add null-check in parser.py"
GATE code / add null-check in parser.py
  dial: auto   floors: (none)   class: routine, reversible
  VERDICT: PROCEED — standing autonomy covers this; no re-ask.  (exit 0)

$ docs.py gate rag --action "drop & rebuild qdrant collection" --destructive --irreversible
GATE rag / drop & rebuild qdrant collection
  dial: ask   floors: no-purge  <- MATCHED   class: DESTRUCTIVE, IRREVERSIBLE
  VERDICT: ASK — floor 'no-purge' is absolute; get explicit go for THIS action.  (exit 1)

# rehydrate:
--- AUTONOMY LEDGER ---
  code           auto
  rag            ask              floors: no-purge
  catalog        ask-destructive  floors: additive-only
  [!] instagram-enrichment/ present but no dial set -> defaulting to ASK
- **fit:** Invariants live in code, not prose: the 'ask before RAG / never wipe catalog / gate expensive actions' rules move out of SKILL.md §2 into a check that exits non-zero. Map-before-build: undeclared present domains default to ASK. Honesty over agreeableness: the gate can't be talked past. It extends, not replaces, the contract gate — contract still governs WHAT to build; autonomy governs WHETHER this class of action may fire and WHO must approve.

### 26. Standing stance register (docs.py stance) — durable freeze + user-named modes
- **one-liner:** A persistent, session-surviving 'stance' (freeze/discussion-only and user-coined modes like sensei/partner) that rehydrate re-arms every session, can block even the lightweight lane, forces memory-writes to be confirmed, and is cleanly retractable.
- **problem:** The user re-declares a freeze EVERY session ('DO NOT MAKE ANY CHANGES UNTIL WE FINALIZE', 'No commits until confirmed by me') because keel has nowhere durable to hold it — the closest thing, clarify-depth, is a single thorough/light toggle, and the lightweight lane is a prose carve-out (SKILL.md §2) that no state can override, so even a declared freeze can't stop a 'trivial reversible edit.' The user also speaks an established vocabulary ('Sensei mode', 'partner mode') that evaporates at session end. And when a standing instruction is cancelled mid-flight ('DO NOT CONSIDER WHAT WAS WRITTEN ABOVE AND CANCELLED'), there's no way to retract it before it calcifies.
- **evidence:** 'DO NOT MAKE ANY CHANGES UNTIL WE FINALIZE' / 'No commits until confirmed by me' (re-declared every session) -> stance set freeze --note '...', re-armed by rehydrate, blocks even the lightweight lane. 'Lets go Sensei mode on till the end of this chat' / 'partner mode' (re-invoked as established vocabulary) -> stance set sensei / stance set partner, durable across sessions. 'JUST BE A PARTNER LEVEL PART OF IT... YOU JUST CONFIRM WITH ME ON WHAT YOU ARE SAVING AS MEMORY' -> partner stance carries memory=confirm, forcing every decision/journal/prefs write to stage as a draft. 'DO NOT CONSIDER WHAT WAS WRITTEN ABOVE AND CANCELLED' -> stance clear + `pending drop <id>` withdraws an in-flight staged item before it lands durably.
- **mechanism:** Add .keel/stance.json holding one active stance: {name, freeze:bool, blocks_lightweight:bool, memory:'confirm'|'silent', autonomy_default, note, declared_ts, sessions_since}. `docs.py stance set <name> [--freeze] [--blocks-lightweight] [--memory confirm] [--autonomy-default ask|ask-destructive|auto] [--note "..."]` records it; a user-coined <name> (sensei, partner) becomes durable vocabulary the next session recognizes. `stance show` / `stance clear` (the retract path) / `stance check` (exit non-zero if the current stance blocks the pending action class). The gate from Innovation 1 consults stance FIRST: freeze -> everything returns FROZEN including the lightweight lane and including auto domains (the hard override prose could never provide). When memory='confirm', cmd_decision/cmd_journal/cmd_prefs auto-force --draft (staging to .keel/pending/ instead of landing), and hydrate requires explicit approval — turning the existing opt-in draft mechanism into a STANDING 'confirm what you save as memory' invariant. rehydrate surfaces the stance LOUDLY at the very top, before anything else, with sessions_since — so a freeze declared once is automatically re-armed on every subsequent session instead of re-typed in anger.
- **sketch:** $ docs.py stance set freeze --note "DO NOT MAKE CHANGES UNTIL WE FINALIZE"
stance set: FREEZE (discussion-only) — blocks builds, lightweight edits, and operational actions.

$ docs.py stance set partner --autonomy-default ask-destructive --memory confirm --note "cofounder; escalate pivotal"

# rehydrate (top of output, before ANY digest):
>>> STANDING STANCE: freeze  (declared 2026-07-10, 4 sessions ago)
    effect: discussion-only — NO builds, NO lightweight edits, NO operational actions.
    note:   "DO NOT MAKE CHANGES UNTIL WE FINALIZE"
    -> lift only on explicit user go:  docs.py stance clear

# under partner stance, a decision auto-stages:
$ docs.py decision --title "switch to embed pipeline"
decision DRAFTED (partner stance: memory=confirm) — lands in docs/ only on your approval at hydrate.

$ docs.py stance clear   # the retract path
stance cleared — freeze lifted; normal dials resume.
- **fit:** Keeps durable memory across sessions (the core keel promise) applied to permission STATE, not just decisions. Invariants in code: the freeze and the memory-confirm rule become enforced state a check reads, not a sentence the model re-reads and drifts from. Note the deliberate naming: the existing modes/ folder holds task-type playbooks, so this governance state is 'stance' to avoid collision, while mapping the user's spoken 'X mode' onto stance set X.

### 27. Judgment escalation checkpoint (docs.py escalate) — a durable, resumable, blocking route-through-me
- **one-liner:** A mid-flight, judgment-triggered escalation that keel RAISES itself for pivotal/irreversible/costly calls: a durable BLOCKED-ON-USER state that survives session end and context compaction, can't be steamrolled, and auto-promotes the user's answer to an ADR so it's never re-litigated.
- **problem:** keel's clarification gate is pre-build PROSE ('STOP — as many questions as needed'), which is exactly the sort of in-context instruction keel's own doctrine says gets talked past under pressure — and it dies with the session. So a genuinely raised question can be steamrolled ('WHY THE FUCK DID YOU CONTINUE WITHOUT ASKING'), and there is no durable record that a pivotal decision is pending the user's call. The user explicitly does NOT want a blanket ask-everything switch; they want keel to escalate when KEEL judges it necessary and route that one call through them — a capability that has no home in the CLI today.
- **evidence:** 'WHY THE FUCK DID YOU CONTINUE WITHOUT ACTUALLY ASKING THE QUESTIONS FROM ME BEFORE STARTING' -> a raised escalation is a durable exit-nonzero-able blocked state, not prose the model talks past. 'how the fuck did you make changes without fucking confirming anything... fucking revert and report first' -> escalate raise BEFORE the consequential action puts the thread in BLOCKED-ON-USER first. 'NOT WHEN I SAY ON, when YOU THINK IT IS NECESSARY... JUST ASK ME IF THERE IS A PIVOTAL CHANGE' -> keel-judged trigger via --because pivotal, precisely a judgment escalation rather than a user-toggled or blanket ask-everything mode.
- **mechanism:** Add .keel/escalations.jsonl. `docs.py escalate raise --domain <d> --question "..." --options "A|B|C" --recommend A --because pivotal|irreversible|cost` records an escalation and marks that thread BLOCKED-ON-USER. It is keel's JUDGMENT that raises it (not a user keyword), which is the exact distinction the user drew. `escalate list`; `escalate resolve <id> --choice X --to-decision "title"` promotes the answer straight to an ADR via the existing cmd_decision path (so it's rehydrate-visible and never re-litigated); `escalate resolve <id> --retract` is the cancel path. rehydrate surfaces unresolved escalations near the top as a hard [!!] block with age in sessions — so a raised-but-unanswered question survives a context compaction, an interrupt, and a brand-new session, and the loop can't quietly proceed past it. Unlike the clarification gate this is durable, resumable, blocking, and self-recording; it is the 'route through me' primitive that lets a domain sit at auto while still catching the rare pivotal call.
- **sketch:** $ docs.py escalate raise --domain external-dm --because irreversible \
    --question "Send outreach DMs to the 12 leads now, or stage drafts for review?" \
    --options "send-now|stage-drafts|skip" --recommend stage-drafts
ESCALATION #3 raised — BLOCKED ON USER (external-dm).
  why: irreversible + external — keels judgment says this needs your call.
  options: [send-now | stage-drafts | skip]   (keel recommends: stage-drafts)
  -> will NOT proceed on this thread until you answer. Recorded durably.

# rehydrate (near top, before the digest):
[!!] BLOCKED — 1 open escalation awaiting YOUR call (raised 2026-07-12, 2 sessions ago):
   #3 external-dm: "Send outreach DMs to the 12 leads now, or stage drafts?"  (rec: stage-drafts)
   -> do NOT proceed on that thread.  docs.py escalate resolve 3 --choice ...

$ docs.py escalate resolve 3 --choice stage-drafts --to-decision "outreach: stage, never auto-send"
resolved #3 -> stage-drafts; promoted to ADR 0021 (durable; wont be re-litigated).
- **fit:** Directly enacts keel's own thesis — 'writing a directive down is not the same as following it; enforcement is a check that runs every rehydrate' — applied to the loudest failure in the corpus. A raised question stops being in-context prose and becomes durable, resumable, blocking state. Auto-promotion to an ADR closes the loop into keel's existing memory tiers so the answer persists. It complements Innovation 1: a domain can stay at auto for throughput while escalate catches the rare pivotal call, giving the user the calibrated middle they asked for instead of a binary ask-everything/ask-nothing switch.

### 28. verify baseline — the last good run as an oracle (shrink guard + improvement gate)
- **one-liner:** A stored fingerprint of the last PASSING run turns 'is this scrape smaller/worse than last time?' into an exit code, and the same fingerprint gates a push on measured improvement.
- **problem:** keel's verify is absolute and memoryless. `_deliverable_hash()` (scripts/docs.py:119) detects only THAT the deliverable changed — never how much or in which direction. A scrape that silently captures 40% fewer rows, or where a broken selector now writes the same constant into every `category` cell, passes every field-level and provenance check (each row present is well-formed), so the regression sails through `verify done` and overwrites a good master. There is also no way to gate a push on IMPROVEMENT — the mirror need.
- **evidence:** 'keep in mind if the scrape size is smaller than last time then something is wrong and needs a reaudit'; 'JUST once re run the reccheck on all qualified and if we see the improvements pass we push to main'; 'why the fuck have we not been catching any of this in the audits.'
- **mechanism:** Add two actions to cmd_verify (scripts/docs.py:478), reusing the existing deliverable-dir resolution. (1) `verify baseline snapshot` — allowed ONLY after a passing `verify run` (reads VERIFY_STAMP, refuses on fail/stale). Computes a fingerprint over declared deliverables: total rows, per-field non-empty fill count, per-field distinct-value cardinality, numeric min/max/mean, bytes, file inventory. Writes `.keel/baselines/<slug>/<ts>-<gitsha>.json`, keeps a ring of the last 5. A baseline is an explicit BLESSED run, not every run. (2) `verify baseline check` — recomputes the fingerprint for the current deliverable, diffs vs the newest baseline, exits non-zero on three distinct regression classes: SHRINK (rows/fill down > --shrink-tol, default 10%) catches silent under-capture; FILL-DROP (a field's fill-rate down > --fill-tol pts even if row count held) catches 'rows arrived but values went blank'; COLLAPSE (a field's distinct cardinality craters, e.g. 380->3) catches the worst/most invisible failure — a broken selector writing a constant, where fill-rate still reads 100% so no fill check ever fires. (3) `verify baseline gate --metric <field/expr> --require improve` — exits 0 only if the named metric STRICTLY improved vs baseline; wire it into pre-push so main advances only on a measured gain.
- **sketch:** $ docs.py verify baseline check
verify baseline — data/master.csv  vs  baseline 2026-07-08 14:02 (git a1b2c3d)
  metric                  baseline   current    delta    verdict
  rows                       4,812     2,905   -39.6%    x SHRINK
  fill brand_name            99.8%     99.7%    -0.1pt    ok
  fill wholesale_price       94.1%     61.2%   -32.9pt   x FILL-DROP
  distinct category             38         3     -35      x COLLAPSE (constant?)
  bytes                     3.9 MB    2.3 MB     -41%     (info)
VERDICT: FAIL — 3 regressions vs last good run; this run captured LESS than baseline.
  -> do NOT overwrite master; keep the prior artifact, investigate the scraper. (exit 1)
- **fit:** This makes references/verify.md's own advice real: 'where an independent oracle exists (an independent enumeration, a known total), cross-check against it instead of trusting the pipeline that produced it to grade itself' — the prior good run IS that oracle. It gives teeth to keel's standing default 'never dispose of fetched/costly data — merge partials': the SHRINK guard is precisely what stops a thin run from clobbering a fat master. Invariant lives as an exit code, not prose. Scope note: a baseline presumes a single canonical `master` artifact, which is exactly the raw->validated->master lifecycle need (f) in the theme — I'd address that graduation as a separate `docs.py data promote` state-machine mechanism rather than fold it in here.

### 29. verify batch — audit WHILE it runs, halt when it rots (layered in-flight audit + circuit breaker)
- **one-liner:** A fast per-batch subset of the audit fires after every chunk of a long run, stamps a rolling pass/fail log, and trips a real HALT flag on consecutive failures — so a run that goes bad at chunk 3 stops at chunk 3, not chunk 300.
- **problem:** keel's verify is a single event at the done gate (references/verify.md 'The hard-gate pattern'; cmd_verify only knows init/run/done/sync). A 5,000-lead enrichment that starts fabricating at batch 3 keeps burning model budget for hours before the one-shot audit ever runs. There is no layered structure (small per-batch checks + a large roll-up) and no corrective loop that re-runs ONLY the bad batches instead of redoing all 5,000.
- **evidence:** 'run an audit if the data being filled does not seem generated or faked by sonnet, run this in parallel while the enrichment happens'; 'why the fuck have we not been catching any of this in the audits that were supposed to happen.'
- **mechanism:** Add `verify batch` to cmd_verify plus a `--batch` fast-mode in the audit template (scripts/docs.py:453 AUDIT_TMPL). (1) `verify batch <n> --window <partial-file>` runs a FAST layer of audit.py — schema + provenance + fabrication sample + per-field fill vs the batch baseline, skipping the expensive whole-dataset cross-file checks — against ONLY the newest incremental partial. Appends {batch,ts,rows,checks:{schema,provenance,fabrication,fill},result} to `.keel/verify/batches.jsonl`. (2) CIRCUIT BREAKER (the teeth): after stamping, evaluate a rolling rule — K consecutive FAILs (default 3) OR windowed fail-rate past --breaker-rate (default 25%). On trip, write `.keel/verify/HALT` with the reason and exit non-zero. The run loop is contracted (documented in references/orchestrate.md) to poll for HALT after each batch and STOP — the deterministic replacement for 'the model should notice it's going wrong.' (3) `verify batch report` is the LARGE overall audit: rolls up the JSONL into per-batch verdicts + the exact failed batch ids, so the corrective loop re-runs only those windows. (4) `verify batch clear` resets HALT + log for a fresh run.
- **sketch:** $ docs.py verify batch 7 --window data/.partial/batch_7.csv
verify batch 7 — 120 rows
  schema        120/120  ok
  provenance    112/120  x 8 rows: no source pointer
  fabrication   118/120  x 2 rows: cited URL 404 / value absent on page   [uses innovation 3]
  fill price     58%     x (batch baseline 91%)
BATCH 7: FAIL (3 layers) — consecutive fails 3/3 -> CIRCUIT BREAKER TRIPPED
  wrote .keel/verify/HALT ('3 consecutive batch fails'). STOP the run; do not spend more.

$ docs.py verify batch report
batches: 7 run / 3 passed / 4 failed (57% fail-rate, breaker tripped at #7)
  FAILED windows to re-run: 4,5,6,7   (1-3 passed, keep them)
- **fit:** Turns verify from a closing ritual into a continuous invariant — the exact move keel already made for hydrate ('durability is a continuous invariant, not a closing ritual', SKILL.md:92). The breaker is a file + exit code, matching references/verify.md 'convert every verification step you'd describe in prose into a committed executable.' The per-batch/roll-up split mirrors the manager/worker orchestration model (cheap frequent checks catch rot early; the expensive whole-run audit still runs at done). Re-running only failed windows honors 'resume is idempotent / never dispose of fetched data' (references/orchestrate.md).

### 30. Trust-tiered provenance — cited + fresh + cross-validated, per-field policy in data-model.md
- **one-liner:** Upgrades keel's anti-fabrication check from 'a source pointer exists' to a three-part per-field trust standard — the citation resolves, its timestamp is within a freshness window, and the claimed value corroborates against the source — so 'did sonnet invent this row' becomes checkable, not hopeful.
- **problem:** keel's provenance check is deliberately shallow: 'does a source pointer exist' (references/verify.md:28-34), and it concedes 'is this claim true mostly isn't' checkable. But the exact fabrication the user is fighting slips through: a delegated Sonnet worker writes a PLAUSIBLE citation URL it never read, or fills a believable price with a stale/invented source. The pointer exists, so provenance PASSES — yet the row is invented. And there is no freshness dimension at all: a real-but-two-year-old citation is treated identically to a fresh one.
- **evidence:** 'run an audit if the data being filled does not seem generated or faked by sonnet'; 'the validity of the citation and the time of the citation and some basic cross validation.'
- **mechanism:** (1) Per-field provenance POLICY declared in data-model.md (versioned invariant, not a magic number in a script), each derived field tagged with a trust tier: `cited` (pointer must exist — today's behavior), `fresh:<window>` (pointer + timestamp within e.g. 90d), `xval:<rule>` (pointer + the claimed value must corroborate — the cited page text actually contains the value, a second source agrees, or a deterministic recompute matches). (2) `docs.py verify provenance` (also the `fabrication` layer inside verify batch): for each row, resolve its declared tier and stamp a per-record TRUST STATE — TRUSTED (all declared conditions met), UNVERIFIED (pointer present, cross-validation not yet run), STALE (citation older than window), FABRICATED (pointer missing/dead, or value not found at source). Records are UNTRUSTED-by-default: a row counts as product-quality only at TRUSTED. Exits non-zero if any FABRICATED, or if a field's TRUSTED fraction is below its declared threshold. (3) The cross-validation is the honest boundary: for URL citations, a cheap deterministic fetch-and-assert-token-present ('does the source actually say this'); for recomputable values, recompute; where no oracle exists, mark UNVERIFIED (never silently TRUSTED) so the gap is visible. The declared field-set stays honest via the existing `verify sync` (scripts/docs.py:502), which already diffs gated fields against data-model.md.
- **sketch:** # data-model.md  (leads)
  email            xval:mx                  # domain MX must resolve
  wholesale_price  fresh:90d + xval:token   # citation <=90d AND page contains the price string
  brand_name       cited                    # pointer must exist

$ docs.py verify provenance
trust states — data/master.csv (2,905 rows)
  TRUSTED     2,410  (83%)
  UNVERIFIED    361  (12%)  — pointer ok, cross-validation not run
  STALE          98  ( 3%)  — citation older than field window
  FABRICATED     36  ( 1%)  — pointer missing/404, or value not on cited page
  worst field: wholesale_price — 36 FABRICATED, 71 STALE
VERDICT: FAIL — 36 fabricated rows; wholesale_price TRUSTED 71% < 90% gate. (exit 1)
  sample: row 1180 cites brandsite.com/x (404); row 1442 price $8.50 not found on cited page.
- **fit:** Extends keel's single most central mechanism (provenance = 'the enforceable anti-fabrication check') along the exact axis references/verify.md flags as the open gap: 'a record can be perfectly well-formed and still be a fabrication; conformance can't catch that.' 'Untrusted-by-default until cited+fresh+corroborated' is the product-quality invariant the user asked for, expressed as declared per-field policy (versioned in data-model.md, kept honest by verify sync) plus an exit code — invariant in code, not prose. It also implements verify.md's 'vet a signal before you gate on it: check against >=3 known-truth records including one that should read FALSE.' And it stays honest about its own limits: UNVERIFIED is a first-class state, not a silent pass — matching keel's 'don't sell blocks you can't enforce.'

### 31. coverage — reverse-provenance audit against an external ground-truth doc
- **one-liner:** Decompose an external source (meeting transcript, spec, tenet list) into a durable, ID'd points ledger, then hard-gate that EVERY source point maps to a place in the deliverable — the mirror image of provenance.
- **problem:** keel's provenance runs one direction: every CLAIM in the deliverable must cite a source. That waves through the user's actual failure — the deliverable that is internally well-cited but SILENTLY OMITS points the ground-truth source raised. The user had to catch this by hand ('reevaluate against every nuance covered by saurabh and me and I saw you missed... AUDIT THE MEET AGAIN') and separately ('are all tenets mapped'). No keel object treats an external document as the oracle and enumerates what the output failed to address, so a missed point is never structurally impossible to hide.
- **evidence:** 'reevaluate it against every nuance covered by saurabh and me and I saw you missed... AUDIT THE MEET AGAIN' and 'are all tenets mapped' — both are reverse-coverage failures against an external oracle (the meeting-audit transcript; the knowledge-graph-rag tenet set). keel today has no mechanism that enumerates source points and fails on an orphan; the user was the enumerator.
- **mechanism:** A command family that inverts provenance. `coverage extract --source <file>` decomposes the external doc ONCE into an append-only ledger of atomic points, each with a stable content-hash ID (re-extraction merges, never drops a point) — the durable, re-runnable artifact, not a vibe. `coverage map <point_id> --to <locator> --status addressed|deferred [--reason]` records where each point is discharged in the deliverable (a claim ID, section, or file+line). `coverage audit` is the gate: it mechanically checks that EVERY point_id has a mapping with a non-empty locator and status=addressed; any point with no mapping, or status=deferred without a reason, fails with exit 1 and is named. The semantic call ('is point 7 addressed?') stays with the agent, but the CLI enforces that no point is silently skipped — exactly like provenance ('does a source pointer exist' is checkable even when 'is it true' isn't). Unaddressed points surface loudly in rehydrate. Lives in .keel/coverage/<source>.points.jsonl (durable memory tier).
- **sketch:** $ docs.py coverage extract --source meetings/2026-07-10-saurabh.md
  34 source points → .keel/coverage/2026-07-10-saurabh.points.jsonl (stable IDs)

$ docs.py coverage audit --source meetings/2026-07-10-saurabh.md
  ADDRESSED    28
  DEFERRED      3  (each carries a --reason)
  UNADDRESSED   3  X
    P07  "cap retry budget per-tenant, not global"   -> no mapping
    P19  "exclude churned logos from the lookalike"   -> no mapping
    P31  "demo must not show internal cost fields"     -> no mapping
  VERDICT: FAIL — 3 source points unmapped. map or --defer (with reason) each. exit 1

Check logic: fail if {p.id for p in points} - {m.point_id for m in mappings if m.locator and m.status=='addressed'} is non-empty, OR any status=='deferred' with empty reason.
- **fit:** Invariant lives in the CLI, not prose; the gate is an exit code that can't be rubber-stamped. It's the mechanical-completeness move keel already trusts for provenance ('no source pointer, no pass') applied in reverse ('no mapping, no coverage'). Honesty over agreeableness: it forces the agent to name what it dropped rather than claim the meet was 'fully addressed.'

### 32. handoff — human-in-the-loop live-test lane with a self-certification ban
- **one-liner:** Split 'done' into an agent-side readiness gate (automated tests green + env actually up) that MUST pass before a human is asked to test, and a human-side gate that only the user can close — with `verify done` structurally blocked from self-closing a reality-verified deliverable.
- **problem:** keel's `verify done` lets the AGENT run the audit and self-certify completion. For anything whose ground truth is reality — live UI, real behavior — the agent cannot be the closing verifier, and the user said so directly and repeatedly. There is no lane that (a) forces automated tests to run BEFORE the agent asks for a manual test, (b) stands the environment up and hands off, (c) ingests the human's observations, and (d) forbids the agent from marking done via its own test. Today all four are absent; 'done' is a self-graded exit code.
- **evidence:** 'DO not test yourself, give me to test'; 'do run tests before asking me to run manual test... turn on the server'; 'have you extremely thoroughly tested it from your side before the hand off?... handing off work without verifying is which i do not appreciate'; and the edge-case demand 'did you run test on if a tenet needs to be deleted how the kg layer acts and other minor yet MAJOR cases' — which becomes a readiness precondition. These map one-to-one onto readiness-first, human-closes, and ingest-observations.
- **mechanism:** A persisted state machine in .keel/handoff.json with enforced transitions: READY-BLOCKED -> HANDED_OFF -> OBSERVED -> ACCEPTED. `handoff open` refuses (exit 1) unless the READINESS gate is green — verify.stamp fresh+pass, the durable edge-case suite green (incl. destructive cases like tenet-deletion -> KG behaves), AND the declared server is actually listening on its port / build succeeds. This enforces 'run tests before asking me to run manual test... turn on the server': the agent cannot request a human test first. When readiness passes, `handoff open` stands the env up, prints the exact test URL and a checklist derived from the contract's edge-cases, and moves state to HANDED_OFF — a state in which `verify done` is BLOCKED. Only `handoff observe --note` (records the human's real observations, timestamped after server-up) and `handoff accept --by-human` close it; failing observations auto-file as new regression/edge-case assertions (durable memory, the ratchet). `verify done` becomes handoff-aware: for a reality-verified deliverable (web-app profile or opted-in), done requires status==ACCEPTED with a non-empty observation post-dating server-up — self-testing satisfies readiness but NEVER handoff. Honest limit stated in keel's own voice: raw tools bypass this and an agent can't be truly prevented from faking a human accept — but the ordering constraint (observations must post-date the stood-up env) plus a loud rehydrate banner ('AWAITING HUMAN OBSERVATIONS') make self-closing detectable, not silent.
- **sketch:** $ docs.py handoff open --deliverable web
  handoff: X BLOCKED — readiness not green.
    audit ....... ok pass (verify.stamp fresh)
    edge-suite .. X 2/9 failing  (docs.py edgecase run: tenet-delete, empty-set)
    server ...... X nothing listening on :3000
  -> agent-side verification must pass BEFORE a human is asked. exit 1

  # after fixes:
  handoff: ok readiness green — env is up.
    TEST HERE -> http://localhost:3000
    Exercise (from contract edge-cases):
      [ ] delete a tenet -> KG reconciles, no orphan edges
      [ ] paste a long note into a card -> no burst
    state: HANDED_OFF — `verify done` is BLOCKED until you record observations.
    then:  docs.py handoff observe --note "..."  ->  docs.py handoff accept --by-human

$ docs.py verify done
  X deliverable is HANDED_OFF and not human-accepted. self-testing cannot close a
    reality-verified deliverable. awaiting `handoff accept --by-human`. exit 1
- **fit:** keel's 'verify the deliverable, never the claim' taken to its honest endpoint: when the deliverable is reality, the one claim the agent can't be trusted to make is 'a human confirmed it.' The gate is a state machine (determinism), not a promise (prose); it enforces map-before-build's sibling, test-before-handoff. It embraces keel's stated honest-limit posture — detect + surface where it can't truly prevent — rather than selling a block it can't enforce.

### 33. render — geometric layout-invariant audit of the RENDERED output
- **one-liner:** Drop a runnable headless-render script into the project (like `verify init` drops audit.py) that loads localhost at declared viewports and asserts mechanical geometry — no overflow, no child escaping its box, nothing offscreen — turning 'cards bursting / paste overflowing' into exit-non-zero assertions.
- **problem:** keel's audit.py operates on data files and schema; _deliverable_hash hashes mtimes and sizes. It has zero access to the rendered DOM or pixel geometry, so it structurally CANNOT observe the exact regressions the user kept hitting: cards bursting out of their boxes, pasted text overflowing, content not in the right container. That leaves the user as the sole verifier of every UI regression — including the mechanically-checkable ones. A claim-audit will never catch overflow.
- **evidence:** 'cards there are places which are bursting/not being viewed in right boxes... paste is overflowing' and 'Just run it on localhost and let me test' (cofounder-viz/sales-deck; brand-intelligence-app leads/ads). Each complaint is a geometric invariant an audit could have asserted; instead the user found them by eye.
- **mechanism:** A sibling of verify (named `render`, not `layout`, to avoid the prototype's existing `layout` command). `render init` drops a real, runnable render_audit script into the project (headless browser, e.g. Playwright). It navigates declared routes at declared viewports (e.g. 375px, 1280px) and evaluates GEOMETRIC boolean assertions over computed layout — not aesthetics: (1) no-overflow: element.scrollWidth <= clientWidth + tol AND scrollHeight <= clientHeight for clamped containers (catches 'paste overflowing'); (2) child-in-box: child.getBoundingClientRect().right/bottom <= parent bounds + tol (catches 'cards bursting / not in right boxes'); (3) on-screen: no declared element at negative offset or beyond viewport unless inside a scroll container (catches 'not being viewed'). `render run` executes it, exits non-zero listing offending selector + viewport, and stamps like verify. It runs on localhost automatically FIRST, so the mechanical subset of visual regressions is caught before the human ever sees the page. Aesthetic correctness ('is it centered nicely') still routes to the human via `handoff` — an explicit, honest division of labor. render.stamp becomes a component of handoff readiness, and rehydrate flags a stale render audit.
- **sketch:** $ docs.py render init
  -> wrote .keel/verify/render_audit.(ts) — declare routes + viewports + selectors.

$ docs.py render run
  route /leads @1280:  ok
  route /leads @375:   X overflow
    .lead-card:nth(7)  scrollWidth 412 > clientWidth 360  (paste overflow)
    .lead-card:nth(7)  child .tag right=+18px past parent box  (bursting)
  route /deck  @1280:  X offscreen
    .slide-note bottom=+240px beyond container, no scroll parent
  VERDICT: FAIL 3 layout invariants. exit 1  (stamped -> feeds handoff readiness)

Core assert: for sel in declared: el=$(sel); fail unless el.scrollWidth<=el.clientWidth+2 AND el.getBoundingClientRect() within parent bounds AND top>=0.
- **fit:** Converts prose review ('make sure nothing overflows') into a committed executable with an exit code — keel's central move, extended to a surface audit.py can't reach. Deliberately mechanical (geometry, not taste), the same discipline as provenance: gate only what a script can decide, and honestly hand the rest (aesthetics) to the human via handoff rather than pretending the agent can judge 'looks right.' Every fixed layout bug becomes a permanent render assertion — the ratchet keel already uses.

### 34. Typed acceptance registry — docs.py accept
- **one-liner:** A durable, per-deliverable-TYPE definition-of-done, learned from the user's rejections and enforced at the done-gate, so the quality bar stops living only in the user's head and getting re-taught every session.
- **problem:** keel's only build-END gate is verify's audit.py, which is shaped for a project CSV (field fill-rate, provenance). There is no memory of what 'good' means for a visualization vs a sales-deck vs an audit. ADRs are per-decision; verify is per-project — NEITHER is keyed to a deliverable TYPE. So every session the user re-teaches 'preserve all non-trivial info', 'attach citations and the volume of proof', 'it has to be shareable', and the agent forgets by the next session. The bar is a fact that decays exactly the way keel says facts decay when they live in prose/memory instead of an enforced check.
- **evidence:** 'PRESERVE ALL THE IMPORTANT NON TRIVIAL INFORMATION IN THE VISUALISATION'; 'attach the citations and the volume of proof'; 'that was not helpful at all, i can't even show anything like that to anyone' — three distinct, per-type quality bars, none of them recorded anywhere, all re-taught each session because the quality bar currently lives only in the user's head.
- **mechanism:** New committed memory tier: docs/acceptance/<type>.md, one file per deliverable type (visualization, sales-deck, audit, research-run, email). Each holds MUST / WILL-NOT criteria, and every MUST names a runnable CHECK (dispatchable by the CLI). rehydrate loads and echoes the acceptance spec for any type touched this session (a new REHYDRATE block), so the bar is re-taught ZERO times. Promotion path that mirrors `supersede` and 'every fixed bug becomes an assertion': when the user rejects a deliverable, `docs.py accept learn <type> --from-rejection "..."` promotes that correction into the type's durable criteria — a rejection becomes a PERMANENT acceptance criterion, ratcheting only stricter. The teeth: `docs.py verify done --type <type>` refuses 'done' until every MUST check for that type passes. Machine checks run (e.g. cite-density greps the artifact for source pointers per proof block; preserve is the check from innovation 3). Human-judgment criteria (e.g. 'shareable / no jarring layout') require `docs.py accept attest <type> <criterion>` that records an attestation stamped with the current deliverable-hash — so it can't be rubber-stamped in advance and goes STALE the moment the artifact changes (same deliverable-hash freshness logic verify already uses). This composes with innovation 2 (the contract template is pre-filled from this spec) and 3 (preserve is one of the named checks).
- **sketch:** docs/acceptance/visualization.md:
  # Acceptance — visualization
  <!-- keel:accept -->
  MUST preserve-all-info        check=preserve         # no non-trivial datum dropped vs prior version
  MUST edit-not-regenerate      check=preserve --edit  # a revision is a diff, not a rewrite
  MUST cite-density>=1.0        check=cite-density     # >=1 source pointer per proof block
  MUST shareable                check=attest           # explicit recorded attestation, deliverable-hash-fresh
  WILL-NOT regenerate-on-edit
  WILL-NOT drop-citations
  <!-- /keel:accept -->
  Learned-from: 2026-07-02 rejection "PRESERVE ALL THE IMPORTANT NON TRIVIAL INFORMATION"

$ docs.py accept learn visualization --from-rejection "make edits, not regenerate; attach citations + volume of proof"
  accept: +2 criteria on visualization (edit-not-regenerate, cite-density) — now enforced at `verify done --type visualization`.

$ docs.py verify done --type visualization
  verify done: ✗ acceptance FAIL (exit 1)
     preserve        ✗  7 fact-units dropped vs v3  (see: docs.py preserve check)
     cite-density    ✓  1.2 pointers/block
     shareable       ✗  no fresh attestation for current deliverable — run: docs.py accept attest visualization shareable
     → 'done' is unclaimable until every MUST passes.
- **fit:** Durable enforced memory over prose; a correction becomes a durable, checked invariant (exactly like an ADR supersede or a regression assertion); honesty over agreeableness (cannot claim done with an un-ticked box); the invariant lives in the CLI + a committed file, not the model's memory. It extends verify's existing 'done needs a fresh passing check' from CSVs to any artifact type.

### 35. Deliverable-intent gate — docs.py deliverable
- **one-liner:** Fire keel's clarify/contract discipline on the deliverable TYPE (viz, research, audit, email) — not just on code/file writes — and force a PRODUCE-vs-FROM slot so the agent stops running off and building the wrong artifact.
- **problem:** The contract gate is explicitly scoped to BUILD = code/files/schema/migrations (SKILL.md §2). Every knowledge-work deliverable — a visualization, a research run, an audit, an email — falls into the lightweight lane, so the agent guesses scope and produces the wrong thing. The sharpest failure is TYPE-confusion: the agent ran a full research pass when the deliverable was a VISUALIZATION built from research already in hand ('BUT THAT WAS NOT YOUR JOB... LEVERAGING THIS INTO A VISUALISATION WAS'). Nothing in the current gate distinguishes 'the output artifact' from 'the input I already have'.
- **evidence:** 'BUT THAT WAS NOT YOUR JOB... LEVERAGING THIS FOR AGENTWORKS INTO A VISUALISATION WAS' (wrong deliverable type); 'if you had to run a full one, why didn't you only get me what i needed' / 'DO NOT repeat research in same direction' (SCOPE slot + coverage ledger).
- **mechanism:** `docs.py deliverable open --type <type> --title "..."` opens a TYPED deliverable and requires an approved contract before its done-gate — the same map-before-build discipline, now triggered by deliverable type rather than by a file-write. The contract template is auto-populated from that type's acceptance spec (innovation 1), so clarify starts from the durable bar instead of a blank guess. Two new mandatory slots close the exact observed failures: (a) PRODUCE = the output artifact type vs FROM = the input already in hand — forcing 'output=visualization, input=existing research' to be stated and approved; (b) SCOPE = targeted slice vs full run, with the narrow ask written down. For the research-run type specifically, opening a deliverable also checks a durable direction-coverage ledger (.keel/coverage/<workstream>.jsonl of directions already run) and WARNS on a near-duplicate direction — making 'DO NOT repeat research in same direction' and 'only get me what i needed' deterministic checks against durable memory rather than the agent's memory. Opening registers the output path so verify's deliverable-hash tracks it. Honest limit, kept consistent with keel's existing stance: for artifacts produced via raw Write/Bash the gate is detect+surface at `deliverable open` and at `verify done --type`, not hard prevention — the same 'detect, don't oversell a block' posture the skill already takes for raw tools.
- **sketch:** $ docs.py deliverable open --type visualization --title "cofounder viz"
  deliverable: visualization/cofounder-viz — CONTRACT REQUIRED before done. Template pre-filled from docs/acceptance/visualization.md:
     PRODUCE:  (?) single shareable HTML visualization
     FROM:     (?) existing research in archive/inputs/ — DO NOT re-run
     SCOPE:    (?) targeted | full        WILL-NOT: regenerate on edit; drop citations
     MUST (from acceptance): preserve-all-info, edit-not-regenerate, cite-density>=1.0, shareable
     → fill PRODUCE/FROM/SCOPE, show the user, then: docs.py contract set + approve

$ docs.py deliverable open --type research-run --title "faire home-decor EU"
  [!] coverage: direction 88% similar to run 2026-06-30 (archive/inputs/run-0003.json) — likely a REPEAT.
     → reuse the prior run or narrow the SCOPE slot; state the targeted slice before spending.

$ docs.py verify done   # with an open deliverable
  verify done: ✗ deliverable 'visualization/cofounder-viz' has no approved contract (PRODUCE/FROM unset).
- **fit:** Map-before-build extended to knowledge work; the plan is SHOWN before acting; options explained in plain language with tradeoffs (keel's clarify house-style); the gate keys on file structure/type, not the model's memory; it reuses, rather than reinvents, the existing contract set/approve/check + deliverable-hash machinery.

### 36. Preservation & edit-not-regenerate check — docs.py preserve
- **one-liner:** A deterministic version-diff of a deliverable that lists every non-trivial fact dropped since the last approved version and flags a wholesale regeneration — turning 'preserve all the info' and 'edit it, don't make it again' from hopes into an exit code.
- **problem:** keel's verify only ever inspects a SINGLE current snapshot (field fill-rate of today's CSV). It has no notion of a prior version, so it cannot catch the two failures the user hit repeatedly on the cofounder viz: (1) the revision silently DROPPED proof — citations, numbers, named claims that were in the last good version; (2) the agent REGENERATED the artifact from scratch when asked to make a small edit, producing 'jarring' output. Both are exactly the kind of drift keel is supposed to gate, and both are cheaply, deterministically detectable — but no baseline mechanism does it.
- **evidence:** 'PRESERVE ALL THE IMPORTANT NON TRIVIAL INFORMATION IN THE VISUALISATION'; 'make edits to the visualisation, not make it again... no jarring proof... attach the citations and the volume of proof'.
- **mechanism:** `docs.py preserve snapshot <artifact>` extracts a set of 'fact-units' from the artifact via deterministic regexes — citations (URLs / [n] refs), numbers-with-units, quoted claims, and TitleCase named entities — and stores them at .keel/preserve/<artifact>/vN.facts.json plus the raw text. Snapshots are taken automatically at each `verify done` so vN is always the last APPROVED version. `docs.py preserve check <artifact>` re-extracts from the current version and set-diffs against the last snapshot: any fact-unit present before and absent now is reported as a DROP, itemized by kind, and fails the check (exit 1) — this is the enforceable form of 'preserve all non-trivial info'. It also computes difflib.SequenceMatcher(prior_text, new_text).ratio(); with `--edit` (a revision was requested), a ratio below a floor (e.g. 0.50) FAILS as 'REGENERATED not edited' — the enforceable form of 'make edits, not make it again'. It is registered as a named CHECK the acceptance registry (innovation 1) requires and the `verify done --type` gate runs, so it is wired into the loop rather than being a standalone tool the agent must remember to invoke.
- **sketch:** $ docs.py preserve snapshot deliverables/cofounder-viz.html
  preserve: snapshot v3 → .keel/preserve/cofounder-viz/v3.facts.json
     captured 214 fact-units: 41 citations, 96 numbers, 63 quoted claims, 14 named entities

$ docs.py preserve check deliverables/cofounder-viz.html --edit
  preserve check: ✗ FAIL (exit 1)
     REGENERATED: text similarity to v3 = 0.19 (< 0.50) — rebuilt from scratch; an edit was requested.
     DROPPED 7 fact-units missing vs v3:
       citation  3x faire.com proof links
       number    "1,284 wholesale buyers"
       claim     "retention 41% vs 22% category avg"
     → edit v3 in place, re-add the dropped proof, then re-run. (auto-run by: verify done --type visualization)
- **fit:** Verify the deliverable, not the claim, and re-verify live — extended from 'is field X filled' to 'did the proof survive this edit'; a ratchet that only gets stricter (every approved version raises the floor of what must be preserved); the invariant is an exit code in the CLI, not a sentence the model can talk past under pressure; cheap and deterministic ('does this fact-unit still appear' is scriptable exactly like 'does a source pointer exist').
