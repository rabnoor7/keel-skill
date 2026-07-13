# CLI Tool

## Survey
- **Invocation & flags/args** — what's the command shape? Positional args vs flags, required vs
  optional, short and long forms?
- **Input sources** — args, stdin, config file, env vars — which, and what wins when more than
  one is set?
- **Output shape & exit-code contract** — what goes to stdout (the payload) vs stderr
  (diagnostics)? What does exit 0 vs each non-zero code mean, precisely?
- **Side-effects & idempotency** — does it write files, call the network, mutate state? Is running
  it twice safe?
- **Distribution** — pipx, single-file script, Homebrew, npm global — how will people actually
  install and run this?

## Build
- **argparse (or equivalent) with real help text.** `--help` is documentation, not an afterthought
  — every flag gets a description.
- **Never block on interactive stdin** unless that's the explicit point of the tool. A script
  piping into this command should never hang waiting on a prompt with no TTY attached.
- **Deterministic output.** Same input, same output, byte for byte where reasonable — no
  timestamps or unstable ordering in normal output unless explicitly requested.
- **Safe by default.** Destructive operations (delete, overwrite, force-anything) require an
  explicit flag or confirmation; offer `--dry-run` so the effect can be seen before it's real.

## Verify
- **Golden-output tests.** Fixed (stdin/args) → expected (stdout, stderr, exit code) pairs,
  checked byte-for-byte or with an intentional, documented fuzz (e.g. timestamps).
- **Exit-code assertions** for both success and every documented failure mode — a tool that always
  exits 0 is unverifiable by any script that depends on it.
- **Idempotency check** — run twice, assert the second run's output/effect matches what the
  contract promised (unchanged, or a defined no-op message).
- **`--help` sanity** — it runs, exits 0, and documents every flag the tool accepts; a flag with no
  help text is a bug, not a nice-to-have.
- These are what `verify/audit.py` runs — golden cases plus exit-code checks, hard-gated, not a
  manual "I tried it and it looked right."
