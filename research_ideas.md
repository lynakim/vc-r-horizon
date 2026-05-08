# Research Ideas

Quick notes on threads to revisit when the project is in a better place.

---

## 1. Uncertainty bounds

The Meter paper does a good job of both presenting interesting results *and* calling out that the error bounds are wide — in an honest, appropriate way. We should do the same: make sure our results include proper uncertainty quantification and that we're transparent about how wide those bounds actually are.

## 2. Curve fitting methods

Explore a couple of alternative fitting methods beyond what we're currently doing — smooth splines being one candidate. Worth making sure we've tried a few approaches and know why we landed where we did.

## 3. Task difficulty framing

We need to nail down what we're actually claiming about task length vs. task difficulty — the blog post needs to be logically consistent here. The key distinctions to sort out:

- **Task length as a proxy for task difficulty** — length stands in for difficulty because harder tasks take longer
- **Task length as an independently useful feature** — length matters on its own, regardless of difficulty
- **Task length as one factor that affects task difficulty** — difficulty is multidimensional, length is one dimension
- **Task length as orthogonal to task difficulty** — difficulty is defined by other things (rigid vs. deformable, number of subtasks, degree of spatial reasoning like a Rubik's Cube), and length is separate

We've discussed this a few times. **Leaning toward: task length as an independently useful feature** — doesn't require claiming it captures difficulty, just that it has explanatory power on its own. Need to commit to this before the post can be logically tight.

The more ambitious version: actually carve out a few difficulty dimensions (rigid vs. deformable, subtask count, degree of spatial reasoning) and show where task length sits relative to them — e.g. "length loads onto X but not Y." Would require re-annotating tasks. Worth revisiting if we want to make a stronger claim.

## 4. Per-system success-rate audit

Many CSV rows compress nuance the original papers don't. A targeted re-audit would tighten data quality without touching the headline numbers. Examples found in the 2026-04-28 audit:

- **TransporterNet** (CSV: 90% on 4-step task) — paper reports per-step rates; end-to-end at 4 steps is ≈66%. (Sim-only, so doesn't move the canonical frontier, but misleading on its face.)
- **HIL-SERL** (CSV: 100%, N=20) — a binomial 95% CI on 20/20 is roughly [83%, 100%], not a point at 100%.
- **ACT/ALOHA** (CSV: 85% at 120s) — 85% is for "slot battery" (a short subtask); the 120s human-time belongs to the threading task. Two facets of the same paper got combined into one row. This *is* on the ≥80% frontier, so the conflation matters more than the others.
- **Pi0/Pi0.5/Pi0.6** (CSV: assorted single rates) — each release reports per-task rates across many tasks; using the headline rate omits the spread.

What to do: define an explicit "success rate at full-task completion, with N reported, lower binomial bound" convention, then re-extract for at least the frontier points. Keep `success_rate` as the central value and add `success_rate_lower_95` (binomial) and `success_rate_basis` ("end-to-end" vs "per-step" vs "best subtask"). At minimum, retire any "100%" rate that came from N≤50 trials.

This has knock-on consequences: if Dactyl Block, ACT/ALOHA, or HIL-SERL drop below 80% under a stricter convention, the ≥80% frontier and its R² move. The headline ≥50% doubling probably doesn't move, but the secondary narrative does.

## 5. Per-system success curves: fixing the visualization for our data

We explored plotting one success-vs-duration curve per system (fitted exponential decay), and identified why it's not supported by our data (see research_log Entry 2). Three candidate fixes if we want curves in the future:

- **Require ≥3 data points per system before plotting a curve.** Only a handful of systems have multi-task breakdowns (Mobile ALOHA, π0.x series). Filters harshly but keeps the figure honest.
- **Non-parametric era envelopes instead of per-system curves.** Draw a Pareto frontier in `(duration, success_rate)` space for each time era — no model required. Trades per-system identity for an honest aggregate boundary.
- **Collect multi-task evaluation data.** The right fix: evaluate the same system at several task durations and fit the curve from actual observations. Currently almost no papers do this systematically. Worth flagging as a gap future benchmarks should fill.

Note the connection to idea #3 (task difficulty framing): the curve-fitting problem is partly a symptom of duration and complexity being conflated. Fitting a single curve across different tasks implicitly assumes duration is the only variable that drives success rate changes — which it isn't.

## 6. Direct human-time baselines for `defended_estimate` rows

23 of 47 main-CSV rows (49%) — including all four lower-frontier anchors (Levine, Dex-Net, QT-Opt, Dactyl Block at 4–10s) — use `human_time_source = defended_estimate`. The dataset has only two genuinely measured human times (HIL-SERL BC baseline 16.1s; ACT/ALOHA slot-battery, paper-reported); most of the `published_baseline` column is episode timeouts used as a loose upper bound on task length, not actual measurements. See research_log Entry 8 for why we chose not to do this before publishing.

**Highest-leverage measurements** (from the Entry 8 discussion):

- *Single-object bin pick* — one careful baselining session (20 trials, household objects) propagates to ~10 rows in the 4–8s cluster: Levine, Dex-Net, QT-Opt, TossingBot, RT-1, RT-2, RT-X, Octo, OpenVLA, BC-Z. Three of those (Levine, Dex-Net, QT-Opt) are on the ≥50% real frontier and anchor the bottom of the exponential.
- *In-hand block reorient to target face* — Dactyl Block (10s, frontier).
- *Multi-step kitchen tasks at 60–200s* — SayCan, Inner Monologue, Code as Policies, UMI dish washing, GR-1, π0.6 SimpleLaundry. Each needs its own session matching the paper's start state.

**Protocol** (matches the HIL-SERL / ACT-ALOHA bar):

- Time from the robot's exact start state to the robot's success criterion. No setup, no cleanup.
- Binary completion only — not partial credit, even when the paper reports rubric_progress.
- Median of 3–5 trials, not single-shot.
- Match the paper's exact starting state photo / description (a "messy" shirt and a flat shirt differ ~5x).
- Record per measurement: task name, paper, start-state photo, success criterion (verbatim from paper), N, median, range, date, who measured.

**Schema change required:** add `direct_baseline` as a `human_time_source` value alongside `defended_estimate`, `published_baseline`, `observed_demo`. Don't overwrite existing `defended_estimate` rows — keep both for audit.

**Expected impact on results:** small. Sensitivity in research_log Entries 1 and 3 already shows the doubling-time finding is robust to reasonable perturbations of the short-end estimates. The value is in tightening reviewer-facing CI on the lower-left intercept, not in shifting the headline.
