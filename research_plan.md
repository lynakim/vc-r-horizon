# Research Plan: Task Horizon Plot for Robotic Manipulation

## Context

METR published influential work plotting the "50% task-completion time horizon" for LLM agents — the length of task (measured in human expert time) that frontier AI agents can complete with 50% reliability. This metric has been doubling every ~7 months across software/reasoning domains. Their July 2025 blog post ([How Does Time Horizon Vary Across Domains?](https://metr.org/blog/2025-07-14-how-does-time-horizon-vary-across-domains/)) extended this analysis to non-software domains (web browsing, self-driving) and found similar exponential growth at different absolute levels.

**No one has done the equivalent analysis for robotic manipulation.** This project will create that plot: tracking the longest-horizon manipulation task that robots can reliably complete, over time (~2015-2025), using human-equivalent time as the primary Y-axis metric. The goal is a research blog post with compelling visualizations, a curated dataset, and narrative analysis.

## Approach: Adapted METR Methodology for Robotics

### Primary Metric: Human-Equivalent Task Duration

For each data point (a system demonstrated in a paper/demo at a point in time), estimate: **"How long would a competent human take to perform this same task?"**

This directly parallels METR's approach and enables cross-domain comparison with their LLM agent plot.

Examples of calibration:
| Robot Task | Est. Human Time |
|---|---|
| Single pick-and-place (one object) | ~5 seconds |
| Sort 5 objects into bins | ~30 seconds |
| OpenAI Dactyl block reorientation | ~10 seconds |
| OpenAI Dactyl Rubik's cube solve | ~3-5 minutes |
| IKEA furniture assembly (simple shelf) | ~15-30 minutes |
| Fold 5 T-shirts from a basket | ~5 minutes |
| Cook a 3-course meal | ~60-90 minutes |
| Clean up an entire kitchen | ~20-30 minutes |

### Reliability Threshold

METR uses 50% success rate. For robotics we should record the reported success rate and note the threshold. Many robotics papers report success rates, so we can filter for "demonstrated at ≥50% success" as the inclusion criterion for the main plot, with sensitivity analysis at other thresholds.

### Categories

Two categories, plotted together and separately to see which tells a clearer story:

1. **Tabletop/Fixed-base Manipulation** — Arm(s) mounted on a table/surface performing manipulation tasks (grasping, assembly, dexterous manipulation, tool use, cooking on a countertop)
2. **Mobile Manipulation** — Robot navigates to location(s) AND performs manipulation (fetch objects, clean rooms, multi-room tasks)

## Data Collection: Key Systems & Papers to Survey

### Era 1: Foundations (~2015-2018)
- **DQN/deep RL grasping** (Levine et al., 2016-2018): Large-scale grasping with ~90% success. Human time: ~3-5s per grasp
- **Sim-to-real pick-and-place** (various, 2017-2018): Single-step tasks. Human time: ~5-10s
- **OpenAI Dactyl block reorientation** (2018): In-hand reorientation. Human time: ~10s
- **BC/imitation learning baselines** (2017-2018): Simple single-step manipulation

### Era 2: Multi-Step Emerges (~2019-2021)
- **OpenAI Rubik's Cube** (2019): Dexterous solve, 60% success on 15-move scrambles. Human time: ~3-5 min
- **IKEA Furniture Assembly** (Lee et al., 2021): Multi-step assembly in sim. Human time: ~15-30 min (varies by piece)
- **SayCan** (Ahn et al., 2022): Language-conditioned mobile manipulation, multi-step kitchen tasks. Human time: ~1-3 min
- **Inner Monologue** (2022): Multi-step tasks with language feedback

### Era 3: Foundation Models (~2022-2024)
- **RT-1** (Brohan et al., 2022): 700+ tasks, single-step, ~97% success on seen tasks. Human time: ~5-10s per task
- **RT-2** (2023): Emergent generalization, 62% on novel scenarios. Single-step tasks. Human time: ~5-10s
- **Code as Policies** (2023): LLM-planned multi-step tasks. Human time: ~1-5 min
- **RT-X / Open X-Embodiment** (2023): 22 embodiments, 527 skills. Mostly single-step
- **Octo** (2024): Open-source generalist policy. Single-step manipulation
- **ACT / ALOHA** (Zhao et al., 2023): Bimanual tasks — threading, cooking. Human time: ~2-5 min
- **FurnitureBench** (Heo et al., 2023): Real-world furniture assembly. Human time: ~10-30 min
- **Mobile ALOHA** (2024): Mobile bimanual manipulation — cooking shrimp, cleaning. Human time: ~5-15 min

### Era 4: Generalist Robots (~2024-2025)
- **π0** (Physical Intelligence, late 2024): Multi-task generalist, laundry folding, table cleanup. Human time: ~5-10 min
- **π0.5** (2025): Broader generalization, multi-step household tasks
- **π0.6** (2025): Reliable laundry folding, kitchen/bedroom cleanup. Human time: ~10-30 min
- **Figure 02** (2025): 10-hour autonomous shifts at BMW (material handling). Human time: equivalent to human shift work
- **1X NEO** (2025): Consumer/service tasks, human-guided with teleoperation fallback
- **Tesla Optimus** (2024-2025): Factory material handling, folding, pouring. Human time: ~1-5 min per task
- **RoboCerebra benchmark** (2025): Avg 2972 sim steps, 3.5 action categories per task
- **VLABench** (2025): Composite tasks ~500 timesteps. Human time: ~2-5 min
- **Autonomous cooking demos** (2024): Stanford's 3-course Cantonese meal robot. Human time: ~60-90 min
- **Circus CA-1** (2025): Autonomous food production in REWE supermarkets. Human time: ~5-10 min per meal

### Additional Data Sources to Mine
- **DROID dataset** (2024): 76k demonstrations, 86 tasks, 564 scenes
- **Open X-Embodiment** (2023): 1M+ trajectories, 22 embodiments, 527 skills
- **CLIPort / TransporterNet** (2021): Multi-step rearrangement
- **PerAct** (2022): 6-DoF multi-task manipulation
- **GNFactor, RVT** (2023): 3D manipulation
- **HIL-SERL** (2024): 2x success rate improvement via human-in-the-loop RL

## Data Sourcing Strategy

**Principle: Literature-first.** We extract every data point possible from published papers, benchmarks, and datasets before considering any self-collected data. Self-collection is a last resort to fill critical gaps.

### Primary Sources: Published Papers & Benchmarks

**Papers with published human completion times** (highest quality — use directly):
- **FurnitureBench** (Heo et al., 2023): Human demonstration times for furniture assembly
- **IKEA Furniture Assembly Env** (Lee et al., 2021): Human solve times documented
- **RoboCerebra** (2025): Trajectory lengths and task decompositions with timing
- **VLABench** (2025): Episode lengths for primitive vs composite tasks
- **DROID** (2024): Demonstration collection times logged (76k demos, 86 tasks)
- **Open X-Embodiment** (2023): Some constituent datasets include human timing
- **ALOHA/ACT** (Zhao et al., 2023): Teleoperation demo times = human baselines
- **Mobile ALOHA** (2024): Demo collection times documented

**Papers with success rates + well-defined tasks** (human time estimable with high confidence):
- **OpenAI Dactyl** (2018, 2019): 60% on 15-move Rubik's Cube — human solve time is well-studied (~3-5 min for casual solver)
- **RT-1, RT-2** (2022, 2023): Extensive success rate tables, single-step tasks with clear descriptions
- **SayCan** (2022): Multi-step kitchen tasks with step-by-step breakdown
- **π0, π0.5, π0.6** (2024-2025): Task videos + success rates for laundry, cleanup, etc.
- **HIL-SERL** (2024): Controlled evaluation with success rates
- **Code as Policies** (2023): LLM-planned multi-step tasks with descriptions

**Lower-quality sources** (include with caveats, annotated as `public_demo`):
- **Figure 02 at BMW** (2025): "10-hour shifts" — impressive but success rate unverified
- **Tesla Optimus** (2024-2025): Public demos, no published success rates
- **1X NEO** (2025): Consumer demos with teleoperation fallback
- **Circus CA-1** (2025): Commercial deployment, limited published metrics
- **Stanford cooking robot** (2024): Individual task success rates, full-meal metric unclear

### Gap Assessment (done AFTER literature extraction)
After building the dataset from literature, we assess:
1. Are there time periods with no frontier data points? → Search harder for papers from that era
2. Are human-time estimates for frontier points well-calibrated? → If critical frontier points rely on rough guesses, those are candidates for self-timing
3. Is the plot telling a coherent story? → If ambiguous, identify which specific data points would resolve it

### Self-Collection (only if needed)
If the literature review reveals critical gaps in human-time calibration for key frontier points, we can plan targeted self-timing of specific household tasks. But this is Phase 2 — we don't plan it until we see where the literature-based dataset falls short.

## Methodology

### Step 1: Literature Survey & Data Extraction
For each system/paper, record:
- **Paper/demo name, authors, date** (use release/arxiv date)
- **Robot hardware** (arm type, gripper, sensors)
- **Task description** (natural language)
- **Number of subtasks / primitives** (secondary metric)
- **Reported success rate** (and number of trials)
- **Sim vs. real** (flag; prefer real-world; show sensitivity with/without sim)
- **Human-equivalent time estimate** (our core metric)
- **Human time source** — one of: `published_baseline`, `self_timed`, `estimated`, `decomposition`
- **Task category** (tabletop manipulation vs. mobile manipulation)
- **Whether this was the "frontier" for its time** (was it the most complex thing reliably done?)
- **Data quality tier** — `benchmark` (controlled eval with N trials), `paper_demo` (paper with reported numbers), `public_demo` (video/press demo, no formal eval)

Store this as a structured CSV/JSON dataset.

### Step 2: Human Time Calibration
For estimating human-equivalent time, use this priority order:
1. **Published human baselines** (from paper) — highest quality, use directly
2. **Self-timed** (you doing the task) — strong calibration for household tasks
3. **Decomposition** — break into subtasks, use published/self-timed subtask times, sum
4. **Expert estimation** — for tasks we can't replicate, use reasonable estimates with documented rationale

Each data point gets a `human_time_source` tag and a confidence level (`high`, `medium`, `low`).

Document calibration methodology transparently in the blog post.

### Step 3: Frontier Identification
For each time period (roughly quarterly from 2016-2025), identify the **frontier system** — the one completing the longest-horizon task at ≥50% success rate. This gives us the "envelope" curve.

Key decision: **Do we plot every system, or just the frontier?**
- Main plot: frontier envelope (longest task at ≥50% success over time)
- Supporting plot: all data points colored by category, with frontier line overlaid

### Step 4: Visualization
Generate plots using Python (matplotlib/plotly):

1. **Main plot** (METR-style): X-axis = date (2016-2025), Y-axis = human-equivalent task duration (log scale, seconds to hours). Frontier envelope line with individual data points. Two series: tabletop manipulation, mobile manipulation.

2. **Combined vs. separate**: Plot both categories together and separately. Determine which tells a clearer story.

3. **Comparison overlay**: Overlay METR's LLM agent horizon line on the same plot to enable direct cross-domain comparison.

4. **Sensitivity plot**: Show how the frontier changes at different success thresholds (30%, 50%, 80%).

### Step 5: Analysis & Narrative
- Is there exponential growth? What's the doubling time?
- How does the robotics horizon compare to LLM agents?
- What drove the biggest jumps? (hardware, algorithms, foundation models, sim-to-real?)
- Where are the plateaus and why?
- What does extrapolation suggest for the next 2-3 years?
- Caveats and limitations

## Key Methodological Challenges & How to Address Them

| Challenge | Approach |
|---|---|
| **Hardware varies wildly** | Note hardware but don't filter by it — we care about what any robot can do at time T |
| **Sim vs. real gap** | Flag sim-only results; prefer real-world; show sensitivity with/without sim |
| **Success rate definitions vary** | Record reported metric verbatim + our interpretation; use 50% threshold for main plot |
| **"Demo" vs. "benchmark"** | Include both but annotate. A YouTube demo with cherry-picked results gets flagged differently than a 100-trial benchmark |
| **Human time estimation is subjective** | Document methodology, provide ranges, do sensitivity analysis |
| **Some tasks are narrow, some are general** | Focus on the specific task demonstrated, not claimed generality |
| **Multi-step tasks: what counts as "one task"?** | The full task as described/demonstrated. "Cook a meal" is one task even if it has 20 subtasks |

## Deliverables (in this repo)

### 1. `research_plan.md`
This document (expanded version of this plan with full references).

### 2. `data/manipulation_horizons.csv`
Structured dataset with columns:
```
date, system_name, paper_url, task_description, human_time_seconds, 
success_rate, num_trials, num_subtasks, category, sim_or_real, 
hardware, is_frontier, notes
```

### 3. `scripts/plot_horizons.py`
Python script to generate all visualizations from the CSV data.

### 4. `scripts/analyze.py`
Statistical analysis: exponential fit, doubling time estimation, comparison with METR data.

### 5. `draft/blog_post.md`
Written blog post draft with embedded figures, narrative analysis, and discussion.

### 6. `figures/`
Generated plot images (PNG/SVG).

## Verification Plan

1. **Data validation**: Cross-check every data point against the original paper — success rate, task description, and any published human times
2. **Human time calibration**: Each frontier data point should have human time from either a published baseline or self-timing; flag any that rely purely on estimation
3. **Plot sanity check**: Verify the frontier line is monotonically non-decreasing and that dates align with paper release dates
4. **Exponential fit quality**: Report R² and confidence intervals on doubling time estimates
5. **Sensitivity analysis**: Show how the plot changes when (a) excluding sim-only results, (b) using different success thresholds, (c) varying human time estimates by ±50%
6. **Run scripts**: `python scripts/plot_horizons.py` and `python scripts/analyze.py` should execute without errors and produce figures

## Execution Order

**Phase 1: Literature-based dataset (do first, go as far as possible)**
1. Create repo structure (`data/`, `scripts/`, `draft/`, `figures/`)
2. Build the CSV dataset from published papers (~40-60 data points), extracting success rates, task descriptions, and any published human times
3. Estimate human-equivalent times for data points lacking published baselines, documenting rationale and confidence level for each
4. Write the plotting script and generate initial visualizations
5. Write the analysis script (exponential fitting, doubling time)
6. Draft the blog post with embedded figures and narrative

**Phase 2: Gap assessment (only if Phase 1 reveals critical issues)**
7. Review the plot and identify any frontier data points where human-time confidence is low
8. Determine if self-timing specific tasks would meaningfully change the story
9. If yes, design a minimal self-timing protocol for those specific tasks

**Phase 3: Finalize**
10. Iterate on visualizations and narrative
11. Commit and push
