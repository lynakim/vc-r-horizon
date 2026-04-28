# Research Log: Robot Manipulation Task Horizon

*Running record of key findings, data decisions, and notable results. Add entries when results are blog-post-worthy or when a decision has meaningful downstream consequences.*

---

## Entry 1 — Doubling Time & Outlier Analysis (2026-04-28)

**Finding:** The frontier doubling time is robust at ~16 months, but fit quality varies dramatically depending on how you handle the Dactyl Rubik's Cube result.

**Full results (log(duration) ~ date, OLS on frontier points):**

| Scenario | Doubling Time | R² | N |
|---|---|---|---|
| ≥50% success (standard frontier) | 16.4 months | 0.84 | 8 |
| ≥80% success (high-reliability frontier) | 15.7 months | 0.98 | 8 |
| ≥50%, Dactyl Rubik's Cube excluded | 15.1 months | 0.98 | 14 |

**Why it matters:**

- Dactyl Rubik's Cube (240s, **60% success**, Oct 2019) holds the ≥50% frontier for 5 years — nothing at ≥50% exceeds 240s until Pi0 (300s) in Oct 2024.
- This creates an artificial 5-year "plateau" that deflates R² to 0.84.
- When raised to ≥80%, Dactyl (60%) drops off and the 2019–2024 gap fills in with steady intermediate progress: TransporterNet (90%, 30s, 2021) → CLIPort (85%, 40s, 2021) → TidyBot (85%, 60s, 2022) → ACT/ALOHA (85%, 120s, 2023). R² → 0.98.
- Removing Dactyl directly at ≥50% has the same effect: R² → 0.98, 14 frontier points, and the same intermediate systems fill the gap.

**Key narrative:** Dactyl was **ahead of its time** — a task-specific RL achievement (Shadow Hand + massive sim-to-real compute) that didn't represent the general field's trajectory. The field was advancing steadily at ≥80% reliability throughout 2019–2024; Dactyl's shadow just masked that progress in the ≥50% view.

**Counterpoint to note:** The doubling time barely changes across scenarios (15–16.4 months). The outlier affects *fit quality*, not the *rate estimate*. This is worth flagging — it means both interpretations (steady progress vs. plateau-then-jump) are consistent with roughly the same underlying growth rate.

**Script:** `scripts/analyze_doubling_time.py`

---
