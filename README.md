# keel

**Claude that remembers your project, refuses to fake "done," and picks up exactly where it left off.**

![version](https://img.shields.io/badge/version-1.1.0-1f6feb)
![python](https://img.shields.io/badge/python-3%20(stdlib%20only)-1f6feb)
![self-tested](https://img.shields.io/badge/self--tested-passing-2ea043)
![skill](https://img.shields.io/badge/Claude%20Code-skill-8957e5)
![license](https://img.shields.io/badge/license-MIT-2ea043)

keel is a [Claude Code](https://claude.com/claude-code) skill that turns Claude into a disciplined
engineering partner instead of a code vending machine. It maps before it writes, clarifies before it
codes, and verifies before it claims done — and it keeps durable, per-project memory so you never
re-explain your work across sessions.

Works for any kind of software — web apps, data pipelines, scraping/automation, CLI tools, ML. Pure
Python 3, standard library only. Nothing to `pip install`.

---

## The problem it kills

Working with an AI over a real project, three things go wrong on repeat:

1. **It forgets.** Every new session, you re-explain the architecture, the decisions, the "we already tried that."
2. **It says "done" when it isn't.** It trusts its own summary instead of checking the actual output.
3. **It loses your work.** A long job — a scrape, a migration, a batch — dies halfway, and there's no way back but from zero.

keel fixes all three, deterministically. The rules that matter live in a small Python CLI that **fails
loudly** — not in prose the model can forget under pressure.

| | Plain Claude | Claude **+ keel** |
|---|---|---|
| **New session** | You re-explain the project | It reads your `docs/` memory first |
| **"Done"** | Trusts its own word | Blocked until a real audit passes |
| **A job dies mid-run** | Restart from zero | Resume exactly where it stopped |
| **A decision you reversed** | May rebuild on stale context | Flagged *before* you build |

---

## See it work

On an existing project, keel opens every session by reading your memory and **failing loudly on anything
that would make the next step wrong.** This is real output — a repo where a decision was reversed in a
note but the ADR still says the old thing, and a batch job was interrupted:

```console
$ python3 ~/.claude/skills/keel/scripts/docs.py rehydrate
======================================================================
KEEL REHYDRATE — digest across all tiers  (keel 1.1.0)
======================================================================

PROFILE: data-pipeline

--- ANCHOR (docs/architecture.md) ---
# Architecture — Lead enrichment pipeline (REHYDRATION ANCHOR)
## What this is
Scrape brand pages, enrich with founder + contact data, export a clean CSV.

--- DOCS INVENTORY: 3 doc(s) — nothing silently skipped ---
   [anchor] docs/architecture.md
   [decisions] 2 · [journal] 0

--- DECISIONS: 2 ADR(s) ---
   0001 — Store leads in a single master.csv
   0002 — Enrich founders via the public web API

[!!] CONTRADICTIONS — 1 lower-tier correction(s) supersede an unmarked ADR:
    ADR 1: memory/correction.md says "…this supersedes ADR 1 — we moved to sqlite…"
    → do NOT act on the stale ADR. Resolve with `docs.py supersede 1` first.

[!] RUN MID-FLIGHT — r8a8c "enrich": 2/4 done, 2 pending, last mark 0m ago
    → resume where it left off: docs.py run resume r8a8c   (do NOT restart from 0)

--- CORRECTIVE ACTIONS (1 blocking · 1 advisory) ---
  [B1] 1 live contradiction(s) — an unmarked ADR is superseded
       → docs.py supersede 1 --title "..."
  [A1] run r8a8c mid-flight: 2/4 done, 2 pending
       → docs.py run resume r8a8c

======================================================================
VERDICT: ⛔ 1 BLOCKING issue(s) — do not build on this state. (1 advisory.)
```

A blank digest means you're clear to build. A blocking issue means the next thing you'd do is based on a
lie — and keel stops you *before* you do it.

---

## Your first session, in 30 seconds

1. **Install it** (below) — keel greets you once, then stays quiet.
2. **Say what you want to build or change.** keel loads your project memory first — or, on a brand-new
   project, starts clean without inventing structure you didn't ask for.
3. **It asks 2–3 plain questions**, then shows you a **build contract** (files, edge-cases, what it will
   *not* do). No code is written until you approve it.
4. **It builds, then verifies the real deliverable** — not its own claim. "Done" is unclaimable until a
   fresh audit actually passes.
5. **Decisions land in `docs/`** as it works. Next session, keel already knows them — and won't let a
   later note silently contradict an earlier decision.

---

## Install

**Ask Claude Code (recommended).** Drop this `keel-skill` folder into a Claude Code session and say:
*"install this keel skill."* Claude copies it to `~/.claude/skills/keel` and shows the one-time intro.

**Or from the command line:**
```bash
./install.sh                      # copies to ~/.claude/skills/keel + prints the intro
```
Then start any session by describing your work, or say **"rehydrate."** Check the version anytime with
`python3 ~/.claude/skills/keel/scripts/docs.py --version`.

Requirements: Python 3 (standard library only).

---

## What you get

**Never re-explain your project.** Committed, human-readable memory (`docs/` — an architecture anchor,
decision records, a journal) that keel reads first, every session. It adapts to *your* layout — README /
CLAUDE / AGENTS anchors, `adr/` folders, single-file `DECISIONS.md` logs — instead of forcing its own.

**Never build on a lie.** Deterministic checks run on every rehydrate and fail loudly: cross-tier
contradictions, a decision reversed but not marked, a stale anchor, dangling references, an audit that
never passed. Blocking issues stop a build; advisories just get surfaced.

**Never fake "done."** The build gate refuses code until you approve a contract; the verify gate refuses
"done" until a real audit passes over the *current* deliverable — and for things only a human can judge
(UI, live flows), it hands off and waits for your verdict instead of self-certifying.

**Never lose a long job.** A per-item work ledger resumes exactly where a dead session stopped; a durable
capture inbox means fetched data can't be silently discarded.

**Never forget what you decided.** Standing state survives sessions and context resets — a freeze stays
frozen, an unanswered escalation stays blocking, a recurring ask stays loud — until *you* clear it.

See every command: `python3 ~/.claude/skills/keel/scripts/docs.py --help` · full list in
[`CHANGELOG.md`](CHANGELOG.md).

---

## How it holds the line

keel's premise is that a model **will** forget, drift, and rationalize under pressure — so the invariants
that must not drift live in deterministic code (`scripts/docs.py`), enforced by exit codes, not in prose
the model can talk past. `SKILL.md` is a thin router; the CLI is the law. It ships with its own
regression tests (`python3 scripts/selftest.py`).

The full doctrine — the loop, the memory model, the gates — is in [`SKILL.md`](SKILL.md) and
[`references/`](references/).

---

## What's inside

- `SKILL.md` — the router (thin; the CLI holds the invariants)
- `scripts/docs.py` — the deterministic memory + enforcement CLI
- `scripts/selftest.py` — regression tests
- `profiles/`, `profiles/web-app.d/` — per-domain playbooks, loaded on demand
- `modes/` — task-type playbooks (scaffold · add-feature · debug · upgrade-migrate · refactor)
- `references/` — memory / verify / orchestrate deep-dives
- `CHANGELOG.md` — what changed, per version · `VERSION` — the current version
- `INSTALL.md` — install steps Claude Code follows

---

## Share it

```bash
zip -r keel-skill.zip keel-skill -x '*/.git/*' '*/.introduced' '*/__pycache__/*' '*/.DS_Store'
```
The one-time intro fires fresh on the recipient's machine — the `.introduced` marker is per-install and
never travels in the zip.

---

## License

[MIT](LICENSE) — use it, fork it, ship it.
