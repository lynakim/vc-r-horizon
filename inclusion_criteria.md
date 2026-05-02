# Inclusion Criteria

How systems get into `data/manipulation_horizons.csv`.

## The bar — five criteria

A row is frontier-eligible only if all five hold.

1. **Real hardware, autonomously evaluated.** Headline evaluation ran on a real robot under autonomous control. Sim-pretrained policies count as real (the substrate of training doesn't matter — what matters is where the headline number was measured). Teleoperated demos do not count, even if labeled autonomous in marketing.

2. **Systematic evaluation.** Success rate comes from a documented protocol in a paper or technical report — not a video, press release, or blog post.

3. **N ≥ 10 real-world end-to-end trials.** Sim trials don't count toward this threshold.

4. **Same task for rate and duration.** The success rate in a row must come from the same task whose human-time we estimate — never pair an easy subtask's success rate with a different, longer task's duration. *Example: ACT/ALOHA's slot-battery (96% at ~14s) and zip-tie threading (20% at ~14s) are two different rows. The previous CSV row "85% at 120s" combined the slot-battery success rate with a guessed threading duration, violating this criterion.*

5. **Grounded human time.** The `human_time_source` column takes one of four values:
   - `published_baseline` — paper reports a human baseline time
   - `observed_demo` — timed from a demonstration video, link in `notes`
   - `analogue` — borrowed from a similar published task, justification in `notes`
   - `defended_estimate` — our estimate, reasoning in `notes`

Anything outside these is flagged as TODO until grounded.

## Soft considerations (not gating)

These shape judgment calls but aren't formal criteria — the dataset already has rows that bend them, so we don't elevate them to gates.

- **Generic-human-task preference.** All else equal, prefer tasks that a near-100% slice of the adult population could execute with no special training (folding shirts, picking up cups) over tasks dominated by a narrow trained sub-population (solving a Rubik's cube, line-worker assembly). The human-equivalent time axis is cleaner when the baseline isn't a choice of population. Used as the reason for removing Dactyl Rubik's Cube (240s, Oct 2019) — see research log 2026-05-02. Caveat: Figure 02 at BMW (84s industrial cycle time, sheet-metal loading) bends this too but is kept for its value as a real autonomous deployment data point, so this consideration isn't applied uniformly.

## Multi-row policy

Default: one row per paper at the longest task meeting N≥10.

Multiple rows per paper are allowed when the paper presents a per-task table with task-specific N≥10 and the tasks span genuinely different durations or capabilities. The point is to capture the spread of capability, not clutter the chart with redundant clustered points.

## Reporting conventions

These are how we record numbers, not gating criteria.

- **Success rate** = the number the paper reports for the chosen task. We don't apply binomial corrections or report lower bounds. Trust the paper's headline; transparency about N is in the `num_trials` column.
- **Success type** = `binary` (fraction of trials that fully succeeded) or `rubric_progress` (average partial-credit score on a multi-point rubric). Both anchor the frontier curve. The `success_type` column tracks which, and the blog post's methodology paragraph explains the difference.
- **Sim/real** = two values: `real` (headline eval ran on real hardware) or `sim` (headline eval ran in simulation only). Sim entries appear on plots as gray triangles for context but don't anchor the curve.
- **`is_frontier`** = TRUE if this row is on the canonical real-world ≥50% frontier (real hardware, headline rate ≥50%, monotonic non-decreasing including ties on date).

## Excluded systems

A non-exhaustive list of systems the search surfaced that don't qualify under criterion 2 (no documented protocol):

- Tesla Optimus, 1X NEO Gamma, Apptronik Apollo, Sanctuary Phoenix
- Figure AI Helix / Helix Logistics / Helix 02 — blog posts only, no N or per-task rates. (Note: Figure 02 at BMW *does* qualify because BMW released aggregate operational metrics over an 11-month deployment.)
- Skild AI

## How we searched the literature

Two-tier process to keep the dataset defensible against "you missed paper X" critique:

1. **Conference proceedings scrape.** Every accepted paper at CoRL, RSS, ICRA award-track, NeurIPS robotics workshops 2020–2026, filtered by title/abstract for manipulation / real-world / long-horizon keywords, then triaged against the five criteria.
2. **Citation graph traversal.** Forward citations from existing frontier rows (π0.6, ALOHA Unleashed, Gemini Robotics, RT-X, Diffusion Policy) via Semantic Scholar; backward citations from the same set. Anything cited by ≥3 of them got a look.

Search and triage are documented in `research_log.md`.

## Methodology references

These are cited in the blog post but not added as data rows:

- [Epoch AI: Where Autonomy Works (2026)](https://epoch.ai/blog/where-autonomy-works-evaluating-robot-capabilities-in-2026) — closest published cousin; uses a 5-tier maturity framework rather than doubling-time analysis.
- [METR Task Horizon Analysis](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) — the methodology this study adapts.
- [AutoEval](https://arxiv.org/abs/2503.24278), [RoboArena](https://arxiv.org/abs/2506.18123) — relevant to the "no shared benchmark" framing.
