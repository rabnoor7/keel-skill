# Mode: add-feature (new capability on existing code)

Most of a project's life. The map is **what already exists**, not a blank survey.

## In DISCUSS

1. **Rehydrate** first (`docs.py read --all`) — the recorded decisions and conventions are
   the authority, not your defaults.
2. **Read the relevant code.** Find where similar features live; infer the conventions in
   place (libraries, layering, naming). Conform to them (precedence: docs → code → prefs →
   defaults).
3. **Map the new feature against the existing structure**: what new entities/migrations, what
   new endpoints, what new pages/components, what existing code it touches. State the **blast
   radius** — what could this change break? — explicitly.
4. **Ask only the genuinely open design questions.** Don't re-ask anything `docs/` already
   settled. (If you find yourself about to re-ask a settled question, that's a `friction:`
   note for the journal.)

No code until the build gate.

## On the build gate → BUILD

Implement following the existing conventions, layer by layer (model → migration → service →
route → frontend), reusing existing components/services rather than duplicating. Record any
new decision as an ADR; update `data-model.md` / `api.md` if the contracts changed.

## On "complete" → TEST

New API behavior gets pytest coverage (auto, against Postgres). New UI gets written frontend
test definitions for the user to run. Save to `docs/testing.md`. Journal what changed,
referencing the ADRs/docs, with a `friction:` line.
