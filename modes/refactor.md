# Mode: refactor (restructure without changing behavior)

Definition first, because the word is vague: **refactor = change the structure of the code
while its observable behavior stays identical.** If behavior changes, it's a feature or a fix,
not a refactor — switch modes and be explicit. Pinning this down is what keeps a "quick
cleanup" from silently altering what the app does.

## In DISCUSS

1. **Rehydrate** and **read the code** to be refactored plus everything that calls it.
2. **Establish the behavior contract.** What is the current observable behavior that must be
   preserved? If there are no tests covering it, that's the first risk — characterization
   tests may be needed before touching anything.
3. **Name the smell precisely.** "It's messy" isn't actionable. Duplication (where, how many
   copies)? A component doing three jobs? Prop drilling? An anemic service with logic in
   routes? Define the target end-state concretely.
4. **Map the blast radius** — every call site that must keep working.

## On the build gate → BUILD

Refactor in small, behavior-preserving steps, against the existing conventions (precedence:
docs → code → prefs → defaults — a refactor is the worst place to introduce a new library).
Apply the DRY/componentisation rules in `references/backend.md` and `references/frontend.md` as
the target structure. Keep the public interfaces stable unless the user agreed otherwise.

## On "complete" → TEST

The pre-existing tests must still pass **unchanged** — that's the proof behavior was
preserved. If you had to add characterization tests first, they stay. Save any new definitions
to `docs/testing.md`. Journal the structural change and why, referencing conventions, with a
`friction:` line.
