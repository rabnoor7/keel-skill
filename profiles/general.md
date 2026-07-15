# Profile: general — goal-shaped, not-only-code outcomes

For projects whose deliverable isn't (primarily) software: a personal brand, an outreach campaign, a
content system, a launch, a research effort, a creative build. keel's discipline applies unchanged — it
just points at a different kind of deliverable. Set with `docs.py profile general`.

## The work here is decomposition first
The user usually arrives with a big fuzzy OUTCOME and **does not yet know its layers.** Do not execute.
Run the **outcome-decomposition loop** (SKILL.md §0a): `docs.py outcome set "<north star>"`, then break it
into ordered OUTCOME-CHECKPOINTS with `docs.py checkpoint add`. Align each checkpoint through
recommendation-first, steelmanned tradeoff choices (§1b house style) and record the decision with
`checkpoint choice`; promote a pivotal one (positioning, niche, audience) to an ADR with `--to-decision`.
The committed `docs/roadmap.md` is the durable shape of the project; rehydrate surfaces "you are here" and
blocks a build on an undecomposed outcome.

**Typical checkpoint layers** (illustrative, not a fixed list — decompose the actual outcome):
- *personal brand*: positioning/niche · target audience · content pillars · platform · format & voice · cadence · growth tactics · metrics
- *outreach campaign*: ICP definition · qualifying framework · channel · message/offer · sequence · volume/cadence · reply handling · success metric
- *content system*: topic strategy · sourcing/ideation · production pipeline · review bar · publishing cadence · distribution · measurement

## Deliverables & verification
- **Deliverables are assets, not code** — posts, a lead list, a page, a script, a deck. Keep finals in a
  clean folder (`data/` by default; `docs.py hygiene` still applies) and rough drafts in `archive/`.
- **Verify against the real-world outcome, not a self-claim.** "Done" means the asset meets the checkpoint's
  recorded acceptance bar (`docs.py accept`) and, when only you can judge it (does the post read well, did
  the message land), it hands off for your verdict (`docs.py livetest`) rather than self-certifying.
- **Provenance still matters:** a claim about what works (a "trick", a benchmark, a competitor's tactic)
  needs a source, same anti-fabrication stance as any keel deliverable.

## What does NOT change
The loop, the gates, the memory model, the honesty-over-agreeableness posture. keel is not a hype engine —
it decomposes the outcome, surfaces the real tradeoffs at each layer, and lets you shape it deliberately.
