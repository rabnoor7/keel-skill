# Automation — browser automation, scraping, RPA

## Survey
- **Target & access** — is this the user's own authenticated session, or public data? Never
  assume; ask. This decides both the technical approach and the legal posture.
- **What data** — exact fields, not "everything on the page."
- **Session & auth persistence** — how does login survive across runs (cookies, device ID, storage
  state)? A fresh session every run looks like an attack to the target site.
- **Rate limits** — does the target publish one? If not, it gets measured (Build), never guessed.
- **Selectors vs endpoints** — check for the site's own JSON API (network tab) before writing a
  DOM scraper. An API is faster, more stable, and less likely to trip detection than replaying
  clicks.
- **Legal/ToS posture** — flag it; whether to proceed is the user's call, not something to
  silently decide either way.

## Build
- **Flakiness is the central problem, not an edge case.** Non-determinism — timing, layout drift,
  transient blocks — is the default state of the web, so retries, explicit waits, and
  idempotent/resumable steps are load-bearing, not polish.
- **Checkpoint every batch.** A run that dies at item 400 of 1,000 resumes at 400 — it doesn't
  restart or lose the first 400.
- **Measure the real rate limit on a small sample before scaling.** Don't inherit a number from
  another project or guess a conservative-sounding round one — run a small batch, watch for
  throttling or blocks, derive the actual ceiling.
- **Stay under the measured limit; stop-and-resume on a block signal rather than evading it** —
  rotating IPs or identities to dodge a limit turns a slowdown into a ban.
- **One active session, reused.** A new or background tab often trips bot-checks that a
  continuously-used foreground session doesn't; don't parallelize by spawning tabs unless you've
  confirmed that's safe for this target.

## Verify
- **Re-fetch a sample and diff against stored data** — the authenticity check. Scraped/API data
  can drift, be cached stale, or be silently fabricated by a subagent; a live re-check against a
  sample is the only thing that catches that.
- **Captured-count vs true-count**, not "has any." If the target claims 1,240 items and 300 were
  captured, that's a 76% miss, not a success with a caveat.
- **Field-level completeness** — per-field fill rate on the captured set; a record with 3 of 10
  fields populated is a partial capture, not a captured record.
- Wire the above into `verify/audit.py` as a hard-gated, non-zero-exit check — a scrape that
  "completed" without tripping an error is not the same claim as a scrape that was verified.
