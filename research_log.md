# Research Log: Robot Manipulation Task Horizon

*Running record of key findings, data decisions, and notable results. Add entries when results are blog-post-worthy or when a decision has meaningful downstream consequences.*

---

## Entry — Post-π0 doubling time slice (2026-05-08)

**Question asked:** What does the doubling time look like if we restrict to results after the π0 release (2024-10-31)?

**Findings (real-world, ≥50%):**

| Slice | Doubling | R² | N | Notes |
|---|---|---|---|---|
| Strict frontier post-π0 (π0 → π0.5) | ~4.5 mo | — | 2 | Two-point implied rate, 300s → 720s in 5.7 mo |
| Frontier from ALOHA Unleashed (Oct 13, 2024) → π0.5 | ~3.0 mo | 0.81 | 3 | Adds last pre-π0 frontier point |
| Binary-only frontier from ALOHA Unleashed → π0.6 | ~17.2 mo | 0.96 | 3 | ALOHA Unleashed Hang Shirt 120s → BEHAVIOR Trash 130s → π0.6 single-shirt fold 200s |
| All real-world ≥50% post-π0 points (log-linear) | ~6.5 mo | 0.15 | 15 | Scattered tasks, not frontier — too noisy to read |

**Takeaway:** No new framing here — the post-π0 "acceleration" is exactly the rubric-vs-binary story already in the blog post. The 3–4.5 mo number is two rubric-scored generalist papers from the same lab (π0 → π0.5). Restrict to binary completion and the post-π0 frontier doubles *slower* than the full-history 14.9 mo, not faster. With N=2–3 over a 12-month window, none of these are statistically meaningful.

**Did not modify the dataset or blog.** Logged here so the question doesn't have to be re-derived.

---

## Entry — Dactyl Rubik's Cube row removed (2026-05-02)

**Decision:** Dropped the `OpenAI Dactyl - Rubik's Cube` row from `manipulation_horizons.csv`.

**Why — the principle (matters for future inclusion calls):** The "human-equivalent time" axis is only meaningful if a near-100% slice of the adult population could execute the task with no special training. A Rubik's cube fails that bar — most adults cannot solve one at all, casual cubers take 1–4 min, speedcubers take seconds. Whatever number we pick is really an arbitrary choice of population, not a property of the task. The horizon should measure how long a robot takes to do things humans just *do*, not things humans need to learn.

**Why — the local issues with this row:** The 240s figure was a `defended_estimate` whose notes never actually defended it; the task description ("apply a 43-move scramble") didn't match the 240s figure (closer to a casual *solve* time, not a scramble); the result is a single-task RL achievement (Shadow Hand + massive sim-to-real compute) that was already a known outlier in our analysis.

**Downstream changes:**
- `≥50% real-world` doubling time: 15.2 mo (R² 0.83, N=9) → **14.7 mo (R² 0.93, N=10)**, 95% CI 11.9–18.0 mo. Removing the outlier sharpens fit quality, in line with what we previously saw when *excluding* it as a sensitivity.
- The post-2019 frontier no longer has a five-year flat stretch anchored on Dactyl. New ≥50% real frontier: Dactyl Block (10s, 2018) → SayCan (90s, 2022) → Code as Policies / ALOHA Unleashed (120s, 2022/2024) → π0 (300s, 2024) → π0.5 (720s, 2025).
- The "Dactyl as ahead-of-its-time outlier" framing in Entry 1 below and in the blog draft's plateau verification (Entry 4) is now moot for the headline curve. Earlier entries kept verbatim as historical record; do not cite the plateau framing forward.
- README headline updated; `scripts/analyze_doubling_time.py` no longer runs the "without Dactyl" sensitivity (redundant once the row is gone). `plot_plateau_scatter` and the 240s anchor line in `plot_scatter.py` removed for the same reason.

**On the principle's status (revisited 2026-05-02):** First impulse was to promote "generic human task" to a formal inclusion criterion. Walked that back — Figure 02 at BMW (84s industrial sheet-metal cycle, trained-line-worker task) also bends the principle, and we kept it for its value as the dataset's only real autonomous deployment point. Applying the principle as a hard gate would force us to drop Figure 02 too, which we don't want. So it lives in `inclusion_criteria.md` as a **soft consideration** rather than a formal criterion, and the blog post should not lean on it as a methodology pillar (current text mentions it in the inclusion-bar paragraph and Limitations §5; revisit if doing a future pass).

---

## Entry 1 — Doubling Time & Outlier Analysis (2026-04-28)

**Finding:** The frontier doubling time is robust at ~15 months across every reasonable framing of the data, but fit quality varies sharply depending on how you handle the Dactyl Rubik's Cube result.

**Frontier definition.** Canonical frontier = real-world systems at ≥50% success. Sim-only results are tracked but don't anchor the envelope (sim/real gap is a known confound, and the project's own methodology calls for sim sensitivity rather than mixing). All scenarios below use real-world systems unless noted.

**Full results (log(duration) ~ date, OLS on frontier points):**

| Scenario | Doubling Time | R² | N |
|---|---|---|---|
| ≥50% success (canonical, real-world) | 15.2 months | 0.83 | 9 |
| ≥80% success (high-reliability, real) | 15.5 months | 0.93 | 7 |
| ≥50% real, Dactyl Rubik's Cube excluded | 14.3 months | 0.97 | 12 |
| Sensitivity: ≥50% incl. sim systems | 16.4 months | 0.84 | 8 |

**Why it matters:**

- Dactyl Rubik's Cube (240s, **60% success**, Oct 2019) holds the ≥50% real-world frontier for 5 years — nothing at ≥50% real-world reliability exceeds 240s until Pi0 (300s) in Oct 2024.
- This creates an artificial 5-year "plateau" that deflates R² to 0.83.
- When raised to ≥80%, Dactyl (60%) drops off and the 2019–2024 gap fills in with steady intermediate progress: Diffusion Policy (88%, 45s, Feb 2023) → ACT/ALOHA (85%, 120s, Mar 2023) → Pi0.6 (97%, 600s, Nov 2025). R² → 0.93.
- Removing Dactyl directly at ≥50% has the same effect: R² → 0.97, 12 frontier points, with intermediate systems (SayCan, Inner Monologue, ACT/ALOHA, Code as Policies) filling the gap.

**Key narrative:** Dactyl was **ahead of its time** — a task-specific RL achievement (Shadow Hand + massive sim-to-real compute) that didn't represent the general field's trajectory. The field was advancing steadily at ≥80% reliability throughout 2019–2024; Dactyl's shadow just masked that progress in the ≥50% view.

**Counterpoint to note:** The doubling time barely changes across scenarios (14–16 months). The outlier affects *fit quality*, not the *rate estimate*. Both interpretations (steady progress vs. plateau-then-jump) are consistent with roughly the same underlying growth rate.

**Notes on data quality (added 2026-04-28 audit):**

- TidyBot date corrected from 2022-03-01 → 2023-05-01 to match arXiv submission (2305.09560). With the corrected date TidyBot is dominated by ACT/ALOHA on the ≥80% frontier, and Diffusion Policy (88%, 45s, Feb 2023) takes its place as a frontier point.
- `is_frontier` CSV column rebuilt to match the canonical envelope (real-world, ≥50%, monotonic non-decreasing including ties): 9 systems.
- Sim-only systems (HER, TransporterNet, CLIPort, IKEA Furniture, ACRONYM, PerAct, RoboCerebra, VLABench) are excluded from the frontier. They appear as gray triangles on plots so the sim/real distinction is visible.

**Scripts:** `scripts/analyze_doubling_time.py`, `scripts/analyze.py`

---

## Entry 2 — Per-system success curves: why the exponential model isn't supported by this data (2026-04-28)

**Context:** We explored a "success rate vs. task duration" visualization — one curve per system showing how reliability falls off as tasks get longer, fitted via `success(t) = exp(-t/τ)` with τ inferred from each system's single observed `(duration, success_rate)` point.

**Finding:** The approach is not supported by our data for three reasons.

**1. A single data point cannot determine a curve.**
Nearly every system gives us one `(t₀, s₀)` observation. The exponential model has one free parameter (τ), so the fit is exact by construction — not evidence of a real decay shape. The resulting curve is 100% model and 0% data. We learn nothing about how this particular system's reliability degrades across task lengths; we just re-express the 50% horizon in curve form.

**2. High-success-rate systems extrapolate to nonsense.**
π0.6 achieves 97% success at 600 seconds. The fitted τ ≈ 19,000s implies a 50% horizon of ~3.8 hours. This extrapolation is almost certainly wrong — but would appear on the figure with the same visual weight as observed data, giving a false impression of empirical grounding.

**3. The model's independence assumption is violated.**
Exponential decay requires independent, constant-rate failures at every step. Real robot failures cascade (a misgrasp early in the task contaminates all downstream steps), are step-specific (grasping difficulty ≠ navigation difficulty), and modern systems can partially recover from errors. The true success-vs-duration relationship is unknown and likely different for every system architecture.

**Implication:** The scatter of raw `(duration, success_rate)` points is more honest than any curve overlay. The story of progress is visible in where the cloud of points sits and how it moves over time — no model required.

**See also:** research_ideas.md item 5 for approaches to fix this if we want curves in the future.

---

## Entry 3 — Major methodology cleanup: written inclusion criteria, success_type, dataset rebuild (2026-05-02)

**What changed:** The dataset was rebuilt from scratch against a written 5-criterion inclusion bar (real hardware autonomously evaluated, systematic eval with documented protocol, N≥10 real-world end-to-end trials, same task for rate and duration, grounded human time). A `success_type` column was added to flag binary task completion vs. rubric/partial-credit progress scores. Several existing rows were corrected for duration errors, aggregate-rate inflation, and one (ALOHA 2) was demoted to reference-only because it's a hardware paper with no quantitative evaluation.

**Why it matters:**

- **Headline doubling time barely moved** (15.2 → 14.1 months at ≥50% real-world). The methodology cleanup is reassuringly robust — the rate finding doesn't depend on the specific row corrections.
- **Frontier composition changed substantially.** 9 → 7 frontier points. The earlier curve had Pi0 / Pi0.5 / Pi0.6 with binary-looking success rates (75% / 70% / 97%) that were actually rubric scores or paper-wide aggregates. Now they're correctly flagged.
- **A surprising finding fell out of the cleanup:** the post-2019 ≥50% real-world frontier extension is carried *entirely* by rubric scores. If we restricted the curve to binary success only, the frontier would *cap at 240s through all of 2025* — the highest-confidence binary result post-2019 is π0.6's single-shirt fold at 200s / 97%, which sits *below* Dactyl Rubik's 240s anchor. The "10-minute household task" narrative the field tells about itself in 2024–2025 rests on partial-credit rubrics, not full task completion.
- **The ≥80% (binary) frontier is much smoother** (R² = 0.95, doubling 20.0 mo, N=11) than the ≥50% frontier (R² = 0.78, doubling 14.1 mo, N=7). This sharpens Entry 1's "Dactyl was ahead of its time" finding: at ≥80%, the field shows steady progress through ALOHA Unleashed (Oct 2024), Gemini Robotics (Mar 2025), and π0.6 single-shirt (Nov 2025). Slower headline rate, much cleaner story.

**Aggregate-rate fixes applied (criterion #4 violations from the previous CSV):**

- **SayCan** 74% → 50%. The 74% was *planning* success, not end-to-end. Per paper, end-to-end at 6 steps is ~50%.
- **TidyBot** moved from 60s/85% (full sort task) to 10s/85% (per-pick subtask). The 85% was per-pick and didn't match the full-task duration.
- **TransporterNet** 90% → 66%. The 90% was per-step rate; end-to-end at 4 steps is ~66% compounded.
- **ACT/ALOHA** 120s → 14s. The previous "85% at 120s" combined slot-battery rate (96% at ~14s) with zip-tie-threading duration (~120s) — a flagrant criterion #4 violation. Now uses slot battery 96% / 14s consistently.
- **Mobile ALOHA** 90s/85% → 45s/95%. The 90s was the cabinet teleop time, but the 85% rate was for cabinet at 30s. Now uses call elevator 95% / 45s — longest task at ≥50%.

**New rows added (round 1, with extracted per-task numbers):**

- ALOHA Unleashed (3 rows: hang shirt 70%/120s, tie shoelace 70%/80s, gear insert 95%/80s — all binary, N=20)
- Gemini Robotics (lunch-box pack 100% / N=20 / 120s, binary)
- UMI (dish washing 70% / N=20 / 60s, binary)
- π0.6 split: single-shirt fold (binary 97%, 200s) + espresso (rubric ~90%, 200s) + diverse laundry (rubric ~75%, 500s)
- π0 / π0.5 reset to rubric_progress with corrected durations and N

**Round 2 deferred:** BEHAVIOR Robot Suite, RL-100, TRI LBM, GR-3, AgiBot/GO-1, BiDex, Manual2Skill, FEAST, Reactive Diffusion Policy, DexUMI, DexWild, Gemini Robotics 1.5 — all flagged as candidates by the systematic search but need a paper-reading pass before adding. Not expected to move the headline; mainly fills in the recent (2024–2026) cluster.

**Sensitivity plot updated.** Switched from {30, 50, 80} thresholds to {50, 70, 80, 90, 95}. The 30% threshold yields the same frontier as 50% in our data (BC-Z at 44%/8s sits below the Dactyl plateau and doesn't extend the curve), so it was visually invisible behind the 50% line. The new five-threshold view reveals the divergence: at ≥70% Dactyl drops out and the curve smooths; at ≥80% the fit is the cleanest (R² = 0.95).

**Files changed in this pass:** `data/manipulation_horizons.csv`, `data/analysis_results.json`, all four figures, `inclusion_criteria.md` (new), `scripts/rebuild_dataset.py` (new — authoritative source of dataset), `scripts/plot_horizons.py` (sensitivity threshold update), `draft/blog_post.md` (numbers + methodology + binary/rubric section).

---

## Entry 4 — Verifying the 2019–2024 gap (2026-05-02)

**What:** A focused search to verify that no real-world manipulation paper between Jan 2020 and Sep 2024 combines (≥240s task) × (≥70% success) × (N≥10 trials) × (full autonomy) × (documented protocol). The Dactyl Rubik's Cube result (Oct 2019, 240s @ 60%) holds the ≥50% real-world frontier for five years before π0 in October 2024, and we wanted to rule out the possibility that we'd missed something during that window.

**Result: gap is real.** Twenty-five candidate systems checked individually. None pass all five criteria.

Closest contenders, with the criterion they fail:

- **SpeedFolding** (Avigal/Goldberg, IROS 2022): 93% but ~120s/garment — fails duration by 2×.
- **Mobile ALOHA** (Jan 2024): 95%+ on best tasks, but those tasks are 22–60s; the longest task (Cook Shrimp at 75s) sits at 40%.
- **HumanPlus** (Stanford, June 2024): 60–100% on tasks 20–50s — duration ~5× under bar.
- **SayCan / Inner Monologue / Code as Policies** (Google 2022): multi-step but the longest evaluated tasks are 90–120s, and the published per-task evaluations don't cross 240s at ≥70%.
- **FurnitureBench** (RSS 2023): real, ≥900s, but best baseline is 15% on the easiest task — fails success rate.
- **STAR autonomous laparoscopic anastomosis** (Krieger et al., Science Robotics Jan 2022): definitely multi-minute, but N=4 pigs in vivo + 5 phantom = 9 total trials, and reports per-stitch accuracy (83%) rather than end-to-end procedure completion. Fails both N and the end-to-end success criterion.
- **dVRK autonomous suturing** literature: no end-to-end full-procedure ≥240s + ≥70% + N≥10 before SutureBot (Oct 2025).
- **YAY Robot, OK-Robot, RoboCat, MimicPlay, AutoRT, BUMBLE, RT-1/2, Diffusion Policy, ACT, VoxPoser, Q-Transformer, BC-Z, PerAct, BAKU, OPTIMUS, RoboCook, HITL-TAMP** — all fail on duration, success rate, or both.
- **Industrial deployments** (Pickle, Symbotic, Berkshire Grey, Sanctuary AI Phoenix) — fail criterion 2 (no published protocol with success-rate tables).

**Two pieces of independent confirmation that the gap is real, not a search artifact:**

1. The **π0 paper** (Black et al., Oct 2024) opens by claiming *"To our knowledge, our work demonstrates the longest dexterous tasks in the end-to-end robot learning literature"* — i.e., the authors of the paper that ends the plateau themselves believe nothing in the literature came close.
2. The **SutureBot paper** (arXiv:2510.20965, Oct 2025) opens by saying *"a fully autonomous suturing pipeline had not yet been demonstrated on physical hardware"* before their work. Surgical robotics is the area most likely to have hidden multi-minute autonomous results, and the field's own authors confirm none existed.

**Implication for the analysis:** The Dactyl Rubik's Cube point is a genuine outlier. Its 240s @ 60% sat alone above every other 2020–2024 real-world result for the entire window. The "ahead of its time" framing in the blog post is correct — the rest of the field was advancing breadth and short-task reliability through 2020–2023, and it took the foundation-model era (π0 onward, late 2024) to actually push duration past 240s. We added a verification paragraph to the blog post citing the π0 and SutureBot self-quotes.

**Round 2 paper additions, also May 2 audit:** Twelve candidates from the systematic search (BEHAVIOR Robot Suite, RL-100, TRI LBM, GR-3, AgiBot/GO-1, BiDex, Manual2Skill, FEAST, Reactive Diffusion Policy, DexUMI, DexWild, Gemini Robotics 1.5) checked against the 3-criterion bar. Seven pass — added to CSV. **None push the ≥50% frontier past π0.5's 720s cap; all fill in below it.** The strongest 2025 binary point at long horizon is BRS Take Trash Outside (130s @ 53%); the strongest short-horizon high-reliability point is RL-100 box folding (42s @ 100%, N=50).

Failed in Round 2: GR-3 (N<10 long-horizon), Manual2Skill (humans do insertion step), FEAST (full-meal N=6), Gemini Robotics 1.5 (N=3–5 real, 90%+ of evals were sim).

CSV is now 52 rows (44 real + 8 sim). Frontier composition and 14.1-month doubling time unchanged.

---

## Entry 5 — Explored METR-style per-paper logistic fits, decided not to adopt (2026-05-04)

**Context:** METR's main figure puts each *model* at one (date, horizon) point, where the horizon is read off a logistic regression of `success ~ log(human_time)` fit across all the tasks that model was evaluated on. We considered doing the same per *paper* in our dataset — the natural analog given that "model" maps loosely to "paper" in robot learning. Five papers had multi-task tables that looked plausibly fit-able: ALOHA Unleashed, Mobile ALOHA, Gemini Robotics (specialist), π0.6, and FurnitureBench.

**What we built:** `data/per_task_evaluations.csv` (29 rows across 4 of the 5 candidates — FurnitureBench dropped because its multi-task structure is at the per-skill level with no duration spread) and `scripts/plot_logistic_horizons.py` (per-paper MLE logistic fit with binomial likelihood, continuous-scoring approximation for rubric rows à la METR Appendix H, within-paper bootstrap CI on the horizon, and a side-by-side comparison plot vs. the existing CSV points).

**Result:** Only one of four fits is usable.

| Paper | N tasks | β | 70% horizon | 95% CI |
|---|---|---|---|---|
| ALOHA Unleashed | 11 | −0.90 | 46s | 7.6–86s |
| Mobile ALOHA | 7 | −1.00 | 84s | 45–4,883s |
| π0.6 | 5 | −0.89 | 991s | 559–228,000s |
| Gemini Robotics specialist | 6 | ≈0 | non-monotonic | — |

ALOHA Unleashed is clean. The other three either have a single noisy row dragging the CI by orders of magnitude (Mobile ALOHA's Cook Shrimp at N=5; π0.6's diverse laundry sitting right at threshold) or violate the model's monotonicity assumption outright (Gemini Robotics — lunch-box at 120s scores 100%, origami at 60s scores 45%; longer ≠ harder when the lab curates a dataset per task).

**Why this method doesn't pay off in our domain:** METR's logistic fit works because HCAST tasks are explicitly drawn from a continuum of human-baseline times — varying duration *is* the experimental design. Robot manipulation papers don't work that way. They evaluate at one or two task durations and vary difficulty along non-duration axes: state randomness (FurnitureBench), language complexity (Gemini Robotics), object diversity (π0.6). The structural assumption "rate falls monotonically with task length within a paper" is not what most of these papers are testing. Forcing a logistic on top of that structure injects more noise than it removes.

**Decision:** Not adopting. Keep the per-system scatter + step-function frontier + exponential fit as the primary plot.

**Artifacts moved to archive (2026-05-04):**
- `archive/scripts/plot_logistic_horizons.py`
- `archive/figures/logistic_horizon_test.png`, `archive/figures/logistic_per_paper_curves.png`

`data/per_task_evaluations.csv` is kept in `data/` — it's a clean per-task evaluation table that may be useful for analyses other than logistic fitting.

If we ever want to revisit this, the place to start is dropping non-monotonic papers from the fit and adding per-task human-time baselines (rather than `defended_estimate`) for the 4–5 papers that do have genuine duration variance.

---

## Entry 6 — Binary vs. mixed frontier diverges only in the foundation-model era (2026-05-04)

The two frontiers are identical from 2016 through Oct 2024. They split only at the last two points: π0 laundry (300s, 70% rubric, Oct 2024) and π0.5 bedroom (720s, 70% rubric, Apr 2025). Binary-only continues through ALOHA Unleashed Hang Shirt (120s, Oct 2024), BRS Take Trash Outside (130s, Mar 2025), and π0.6 single-shirt (200s, Nov 2025). Mixed: 14.7 mo doubling, R²=0.93, N=10. Binary-only: 17.8 mo doubling, R²=0.91, N=10. The gap between the curves is real but recent and narrow — it's a 2024–2025 generalist-VLA phenomenon. Plot: `figures/binary_vs_mixed_frontier.png`.

The forward-looking implications — that the recent rubric run is real but ambiguous progress, that the field needs a consistent scoring convention, that task length is one capability axis among many — were folded into the blog post (binary-vs-rubric section + Limitation #6) rather than tracked here.

---

## Entry 7 — Dactyl→SayCan gap audit: filled with four 2019–2021 rows (2026-05-05)

**Trigger:** The chart showed essentially zero real-world progress between Dactyl Block (Jul 2018) and SayCan (Apr 2022) — only TossingBot (Apr 2019) sat in that window. That's not what actually happened in the field; the prior Entry 4 audit was scoped to *240s+ frontier* candidates and never looked at shorter-horizon real-world results from the period.

**Verification of the gap (the original framing):** Still true at the 240s+ tier. Nothing in 2019–2021 combines (≥240s task) × (≥70% success) × (N≥10) × (autonomous) × (documented protocol). The π0 / SutureBot self-quotes from Entry 4 still hold at that bar.

**But:** there's plenty of *shorter-horizon* real-world progress that should be visible on the chart. Four rows added (all real, autonomous, N≥10, documented protocol):

- **Form2Fit** (2019-10-31, arxiv 1910.13675) — UR5e + suction kit assembly, 94% on novel kits, N=20/condition. ICRA 2020.
- **MT-Opt** (2021-04-16, arxiv 2104.08212) — multi-task QT-Opt successor, 89% on common-task lifting (multi-task transfer to rare tasks ~50%). 800k+ shared real-robot episodes; direct precursor to the RT-1 dataset pipeline.
- **Implicit Behavioral Cloning** (2021-09-01, arxiv 2109.00137) — Franka, ~87% on push-block precise insertion (1mm tolerance) vs ~55% explicit BC. 7 real-robot tasks at N≈50 each. CoRL 2021.
- **RGB-Stacking** (2021-10-12, arxiv 2110.06192) — DeepMind, Sawyer arm, sim-to-real 3-block stacking. 82% Skill Mastery / 54% Skill Generalisation. CoRL 2021.

**Frontier impact:** Form2Fit (30s @ 94%, Oct 2019) becomes a new frontier point — slots between Dactyl Block (10s, Jul 2018) and SayCan (90s, Apr 2022) at ≥50% reliability. The other three are below the envelope. New ≥50% real-world frontier: Levine → Dex-Net → QT-Opt → Dactyl Block → **Form2Fit** → SayCan → Inner Monologue → Code as Policies → ALOHA Unleashed Hang Shirt → π0 → π0.5.

**Doubling-time numbers (≥50% real, OLS on log-duration ~ date):**

- Before: 14.7 mo, R² 0.93, N=10
- After: 14.9 mo, R² 0.92, N=11

Headline barely moved. The ≥80% scenario is unaffected (Form2Fit at 94% sits naturally in the existing ≥80% sequence; doubling stays at ~20 mo, R² ≈ 0.92).

**Reframe of earlier entries:** Entry 1's "Dactyl as ahead-of-its-time outlier with a 5-year flat stretch" framing was already softened in the 2026-05-02 entry after the Rubik's Cube row was dropped. With Form2Fit now on the frontier, the post-2018 ≥50% trajectory has a real Oct-2019 anchor and the "flat stretch" framing is fully retired. Mention of it remains in earlier entries as historical record only.

**Files changed:** `scripts/rebuild_dataset.py` (4 new rows), `data/manipulation_horizons.csv` (47 rows now), `data/analysis_results.json`, all regenerated figures.

---

## Entry 8 — Considered (and deferred) collecting our own human-time baselines (2026-05-08)

**Context:** 23 of 47 main-CSV rows (49%) carry `human_time_source = defended_estimate`, including all four lower-frontier anchor points (Levine, Dex-Net, QT-Opt, Dactyl Block at 4–10s). The two genuinely measured rows in the dataset are HIL-SERL (BC baseline at 16.1s, N=100) and ACT/ALOHA slot-battery (paper-reported direct human time); the rest of the `published_baseline` column is mostly episode timeouts repurposed as task length, which is a loose upper bound rather than a measurement.

**What we considered:** A short baselining session — a single "single-object bin pick" trial (covers ~10 frontier and near-frontier rows in the 4–8s cluster), an in-hand block reorient (Dactyl Block, frontier), and the multi-step kitchen tasks (SayCan, Inner Monologue, Code as Policies, UMI, GR-1). Estimated ~2–3 hours of stopwatch work. Highest leverage: the four lower-frontier rows that anchor the bottom of the exponential fit, plus the 90–200s multi-step rows that carry weight near the upper end.

**Decision: not doing it now.** Optimising for time-to-publish on the blog post. The doubling time finding is robust across reasonable perturbations to these short-end estimates (we've already checked sensitivity in Entries 1 and 3 — rate barely moves), and the methodology section is honest about the `defended_estimate` provenance. Spending another half-day on stopwatch work would tighten the lower-left of the curve a bit but wouldn't change the headline.

**What it would gain if we revisit:** A new `human_time_source = direct_baseline` value, tighter CI on the early-frontier intercept, and a better answer to "how do you know it's 4 seconds and not 7" if a reviewer pushes on Levine / Dex-Net / QT-Opt. Filed as research-ideas item #6 with the protocol notes (start state, success criterion, median-of-N) that came out of the Entry 8 discussion. The published-baseline reference cluster (HIL-SERL, ACT/ALOHA) sets the protocol bar.

**Status:** filed, not scheduled.

---
