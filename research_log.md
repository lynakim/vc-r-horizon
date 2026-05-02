# Research Log: Robot Manipulation Task Horizon

*Running record of key findings, data decisions, and notable results. Add entries when results are blog-post-worthy or when a decision has meaningful downstream consequences.*

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
