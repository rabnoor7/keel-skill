# keel — a disciplined engineering partner (Claude Code skill)

keel is a Claude Code skill for building and evolving software of any kind — web apps, data pipelines,
scraping/automation, CLI tools, ML. It maps before it writes, clarifies before it codes, and verifies
before it claims "done." It keeps durable, per-project memory so you don't re-explain decisions across
sessions.

The invariants that must not drift live in code (`scripts/docs.py`), not in prose — `SKILL.md` is a thin
router that the CLI enforces.

## Install

**Option A — ask Claude Code (recommended).** Drop this `keel-skill/` folder into a Claude Code session and say:
*"install this keel skill."* Claude copies it into `~/.claude/skills/keel` and shows you a one-time
introduction. (`INSTALL.md` is the instruction file Claude follows.)

**Option B — command line.**
```bash
./install.sh          # copies to ~/.claude/skills/keel and prints the intro
```
or manually: `cp -R keel-skill ~/.claude/skills/keel`

Requirements: Python 3 (standard library only). Nothing to `pip install`.

## Use it

Start any session by describing what you want to build or change. On an existing project, say "rehydrate"
(or just start) and keel loads your `docs/` memory first — it reads YOUR layout (README/CLAUDE/AGENTS
anchors, `adr/` folders, single-file `DECISIONS.md` logs) without forcing its own. See every command with:
```bash
python3 ~/.claude/skills/keel/scripts/docs.py --help     # docs.py --version prints the installed version
```

## What's new in 1.1

- **Standing state that survives sessions** — `stance` (freeze / confirm-memory), `escalate`
  (BLOCKED-ON-USER checkpoints that become ADRs on resolution), `ask` (evidence-gated ask ledger in
  committed `docs/asks.md`).
- **Long-job durability** — `run` (per-item work ledger; resume exactly where a dead session left off),
  `sink` (durable capture inbox with dedup import; fetched data can never be silently disposed).
- **Recall & integrity** — `match` ("is this already decided?" at orient), `orphans` (dangling-reference
  check), honest decision digests (`[SUPERSEDED]` tags, nothing silently truncated), anchor pointer-rot
  detection, severity-split rehydrate (blocking vs advisory + a corrective-actions footer; `--full` shows
  everything).
- **Quality gates** — `preserve` (edit-not-regenerate proof), `accept` (typed definition-of-done),
  `coverage` (did the output address every point of a source?), `critique` (assumption/research/alternatives
  gate on big plans), `smoke` (tiny sample before an expensive run), `livetest` (human live-test lane —
  self-certification banned), `route` (task-class → model policy, advisory).
- **Multi-worktree** — `handoff`: an append-only channel all git worktrees of a repo share (same-machine).

## Platform & privacy notes

- **Windows**: supported with one degradation — whiteboard posts skip file locking (`fcntl` is Unix-only);
  everything else works.
- **Privacy**: everything keel writes stays on your machine. `.keel/` (private state, auto-gitignored)
  holds captured `sink` payloads in plaintext — treat scraped/PII data accordingly. `docs.py feedback`
  writes only to your own `~/.claude/keel/feedback.jsonl`; nothing is ever transmitted anywhere.

## Share it

Zip the folder and send it — the recipient installs it the same way:
```bash
zip -r keel-skill.zip keel-skill -x '*/.git/*' '*/.introduced' '*/__pycache__/*' '*/.DS_Store'
```
The one-time intro fires fresh on the recipient's machine: the `.introduced` marker is per-install and
never travels in the zip.

## What's inside

- `SKILL.md` — the router (thin; the CLI holds the invariants)
- `scripts/docs.py` — the deterministic memory + enforcement CLI
- `scripts/selftest.py` — regression tests (`python3 scripts/selftest.py`)
- `profiles/`, `profiles/web-app.d/` — per-domain playbooks, loaded on demand
- `modes/` — task-type playbooks (scaffold · add-feature · debug · upgrade-migrate · refactor)
- `references/` — memory / verify / orchestrate deep-dives
- `VALIDATION.md` — the dogfood harness
- `INSTALL.md` — install instructions Claude Code follows
