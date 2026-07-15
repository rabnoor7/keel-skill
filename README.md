# keel

### Bring the goal you can't break down. Leave with the plan *you chose*.

![version](https://img.shields.io/badge/version-1.2.0-1f6feb)
![python](https://img.shields.io/badge/python-3%20(stdlib%20only)-1f6feb)
![self-tested](https://img.shields.io/badge/self--tested-passing-2ea043)
![license](https://img.shields.io/badge/license-MIT-2ea043)

keel is a [Claude Code](https://claude.com/claude-code) skill that turns Claude into a disciplined partner
instead of a vending machine. Tell it a big fuzzy outcome — *build my personal brand, reach 1,000 people,
launch the thing* — and instead of diving in and guessing, it **decomposes the outcome into checkpoints you
steer**, one plain choice at a time. You reach *exactly* what you wanted — aligned — without burning a
fortune flailing your way to clarity.

Works for goal-shaped projects **and** software of any kind (web apps, data pipelines, automation, CLI, ML).
Pure Python 3, standard library only. Nothing to `pip install`.

---

## It won't dive in and guess

Type a fuzzy goal into an AI and it eagerly builds *something* — silently skipping the load-bearing
decisions you hadn't made yet, because they weren't clear in your head either. You get a partial, misaligned
result, you test, you redo, and *only then* do you find out what you actually meant.

keel refuses to execute a fuzzy outcome. It's a hard stop — an **exit code, not a polite suggestion:**

```console
$ docs.py contract check
✗ OUTCOME NOT DECOMPOSED — "build my personal brand" has 0 checkpoints.
  A fuzzy outcome must be broken into aligned checkpoints before any build.
```

Then it breaks the goal into its real layers and surfaces the decisions you didn't know were decisions — as
plain either/or choices, each argued at its strongest, so *you* shape the result.

---

## Clarity is the cheapest thing you'll ever buy

The expensive way to find out what you actually wanted is to build the wrong thing first. Deciding up front
costs a few questions. Discovering it halfway through costs the whole detour — and every token spent on it.

| Without decomposition | With keel |
|---|---|
| type a fuzzy goal → AI builds *something* → "oh, not that" → redo → repeat | decompose → decide each checkpoint → aligned → build **once** |
| you flail your way to clarity, paying for every wrong turn | clarity first; a new idea lands on a checkpoint, not another redo |
| the AI silently made the calls you never saw | you make the calls that shape the project — deliberately |

**Same destination. A fraction of the wandering — and the token bill that comes with it.**

---

## See it work

Open any session and keel tells you where you are and the one thing to decide next. The course lives in a
plain file you own — close the tab, switch machines, come back in a month; the map and every decision are
still there. This is real output:

```console
$ docs.py rehydrate
--- ROADMAP: build my personal brand on social media ---
   [x] 1. positioning / niche      choice: micro-niche: career-transition tech pros
   [~] 2. target audience   <- YOU ARE HERE
                                    choice: mid-career engineers eyeing a pivot, on LinkedIn
   [ ] 3. content pillars
   [ ] 4. platform choice
   [ ] 5. cadence
   [ ] 6. metrics
   → next undecided checkpoint: #3 content pillars — align it before building on it
```

A pivotal choice — your niche, your positioning — can be promoted to a permanent, searchable record, so you
(or the AI) never re-litigate it by accident.

---

## Who it's for

<table>
<tr>
<td width="33%" valign="top">

**If you don't write code**
*creators · founders · career-changers*

- **Beat the blank page** — a goal too big to start becomes questions you can answer today.
- **Decide like an expert without being one** — the calls amateurs get silently wrong become plain choices, each argued at its strongest.
- **Get what you *meant*** — aligned to the project in your head, not a guess at it.

</td>
<td width="33%" valign="top">

**If you do write code**
*engineers · data & ML · solo devs*

- **"Done" that can't be faked** — unclaimable until a real check passes on the *current* deliverable.
- **Memory that outlives the context window** — a freeze you set Monday still blocks the build Thursday.
- **Long jobs resume, never restart** — a migration that dies at row 6,000 resumes at 6,001.

</td>
<td width="33%" valign="top">

**If you run agents at scale**
*power users · small teams*

- **A brain that travels** — git-committed markdown + a stdlib script, readable by any agent or a bare shell.
- **Parallel worktrees that can't race** — agents coordinate through an append-only channel.
- **Grunt runs cheap** — delegate bulk work to a smaller model, keep judgment on your lead (~⅓–½ cheaper on grunt-heavy runs).

</td>
</tr>
</table>

---

## What it is — and what it isn't

keel's whole soul is honesty over agreeableness. It would be off-brand to oversell on its own README, so
here's the straight version.

| ✓ What's real | ✕ What it isn't |
|---|---|
| **The gates have teeth** — a fuzzy outcome or a failed audit is a hard stop (an exit code), not a suggestion. | **Not an unbreakable cage** — the teeth bite when work routes through the tool; a raw edit can still go around it. |
| **The memory and checks are portable** — plain markdown + a zero-dependency script run under any agent, or none. | **Not turnkey on every AI yet** — the memory travels everywhere; the discipline needs a one-file adapter per harness, and cost-routing is Claude-aware today. |
| **It's discipline, written down and enforced** — nothing hides in a vendor's black box. | **Not a strategist that thinks for you** — it surfaces the decisions and the tradeoffs; the choices stay yours. |

---

## Your first session, in 30 seconds

1. **Install** (below) — keel greets you once, then stays quiet.
2. **Say the goal** — fuzzy is fine. It reads your project first, or starts clean without inventing structure you didn't ask for.
3. **Steer the checkpoints** — it breaks the outcome into layers and asks you the shaping choices, in plain language. No code until you've approved the plan.
4. **Build, aligned** — only now does it build, against a plan you chose; it verifies the real deliverable before "done," and remembers every decision next session.

## Install

**Ask Claude Code (recommended).** Drop this `keel-skill` folder into a Claude Code session and say:
*"install this keel skill."* Claude copies it to `~/.claude/skills/keel` and shows the one-time intro.

**Or from the command line:**
```bash
./install.sh                      # → ~/.claude/skills/keel + prints the intro
```
Check the version anytime: `python3 ~/.claude/skills/keel/scripts/docs.py --version`.
Requirements: Python 3 (standard library only).

---

## How it holds the line

keel's premise is that a model **will** forget, drift, and rationalize under pressure — so the invariants
that must not drift live in deterministic code (`scripts/docs.py`), enforced by exit codes, not in prose the
model can talk past. `SKILL.md` is a thin router; the CLI is the law. It ships with its own regression tests
(`python3 scripts/selftest.py`). The full doctrine is in [`SKILL.md`](SKILL.md) and [`references/`](references/).

**What's inside** — `SKILL.md` (the router) · `scripts/docs.py` (the memory + enforcement CLI) ·
`scripts/selftest.py` (regression tests) · `profiles/` (per-domain playbooks, incl. `general` for non-code
outcomes) · `modes/` (task playbooks) · `references/` (deep-dives) · [`CHANGELOG.md`](CHANGELOG.md) · `VERSION`.

## Platform & privacy

- **Windows**: supported with one degradation — whiteboard posts skip file locking (`fcntl` is Unix-only); everything else works.
- **Privacy**: everything keel writes stays on your machine. `.keel/` (private state, auto-gitignored) holds captured payloads in plaintext — treat scraped/PII data accordingly. `docs.py feedback` writes only to your own `~/.claude/keel/feedback.jsonl`; nothing is ever transmitted.

## Share it

```bash
zip -r keel-skill.zip keel-skill -x '*/.git/*' '*/.introduced' '*/__pycache__/*' '*/.DS_Store'
```
The one-time intro fires fresh on the recipient's machine — the `.introduced` marker is per-install and never travels in the zip.

## License

[MIT](LICENSE) — use it, fork it, ship it.
