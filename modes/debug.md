# Mode: debug (something is broken)

Here the map is **the chain of what could produce the symptom**, then isolation. You are not
interrogating the user about preferences — you're narrowing down a cause.

## Method

1. **Rehydrate** (`docs.py read --all`) for context, then **reproduce or pin the symptom
   precisely.** Define the failure in concrete terms before reasoning — "it's broken" isn't a
   symptom; "POST /orders returns 500 when items is empty" is.
2. **Build the dependency/cause chain.** What must each be true for the symptom to appear?
   Decompose backward into checkable sub-claims.
3. **Proof by elimination.** Enumerate the candidate causes and rule them out one at a time
   rather than asserting the likely one: e.g. for a 500 — (A) request validation, (B) service
   logic, (C) DB constraint/migration drift, (D) auth/permission, (E) environment/config.
   Show why it's not A, not B, until one remains.
4. **Reductio when stuck.** Assume the bug is NOT in the suspected function. Then something
   upstream must explain the symptom — is it? If nothing upstream can, the contradiction puts
   the bug back in that function.
5. **Surface the hidden assumption.** In code, the bug usually lives in an unverified
   assumption: "this returns sorted data" — verified or assumed? "this is awaited" — is it?
   "the test DB has this migration" — checked? Name it, then verify it.

## Gates still apply

Diagnosis happens in DISCUSS — investigate, read, reason, propose the fix and where it goes.
**Don't write the fix until the user says to build.** A confirmed diagnosis is not consent to
edit.

## After the fix (TEST)

Add a regression test that reproduces the original failure (API: pytest, auto; frontend:
defined for the user). Save to `docs/testing.md`. Journal the root cause — not just the
symptom — with a `friction:` line. If the bug came from a wrong assumption that the docs
implied, note that so the docs get corrected.

## Diagnose from data on hand before re-acquiring

Before any re-fetch, re-scrape, re-run, or full rebuild, prove the defect isn't correctable from
data already on disk — reparse, patch, a 1-line fix. Re-acquisition is the last resort, not the
reflex: a provable 1-line key-collision fix beats a 485-page re-scrape. Flip side of "measure a
small sample before scaling," which governs starting work — this governs redoing it.
