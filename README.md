# keel

### Bring the goal you can't break down. Leave with the plan *you chose*.

![version](https://img.shields.io/badge/version-1.3.1-1f6feb)
![python](https://img.shields.io/badge/python-3%20(stdlib%20only)-1f6feb)
![self-tested](https://img.shields.io/badge/self--tested-passing-2ea043)
![license](https://img.shields.io/badge/license-MIT-2ea043)

keel is a [Claude Code](https://claude.com/claude-code) skill that turns Claude into a disciplined partner
instead of a vending machine. Tell it a big fuzzy outcome — *build my personal brand, reach 1,000 people,
launch the thing* — and instead of diving in and guessing, it **decomposes the outcome into checkpoints you
steer**, one plain choice at a time. You reach *exactly* what you wanted, aligned — spending a fraction of
the tokens, trusting the "done," and able to pick it up in any session, on any machine, even in another AI.

Works for goal-shaped projects **and** software of any kind. Pure Python 3, standard library only.

---

## It won't dive in and guess

Type a fuzzy goal into an AI and it eagerly builds *something* — silently skipping the load-bearing
decisions you hadn't made yet, because they weren't clear in your head either. keel refuses. A fuzzy outcome
is a hard stop — an **exit code, not a polite suggestion:**

```console
$ docs.py contract check
✗ OUTCOME NOT DECOMPOSED — "build my personal brand" has 0 checkpoints.
```

Then it breaks the goal into its real layers and surfaces the decisions you didn't know were decisions — as
plain either/or choices, each argued at its strongest, so *you* shape the result. Open any session and it
tells you where you are and the one thing to decide next:

```console
$ docs.py rehydrate
--- ROADMAP: build my personal brand on social media ---
   [x] 1. positioning / niche      choice: micro-niche: career-transition tech pros
   [~] 2. target audience   <- YOU ARE HERE
                                    choice: mid-career engineers eyeing a pivot, on LinkedIn
   [ ] 3. content pillars     [ ] 4. platform     [ ] 5. cadence     [ ] 6. metrics
   → next undecided checkpoint: #3 content pillars — align it before building on it
```

---

## The token bill you don't see

The expensive way to find out what you actually wanted is to build the wrong thing first. keel saves tokens
two ways — and the big one costs you nothing to turn on:

**1. Clarity before flailing — for everyone.** Without decomposition you pay for every wrong turn:

| Without keel | With keel |
|---|---|
| fuzzy goal → AI builds *something* → "oh, not that" → redo → repeat | decompose → decide each checkpoint → aligned → build **once** |

You stop paying to *discover* what you meant halfway through. New ideas land on a checkpoint, not another
full redo. **Same destination, a fraction of the wandering.**

**2. Grunt runs on a cheaper model — if you run agents.** Declare your lead model; keel keeps judgment,
orchestration, and verification on it and pushes bulk work (scraping, extraction, repetitive edits) down to
a smaller one, with the lead judging the result. Where the price gap is ~5:1, that's **roughly a third to a
half off on grunt-heavy runs.** (Honest: it's *advisory* — keel names what to delegate; it can't switch the
model for you, and the ladder is Claude-aware today.)

---

## Trust the "done"

"Done" is the most abused word in AI — the "485/485 complete" where every field was empty. keel makes it
unclaimable until it's earned:

- **A real audit must pass on the *current* deliverable** — not because the model said so. It fails if the
  audit never ran, failed, or the thing changed since. Every bug you fix becomes a permanent regression check.
- **A claim with no source fails as fabrication.** Derived data without provenance doesn't pass.
- **What only *you* can judge, you judge** — for a UI or a live flow, it hands off and waits for your verdict
  instead of self-certifying.
- **What you decided *stays* decided** — a freeze you set Monday still blocks the build Thursday, after the
  context window is long gone; an unanswered "should I?" stays blocking until you answer it.

---

## Pick it up anywhere — sessions, machines, even other AIs

Your project's brain is committed **markdown** in `docs/`; the checks are a **stdlib Python script**. Nothing
lives in a vendor's black box, so it goes wherever you do:

- **Across sessions** — close the tab; the next one runs `rehydrate`, knows everything you decided, and
  refuses to build on a decision you already reversed.
- **Across machines & handoffs** — a teammate clones the repo, runs one command, and inherits the whole plan,
  the rationale, and "you are here" — no tribal-knowledge download.
- **Across parallel agents** — fan out worktree agents that coordinate through an append-only channel instead
  of clobbering a shared file.
- **Across AIs — honestly** — the memory *and* the checks read and run under any agent (Codex, Antigravity, a
  bare shell) or none. What travels turnkey: your data and the enforcement script. What needs a one-file
  adapter per harness: the *reflex* to obey the CLI. **The brain is portable; the discipline gets re-wired.**

---

## What it is — and what it isn't

keel's whole soul is honesty over agreeableness. Overselling on its own README would be off-brand:

| ✓ What's real | ✕ What it isn't |
|---|---|
| The gates have teeth — a fuzzy outcome or a failed audit is a hard stop (an exit code). | Not an unbreakable cage — teeth bite when work routes through the tool; a raw edit can go around it. |
| The memory and checks are portable — plain markdown + a zero-dependency script. | Not turnkey on every AI yet — the memory travels; the discipline needs a per-harness adapter. |
| It's discipline, written down and enforced — no vendor black box. | Not a strategist that thinks for you — it surfaces the decisions; the choices stay yours. |

---

## Your first session, in 30 seconds

1. **Install** — keel greets you once, then stays quiet.
2. **Say the goal** — fuzzy is fine. It reads your project first, or starts clean.
3. **Steer the checkpoints** — it breaks the outcome into layers and asks you the shaping choices, in plain language. No code until you approve the plan.
4. **Build, aligned** — only now does it build, verifies the real deliverable before "done," and remembers every decision next session.

```bash
./install.sh                      # → ~/.claude/skills/keel
python3 ~/.claude/skills/keel/scripts/docs.py --version   # keel 1.3.1
```
Requirements: Python 3 (standard library only).

---

**What's inside** — `SKILL.md` (the router) · `scripts/docs.py` (the memory + enforcement CLI) ·
`scripts/selftest.py` (regression tests) · `profiles/` (per-domain playbooks, incl. `general` for non-code
outcomes) · `modes/` · `references/` · [`CHANGELOG.md`](CHANGELOG.md) · `VERSION`.

**Platform & privacy** — Windows supported (whiteboard skips file-locking; everything else works). Everything
keel writes stays local; `.keel/` is auto-gitignored; `docs.py feedback` writes only to your own machine,
never transmitted.

**Share** — `zip -r keel-skill.zip keel-skill -x '*/.git/*' '*/.introduced' '*/__pycache__/*' '*/.DS_Store'`
· the one-time intro fires fresh on the recipient's machine.

## License
[MIT](LICENSE) — use it, fork it, ship it.
