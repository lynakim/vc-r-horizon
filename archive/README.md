# Archived Analyses

These scripts and figures were generated during exploratory analysis but weren't useful enough to keep in the main flow.

---

## Distribution plots (`plot_distributions.py`)

**What it does:** Basic histogram and breakdown plots across the full dataset — success rate distribution, task duration distribution, success vs. duration scatter, breakdown bars by category/sim/quality/frontier, papers per year, subtask count histogram, and a sim vs. real box plot.

**What was kept:** `dist_breakdowns.png` (dataset composition summary), `dist_success_sim_vs_real.png` (sim vs. real box plot) — both moved back to `figures/`.

**Why the rest is archived:** The remaining histograms are descriptive dataset summaries that don't surface findings beyond what the main horizon plot already shows.

---

## Success curves (`plot_success_curves.py`)

**What it drove:** Explored whether systems with higher success rates tend to tackle shorter or longer tasks, and whether there's a reliability-complexity frontier.

**What was kept:** `success_vs_duration_curves.png` — moved back to `figures/`.

**Why the script is archived:** The script generates several variants; the one useful output has been kept in figures.

---

## Subtask complexity analysis (`analysis_subtask_complexity.png`)

**What it drove:** Looked at whether `num_subtasks` is growing over time independently of duration, whether more subtasks correlates with longer tasks, and whether success rate drops with more subtask steps.

**Why archived:** The subtask count field is too loosely defined across papers to support clean analysis — different papers decompose the same task differently. The correlations exist but aren't meaningful enough to highlight.

---

## Sim-to-real gap analysis (`analysis_sim_to_real.png`)

**What it drove:** Compared success rates between sim and real-world systems, stratified by task duration bin and data quality tier.

**Why archived:** The sample sizes per bin are too small (n=1–3) to draw reliable conclusions. The aggregate sim vs. real comparison is already summarized in the distributions box plot.
