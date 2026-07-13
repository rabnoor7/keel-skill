# ML

## Survey
- **Task & data** — what's being predicted/generated, from what inputs? Where does the data come
  from, and how is it split (train/val/test)? Check explicitly for **leakage** — features that
  encode the label, or splits that let future information reach training.
- **The eval metric + threshold** — define "good" as a number *before* building: which metric
  (accuracy/F1/AUC/RMSE/perplexity/...) and what score counts as acceptable. A model with no
  pre-committed number will always look successful in retrospect.
- **Baseline to beat** — a naive baseline (majority class, current heuristic, previous model in
  production). If the new model doesn't beat it, it isn't done, however sophisticated it is.
- **Reproducibility** — seed(s), library versions, and a hash/version of the training data.
  Missing any one of the three means "reproduce this result" isn't answerable later.

## Build
- **Pin data and seeds.** The exact training data (versioned or hashed) and the random seed(s) are
  recorded alongside the run, not just the code.
- **Separate train/eval, strictly.** Eval data never touches feature engineering, hyperparameter
  search, or early-stopping decisions — those only see train/val.
- **Log every run** — hyperparameters, metric(s), data version, seed, git commit. A run with no
  log is a result no one can compare anything else against later.

## Verify
Verification is **metrics against a pre-committed threshold**, not pass/fail on "it runs":
- **Held-out evaluation** — the metric computed only on data the model never saw, train or val.
- **Compare to baseline** — report the delta, not just the absolute number.
- **Threshold check** — the metric from Survey, hard-gated: below the bar means not done,
  regardless of how much work went into getting there.
- **Drift check where relevant** — for anything that sees new data post-deployment, define what
  monitoring would catch a metric regression.
- **Reproducibility check** — same seed + same data version reproduces the same metric, within a
  documented tolerance for legitimate nondeterminism (e.g. GPU ops).
A model that **runs** is not a model that **works** — the eval metric, measured honestly against
the threshold in `verify/audit.py`, is the deliverable, not the code.
