# Changelog

All notable changes to keel. Versions follow semver; `docs.py --version` reports the installed version.

## [1.6.1] — 2026-07-21

### Two fixes from the first blind drift battery (real-usage findings, both locked)

- **The cross-writer guard no longer cries wolf.** Every CLI call gets a fresh process id, so a normal
  same-session `discuss open` → `close` (separate shell invocations — the standard agent pattern)
  tripped the accidental-cross-session guard and demanded a `--writer` retry. The guard now fires only
  when an EXPLICIT writer label (KEEL_WRITER / --as) mismatches; pid-fallback labels never gate — they
  are per-invocation noise, and a guard that fires on noise trains everyone to ignore it. Its ratified
  intent (catch ACCIDENTAL cross-session closes) is unchanged and still enforced for labeled sessions.
- **Clipped text now says so.** The approval echo, the presence line's last-capture titles, and roadmap
  choice lines truncated mid-word with no ellipsis — a clipped tail read as data loss ("…go ahead and
  bu"). All now clip through the shared ellipsis helper. Intended visible diff: an `…` appears where
  long strings were already being cut silently.

## [1.6.0] — 2026-07-20

### Record integrity: who approved it, and who settled it (two fixes, both earned by real failures)

- **Approval now records WHO and ON WHAT WORDS (agent-facing).** `contract approve` flipped a single
  boolean that the agent could set itself — so an approval nobody granted was indistinguishable from one
  they did, and every downstream ✓ (hook, witness, resume) inherited that hole. `approve` now **requires
  `--by <who>` and `--echo "<the user's actual words>"`** and refuses without both; `contract check`
  displays `approved by <by>: "<echo>"`. The same side-door in **`set --approved` is closed too** (it was a
  second self-approve path). The echo is stored **verbatim** — doctrine is to quote the user, never to
  paraphrase or parrot it back at them. **Nothing you see changes:** the attribution surfaces only in
  agent-read `contract check` output, and if you ask. Stated honestly, in the tool's own words: these
  fields raise the cost of a false record and make a witness possible — **they do not prove the approval
  happened.**
- **Two sessions can no longer silently overwrite each other's discussion threads.** Caught live: two
  concurrent sessions shared one `.keel/discuss.jsonl`; thread ids were allocated from an **unlocked** read,
  and `close` addressed a bare integer in one unscoped namespace — so one session closed a thread the other
  had opened, recording a resolution from a conversation that thread never had. Not loud loss: a record that
  **reads as a decision nobody made**, which is the one direction a memory tool must never fail. Now: id
  allocation happens **under the lock** (concurrent writers can never mint the same id); each row records the
  **writer** that opened it; `close` **appends** a status row instead of rewriting the file, so parallel
  writers cannot clobber each other and the store keeps who-closed-what-when; readers reconcile base rows
  with appended status rows.
- **New refusal (deliberate, and the one behavior that can now say no where it used to say yes):** closing a
  thread opened under a different writer label refuses, names the label and the override, and states its own
  limit — *"Labels are self-reported, never verified — this catches an ACCIDENTAL cross-session close, it is
  not a permission check."* Re-run with `--writer <label>` to do it on purpose. Writer identity is a
  **best-effort hint, never proof**; `--as` / `KEEL_WRITER` set it, and an absent label **never** gates
  anything (legacy rows close exactly as before). The already-closed message names the closer for forensics
  — `already closed by "sam" (self-reported at close)` — and where the closer is unknown it simply says
  `already closed` rather than inventing one.

### Mixed 1.5 / 1.6 installs (verified by execution, both directions)

Both shapes are readable by both versions and **no data is lost in either direction**, with one named
asymmetry: a **1.5 reader treats a thread that 1.6 closed as still open**, because 1.5 reads only the base
row's inline status and not the appended close. The consequence is that 1.5 **over-blocks** — the thread
keeps showing in `discuss list` and keeps gating `contract check`. It errs toward *"still being shaped,"*
never toward a settlement nobody made. A 1.5 `close` rewrites the store in place and **preserves** the rows
1.6 appended (unknown keys survive the round-trip); a 1.6 reader reconciles **both** shapes — legacy inline
statuses and appended status rows, last-wins — and degrades its forensics honestly on threads 1.5 closed.

Non-adopter output is **byte-identical** to 1.5.0: `rehydrate`, `status`, and `status --line` verified
unchanged on copies of six real projects. Every fix carries a permanent selftest assertion (77 total), each
verified to actually fail when its fix is removed.

## [1.5.0] — 2026-07-18

### Visibility + legibility overhaul (driven by a live field complaint + a from-scratch re-audit of 94 real sessions)
- **Presence-line fabrication → relay.** The `▸ keel …` line the agent shows you was being *hand-written* —
  a real session surfaced `Layer 6 active · ADR 0001 = single project (verified: 1 project live) ·
  dependencies supported`, none of which keel emits. `status --line` now carries the last captured record
  itself, so the agent **relays the tool's line verbatim** instead of inventing one. SKILL.md §0c: relay
  keel's signature line; never launder it through `head`/`tail`/`grep` (the field corpus did this 280+ times).
- **Speak the recorded THING, not keel's jargon (prose legibility).** A real-session audit found **5000+**
  raw `ADR N`/`checkpoint`/`Layer N` tokens spoken straight at users — the bigger half of "half of this is
  non-understandable", and it lives in the agent's *own prose*, which only doctrine reaches. SKILL.md §0c:
  name a captured thing by the **thing keel actually recorded** (its title), not the `ADR N` handle and not a
  paraphrase (which drifts); keep the handle only when actionable; **mirror the user's register**. Titles are
  now robust — a decision with no `# ` heading de-slugs its filename instead of showing the raw slug.
- **"keel updated" signal, on ANY command (staleness + mid-session reach).** A session loads keel's doctrine
  **once** and won't act on new behavior until `/keel` is re-invoked — and nothing told you it changed. keel
  now stores a `.last_seen` marker and, when the install moves past it, says so **once** ("keel updated X → Y
  … re-invoke /keel") — on rehydrate, on `status`, and on the next capture command (the field case: an update
  pushed mid-session that never surfaced). `status --line` carries a compact `⟳ X→Y` token. First run on an
  install is **silent** (byte-identical for non-adopters); `--version`/`--help` untouched.
- **Fresh-capture.** The presence line now says **✓ just saved: <record>** for anything written since the
  last presence (keel reporting a capture the turn *after* it lands), reverting to **last:** once reported.
- **Legibility.** `phase X/Y` → plain `X/Y steps done`; the panel's cryptic `[x][~][ ]` roadmap glyph bar →
  plain `X/Y done · on now: #k title` (the 1.4.1 contradiction-honesty signal is independent of the bar, so
  it survives); the presence line dropped its agent-facing command trailer (confused users when relayed);
  journals show their **heading title**, not the `-slug.md` filename.
- **Lingering discuss threads** now show a quiet `(open Nd)` age past a 2-day threshold — same-session
  threads stay clean, so it never cries wolf.

rehydrate/round-trip stays **byte-identical** on every real project tested (one intended exception: a
decision whose title was a raw filename slug now reads as words). The invisible path is untouched; only the
surfaces you see got better. Every fix carries a permanent selftest assertion.

## [1.4.2] — 2026-07-18

### Fixed (CRITICAL — silent memory loss, found by a field audit of real sessions)
- **cwd/ROOT anchoring.** `docs.py` used `ROOT = os.getcwd()` with no anchor, so if the shell drifted (a
  chained `cd` in a long session) keel silently wrote a project's memory into the wrong place — a stray
  subdirectory, or (observed in the wild) into keel's **own install dir**, so the project got **zero durable
  memory** and the shared install got polluted, with no error and a cheerful `✅ clean` every time. Now:
  `ROOT` resolves to the nearest ancestor holding a `.keel/` marker (a subdir drift lands on the real
  project), honors an explicit `KEEL_ROOT` env override, and `docs.py` **refuses to run inside keel's own
  install dir** (the catastrophic case) with a clear, actionable message. Byte-identical when run from a real
  project root. **Absolute-invocation examples everywhere** (the mine showed 87% of real sessions copied the
  old relative `python3 scripts/docs.py` example, which is what forced the `cd` into the skill dir).
  Safety rails, hardened by an adversarial audit: the refusal keys on the canonical **install area
  (`~/.claude/skills`)** — realpath'd, checked against the *resolved* root — so it can't be defeated by a
  `/var`↔`/private` symlink, a **vendored/dev copy** of `docs.py` inside a real project stays usable, and an
  explicit `KEEL_ROOT` is a **genuine escape from anywhere**. The ancestor search **never anchors at/above
  `$HOME`** (a stray `~/.keel` can't merge projects) and **announces** when it climbs to an ancestor's
  `.keel` (a stray marker in a shared parent like `~/code` is visible, never silent). `KEEL_ROOT` at a
  nonexistent path fails loud. And `--content`/`--from` are **never discarded** by a positional note (the
  positional becomes the label).
- **No more silent capture loss.** `journal`/`decision` now accept a bare positional note
  (`docs.py journal "what happened"`, title auto-derived) so the common shape can't fail for lack of
  `--title`. Doctrine added: **never silence keel's stderr (`2>/dev/null`) or assume a capture landed** —
  that exact combination lost 4 load-bearing records in the field.
- **Absolute-path invocation doctrine** (SKILL.md Standing defaults): always run keel by absolute path from
  the project root; never `cd` into the skill dir.

### Compatibility
- **Byte-identical to 1.4.1 when run from a real project root** (proven on two real repos across
  rehydrate/contract/status). The only behavior changes are the three fixes above. Selftest-locked (cwd
  anchor climbs to the ancestor `.keel`, returns cwd for a fresh project, honors `KEEL_ROOT`; positional
  journal derives a title).

## [1.4.1] — 2026-07-18

### Fixed (`status` was a facade where it promised a lie-detector — caught by a UX dogfood on real state)
- **The self-contradiction now shows.** A checkpoint left `undecided` while carrying a recorded choice (the
  "roadmap lies live" bug) rendered as a plain `[ ]` in the `status` bar — **indistinguishable from "not
  started."** A blind agent reading it concluded "haven't started 4 or 5 yet," which was flatly wrong (both
  were built + verified). It now renders as `[!]` with a legend, plus a **NEEDS RECONCILING** section that
  lists every integrity issue with a count.
- **"verify: pass" no longer falsely reassures.** When the deliverable tracker points at a dir that doesn't
  exist (staleness net inert), the line now reads `pass  ⚠ but tracker INERT … this "pass" can never go
  stale` instead of a bare "pass."
- **`status` surfaces its health count; the footer is dynamic** (`NEEDS RECONCILING (N)` + "fixes: rehydrate"
  vs "✓ no integrity issues") instead of a static line, and **`status --line` carries a `⚠N` marker** so the
  one-liner can never look clean while integrity signals wait.
- **Truncation now shows `…`** so a clipped tail reads as "more here," not as a bug/data-loss.

### Compatibility
- `rehydrate` and every other command **byte-identical to 1.4.0** (only `status` changed — proven on two
  real projects). The health signals reuse the same detectors `rehydrate` uses (no parallel source of truth),
  and are cry-wolf-safe (a consistent roadmap reports nothing). Locked by new `selftest.py` assertions.

## [1.4.0] — 2026-07-17

### Added (visibility — you can now SEE keel is running and what it captured)
- **`docs.py status`** — a clean, glanceable panel of what keel HAS and what's OPEN for this project:
  *in-memory* (decisions · journal · roadmap phases with "you are here" · open asks) and *open-now*
  (discuss threads · escalations · stance · contract · verify). Always recomputed from disk — a
  lie-detector, never a stored number. It is a pure **readout: it never gates** (exits 0 even under an
  active freeze, where `rehydrate`/`contract` still block). Answers "is keel even tracking anything? what's
  in memory?" **inline** — no more forking a chat to see project state (a fork is a stale snapshot).
- **`docs.py status --line`** — the one-line ambient form (`▸ keel · N in memory · 1 thread open`).
- **Visibility doctrine (SKILL.md §0c):** two dissociated surfaces — a compact **presence line** the agent
  surfaces on turns where keel actually captured something or has open/blocking state (naming only what's
  *contextually live*, silent on quiet turns — no manufactured noise), and the fuller **status panel**
  on-demand or after a heavier run/milestone. Fixes the #1 user complaint: "I can't tell keel is running or
  what it noted." Detection of "a heavy run" is agent judgment (keel can't see the conversation); `status`
  supplies the facts.

### Compatibility
- **Purely additive.** `status` is a new command; every existing command is **byte-identical to 1.3.2**
  (proven on two real projects). The presence line is agent doctrine, not a change to any command's output.
  Validated by a blind-agent battery: silent on quiet turns · inline (never forks) on "what's tracked?" ·
  helpful (non-noisy) on capture turns. Selftest-locked, including that `status` never gates.

## [1.3.2] — 2026-07-17

### Added (integrity advisories — keel now catches when it was silently wrong about your project)
- **Roadmap self-contradiction detector.** `rehydrate` flags any checkpoint left `undecided` that already
  carries a recorded choice — the "roadmap lies live" symptom (a status write dropped, e.g. lost from an
  `&&` chain when an earlier command exited non-zero). Advisory, never blocking; precise by construction
  (undecided + has-choice), so no cry-wolf. Caught a real instance on a live project's roadmap.
- **Deliverable-tracker health.** If a `verify` workflow tracks a deliverable dir that doesn't exist, its
  staleness net is silently inert (the hash is empty both sides). `rehydrate` now flags this — but ONLY when
  a verify stamp exists, so a project not using verify is never nagged. New `docs.py deliverables [dir …]`
  shows/sets which dirs `verify` watches (default `data/`), so you can point it at your real output.
- **Multi-part fidelity for Discussion Mode.** `discuss open --thread A --thread B …` is repeatable — one
  call arms every part of a multi-part input as a set, and the build stays gated until EACH is closed, so a
  numbered part can't quietly evaporate ("answered 3 things, only 1 got tracked"). The breakdown is still the
  agent's judgment (keel can't see the conversation); this makes it durable + gated, not automatic.

### Compatibility
- **Byte-identical to 1.3.1** for any project without a self-contradicting roadmap and without a verify-tracked
  missing dir — proven on real projects (one byte-identical, one where both detectors correctly surfaced real
  latent bugs). Additive advisories only; nothing new blocks. Each behavior locked by a `selftest.py`
  assertion, including cry-wolf guards (a consistent roadmap and a non-verify project stay silent).

## [1.3.1] — 2026-07-17

### Fixed (honesty pass — three behaviors the code didn't actually do, found by a claims-vs-code audit)
- **`livetest reject` now keeps `verify done` blocked.** A user-rejected live test set state `rejected`, but
  `verify done` only checked `handed_off` — so a deliverable the user called broken could still pass "done".
  Now a rejected live test blocks done until you fix it, re-arm, and earn a fresh `livetest confirm`. The
  flagship "self-certification is banned" is now true on the reject path, not only while a test is pending.
- **`route check` is genuinely advisory now (exit 0).** It called `sys.exit(1)` while SKILL.md and its own
  output promise "detects + surfaces, never blocks" — and keel can't act on it anyway (it cannot switch the
  harness model). It now surfaces mis-routed items just as loudly and exits 0; nothing downstream can be
  gated by it.
- **Freeze doc corrected to what freeze actually gates.** SKILL.md claimed a freeze blocks "builds, edits,
  ops, or doc landings"; in reality it hard-gates `contract check` (builds) and `hydrate` (memory landings)
  and stages drafts — it cannot stop a raw `Write`/`Edit` (no gate can). The doctrine and the rehydrate
  freeze banner now say exactly that.
- **Stale README version badge** (showed 1.2.0 since the 1.3.0 release) corrected.

### Compatibility
- **Byte-identical to 1.3.0** for anyone who doesn't hit a rejected live test, a flagged route check, or an
  active freeze — proven on live keel state from two real projects. Each behavioral fix is locked by a
  permanent `selftest.py` assertion (a rejected live test blocks done · a confirmed one unblocks · route
  check stays advisory).

## [1.3.0] — 2026-07-17

### Added
- **Discussion Mode** (`docs.py discuss open/close/list`) — §0a's decompose-before-execute reflex,
  generalized to ANY point in a session. When an input is *outcome-shaping* (changes what gets built, whose
  call it is, or adds a new direction/idea/question), keel arms a discussion thread and shapes it WITH the
  user through cascading, steelmanned either/or choices before building on it — **augmentation, not
  automation**: the goal of an option round is the user's *clarity*, not their selection, and the free text
  a user attaches to a pick is treated as the payload (its own tracked thread), never a dropped footnote.
  Narrow-technical forks are resolved and stated, never turned into ceremony.
- **Teeth at the build moment, and only there.** `contract check` refuses while any discussion thread is
  open (exit 1, naming them); `rehydrate` surfaces open threads **advisory-only** (orientation, not
  obstruction). Exit is **per-thread** — a converged thread closes immediately (`discuss close <id>
  [--choice "..."] [--to-decision "<title>"]`, promotable to a durable ADR) while others stay open; a
  settled thread is never re-asked. Detection is doctrine (SKILL.md §0b) — the CLI can't see the
  conversation; arming is the agent's reflex.

### Compatibility
- **Purely additive.** `discuss` is a new command; with no open thread, `rehydrate` and `contract check`
  are **byte-identical to 1.2.0** — proven on live keel state from two real projects. A user who never opens
  a discussion thread sees zero change. Grounded in a blind-model battery (arm on outcome-shaping · stay
  silent on narrow-technical · harvest the attachment) + full-lifecycle sandbox + selftest locks.

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
