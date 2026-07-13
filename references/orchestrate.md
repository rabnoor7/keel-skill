# Orchestrate — multi-agent work

Loaded only when this session delegates to other agents/sessions. A solo session never loads this
file — nothing here applies to one model doing its own work end to end.

## Manager / worker split

You (the capable model) DESIGN the task and VERIFY the output. Cheaper/faster models do the
expensive mechanical grunt: bulk extraction, repetitive edits across many files, running the same
transform N times. The split is about cost, not trust — grunt work is cheap to redo, judgment
is not.

**Never delegate judgment.** Anything that requires interpreting ambiguity, choosing between
tradeoffs, or deciding whether a result is actually correct stays with you. A worker that hits a
judgment call should surface it, not resolve it and move on.

## Verify every submission — field-level, before accepting

Never accept a worker's "done" or "N/N complete" at face value. Verify each submission against the
concrete spec you gave it, field by field. The canonical failure this guards against: a worker
reports "485/485 done," and every row's key fields are empty — the count was true, the work
wasn't. A matching row-count is not evidence of correctness; it's evidence the loop terminated.
Same rule as `references/verify.md`, applied to a worker's output instead of a final deliverable —
never rubber-stamp a submission because the summary sounds finished.

## Coordination: append-only, not shared-editable

Parallelize freely — running workers concurrently is where the throughput comes from. Parallel
roles coordinate through two primitives, both provided because "just share a file" races:

- **Whiteboard** — `docs.py whiteboard post <role> <note>` is an atomic append. Agents post
  progress/findings there; nobody edits another agent's entry. A shared editable file (two agents
  writing the same doc) races by construction — last write wins, first write vanishes.
- **Claims** — `docs.py claim <resource>` fails immediately if the resource (a file, a browser
  tab, an id range, an API budget) is already held. Claim before touching, release when done. This
  is how two agents avoid clobbering the same target — coordination by construction, not by
  agents remembering to check with each other first.

## Model tier and cost

State the tradeoff plainly when you choose it: cheap/fast models for grunt (high volume, low
judgment, cheap to verify after the fact); the capable model for design and verification (low
volume, high judgment, expensive to redo if wrong). Spending capable-model time on grunt work is
waste; spending cheap-model time on judgment calls is how you get the 485/485-empty-fields
failure.

## Resumability (universal — not just multi-agent)

Any long-running batch, solo or delegated, follows the same rule:

- Save incrementally, after every batch — not once at the end.
- A stop (crash, interrupt, rate limit) never loses completed work.
- Resume is idempotent: skip what's already done, don't redo it, don't duplicate it.
- Never dispose of fetched or costly-to-reacquire data because a run was interrupted — merge
  partial results into the master output. A half-finished run still owes you everything it
  finished.
