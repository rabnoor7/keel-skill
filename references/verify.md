# Verify — checking a deliverable

Verify the deliverable, not the claim. "Done," "N/N complete," a green checkmark from a subagent —
none of these are evidence. Re-verify live: run the code, query the data, re-derive the count
yourself, even when the record says it already passed. A stale "verified" from three edits ago is
worse than no verification, because it's trusted.

## Field/spec level, not row-count

Verification means checking each field against a concrete spec — the schema, the contract, the
acceptance criteria — not confirming the right number of rows exist. Row-count is the weakest
signal that survives review: a table with 485 rows and every key field blank still counts as
"485." Write down what each field is supposed to contain, then check that — not just that the
field is present.

## Conformance vs veracity — two different questions

- **Conformance** — does this match the spec/schema? Shape, types, required fields, referential
  integrity. Deterministic, cheap, fully automatable: a script either finds the mismatch or it
  doesn't.
- **Veracity** — is it *true*? A record can be perfectly well-formed and still be a fabrication —
  conformance can't catch that, because it never looks outside the document itself. Veracity needs
  an external source to check against.

A generic "verify vs spec" only checks conformance, so it waves a well-formed lie straight through.
That gap is exactly where fabricated data hides.

## Provenance is the enforceable anti-fabrication check

For veracity, require **provenance**: every derived datum carries a source pointer — a URL, a
file+line, a query+timestamp, a citation. `docs.py verify` treats a row with no citation as
fabricated and fails it, full stop. This is deliberately mechanical: "does a source pointer exist"
is checkable by a script, "is this claim true" mostly isn't — so provenance is the closest thing to
an automatable veracity check there is. No provenance, no pass.

## The hard-gate pattern

Verification that lives in prose gets skipped under pressure — the same failure mode as everything
else this skill guards against. So it doesn't live in prose:

- `docs.py verify init` drops a real, runnable audit script into the project — not a checklist,
  code.
- `docs.py verify run` executes it and **exits non-zero on failure.** That exit code is the only
  form of "verified" that's reliable by construction — it can't be rubber-stamped, agreed with, or
  talked past.

Convert every verification step you'd otherwise describe in prose into a committed executable.
Prose is a suggestion the model can forget under pressure; an exit code is a gate.

## Applies beyond code

Data, reports, and research deliverables verify the same way: conformance (matches the requested
shape/fields) plus veracity (provenance per datum) plus a runnable check — not eyeballing output.
Where an independent oracle exists — an independent enumeration, a second source, a known total —
cross-check the deliverable against it instead of trusting the pipeline that produced it to also
grade itself.

## Vet a signal before you gate on it

Before any field, flag, or count becomes load-bearing — you're about to classify, gate, rank, or
branch on it — name its authoritative source and check it against at least 3 known-truth records,
including one where it should read FALSE. Convenient fields lie: a flag that's actually the
viewer's own account attribute (true for every record); a count that silently excludes
out-of-stock; a regex that matches boilerplate on 482 of 482 rows. Cheap, deterministic, and it
kills the whole class of "built on a lie."

## Model legitimate absence — don't cry wolf

A completeness/fill-rate gate must encode per-field expected-fill and legitimate-null conditions
plus a tier or segment dimension — never one blanket null threshold. A no-minimum record
legitimately has `min_order=0`; a 0-review record legitimately has no rating; a shallow/pending
tier row is PENDING, not FAIL. A gate that false-alarms on legitimate nulls trains the operator to
ignore it — exactly as dangerous as one that's too lax.

## "Done" needs a fresh passing check

The contract gates the start of a build; the same rigor has to gate the end. Nothing is done until
a real audit has actually run and passed on this version of the deliverable — re-verify live,
never on a claim. Keep the audit's checked field-set in sync with the data model too: a gate on a
stale/removed field, or a missing gate on a live one, is its own bug — one project's audit kept
gating fields that had already been moved out of scope. `docs.py verify run` + the done-gate +
`docs.py verify sync` enforce this.

## Every fixed bug becomes a permanent assertion

When you fix a defect, encode it as a named regression assertion in the project's audit so it
can't silently come back — e.g. after fixing a truncation-at-20 bug, assert every record with
count > N has >= N captured. Skip this and a later agent can reintroduce the exact bug you just
fixed. The audit is a ratchet, not a one-shot: it only ever gets stricter.
