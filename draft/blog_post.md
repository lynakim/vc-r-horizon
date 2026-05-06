# The Task Horizon for Robotic Manipulation: A Meta-Analysis of Published Results

*How long a task can robots reliably complete — and how fast is that improving?*

## Introduction

METR's [time horizon analysis](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) produced one of the most important charts in AI: the length of tasks that frontier LLM agents can complete with 50% reliability has been doubling every ~7 months. Their follow-up, [How Does Time Horizon Vary Across Domains?](https://metr.org/blog/2025-07-14-how-does-time-horizon-vary-across-domains/), extended this to web browsing, self-driving, and competitive programming — finding exponential growth everywhere, just at different rates.

One domain conspicuously absent from their analysis: **robotic manipulation**. Can we build the same chart for physical robots?

We set out to answer this question by surveying a decade of robotic manipulation research (2016–2025), extracting the longest task each frontier system could complete at ≥50% success, and measuring that task in human-equivalent time. The result is, to our knowledge, the first task horizon plot for robotics that aggregates across the field at this scale.

**A note on what this is.** This study is a meta-analysis: we aggregated published numbers from 43 papers, technical reports, and benchmarks; we did not run a single new robot trial. METR's own studies are not meta-analyses — they evaluate every model on a shared, controlled task suite with measured human baselines, which is the gold standard for this kind of analysis. We can't replicate that for robotics today because the underlying infrastructure doesn't exist (more on why below, and on what it would take to build it in [On the future of robot eval](#on-the-future-of-robot-eval)). What we can do is rigorously aggregate what's already been published, document every judgment call, and publish the dataset so disagreements can be re-run rather than just argued.

A caveat upfront: wide-scale unified evaluation is a harder problem for robotics than it is for LLMs. Manipulation results come in too many different shapes — different hardware, different task setups, different scoring protocols — to be made consistent the way LLM evaluations can be. That's a structural feature of the field, and it shapes everything that follows. We've done our best to extract a consistent signal from what's available; we don't claim the result is perfect, and we fully expect individual rows to be debated. The next section explains why the inconsistency is unavoidable for now.

## Why this is harder than the LLM version

The ideal way to do a study like this is the way METR did theirs: take many frontier systems, run them on the same task suite under the same scoring protocol, contract human experts to baseline the same tasks, and read the trend line off the resulting matrix. None of that infrastructure exists for robotic manipulation, and it's not just an oversight — the structure of the field makes it nearly impossible to assemble.

When a new robotics paper comes out, it typically introduces a new policy *and* a new hardware platform *and* a new task set *and* a new evaluation protocol, all at once. There is no equivalent of "swap GPT-4 for Claude on the same prompt and re-score" — you cannot run π0's policy on Dactyl's hand on Mobile ALOHA's tasks, because every layer of the stack is bespoke. The result is that almost every dimension that matters for measuring capability varies from paper to paper:

- **Hardware varies.** Single-arm, bimanual, mobile bimanual, dexterous five-fingered hand, parallel-jaw gripper. A "manipulation" success on one platform is not interchangeable with one on another.
- **Settings vary.** Lab tabletop with controlled lighting, a researcher's kitchen, a novel home the robot has never seen. The same policy can swing dozens of percentage points in success rate across these conditions.
- **Tasks vary.** Rigid pick-and-place, deformable folding, articulated-object opening, multi-step kitchen cleanup. There is no shared task suite that frontier systems are routinely benchmarked on.
- **Policies vary, and so do their training distributions.** A policy fine-tuned on 50 demonstrations of the exact eval task is not directly comparable to a generalist policy evaluated zero-shot on it, even if both report the same headline number on the same task.
- **Success criteria vary.** Some papers report binary task completion ("did the robot finish the full task, yes/no"). Others report partial-credit rubric progress ("on average, how far through the task did the robot get"). A 0.7 rubric score and a 70% success rate are not the same number, and treating them as such would inflate the recent frontier substantially.
- **Trial counts vary.** Ten trials in some papers, a hundred in others, a thousand in a few. The headline success rates are not equally well-measured.
- **Even "the same task" varies.** π0.6's "fold a single shirt" and π0's "fold laundry from a basket" are both reported as folding, but they are very different evaluations. We have to decide, row by row, which version of the task the headline number is actually measuring.

Each of these on its own would be manageable; together, they mean we're never comparing the same thing twice. Shared simulation benchmarks do exist — LIBERO, CALVIN, ManiSkill, RLBench — and frontier VLAs do report on them, but the longest-horizon suites top out at tens of seconds per task and are largely saturated by current generalist policies, while the real-world frontier we're tracking is at five to fifteen minutes. The field's recent responses to this gap — [AutoEval](https://arxiv.org/abs/2503.24278) (Berkeley, 2025), [RoboArena](https://arxiv.org/abs/2506.18123) (2025), and [ManipulationNet](https://manipulation-net.org/) — all work around the missing shared task suite rather than build a harder one (see [On the future of robot eval](#on-the-future-of-robot-eval)). Until something like that lands and is widely adopted, any longitudinal study of robotic manipulation capability is going to involve the kind of cross-evaluation stitching we do here.

A concrete example of this gap. We tried to replicate METR's per-model methodology directly: for each frontier paper, fit a logistic regression of `P(success) ~ log(human_time)` across that paper's tasks, read off the duration at which the curve crosses 70% reliability, and use that fitted horizon (with a within-paper bootstrap CI) as the paper's data point. To pull this off cleanly, a paper needs four things at once: (1) at least four tasks evaluated under the same policy, (2) those tasks spread across at least one order of magnitude in human-equivalent time, (3) success rates spread across the threshold (so the horizon is interpolated, not extrapolated), and (4) enough trials per task that each rate isn't a coin flip. Of the five most multi-task-rich papers in our dataset (ALOHA Unleashed, Mobile ALOHA, Gemini Robotics specialists, π0.6, FurnitureBench), exactly one — ALOHA Unleashed — produced a clean fit. The others either had a single noisy row dragging the bootstrap CI by orders of magnitude, or violated the model's monotonicity assumption outright (Gemini Robotics' specialist hit 100% on its longest task and failed on its shortest, because the lab curated a separate dataset for each task — longer ≠ harder when training is task-specific). The structural reason is what the bullet list above describes: robotics papers don't sweep duration as an experimental design variable the way HCAST does. They vary state randomness, language complexity, or object diversity instead, and a logistic over duration just isn't what those experiments are measuring. We'd consider this one of the central methodological challenges of doing a study like this in robotics, and a reason to be excited about whatever benchmark eventually does sweep duration the way HCAST does.

Given that, we made consistent choices and documented them. We applied the same inclusion bar to every row (real hardware, autonomous control, ≥10 real-world trials, success rate from a documented protocol). We tracked binary vs. rubric success in a dedicated column rather than averaging them together. We treated sim and real-world results as separate frontiers. We recorded human-equivalent time with explicit confidence tiers, and used measured baselines where we could.

What we cannot do is make the underlying evaluations comparable in the way METR's are. There are judgment calls on essentially every row, and a reasonable analyst would draw the frontier somewhat differently than we have. The dataset, the inclusion criteria, and the per-row provenance are all in the repository so that anyone who disagrees with a specific call can swap it out and re-run the analysis. We think the headline shape — exponential growth, ~15-month doubling at ≥50%, multi-year stalls broken by paradigm shifts, a real acceleration from 2024 — survives most reasonable variations on those calls. The exact numbers will not.

## Methodology

### The Metric

Following METR, we define the **manipulation task horizon** as:

> The duration (in human-equivalent time) of the longest task that a robotic manipulation system can complete with ≥50% success rate.

**Human-equivalent time** is how long a competent human would take to perform the same task. This enables direct comparison with METR's LLM agent results, which use the same unit.

We treat task duration as an **independently useful feature** — not as a proxy for task difficulty. Task difficulty is multidimensional (rigid vs. deformable objects, number of subtasks, degree of spatial reasoning required, etc.) and is not what we're directly measuring here. Duration is a meaningful capability metric on its own: it captures how long a robot can sustain reliable performance, regardless of whether a longer task is "harder" in any particular sense. The reason this matters operationally: per-step failure probability compounds over the length of a task, so each additional unit of autonomous duration directly determines how much human supervision a deployment requires. Task horizon is, in that sense, a fairly direct measure of the operational-cost axis of robot deployment, even when it doesn't tell you which specific tasks are harder than others.

### Meta-Analytic Extraction

This study is a meta-analysis. We surveyed 43 robotic manipulation rows from published papers, benchmarks, and demonstrations spanning 2016–2025 and re-aggregated their reported numbers under a single inclusion bar and a single set of conventions. We did not run any new robot trials. For each row, we recorded:

- The longest task demonstrated at ≥50% success
- The reported success rate and number of evaluation trials
- Human-equivalent completion time (from published baselines where available, otherwise estimated)
- Whether the evaluation was a controlled benchmark, paper demo, or public demo
- The robot hardware and whether it was simulated or real-world

We categorized systems into **tabletop/fixed-base manipulation** (arm mounted on table) and **mobile manipulation** (robot navigates + manipulates).

### Inclusion Bar

For a paper to be included as a frontier-eligible row in the dataset, three criteria must all hold:

1. **Real hardware, autonomously evaluated.** The headline evaluation ran on a real robot under autonomous control. Sim-pretrained policies count as real (the substrate of training doesn't matter). Teleoperated demos do not, even when labeled autonomous in marketing.
2. **Systematic evaluation.** Success rate from a documented protocol in a paper or technical report — not a video, press release, or blog post.
3. **N ≥ 10 real-world end-to-end trials.** Sim trials don't count toward this threshold.

Systems that fail any of these — Tesla Optimus, 1X NEO, Apptronik Apollo, Sanctuary Phoenix, Figure AI's Helix product line — are excluded from the frontier curve. The full inclusion criteria, including audit conventions for how individual rows are recorded, are documented in `inclusion_criteria.md`.

### Binary vs. rubric success

Different papers report success differently. We track this distinction explicitly via a `success_type` column:

- **Binary success**: fraction of trials where the full task was completed (e.g., HIL-SERL "100/100 RAM insertions").
- **Rubric progress**: average partial-credit score on a multi-point rubric (e.g., π0 reports "~0.7 progress on a 5-point laundry rubric"). A 0.7 rubric score is *not* the same as a 70% binary success rate — it can be high even when no episode fully succeeded.

Both are admitted to the frontier and the chart plots them on the same axis. We surface the distinction in row metadata and in the analysis below — it has a real impact on how the recent (2024–2025) part of the curve should be read.

### Frontier Definition

The **canonical frontier is defined over real-world systems only**, at ≥50% success. Sim-only results are still plotted (as gray triangles, distinct from real-world points) and used in a sensitivity check, but they do not anchor the envelope. Mixing sim and real on a single capability frontier inflates apparent progress: a sim-only success rate doesn't tell you what the field can deliver on physical hardware, where the dominant difficulty lives.

### Reliability Threshold

Like METR, we use 50% success as the primary threshold. We also present sensitivity analysis at 70%, 80%, 90%, and 95% thresholds. (For the ≥30–60% real-world frontier, no real systems in those brackets advance the envelope past the ≥50% line, so all four thresholds yield the same frontier in this dataset.)

### Per-row caveats

Beyond the structural heterogeneity discussed above, three sources of per-row noise are worth flagging explicitly:

1. **Human time estimation.** METR contracted human experts to time each task. We rely on published baselines where available and estimates elsewhere, recorded with confidence tiers in the dataset.
2. **Success rate definitions vary.** Some papers report task-level success, others report per-step success. We use the most appropriate whole-task metric available and note when we had to choose.
3. **Demo vs. benchmark.** Some data points come from rigorous 100+ trial evaluations; others from paper demos with ~20 trials. We mark the data quality tier on each row.

## Results

### The Main Plot

![Robotic Manipulation Task Horizon Over Time](../figures/main_horizon_plot.png)
*Figure 1: The longest robotic manipulation task completed at ≥50% success rate, measured in human-equivalent time. The frontier line connects systems that set new records for task complexity.*

The frontier shows three distinct phases:

**Phase 1: Single-step grasping (2016–2018).** The earliest systems could grasp a single object (~4–5 seconds of human-equivalent time). Levine et al., Dex-Net, and QT-Opt all sat in this band. The notable cap on the period was OpenAI's Dactyl Block (2018), which reoriented a block using dexterous in-hand manipulation — a ~10-second task, but one requiring unprecedented dexterity for the time.

**Phase 2: LLM planners push to ~2 minutes (2022).** Real-world progress between Dactyl and SayCan was carried by short tabletop tasks — Form2Fit's 30-second kit assembly (94%, Oct 2019) is the only ≥50% frontier point in that window — and then the frontier jumped when LLM-driven planners arrived. SayCan (90s, Apr 2022), Inner Monologue (90s, Aug 2022), and Code as Policies (120s, Sep 2022) used language models to chain primitive skills into multi-step kitchen and tabletop tasks. The behaviors at the bottom of the stack were still short, but the field had figured out how to compose them.

**Phase 3: The foundation model era (2024–2025).** ALOHA Unleashed pushed binary-success multi-step manipulation to 120s in late 2024. Then π0 reported ~70% partial-credit progress on **5-minute** post-train tasks — folding towels, clearing tables, assembling boxes. π0.5 (2025) reported ~70% partial-credit progress on **12-minute** kitchen and bedroom cleaning tasks in novel homes. π0.6 achieved **97% binary success on a single-shirt fold** (200s) and ~90% partial-credit progress on espresso-making. These systems are generalists — they can fold laundry, clean kitchens, and sort groceries, not just execute one rehearsed skill. *Important nuance: the multi-minute extension of the recent frontier is carried by partial-credit rubric scores, not binary task completion. We discuss this in detail in [Binary frontier vs. rubric frontier](#binary-frontier-vs-rubric-frontier).*

Notably, Mobile ALOHA's cooking shrimp demo (often cited as a breakthrough) only achieved 40% autonomous success — below our 50% threshold. Its most reliable long task was "use two-door cabinet" at 85% (~90 seconds). The viral 3-course meal demo was actually teleoperated, not autonomous. This illustrates why rigorous success rate tracking matters.

### Two stalls, two breakthroughs

The frontier doesn't grow smoothly — it stalls, then jumps. Two stalls are visible in the post-2018 data:

**The 2018–2022 single-step stall.** From Dactyl Block (10s, mid-2018) through Form2Fit (30s, Oct 2019) to SayCan (90s, Apr 2022), no real-world system at ≥50% pushed past ~30 seconds, and the 2019–2021 progress was confined to short single-step tabletop tasks (Form2Fit kit assembly at 94%; MT-Opt multi-task lifting at 89%; IBC precise insertion at 87%; RGB-Stacking 3-block stacks at 82%). During this period the field made enormous progress on other axes — RT-1 achieved 97% success on 700+ single-step tasks, RT-2 demonstrated emergent semantic reasoning, the Open X-Embodiment project aggregated 1M+ trajectories across 22 robots — but each individual task that any of these models executed was still a single pick-and-place taking ~8 seconds. 2020–2023 was the era of **scaling breadth, not depth**. (Note: "short" and "long" here refer strictly to duration — we're not making a claim that the longer tasks in this dataset are harder in any well-defined sense, only that sustaining reliable performance over longer durations is the capability we're tracking.)

**The 2022–2024 ~2-minute ceiling.** After SayCan / Inner Monologue / Code as Policies pushed the frontier to ~120s in 2022, the next jump didn't come for two years. We were skeptical of this when we first saw it, so we did a focused literature search across 2020–2024: every major manipulation paper from CoRL, RSS, and ICRA in that window, surgical robotics (autonomous suturing, anastomosis), industrial deployments (Pickle, Symbotic, Berkshire Grey), and agricultural picking. **No paper combines a ≥240s task at ≥70% success with N≥10 trials and full autonomy** before late 2024. The closest contenders all fail one criterion: SpeedFolding gets 93% but at only ~120s/garment; Mobile ALOHA's 95%+ tasks are <60s; FurnitureBench's 900s tasks sit at 15%; YAY Robot's full-task success is 5–65%. Even surgical robotics — where individual procedures naturally run multi-minute — didn't produce a rigorous full-procedure ≥240s + ≥70% + N≥10 result before SutureBot in October 2025, which itself opens by saying *"a fully autonomous suturing pipeline had not yet been demonstrated on physical hardware"* before their work. The π0 authors are blunt about this in their own paper: *"To our knowledge, our work demonstrates the longest dexterous tasks in the end-to-end robot learning literature."*

Each stall ended when a new architecture arrived: LLM-as-planner in 2022 (chaining primitives without learning the full sequence end-to-end), and VLA foundation models in 2024 (learning the full sequence end-to-end at scale). Both stalls in retrospect look like the field needing the right substrate to push past the previous limit, not a lack of effort during the gap.

### Robot vs. LLM Agent Comparison

![Robot Manipulation vs. LLM Agent Task Horizons](../figures/robot_vs_llm_comparison.png)
*Figure 2: Robot manipulation frontier compared to METR's approximate LLM agent horizon. Both use human-equivalent time at 50% reliability.*

The comparison reveals:
- **LLM agents are an order of magnitude ahead** on task horizon: METR's stated anchor is Claude 3.7 Sonnet at ~60 minutes (Feb 2025), against ~10 minutes for the robotic manipulation frontier in the same window
- **Robot manipulation is growing more slowly** — the overall doubling time is **~14.9 months** (95% CI: 12.1–18.6 months) vs. METR's ~7 months for LLM agents, making it roughly **2.1x slower**
- The robotics curve is **more stepped** than the LLM curve — progress comes in discrete jumps when new paradigms emerge (LLM planners → foundation models), rather than the smooth exponential of LLM scaling

We avoid hand-eyeballing per-model points for METR's curve (an earlier draft did this and the values didn't match METR's published numbers). Instead the LLM line is anchored on the one quantitative value METR explicitly states in their March 2025 post — Claude 3.7 Sonnet at ~60 minutes — and projected with their reported 7-month doubling.

The gap makes intuitive sense: LLM agents operate in the digital world where execution is instant and errors are cheaply recoverable. Robots must plan, perceive, and actuate in the physical world where every motion takes real time and mistakes can be catastrophic.

### Category Breakdown

![Task Horizon by Category](../figures/category_comparison.png)
*Figure 3: Tabletop manipulation (left) vs. mobile manipulation (right). Mobile manipulation shows steeper recent growth.*

The split reveals different dynamics:
- **Tabletop manipulation** has a longer history and a more gradual frontier, anchored on early grasping benchmarks (Levine, Dex-Net, QT-Opt) and Dactyl Block before LLM planners and foundation models arrived
- **Mobile manipulation** is newer (first frontier point in 2022) but is on a similar exponential — doubling time ~19 months — driven by the recent wave of SayCan, Mobile ALOHA, and π0.x systems
- When combined, the story is cleaner than when separated — the overall frontier is what matters most

### Sensitivity to Success Threshold

![Sensitivity Analysis](../figures/sensitivity_thresholds.png)
*Figure 4: How the frontier changes at different success rate thresholds (50%, 70%, 80%, 90%, 95%).*

At ≥50% (the canonical threshold) the frontier traces early grasping → Dactyl Block → Form2Fit → SayCan / Inner Monologue / Code as Policies → ALOHA Unleashed → π0 → π0.5. At ≥70% the frontier loses SayCan and Code as Policies (both below 70%) but the overall shape is similar. At ≥80–95% the frontier is the cleanest fit (R² ≈ 0.95), running through ALOHA Unleashed's gear-insertion, Gemini Robotics' lunch-box, and π0.6's single-shirt fold. The ≥30–60% thresholds yield the same frontier as ≥50% in our data — no real-world system in the 30–49% bracket extends the envelope past the ≥50% curve. (The would-be ≥30% additions — IKEA Furniture Assembly, RoboCerebra, VLABench — are all sim-only.)

## Quantitative Analysis

### Doubling Time

We fit a log-linear exponential model to the frontier — i.e., we regress log(task duration) on date — and report R² and the implied doubling time. Fitting the canonical real-world ≥50% frontier gives:

| Scope | Doubling Time | R² | N |
|---|---|---|---|
| All categories combined (real-world, ≥50%) | **14.9 months** (95% CI: 12.1–18.6) | 0.92 | 11 |
| Tabletop only | 16.0 months | 0.92 | 7 |
| Mobile manipulation only | 18.8 months | 0.54 | 4 |

The overall doubling time of ~14.9 months places robot manipulation between METR's findings for LLM agents (~7 months) and self-driving (~20 months for Tesla FSD), but closer to self-driving. The mobile-only fit is much noisier (R² 0.54 on 4 points), so we don't read much into the per-category split.

The point estimate is stable across alternative framings: ≥80% gives 20.7 months (R² 0.92, N=12), ≥95% gives 15.4 months, ≥70% gives 16.8 months. Including sim systems alongside real ones gives the same 14.9 months / R² 0.92. The headline finding: **the doubling time is in a 14–20 month band** depending on threshold, with the high-reliability ≥80% frontier giving the cleanest fit. At ≥80%, the frontier runs through Dactyl Block, Diffusion Policy (88% / 45s, Feb 2023), ACT/ALOHA (85% / 120s, Mar 2023), ALOHA Unleashed's gear-insertion (95% / 80s, Oct 2024), Gemini Robotics' lunch-box (100% / 120s, Mar 2025), and π0.6 (97% / 200s, Nov 2025) — a near-straight log-linear progression.

### Binary frontier vs. rubric frontier

A structural issue surfaced in our methodology audit: modern long-horizon manipulation papers — π0, π0.5, GR00T N1, Gemini Robotics 1.5 — report **partial-credit rubric scores** rather than binary task success. A 0.7 rubric score on a 5-point laundry rubric is not the same as 70% binary task completion: it averages partial successes (e.g., the robot fully folded 3 of 5 items in a typical episode) and can be high even when *no* episode fully succeeded.

We track this distinction explicitly via the `success_type` column. The implication for the frontier curve:

- The **post-2024 ≥50% frontier extension is carried by rubric scores, not binary success.** π0's 5-min laundry folding (rubric ~0.7) and π0.5's 12-min bedroom cleanup (rubric ~0.7) are the rows that push the curve past 200s.
- If we restricted the frontier to **binary success only**, the longest reliable point through 2025 is π0.6's single-shirt fold at 200s / 97% (Nov 2025).
- The **≥80% binary frontier** shows steady progress without the rubric extension: ALOHA Unleashed (gear insertion 95% / 80s, Oct 2024), Gemini Robotics (lunch-box pack 100% / 120s, Mar 2025), and π0.6 (single-shirt fold 97% / 200s, Nov 2025).

This means the field's recent narrative ("we can do 10-minute household tasks") rests primarily on partial-credit rubrics, not full task completion. Both are progress, but they measure different things — and the divergence between them is recent and narrow. The binary and mixed frontiers are identical from 2016 through October 2024, splitting only at the last two rubric points (π0 in Oct 2024 and π0.5 in Apr 2025). The recent rubric run could be read as "rapid generalist progress" or as "incompatible yardsticks make the trend hard to read" — and both readings are partly right, which is why we carry both curves rather than picking one. A consistent scoring convention for long-horizon tasks — a community-level shared definition of "fully completed" for canonical tasks like a folded basket of laundry or a clean kitchen — would resolve the ambiguity. Until that exists, anyone repeating this analysis in a year will face the same problem multiplied by however many new generalist papers ship.

### Comparison with METR Domains

| Domain | Doubling Time | Source |
|---|---|---|
| LLM agents (software/reasoning) | ~7 months | METR |
| LLM agents (recent, 2024–25) | ~4 months | METR |
| Web browsing (WebArena/OSWorld) | ~7 months | METR |
| **Robot manipulation (this work)** | **~14.9 months** | **This analysis** |
| Self-driving (Tesla FSD) | ~20 months | METR |

Robot manipulation is the second-slowest domain — roughly 2.1x slower than LLM agents but modestly faster than self-driving. This likely reflects the compounded difficulty of the physical-world feedback loop: every iteration requires real hardware, real sensor data, and real actuation, making the cycle time for improvement fundamentally longer than in purely digital domains.

## What's Driving the Recent Acceleration?

The jump from 2024 onward is driven by three converging trends:

1. **Vision-Language-Action (VLA) models.** π0 and its successors combine internet-scale vision-language pretraining with robot action prediction, enabling end-to-end learning of long sequences and zero-shot generalization to new tasks and environments. This is the substrate that broke the 2022–2024 ~2-minute ceiling.

2. **Co-training across embodiments.** Training on data from multiple robot types (the Open X-Embodiment insight) produces more robust policies that handle the variability of real-world tasks.

3. **Bimanual and mobile platforms.** ALOHA and Mobile ALOHA showed that relatively low-cost bimanual setups can tackle tasks (cooking, folding) that were previously out of reach. The hardware got cheaper while the policies got better.

## Related Work

Several parallel efforts inform this analysis:

- **METR's own criticisms apply here too.** METR has acknowledged that human time estimation is noisy (~80% of baselines fall within 3x of "true" task length), and that their tasks don't reflect full real-world complexity. These issues are amplified for robotics, where we lack METR's controlled evaluation infrastructure. See [MIT Technology Review's analysis](https://www.technologyreview.com/2026/02/05/1132254/this-is-the-most-misunderstood-graph-in-ai/) for a thorough discussion.

- **Epoch AI** found a [100x compute gap](https://epoch.ai/data-insights/compute-for-robotic-manipulation) between frontier AI trends and robotics — with data scarcity (not compute) as the bottleneck. Their [2026 robot capability assessment](https://epoch.ai/blog/where-autonomy-works-evaluating-robot-capabilities-in-2026) found robots work 3–10x slower than humans and struggle with novel objects without retraining.

- **ManipulationNet** ([manipulation-net.org](https://manipulation-net.org/)) is building standardized hardware kits and distributed evaluation to create a "historical record of robotic manipulation capability" — the closest analog to METR for robotics, but still in early stages.

## Limitations

1. **This is a meta-analysis, not a unified evaluation.** Every row is somebody else's reported number, extracted under our conventions and inclusion bar but not re-measured. We don't have shared tasks, shared hardware, or shared scoring across rows. METR's studies are not meta-analyses, and the methodology gap is real — see [On the future of robot eval](#on-the-future-of-robot-eval) for what closing it would take.

2. **Publication and selection bias.** Authors choose which tasks to publish success rates for, and unsuccessful long-horizon attempts are systematically underreported. We may also be missing systems that pushed the frontier but weren't widely cited or didn't report success rates in a form we could include.

3. **Small frontier sample size.** The canonical frontier has 10 points spanning ~10 years. The exponential fit is suggestive but not definitive — the bootstrap CI (11.9–18.0 months) reflects the small N.

4. **Heterogeneous evaluations.** Unlike METR, we cannot evaluate all systems on identical tasks. Hardware, evaluation protocols, and success criteria differ across every data point.

5. **Human time estimation.** Some human-equivalent times are estimated rather than measured. We mark these in the dataset with confidence levels. METR themselves found this estimation is noisy even with controlled conditions.

6. **"Task horizon" ≠ "useful work."** As critics of METR's approach have noted, a 15-minute task horizon doesn't mean robots can replace 15 minutes of human work. Real tasks involve variability, error recovery, and context that benchmarks don't capture.

7. **Task length is one capability axis, not the only one.** The horizon metric captures temporal extension — how long the robot can sustain a coherent task. It does not capture object generalization, robustness across novel environments, in-hand dexterity, error recovery, or speed relative to humans. A robot that completes one 12-minute task at 70% rubric in a curated lab is not strictly more capable than one that completes 30-second tasks at 95% binary across 100 unseen kitchens — those are different kinds of progress, and a single duration-vs-time chart compresses them into one number.

## On the future of robot eval

There's a feedback loop between what a field benchmarks and what it builds. Shared benchmarks function as coordination mechanisms — they tell labs how they're being scored, and labs train toward what they're scored on. Coding and math became the first capabilities where LLMs reached frontier-human level in part because they were the capabilities the field built sharp benchmarks for: HumanEval, SWE-bench, MATH, AIME, GSM8K. The benchmarks reflected real demand, but they also pulled the field toward those capabilities — and away from ones that weren't measured as cleanly.

Robotics is missing the equivalent. There is no shared benchmark that frontier robotics labs are racing each other on, so there is no analogous coordinating force pulling the field toward a particular capability profile. Each lab pursues whatever its own evaluation suite measures, and — as this meta-analysis surfaced — even basic cross-paper comparison is hard.

### What kind of benchmark robotics needs

We think the gap-filling benchmark for robotics is **physical intuition**: a curated set of tasks that any reasonably coordinated human can do without practice, that exercise the physical reasoning robots need to be useful in the real world. Pour water into a cup. Stack mismatched objects without them tipping. Pick up a soft object without crushing it. Hand a tool to a person and get one back.

The closest analog on the LLM side is ARC-AGI — tasks that are easy for humans, deliberately resistant to the pretraining shortcuts the field is already optimized for, and general enough that solving them implies real capability rather than test-set memorization. The robotics version of this should not be contorted lab setups designed to flatter the most recent paper. It should be the physical-world equivalent of "any human could do this without preparation."

A benchmark like that does two things at once. It gives the field a yardstick that is hard to overfit because the underlying skills are general. And it makes the gap between robots and humans legible to people outside robotics: "the frontier system can't reliably pour water" reads differently than "the frontier system got 65% on RoboLab-V2."

### Generalization is one axis, not the only one

A second gap: we have no community-level way to measure cross-task generalization. Robotics papers report performance on tasks the policy was trained for. Very few report the same policy on tasks it wasn't trained for, on the same hardware. So we can't tell whether a system's apparent capability is broad physical understanding or careful per-task fine-tuning.

Generalization isn't always what matters. For high-throughput manufacturing or assembly, the opposite — extreme reliability on a narrow set of tasks at speed and precision — is the right thing to optimize. The same is true on the LLM side: a model deployed for contract review or medical coding doesn't need to be the most generalist system, it needs to be the most reliable one in its slice. A benchmark that only measured generalization would mislabel narrow excellence as failure.

But cross-task generalization on shared hardware is *independently useful to measure* — it determines whether a single robotic system can serve many use cases or has to be rebuilt for each one, and that distinction sits underneath most of the commercial bets the field is currently making. Right now no one can answer it rigorously, because no one publishes the data needed to. A serious robot eval should track generalization alongside narrow task horizon, not collapse them into one number.

### What such a benchmark would still miss

Even a clean benchmark for physical intuition and generalization would only measure one slice of the deployment gap. Real deployments aren't graded on whether a robot can autonomously fold a shirt — they're graded on whether it can ask the right clarifying question when the laundry includes something delicate, recover from its own mistakes without a human reset, hand a tool to a person and get one back, and gather context from a novel environment before deciding what to do. The gap between "robot completes 15-minute task at 70%" and "robot is useful in someone's home" lives largely off the duration axis — in context-gathering, error recovery, and human-robot collaboration. We see those as complementary frontiers, not substitutes.

### Why this hasn't happened yet

Six structural problems make rigorous robotics eval hard, and the meta-analysis hit all of them:

1. **Bundled papers.** Every paper introduces a new policy + hardware + tasks + eval at once. There is nothing to hold constant across rows.
2. **No shared task suite** that frontier labs are routinely benchmarked on.
3. **Hardware Cambrian phase.** Standardizing on one platform is premature; tracking it as a covariate is the realistic path.
4. **Real-world eval is slow.** N=10 is a lab afternoon; N=100 is a project. Physical trials do not parallelize the way API calls do.
5. **Scoring divergence.** Binary completion vs. partial-credit rubric, with no community-level definition of "fully complete" for canonical tasks like a folded basket of laundry.
6. **No funder.** Centralized eval — task suite, hardware fleet, human baselines, neutral lab — runs $5–20M/year. METR exists because someone funded METR.

These cluster into three asks for three audiences. **Researchers and benchmark builders** can solve the cheapest two (task suite, scoring conventions) through workshop-level coordination — no new money required, just convergence. CoRL, RSS, and ICRA could push it next cycle. **A new institution** is needed to actually run the eval — pooling real-world trials, tracking hardware as a covariate, decoupling policy submission from hardware ownership. The closest seeds today come at the problem from three different angles: [ManipulationNet](https://manipulation-net.org/) is building standardized hardware kits and a shared task suite directly; [AutoEval](https://arxiv.org/abs/2503.24278) (Berkeley, 2025) automates real-robot evaluation on the BridgeData WidowX setup so policies can be tested around the clock without operator effort, but defines no shared task list; and [RoboArena](https://arxiv.org/abs/2506.18123) (2025) skips standardization entirely, ranking policies via crowdsourced double-blind pairwise preferences across academic labs on DROID hardware. None yet has METR's rigor or scale, and none on its own resolves both the shared-task-suite and shared-difficulty-axis problems. **A funder** is needed to bankroll the institution: a frontier-lab consortium (the MLCommons playbook), a philanthropic foundation, or a public-sector vehicle (NIST, DOE, ARIA). Each is a different pitch.

### A call to the community

We're publishing this meta-analysis partly because writing it made vivid how hard trend-line analysis in robotics is to do well right now, and partly because we think the absence of shared eval infrastructure is the single biggest thing holding back the field's ability to know how fast it is actually moving. Capital allocation, research priorities, and the broader narrative around when robots become useful all hinge on that.

If you're a researcher with a multi-lab benchmark proposal, a foundation thinking about capability-tracking work, an agency thinking about robot capability as a measurement target, or a frontier lab willing to submit policies to third-party eval — we'd like to hear from you. The first version of this benchmark does not have to be perfect. It has to exist, and it has to start pulling the field's effort toward measuring the right things.

## Conclusion

The robotic manipulation task horizon has been doubling roughly every 15 months at ≥50% reliability, every 20 months at ≥80% — slower than LLM agents (~7 months) and modestly faster than self-driving (~20 months). But the smooth exponential masks a stepped history: two multi-year stalls (sub-15-second tasks through 2018–2022, sub-2-minute tasks through 2022–2024) broken by paradigm shifts (LLM planners in 2022, VLA foundation models in 2024). The recent extension to 10–15 minute tasks is carried primarily by partial-credit rubrics. By binary completion, the field is at ~3 minutes; by rubric, 10–15. Both are real progress, and both are how the field measures itself.

A reader could extrapolate to "1-hour household tasks by 2028" and "multi-hour tasks by 2030." We've drafted those numbers and removed them, because the line they extend is the least trustworthy part of this analysis: N=10, an 11.9–18.0 month CI, two of the last three frontier points carried by rubric, and a track record of step-functioning rather than smooth growth. The thing more likely to predict where robotics actually is in 2028 is whether the field gets a third architectural jump on the order of LLM-as-planner or VLA — and whether shared eval infrastructure exists by then to tell us if it has.

The signals to watch: whether the binary frontier closes the gap on the rubric frontier, whether generalist policies hold up under pre-registered third-party eval when that exists, and whether another architectural shift arrives before the current one stops paying out. If those happen, the trend is real. If they don't, the doubling time will look in retrospect like an artifact of a field that hadn't yet figured out how to measure itself.

## Dataset & Code

The full dataset (43 rows, with sources and confidence annotations) and all analysis code are available in this repository:
- `data/manipulation_horizons.csv` — structured dataset
- `inclusion_criteria.md` — how systems are admitted to the dataset
- `scripts/rebuild_dataset.py` — authoritative source of the dataset, with per-row provenance
- `scripts/plot_horizons.py` — visualization code
- `scripts/analyze.py` — statistical analysis

We welcome contributions: if you know of a system we missed or have better data for an existing entry, please open an issue or PR.

---

*This analysis was inspired by [METR's task horizon work](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) and their [cross-domain extension](https://metr.org/blog/2025-07-14-how-does-time-horizon-vary-across-domains/). We thank the robotics research community for publishing the benchmarks and evaluations that made this analysis possible.*
