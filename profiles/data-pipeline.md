# Data Pipeline

Read → derive → write, at whatever volume. Storage-agnostic by default — the pipeline shape
matters more than the stack.

## Survey
- **I/O contracts** — what shape is the source (API, file, DB, stream)? What shape must the sink
  be? Get concrete field lists, not "whatever comes back."
- **Storage choice** — relational, columnar, object storage, or none (stream-through)? Don't
  default to Postgres; pick for the access pattern — analytics scan, point lookup, and archive
  each want something different.
- **Schema & data-quality expectations** — required fields, allowed nulls, valid ranges/enums,
  uniqueness constraints. Written down before the first run, not reverse-engineered after a bad
  one.
- **Idempotency & resumability** — can this re-run safely on partial failure? What's the resume
  point — offset, cursor, watermark, last-id?
- **Volume & throughput** — rows/files/GB now and at 10x; does it fit in memory, or does it need
  to stream/chunk?

## Build
- **Pure read → derive → write.** Derivation logic is separable from I/O so it can be tested
  without touching the real source or sink.
- **Idempotent and checkpointed.** Re-running must not double-count, double-append, or corrupt
  state. Persist a checkpoint (last offset/id/batch) after every unit of work, not at the end.
- **Incremental save, never one end-of-run write.** A crash at row 90,000 of 100,000 should cost
  10,000 rows of rework, not 100,000.
- **Never dispose of the source or fetched data.** Merge partials, don't overwrite — a re-fetch is
  expensive and sometimes impossible (rate limits, upstream records since deleted).

## Verify
Verification is **data-quality assertions**, not a run log. Explicitly NOT verification: "N rows
saved," "the file exists," "it has some value in it." This is what `verify/audit.py` should
assert, hard-gated — **exits non-zero on any failure**:
- **Schema conformance** — every row matches the declared types/enums/required fields.
- **Null/empty rates per FIELD**, not aggregate row counts — a field that's 40% empty is a defect
  even when the row count looks fine.
- **Row-count deltas** — source count vs sink count, reconciled and explained (filtered? deduped?
  failed?), not just "some rows arrived."
- **Dedup and orphan checks** — no unintended duplicate keys; no foreign references pointing at
  rows that don't exist.
- **Cross-file/cross-table integrity** — when derived data spans multiple outputs, they must agree
  with each other, not just each look fine in isolation.
- **Provenance for every derived field** — a pointer back to the source record it came from. A
  derived value with no source pointer is fabricated until proven otherwise.
