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
(or just start) and keel loads your `docs/` memory first. See every command with:
```bash
python3 ~/.claude/skills/keel/scripts/docs.py --help
```

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
