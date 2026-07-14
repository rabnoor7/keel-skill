# keel — Innovation Backlog

Ranked by **value × evidence ÷ build-cost**, mined from real sessions across 10 repos and filtered through 3 adversarial lenses. Each tag reads `[keeps · highs · build]` — `keeps`/`highs` are the adversarial judges' retention/high-value votes (max 3 each); `build` is implementation cost.

**Why so many are cheap:** nearly every item reuses the same four primitives keel already ships — an append-only `.keel/*.jsonl` tier, the `_append_jsonl`/`_load_jsonl` helpers, the `verify` stamp pattern, and the rehydrate `problems++ → exit 1` loop. New invariants land as *computed* checks (replay the ledger), never hand-maintained counters that lie.

**Two structural notes up front:**
- **Naming clash:** two survivors both proposed `docs.py handoff`. I keep `handoff` for cross-worktree coordination and rename the human-test lane to **`livetest`**.
- **Shared dependency:** `preserve`, `coverage`, and `deliverable` all register as *named checks* in a small **acceptance registry** (`docs/acceptance/<type>.md`). That registry ships as part of `deliverable` (#8); the other two degrade gracefully to standalone until it exists.

**Composition map:** `run`+`sink` (called together per item) · `escalate`+`stance` (the gate consults stance first) · `verify batch` pulls in `run`, trust-provenance, and `verify baseline` as its oracle · `substrate`+`orphans` (orphans resolves refs *inside* declared anchors) · `coverage` is the mirror of provenance.

---

## Ship-now / high-value

### 1. `run` — durable resumable work-ledger (execution cursor)
*[keeps 3 · highs 3 · build: Low–Med]*
An append-only per-item ledger that makes "where did I leave off", ETA, and idempotent resume deterministic — and blocks a clean rehydrate while any run is mid-flight.

- **Need:** keel's only progress-like state is the decision pending-queue, drained at loop *end*. Long scrapes/swarms die before hydrate ever runs, so "continue exactly where you left off" cannot be reconstructed and a fresh rehydrate shows nothing in flight. The checkpoint-every-unit invariant sits inert as prose in **five** places and is enforced zero. Evidence: *"CONTINUE EXACTLY WHERE YOU LEFT OFF DO NOT MISS OUT ON ANYTHING"*; *"is it running rn? / how long till it finishes?"*; *"how the fuck will rehydrate work if nothing is written here."*
- **Mechanism:** new EXECUTION tier `.keel/runs/<id>.jsonl`. Line 1 = MANIFEST (label, total, item universe, host, ts); every later line = one fsync'd ITEM record (`id, done|failed|skip, by=<agent>, ts`) — that line *is* the checkpoint the prose demanded. All of progress/position/rate/ETA/by-agent is **computed by replaying the ledger**. An open run (no close record) with pending>0 is a loud rehydrate problem → exit 1. `run resume` prints the exact pending item-ids (manifest − done − skip), feeding straight back into the worker loop.
- **Sketch:**
```
run start --label faire-enrich --count 1000        -> RUN r7a3, 0/1000
run mark r7a3 brand_88231 --status done --by agent-3   (append-only, per item)
run resume r7a3   -> prints 581 pending ids (idempotent skip-what's-done)
# rehydrate: [!] RUN MID-FLIGHT r7a3 412/1000, 581 pending, last mark 3m ago -> resume, don't restart
```

### 2. `escalate` — judgment escalation checkpoint (route-through-me)
*[keeps 3 · highs 3 · build: Med]*
A mid-flight, **keel-judged** escalation for pivotal/irreversible/costly calls: a durable BLOCKED-ON-USER state that survives session end and compaction, can't be steamrolled, and auto-promotes the user's answer to an ADR so it's never re-litigated.

- **Need:** keel's clarification gate is pre-build *prose* ("STOP — ask as many questions as needed") — exactly the in-context instruction keel's own doctrine says gets talked past under pressure, and it dies with the session. The user does **not** want blanket ask-everything; they want keel to escalate when *keel* judges it necessary. Evidence: *"WHY THE FUCK DID YOU CONTINUE WITHOUT ACTUALLY ASKING"*; *"how the fuck did you make changes without confirming… revert and report first"*; *"NOT WHEN I SAY ON, when YOU THINK IT IS NECESSARY… JUST ASK ME IF THERE IS A PIVOTAL CHANGE."*
- **Mechanism:** `.keel/escalations.jsonl`. `escalate raise --because pivotal|irreversible|cost` records it and marks the thread BLOCKED-ON-USER — it's keel's *judgment* that raises it, not a user keyword (the exact distinction drawn). `escalate resolve <id> --choice X --to-decision "…"` promotes the answer to an ADR via the existing `cmd_decision` path (rehydrate-visible, never re-litigated); `--retract` cancels. rehydrate surfaces unresolved escalations at the very top as a hard `[!!]` block with age-in-sessions → survives compaction, interrupt, and a brand-new session. Durable, resumable, blocking, self-recording — the "route through me" primitive that lets a domain sit at auto while still catching the rare pivotal call. *Honest limit:* binds threads routed through keel; detect-and-surface, not hard-prevent.
- **Sketch:**
```
escalate raise --domain external-dm --because irreversible \
  --question "Send outreach DMs now, or stage drafts?" --options "send|stage|skip" --recommend stage
ESCALATION #3 — BLOCKED ON USER. will NOT proceed on this thread. Recorded durably.
# rehydrate top: [!!] BLOCKED — 1 open escalation (raised 2 sessions ago) #3 …
escalate resolve 3 --choice stage --to-decision "outreach: stage, never auto-send"  -> ADR 0021
```

### 3. `stance` — standing stance register (durable freeze + user-named modes)
*[keeps 3 · highs n/a — source record truncated; value inferred from the very-high autonomy theme + direct repeated evidence · build: Low–Med]*
A persistent, session-surviving stance (freeze / discussion-only, plus user-coined modes like *sensei*, *partner*) that rehydrate re-arms every session, can block even the lightweight lane, forces memory-writes to be confirmed, and is cleanly retractable.

- **Need:** the user re-declares a freeze *every* session because keel has nowhere durable to hold it — and the lightweight-lane prose carve-out means even a declared freeze can't stop a "trivial reversible edit." Their vocabulary (*Sensei mode*, *partner mode*) evaporates at session end. Evidence: *"DO NOT MAKE ANY CHANGES UNTIL WE FINALIZE"* / *"No commits until confirmed by me"*; *"Lets go Sensei mode on till the end of this chat"*; *"JUST BE A PARTNER… you just confirm with me on what you are saving as memory"*; *"DO NOT CONSIDER WHAT WAS WRITTEN ABOVE AND CANCELLED."*
- **Mechanism:** `.keel/stance.json` holds one active stance `{name, freeze, blocks_lightweight, memory:'confirm'|'silent', autonomy_default, note, declared_ts, sessions_since}`. The `escalate` gate consults stance **first**: `freeze` returns FROZEN for *everything* including the lightweight lane and auto domains — the hard override prose can't provide. `memory='confirm'` forces `decision`/`journal`/`prefs` to auto-`--draft` into `.keel/pending/`, turning the existing opt-in draft into a standing "confirm what you save" invariant. rehydrate re-arms the stance loudly at the very top with `sessions_since`; `stance clear` is the retract path.
- **Sketch:**
```
stance set freeze --note "DO NOT MAKE CHANGES UNTIL WE FINALIZE"
# rehydrate top: >>> STANDING STANCE: freeze (declared 4 sessions ago) — NO builds/edits/ops. clear to lift.
stance set partner --autonomy-default ask-destructive --memory confirm   # decisions now auto-stage as drafts
```

### 4. `sink` — offline capture-inbox with idempotent reconcile
*[keeps 3 · highs 3 · build: Low–Med]*
A durable landing zone where fetched payloads go the instant they're captured, hash-deduped and idempotently imported into the master when the backend returns — so fetched data can never be silently disposed.

- **Need:** keel flushes *decisions* continuously but has no continuous-flush path for the expensive fetched *artifact*. When the backend/master is unreachable mid-run, hours of rows evaporate; "never dispose fetched data, merge partials" has no teeth. Evidence: *"Backend offline — saved 500 ads to the repo inbox… it stopped in the middle"* (a hand-rolled version with no primitive behind it); *"FUCKING INTERNALISE THAT WHENEVER HOURS ARE SPENT TO FETCH DATA DON'T just dispose it… ENTER IT IN THE MASTER CSV."*
- **Mechanism:** `.keel/inbox/<stream>.jsonl`, append-only; each record = payload + computed content-hash (dedup key) + provenance + intended target. `sink add` is where data goes the moment it's fetched — durable even when the target is down. `sink import` reconciles idempotently: hash not in the sidecar index → merge + mark reconciled; dups skipped by construction. A non-empty unreconciled stream is a loud rehydrate problem → exit 1. **Composes with `run`:** a worker does `run mark <id> done` **and** `sink add <payload>` per item — cursor and payload flushed together.
- **Sketch:**
```
sink add --stream ads --target data/master.csv --provenance <url> --from row.json   # target DOWN -> held
sink import --stream ads   -> 500 buffered -> 483 new merged, 17 hash-dup -> master now 12,340 rows
# rehydrate: [!] CAPTURE INBOX — 500 records captured while target unavailable, not yet merged
```

### 5. `ask` — standing user-ask ledger with verify-bound resolution
*[keeps 3 · highs 2 · build: Low–Med]*
Every user-facing ask becomes a tracked entry that can only reach VERIFIED-RESOLVED when bound to a passing named assertion; if that assertion later fails, the ask auto-flips to REGRESSED and rehydrate surfaces it with its re-raise count.

- **Need:** the model repeatedly claims an ask resolved; the user repeatedly re-raises it; nothing counts the re-raises or binds "resolved" to a real check. "I've asked for this so many times" is today an *emotion*; it should be a deterministic counter the model is forced to see. Evidence: *"STill i hover info is overflowing… WTH I have asked for this so many times"*; *"still seems to be not additive."*
- **Mechanism:** reuses verify's exit-code ratchet. `ask add "<text>"` normalizes to a token set and fuzzy-matches open+resolved asks; a match against a RESOLVED entry increments `raised_count`, flips to REGRESSED, stamps the re-raise date. `ask resolve <id> --bind audit.py::test_x` binds to a named assertion; status stays CLAIMED (never VERIFIED) until `verify run` passes *with that assertion present*. An ask with no bindable check **cannot** be marked resolved. rehydrate re-evaluates every VERIFIED ask against the latest stamp+deliverable-hash and fails loudly on regression.
- **Sketch:**
```
ask add "hover tooltip overflows the card"
 -> matched RESOLVED #7 (overlap 0.82): raised 3->4, VERIFIED->REGRESSED
# rehydrate: [!!] ASK REGRESSED #7 resolved 06-02, bound check now FAILS, raised 4x. Don't re-close without green bind.
```

### 6. `verify baseline` — the last good run as an oracle (shrink/collapse guard)
*[keeps 3 · highs 3 · build: Med]*
A stored fingerprint of the last *passing* run turns "is this scrape smaller/worse than last time?" into an exit code — and the same fingerprint can gate a push on measured improvement.

- **Need:** keel's verify is absolute and memoryless: `_deliverable_hash()` sees *that* the deliverable changed, never how much or which direction. A scrape that captures 40% fewer rows, or where a broken selector writes the *same constant* into every `category` cell, passes every field-level check and overwrites a good master. Evidence: *"if the scrape size is smaller than last time then something is wrong and needs a reaudit"*; *"why the fuck have we not been catching any of this in the audits."*
- **Mechanism:** two actions on `cmd_verify`. `baseline snapshot` (allowed only after a passing run) fingerprints declared deliverables — rows, per-field fill-count, **per-field distinct cardinality**, numeric min/max/mean, bytes, file inventory → `.keel/baselines/<slug>/<ts>-<sha>.json` (ring of 5). `baseline check` diffs current vs newest baseline and exits non-zero on three classes: **SHRINK** (rows/fill down > tol), **FILL-DROP** (a field went blank though rows held), **COLLAPSE** (cardinality craters 380→3 — the invisible constant-writing selector, where fill-rate still reads 100%). Optional `baseline gate --require improve` wires into pre-push.
- **Sketch:**
```
verify baseline check
  rows              4,812 -> 2,905   -39.6%   x SHRINK
  fill wholesale    94.1% -> 61.2%   -32.9pt  x FILL-DROP
  distinct category    38 -> 3       x COLLAPSE (constant?)
VERDICT FAIL — do NOT overwrite master; keep prior artifact. (exit 1)
```

### 7. `preserve` — preservation & edit-not-regenerate check
*[keeps 3 · highs 2 · build: Med]*
A deterministic version-diff that lists every non-trivial fact dropped since the last approved version and flags a wholesale regeneration — turning "preserve all the info" and "edit it, don't make it again" into exit codes.

- **Need:** keel's verify only ever inspects a single current snapshot, so it can't catch the two repeated cofounder-viz failures: (1) a revision silently *dropped* proof — citations, numbers, named claims; (2) the agent *regenerated* from scratch when asked for a small edit, producing "jarring" output. Both are cheaply, deterministically detectable. Evidence: *"PRESERVE ALL THE IMPORTANT NON TRIVIAL INFORMATION"*; *"make edits… not make it again… attach the citations and the volume of proof."*
- **Mechanism:** `preserve snapshot` extracts fact-units via deterministic regex — citations (URLs/`[n]`), numbers-with-units, quoted claims, TitleCase entities → `.keel/preserve/<artifact>/vN.facts.json` + raw text, auto-captured at each `verify done` (so vN = last approved). `preserve check` set-diffs current vs snapshot: any fact present-before-absent-now is a DROP (exit 1). It also computes `difflib.SequenceMatcher(prior, new).ratio()`; with `--edit`, a ratio below a floor (e.g. 0.50) FAILS as "REGENERATED not edited." Registered as a named check the acceptance registry runs.
- **Sketch:**
```
preserve check deliverables/cofounder-viz.html --edit
  x REGENERATED: similarity to v3 = 0.19 (< 0.50) — rebuilt from scratch, an edit was requested
  x DROPPED 7 fact-units: 3 faire.com links, "1,284 wholesale buyers", "retention 41% vs 22%"
```

---

## Bigger bets

### 8. `deliverable` — deliverable-intent gate (+ acceptance registry) ⟵ foundational keystone
*[keeps 3 · highs 1 · build: Med–High]*
Fire keel's clarify/contract discipline on the deliverable **type** (viz, research, audit, email) — not just code/file writes — and force a PRODUCE-vs-FROM slot so the agent stops building the wrong artifact. *Leads the bigger-bets tier because it is the entry point for all non-build work (a very-high theme) and ships the acceptance registry that `preserve` and `coverage` bind to.*

- **Need:** the contract gate is scoped to BUILD = code/files/schema, so every knowledge-work deliverable falls into the lightweight lane and the agent guesses scope. The sharpest failure is type-confusion. Evidence: *"BUT THAT WAS NOT YOUR JOB… LEVERAGING THIS INTO A VISUALISATION WAS"*; *"if you had to run a full one, why didn't you only get me what i needed"* / *"DO NOT repeat research in same direction."*
- **Mechanism:** `deliverable open --type <t> --title …` opens a typed deliverable requiring an approved contract before its done-gate, auto-populated from `docs/acceptance/<type>.md` (the durable per-type bar — the **acceptance registry**). Two mandatory slots close the observed failures: **PRODUCE** (output artifact) vs **FROM** (input already in hand), and **SCOPE** (targeted slice vs full run). For `research-run`, opening checks a durable direction-coverage ledger and WARNS on a near-duplicate direction. Registers the output path so `verify`'s deliverable-hash tracks it. *Honest limit:* for raw Write/Bash artifacts it's detect-and-surface at `open` and `verify done --type`, not hard-prevent.
- **Sketch:**
```
deliverable open --type visualization --title "cofounder viz"
  CONTRACT REQUIRED. PRODUCE:(?) single HTML viz  FROM:(?) existing research — DO NOT re-run  SCOPE:(?)
  MUST (from acceptance): preserve-all-info, edit-not-regenerate, cite-density>=1.0
deliverable open --type research-run --title "faire EU"
  [!] coverage: 88% similar to run 2026-06-30 — likely a REPEAT. narrow SCOPE before spending.
```

### 9. `verify batch` — in-flight layered audit + circuit breaker
*[keeps 3 · highs 2 · build: Med–High]*
A fast per-batch subset of the audit fires after every chunk of a long run, stamps a rolling pass/fail log, and trips a real HALT flag on consecutive failures — so a run that goes bad at chunk 3 stops at chunk 3, not chunk 300.

- **Need:** keel's verify is a single event at the done gate. A 5,000-lead enrichment that starts fabricating at batch 3 burns budget for hours before the one-shot audit runs; there's no corrective loop that re-runs only the bad batches. Evidence: *"run an audit if the data being filled does not seem generated or faked by sonnet, run this in parallel while the enrichment happens"*; *"why the fuck have we not been catching any of this in the audits."*
- **Mechanism:** `verify batch <n> --window <partial>` runs a FAST audit layer (schema + provenance + fabrication sample + fill-vs-batch-baseline, skipping whole-dataset cross-checks) on the newest partial only, appending to `.keel/verify/batches.jsonl`. **Circuit breaker (the teeth):** K consecutive FAILs or windowed fail-rate past a threshold writes `.keel/verify/HALT` and exits non-zero; the run loop is contracted to poll HALT after each batch and STOP. `verify batch report` rolls up exact failed batch-ids for targeted re-run. Composes with `run` and pulls trust-provenance (#10) as its fabrication layer.
- **Sketch:**
```
verify batch 7 --window data/.partial/batch_7.csv
  provenance 112/120 x   fabrication 118/120 x   fill price 58% x (baseline 91%)
BATCH 7 FAIL — consecutive 3/3 -> CIRCUIT BREAKER TRIPPED, wrote HALT. STOP the run.
verify batch report -> FAILED windows to re-run: 4,5,6,7 (keep 1-3)
```

### 10. `verify provenance` — trust-tiered provenance (cited + fresh + cross-validated)
*[keeps 3 · highs 2 · build: High — the only item with real network I/O]*
Upgrades the anti-fabrication check from "a source pointer exists" to a three-part per-field trust standard: the citation resolves, its timestamp is fresh, and the claimed value corroborates against the source.

- **Need:** keel's provenance is deliberately shallow ("does a pointer exist"), so the exact fabrication in play slips through: a delegated Sonnet writes a plausible URL it never read, or a believable price with a stale/invented source. The pointer exists → provenance passes → the row is invented. No freshness dimension exists at all. Evidence: *"run an audit if the data being filled does not seem faked by sonnet"*; *"the validity of the citation and the time of the citation and some basic cross validation."*
- **Mechanism:** per-field **policy in data-model.md** (versioned, not a magic number): `cited` / `fresh:<window>` / `xval:<rule>`. `verify provenance` stamps each row TRUSTED / UNVERIFIED / STALE / FABRICATED; records are untrusted-by-default. Cross-validation is the honest boundary — for URLs, a cheap deterministic fetch-and-assert-token-present ("does the page actually say this"); for recomputables, recompute; where no oracle exists, mark UNVERIFIED (never silently TRUSTED). Exits non-zero on any FABRICATED or a field below its TRUSTED threshold. `verify sync` keeps the declared field-set honest.
- **Sketch:**
```
# data-model.md:  wholesale_price  fresh:90d + xval:token
verify provenance
  TRUSTED 2,410 (83%)  UNVERIFIED 361  STALE 98  FABRICATED 36
  worst: wholesale_price 36 FABRICATED, TRUSTED 71% < 90% gate
  sample: row 1180 cites brandsite.com/x (404); row 1442 price $8.50 not on cited page   (exit 1)
```

### 11. `livetest` — human-in-the-loop live-test lane with a self-certification ban
*[keeps 3 · highs 2 · build: Med–High]* *(source proposed `handoff`; renamed to avoid the #14 clash)*
Split "done" into an agent-side readiness gate (automated tests green + env actually up) that MUST pass before a human is asked to test, and a human-side gate only the user can close — with `verify done` structurally blocked from self-closing a reality-verified deliverable.

- **Need:** `verify done` lets the *agent* self-certify. For anything whose ground truth is reality (live UI, real behavior) the agent cannot be the closing verifier, and the user said so repeatedly. Evidence: *"DO not test yourself, give me to test"*; *"do run tests before asking me to run manual test… turn on the server"*; *"have you extremely thoroughly tested it from your side before the hand off?"*; and the edge-case demand *"did you run test on if a tenet needs to be deleted how the kg layer acts."*
- **Mechanism:** a persisted state machine `.keel/handoff.json`: READY-BLOCKED → HANDED_OFF → OBSERVED → ACCEPTED. `livetest open` refuses (exit 1) unless the readiness gate is green — verify stamp fresh+pass, the durable edge-case suite green (incl. destructive cases like tenet-deletion), AND the declared server actually listening on its port. On green it stands the env up, prints the test URL + an edge-case checklist, and moves to HANDED_OFF — where `verify done` is BLOCKED. Only `livetest observe --note` (timestamped *after* server-up) and `accept --by-human` close it; failing observations auto-file as new regression assertions. *Honest limit, in keel's own voice:* raw tools bypass this and a fake human-accept can't be truly prevented — but observations-must-post-date-server-up plus a loud "AWAITING HUMAN OBSERVATIONS" banner make self-closing detectable, not silent.
- **Sketch:**
```
livetest open --deliverable web
  x BLOCKED — edge-suite 2/9 failing (tenet-delete, empty-set); nothing listening on :3000
# after fixes: ok env up. TEST -> http://localhost:3000. state HANDED_OFF; verify done is BLOCKED.
verify done -> x HANDED_OFF and not human-accepted; self-testing cannot close this. (exit 1)
```

### 12. `coverage` — reverse-provenance audit against an external ground-truth doc
*[keeps 3 · highs 1 · build: Med]*
Decompose an external source (meeting transcript, spec, tenet list) into a durable ID'd points ledger, then hard-gate that **every** source point maps to a place in the deliverable — the mirror image of provenance.

- **Need:** provenance runs one direction (every claim must cite a source) and waves through the real failure: a deliverable that is internally well-cited but silently *omits* points the source raised. The user had to be the enumerator. Evidence: *"reevaluate against every nuance covered by saurabh and me and I saw you missed… AUDIT THE MEET AGAIN"*; *"are all tenets mapped."*
- **Mechanism:** `coverage extract --source <file>` decomposes the doc once into `.keel/coverage/<source>.points.jsonl` — atomic points with stable content-hash IDs (re-extraction merges, never drops). `coverage map <id> --to <locator> --status addressed|deferred [--reason]` records discharge. `coverage audit` fails (exit 1) if any point has no addressed mapping, or a deferred with empty reason. The semantic "is point 7 addressed" stays with the agent; the CLI enforces no point is silently skipped. Unaddressed points surface in rehydrate. Binds as a named check in the acceptance registry.
- **Sketch:**
```
coverage extract --source meetings/2026-07-10-saurabh.md -> 34 points (stable IDs)
coverage audit
  ADDRESSED 28  DEFERRED 3  UNADDRESSED 3 x
    P07 "cap retry budget per-tenant, not global" -> no mapping
  FAIL — 3 source points unmapped. map or --defer (with reason). (exit 1)
```

### 13. `substrate` — external anchors of truth as first-class, divergence-gated tiers
*[keeps 3 · highs 2 · build: Med–High]*
Let the user DECLARE that `agents.md` / an Obsidian vault / a Graphiti KG is the real anchor-of-truth, then have rehydrate read it and fail loudly when it has drifted out of sync with landed decisions.

- **Need:** keel assumes its own `docs/` is the source of truth, but this user's anchor lives in a living `agents.md`, an Obsidian vault, and a Graphiti KG — none of which keel reads or knows the freshness of. Their substrate is *inverted* from keel's assumption. Evidence: *"do we have all the latest up to date everything in agents.md about the exact state of things"*; *"I have my own rag and am using graphiti for kg."* (Corroborated: this environment exposes an Obsidian MCP.)
- **Mechanism:** `substrate add --path … --kind anchor|vault|kg` → `.keel/substrate.json` with a synced watermark (last ADR n + ts). rehydrate gains a SUBSTRATE block: file-backed anchors get hash+mtime **bidirectional** divergence ("agents.md is N landed decisions behind"; "agents.md changed since architecture.md") reusing the contradiction extractor; service-backed anchors (Graphiti/RAG — unhashable) get a deterministic **sync-debt ledger** (count of decisions+findings past the watermark). keel does **not** push to Graphiti/Obsidian (that's the MCP tools' job) — it owns the ledger; `substrate sync` records the watermark after the agent pushes. Honors keel's detect-and-surface boundary.
- **Sketch:**
```
substrate add --path ../knowledge-graph-rag/agents.md --kind anchor
# rehydrate: anchor agents.md [!] BEHIND — ADR 0011,0012,0013 landed after it
#            kg graphiti://faire-lead [!] SYNC DEBT — 3 decisions, 2 findings since 2026-06-30
VERDICT exit 1 (an out-of-date declared anchor is a loud failure)
```

### 14. `orphans` — dangling-reference / graph-integrity check over the memory graph
*[keeps 3 · highs 2 · build: Med]*
Resolve every cross-reference in the memory graph (ADR→entity, journal→`decisions/NNNN`, `file#anchor`, substrate→repo path), classify each orphan by **why** it dangles, and auto-repair the unambiguous ones.

- **Need:** keel's single-source rule says every mention *links* to its canonical home — but nothing checks those links resolve. References rot silently (a journal points at a superseded ADR; an ADR cites a renamed anchor). The user had to catch this himself *and* ask why keel didn't fix it proactively. Evidence: *"DEEP DIAGNOSE ON WHAT AND WHY ARE THESE ORPHANS"*; *"Why did you not update the orphans yourself first."*
- **Mechanism:** a pure reference-resolution pass wired into rehydrate (exit non-zero on any orphan). EXTRACT every intra-memory ref (`decisions/NNNN`, `#anchor`, `[..](path)`, and refs inside declared substrate files). RESOLVE each against disk/headings/ADR set. CLASSIFY the "deep diagnose": target-deleted | target-renamed (fuzzy nearest + score) | target-superseded (names the successor) | path-moved. `orphans --fix` rewrites the unambiguous cases (superseded→successor, high-confidence 1:1 rename) and lists ambiguous ones to confirm. Distinct from the existing contradiction check, which only detects supersession *claims* and never resolves a reference *target*.
- **Sketch:**
```
orphans
  journal…:4  "see decisions/0008"       target-superseded -> successor 0012   [auto-fixable]
  0011…:9     "data-model.md#brand_id"    target-renamed -> brand_key (0.82)    [confirm]
  agents.md   "faire-lead/pipeline.py"     path-moved -> not on disk             [confirm]
  orphans --fix applies the 1 auto-fixable; re-run for the 2 needing confirmation.
```

### 15. `handoff` — cross-worktree coordination tier (report-up + inbound handoffs)
*[keeps 3 · highs 3 — judged strong; lands in bigger-bets only for the git plumbing, not weak evidence · build: Med–High]*
A shared, addressed, append-only handoff/report ledger keyed to the git common dir so it spans worktrees — turning keel's flat one-filesystem peer model into a hierarchical manager/worker channel.

- **Need:** keel's whiteboard + claim locks live in `.keel/` under a single cwd. The instant a Sonnet grunt works in a separate `git worktree`, the two share no `.keel/` and neither can see the other. The user's real handoffs are loose files keel doesn't recognize as memory, with no from/to, source-commit, or status, and no report-up channel to the Opus manager. Evidence: *"intelligence managed by opus and grunt work by sonnet"* / *"tell me what's wrong to report to your opus manager"*; *"still pending in the other sonnet session in a separate worktree which i branched from here."*
- **Mechanism:** a coordination tier keyed to `git rev-parse --git-common-dir` — the one path every linked worktree agrees on (the deterministic fix for the single-filesystem assumption). `handoff send/report` writes append-only JSONL there (`{id, from_role, to_role, kind, title, body_path, source_sha, worktree, status}`). rehydrate gains a CROSS-WORKTREE panel: runs `git worktree list`, lists siblings + HEADs, shows OPEN handoffs addressed to me, and flags loudly my outbound handoffs still unconsumed. `handoff import <file>` ingests an ad-hoc `IG-audit-handoff-*.md` stamped with author role + commit, so keel finally treats it as recognized memory.
- **Sketch:**
```
handoff send --to grunt --kind handoff --title "IG audit: enrich 485 rows" --from-file handoff.md
handoff report --to manager --re 7 --title "audit done: 3 fields still empty"
# rehydrate: [!] 1 OPEN handoff addressed to me (report from grunt @f77b10, re #7)
#            [!] 1 handoff I emitted UNCONSUMED: #7 -> grunt (4h) — work may be stranded in worktree ig-audit (exit 1)
```

### 16. `smoke` — config-bound go/no-go before expensive or irreversible long runs
*[keeps 3 · highs 2 · build: Med]*
`smoke arm/run/gate`: declare a tiny end-to-end sample bound to the **exact config** the long run will use, run it fanned-out per endpoint/IP, and stamp a go/no-go the launch refuses without — the symmetric before-gate to verify's after-gate.

- **Need:** the user performs this ritual by hand every time and keel gives it no enforcement. SKILL.md *says* "measure real limits on a small sample" but nothing backs it: nothing prevents launching untested, and nothing catches the bait-and-switch where the 1-min test ran on a *different* config than the launch (smoke on 1 IP, launch on 8 including 2 blocked). Evidence: *"I've turned on vpn in one browser and not in other, run quick 1 min test that everything is working then start long running execution"*; *"let's spec a multi-IP build and then run a small test on multi-ip system."*
- **Mechanism:** the exact analog of verify (verify gates *done* after via a stamp bound to the deliverable-hash; smoke gates *go* before via a stamp bound to a **config hash**). `smoke arm` declares the sample + full pipeline + pass criteria + a fingerprint of the launch config (endpoints/IP set/collection/model). `smoke run` executes on the sample, fanning out **per endpoint/IP requiring all-green per-endpoint** (aggregate is exactly what hides one dead IP), stamps `.keel/smoke.stamp`. `smoke gate` passes only if a fresh smoke exists, PASSED, and its config_hash **equals** the config about to launch — killing both the per-endpoint-hidden failure and the config bait-and-switch. *Honest limit:* binds runs routed through keel.
- **Sketch:**
```
smoke run
  fetch ip1 ok  ip2 ok  ip3 x (bot-check block)
  VERDICT x ip3 will block 1/3 of the run. Fix or drop, re-arm, re-smoke. (exit 1)
smoke gate
  x config CHANGED — smoked {3 ips, brands_v3}, launching {8 ips, brands_v4}. 5 new ips UNTESTED. (exit 1)
```

---

## Build these three first — and why

**1. `run` (execution cursor).** Highest value ÷ cost in the set. The "checkpoint after every unit, resume idempotently" invariant is written **five times** as prose across profiles and enforced **zero** times — the single largest gap between what keel promises and what it guarantees. The mechanism is the cheapest possible: append one fsync'd line per item, compute everything else by replaying the ledger, reuse the existing helpers and the rehydrate `problems++ → exit 1` loop. It is the spine every long-job feature hangs off, and it directly answers the most-recurring operational questions ("is it running", "how long left", "continue where you left off").

**2. `escalate` (route-through-me).** The most visceral, most-repeated evidence in the entire corpus is about the same failure — continuing without asking, making irreversible changes without confirming. keel's current defense is *prose the model talks past*, and it dies with the session. `escalate` is the novel primitive that has no home in the CLI today: a durable BLOCKED-ON-USER state that survives compaction and a fresh session, raised by *keel's judgment* (the exact distinction the user drew against a blanket switch), and auto-promoted to an ADR on resolution. Highest-pain fix, confirmed keeps 3 / highs 3.

**3. `sink` (capture-inbox).** Chosen over the slightly higher-ranked `stance` deliberately: it is the third **judge-confirmed keeps 3 / highs 3** item (maximum adversarial certainty — `stance`'s high-value vote was truncated in the source and is genuinely unknown), it covers a distinct strong theme (data-artifact lifecycle) rather than double-covering autonomy, and it is **designed to compose with `run`** — a worker calls `run mark` and `sink add` together per item, so building them adjacently flushes cursor and payload as one durable act. It closes the "hours of fetched data silently disposed" failure that no current primitive touches.

**Build immediately after:** `stance` (#3 by rank — the standing-mode counterpart to `escalate`; together they fully discharge the very-high autonomy theme) and `ask` (#5 — a cheap accountability win that turns "I've asked this so many times" into a bound, regression-aware counter). Both are Low–Med build and reuse machinery `run`/`escalate` will already have established.