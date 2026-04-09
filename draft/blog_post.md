# The Task Horizon for Robotic Manipulation: A METR-Style Analysis

*How long a task can robots reliably complete — and how fast is that improving?*

## Introduction

METR's [time horizon analysis](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) produced one of the most important charts in AI: the length of tasks that frontier LLM agents can complete with 50% reliability has been doubling every ~7 months. Their follow-up, [How Does Time Horizon Vary Across Domains?](https://metr.org/blog/2025-07-14-how-does-time-horizon-vary-across-domains/), extended this to web browsing, self-driving, and competitive programming — finding exponential growth everywhere, just at different rates.

One domain conspicuously absent from their analysis: **robotic manipulation**. Can we build the same chart for physical robots?

We set out to answer this question by surveying a decade of robotic manipulation research (2016–2025), extracting the longest task each frontier system could complete at ≥50% success, and measuring that task in human-equivalent time. The result is, to our knowledge, the first "METR-style" task horizon plot for robotics.

## Methodology

### The Metric

Following METR, we define the **manipulation task horizon** as:

> The duration (in human-equivalent time) of the longest task that a robotic manipulation system can complete with ≥50% success rate.

**Human-equivalent time** is how long a competent human would take to perform the same task. This enables direct comparison with METR's LLM agent results, which use the same unit.

### Defining Tasks and Subtasks

A key question for this analysis is: **what counts as a "task"?**

We define a **task** as the full end-to-end objective given to the robot — the complete job it must finish autonomously, from start state to goal state, without human intervention. "Fold a basket of laundry" is one task. "Clean the kitchen" is one task.

A **subtask** (or primitive) is a discrete manipulation action within that task — a single grasp, a single placement, a single wipe. "Pick up shirt," "fold shirt in half," and "place shirt on stack" are three subtasks of the laundry-folding task. The `num_subtasks` column in our dataset records how many such primitives compose each task.

This distinction matters because task duration can be misleading without it. Consider two 10-minute tasks:

- **Stacking 50 identical boxes** — 50 repetitions of the same pick-and-place primitive. Long duration, but low *compositional complexity*: each subtask is identical and independent, and failure on one box doesn't cascade.
- **Making an espresso** — grinding beans, tamping, extracting, steaming milk, pouring, cleaning. Fewer subtasks, but each is different, order-dependent, and errors compound (grounds in the portafilter can't be un-tamped).

Both take a human ~10 minutes, so they'd appear equivalent on our plot. But they represent fundamentally different levels of difficulty. We return to this issue in [Task Difficulty: Beyond Duration](#task-difficulty-beyond-duration) below.

### Data Collection

We surveyed 35 robotic manipulation systems from published papers, benchmarks, and demonstrations spanning 2016–2025. For each, we recorded:

- The longest task demonstrated at ≥50% success
- The reported success rate and number of evaluation trials
- Human-equivalent completion time (from published baselines where available, otherwise estimated)
- Whether the evaluation was a controlled benchmark, paper demo, or public demo
- The robot hardware and whether it was simulated or real-world

We categorized systems into **tabletop/fixed-base manipulation** (arm mounted on table) and **mobile manipulation** (robot navigates + manipulates).

### Reliability Threshold

Like METR, we use 50% success as the primary threshold. We also present sensitivity analysis at 30% and 80% thresholds.

### Important Caveats

This analysis differs from METR's in several key ways:

1. **No unified benchmark.** METR evaluated multiple models on the same task suite. In robotics, different systems are evaluated on different tasks with different hardware, so we're comparing across heterogeneous evaluations.
2. **Human time estimation.** METR contracted human experts to time each task. We rely on published baselines where available and estimates elsewhere.
3. **Success rate definitions vary.** Some papers report task-level success, others report per-step success. We use the most appropriate whole-task metric available.
4. **Demo vs. benchmark.** Some data points are from rigorous 100+ trial evaluations; others are from paper demos with ~20 trials.

We document the data quality tier for each point and discuss how these limitations affect the results.

## Results

### The Main Plot

![Robotic Manipulation Task Horizon Over Time](../figures/main_horizon_plot.png)
*Figure 1: The longest robotic manipulation task completed at ≥50% success rate, measured in human-equivalent time. The frontier line connects systems that set new records for task complexity.*

The frontier shows three distinct phases:

**Phase 1: Single-step grasping (2016–2018).** The earliest systems could grasp a single object (~4–5 seconds of human-equivalent time). The major breakthrough was OpenAI's Dactyl (2018), which reoriented a block using dexterous in-hand manipulation — a ~10-second task, but one requiring unprecedented dexterity.

**Phase 2: The Rubik's Cube leap (2019).** OpenAI's follow-up pushed the frontier to **4 minutes** — solving a Rubik's Cube with a dexterous robot hand at 60% success. This remains one of the most impressive single-task demonstrations in manipulation history, and it held the frontier for nearly five years.

**Phase 3: The foundation model era (2024–2025).** π0 (late 2024) broke through to **5-minute** multi-step tasks — folding towels, clearing tables, assembling boxes — at 75% success. π0.5 (2025) pushed to **10-minute** kitchen cleaning tasks, and π0.6 achieved **97% success on laundry folding** and >90% on espresso making. These systems are generalists — they can fold laundry, clean kitchens, and sort groceries, not just execute one rehearsed skill.

Notably, Mobile ALOHA's cooking shrimp demo (often cited as a breakthrough) only achieved 40% autonomous success — below our 50% threshold. Its most reliable long task was "use two-door cabinet" at 85% (~90 seconds). The viral 3-course meal demo was actually teleoperated, not autonomous. This illustrates why rigorous success rate tracking matters.

### The 2019–2024 Plateau

The most striking feature of the plot is the **five-year gap** between the Rubik's Cube (October 2019) and Mobile ALOHA (January 2024). During this period, enormous progress was made — RT-1 achieved 97% success on 700+ single-step tasks, RT-2 demonstrated emergent reasoning, and the Open X-Embodiment project aggregated 1M+ trajectories across 22 robots — but **none of these systems pushed the frontier on task horizon**.

Why? Because 2020–2023 was the era of **scaling breadth, not depth**. The field prioritized making robots that could do many short tasks (pick X, place Y, push Z) rather than one long task reliably. Foundation models like RT-1/RT-2 could follow hundreds of instructions but each instruction was a single pick-and-place taking ~8 seconds. The equivalent in the LLM world would be if models got better at answering many types of questions but never progressed beyond one-paragraph answers.

This breadth-first strategy was arguably necessary — you need reliable primitives before you can chain them into long tasks. But it means the task-horizon metric was flat for five years even as the field was making rapid progress on other axes.

### Robot vs. LLM Agent Comparison

![Robot Manipulation vs. LLM Agent Task Horizons](../figures/robot_vs_llm_comparison.png)
*Figure 2: Robot manipulation frontier compared to METR's approximate LLM agent horizon. Both use human-equivalent time at 50% reliability.*

The comparison reveals:
- **LLM agents are ~10–100x ahead** on task horizon, depending on the year
- **Robot manipulation is growing more slowly** — the overall doubling time is ~16.4 months (95% CI: 13.8–29.2 months) vs. METR's ~7 months for LLM agents, making it roughly **2.3x slower**
- The robotics curve is **more stepped** than the LLM curve — progress comes in discrete jumps when new paradigms emerge (dexterous RL → foundation models), rather than the smooth exponential of LLM scaling

The gap makes intuitive sense: LLM agents operate in the digital world where execution is instant and errors are cheaply recoverable. Robots must plan, perceive, and actuate in the physical world where every motion takes real time and mistakes can be catastrophic.

### Category Breakdown

![Task Horizon by Category](../figures/category_comparison.png)
*Figure 3: Tabletop manipulation (left) vs. mobile manipulation (right). Mobile manipulation shows steeper recent growth.*

The split reveals different dynamics:
- **Tabletop manipulation** has a longer history and a more gradual frontier, anchored by the Rubik's Cube outlier
- **Mobile manipulation** is newer but growing faster (doubling time ~5.3 months), driven by the recent wave of Mobile ALOHA and π0.x systems
- When combined, the story is cleaner than when separated — the overall frontier is what matters most

### Sensitivity to Success Threshold

![Sensitivity Analysis](../figures/sensitivity_thresholds.png)
*Figure 4: How the frontier changes at different success rate thresholds.*

At the ≥30% threshold, the frontier extends further (systems attempting harder tasks with lower reliability). At ≥80%, the frontier is more conservative, reflecting only highly reliable systems. The shape is similar across thresholds, suggesting the results aren't an artifact of the 50% cutoff.

## Quantitative Analysis

### Doubling Time

Fitting an exponential to the frontier:

| Scope | Doubling Time | R² | Points |
|---|---|---|---|
| All categories combined | **16.4 months** (95% CI: 13.8–29.2) | 0.843 | 8 |
| Tabletop only | 16.5 months | 0.769 | 6 |
| Mobile manipulation only | 14.0 months | 0.852 | 6 |

The overall doubling time of ~16.4 months places robot manipulation between METR's findings for LLM agents (~7 months) and self-driving (~20 months for Tesla FSD), but closer to self-driving.

### Comparison with METR Domains

| Domain | Doubling Time | Source |
|---|---|---|
| LLM agents (software/reasoning) | ~7 months | METR |
| LLM agents (recent, 2024–25) | ~4 months | METR |
| Web browsing (WebArena/OSWorld) | ~7 months | METR |
| **Robot manipulation (this work)** | **~16.4 months** | **This analysis** |
| Self-driving (Tesla FSD) | ~20 months | METR |

Robot manipulation is the second-slowest domain — roughly 2.3x slower than LLM agents but modestly faster than self-driving. This likely reflects the compounded difficulty of the physical-world feedback loop: every iteration requires real hardware, real sensor data, and real actuation, making the cycle time for improvement fundamentally longer than in purely digital domains.

## What's Driving the Recent Acceleration?

The jump from 2024 onward is driven by three converging trends:

1. **Vision-Language-Action (VLA) models.** π0 and its successors combine internet-scale vision-language pretraining with robot action prediction, enabling zero-shot generalization to new tasks and environments.

2. **Co-training across embodiments.** Training on data from multiple robot types (the Open X-Embodiment insight) produces more robust policies that handle the variability of real-world tasks.

3. **Bimanual and mobile platforms.** ALOHA and Mobile ALOHA showed that relatively low-cost bimanual setups can tackle tasks (cooking, folding) that were previously out of reach. The hardware got cheaper while the policies got better.

## Related Work

Several parallel efforts inform this analysis:

- **METR's own criticisms apply here too.** METR has acknowledged that human time estimation is noisy (~80% of baselines fall within 3x of "true" task length), and that their tasks don't reflect full real-world complexity. These issues are amplified for robotics, where we lack METR's controlled evaluation infrastructure. See [MIT Technology Review's analysis](https://www.technologyreview.com/2026/02/05/1132254/this-is-the-most-misunderstood-graph-in-ai/) for a thorough discussion.

- **Epoch AI** found a [100x compute gap](https://epoch.ai/data-insights/compute-for-robotic-manipulation) between frontier AI trends and robotics — with data scarcity (not compute) as the bottleneck. Their [2026 robot capability assessment](https://epoch.ai/blog/where-autonomy-works-evaluating-robot-capabilities-in-2026) found robots work 3–10x slower than humans and struggle with novel objects without retraining.

- **ManipulationNet** ([manipulation-net.org](https://manipulation-net.org/)) is building standardized hardware kits and distributed evaluation to create a "historical record of robotic manipulation capability" — the closest analog to METR for robotics, but still in early stages.

## Task Difficulty: Beyond Duration

Human-equivalent time is a useful single metric for cross-domain comparison with METR, but it flattens important distinctions. Not all minutes are equally hard. We see at least three axes of difficulty that duration alone doesn't capture:

**1. Compositional complexity.** How many *distinct* subtasks does the task require, and how do they depend on each other? A task with 12 different ordered subtasks (π0.6's laundry folding: sort, pick, shake, fold, stack — repeated across varied garments) is harder than a task with 12 identical subtasks (bin-picking 12 objects). Our dataset records `num_subtasks`, but this is a rough proxy — it counts steps without weighting their diversity or interdependence.

**2. Error tolerance and recoverability.** Some tasks are forgiving: if you drop a box while stacking, you pick it up and try again. Others are not: if you crack an egg into a pan at the wrong moment, there's no undo. Tasks with irreversible steps or tight physical tolerances (e.g., Dactyl's Rubik's Cube, where one fumble drops the cube) are harder than their duration suggests. This is partly why success rates vary so widely — π0.6 achieves 97% on laundry folding but only 20% on box assembly, despite similar durations, because box assembly has tighter tolerances and less room for recovery.

**3. Environmental variability.** A task performed on the same 5 objects in the same lab is easier than the same task performed zero-shot in a novel kitchen with unseen objects. The foundation model era (π0 onward) is notable not just for longer tasks but for performing them in diverse, unstructured environments — a qualitative shift that the time metric doesn't reflect.

**Why we still use duration as the primary metric.** Despite these limitations, human-equivalent time has a key advantage: it's comparable across domains. METR uses it for LLM agents, and the cross-domain comparison (robotics at ~16 months doubling time vs. LLM agents at ~7 months) is one of the most informative outputs of this analysis. A multidimensional difficulty score would be more accurate but would sacrifice comparability.

**What this means for interpretation.** The recent frontier systems (π0, π0.5, π0.6) aren't just doing *longer* tasks — they're doing *harder* tasks along all three axes: more diverse subtasks, less forgiving physical constraints, and more varied environments. The time metric undersells their progress. Conversely, some earlier long-duration data points (like Dactyl's Rubik's Cube) represent narrow but deep difficulty — a single rehearsed task executed with extreme dexterity. The frontier line treats these as equivalent, and readers should keep this nuance in mind.

Future work could develop a composite difficulty score incorporating compositional complexity, error tolerance, and environmental diversity. For now, we flag these dimensions qualitatively and note where they affect the interpretation of specific data points.

## Limitations

1. **Small frontier sample size.** We have only 6 frontier points spanning 9 years. The exponential fit is suggestive but not definitive.

2. **Heterogeneous evaluations.** Unlike METR, we cannot evaluate all systems on identical tasks. Hardware, evaluation protocols, and success criteria differ across every data point.

3. **Human time estimation.** Some human-equivalent times are estimated rather than measured. We mark these in the dataset with confidence levels. METR themselves found this estimation is noisy even with controlled conditions.

4. **Selection bias.** We may be missing systems that pushed the frontier but weren't widely cited or didn't report success rates.

5. **The Rubik's Cube is an outlier.** Dactyl's Rubik's Cube solve is a unique single-task achievement that required massive compute and a custom setup. It's arguably not on the same "generality trajectory" as the foundation model era. Excluding it would change the fitted doubling time significantly.

6. **"Task horizon" ≠ "useful work."** As critics of METR's approach have noted, a 15-minute task horizon doesn't mean robots can replace 15 minutes of human work. Real tasks involve variability, error recovery, and context that benchmarks don't capture. See [Task Difficulty: Beyond Duration](#task-difficulty-beyond-duration) for a fuller discussion of what the time metric misses.

## Conclusion

The task horizon for robotic manipulation is growing — roughly doubling every 10.6 months. But the growth is uneven, with a notable five-year plateau from 2019–2024 when the field prioritized breadth over depth. The foundation model era (2024–present) has broken through this plateau, with generalist policies now completing 10–15 minute household tasks that would have been science fiction just two years ago.

If the current exponential holds, we might expect robots to reliably complete **1-hour household tasks by ~2028** and **multi-hour complex tasks by ~2030**. But the history of this field suggests that progress comes in steps, not smooth curves — the next paradigm shift matters more than the trend line.

## Dataset & Code

The full dataset (35 systems, with sources and confidence annotations) and all analysis code are available in this repository:
- `data/manipulation_horizons.csv` — structured dataset
- `scripts/plot_horizons.py` — visualization code  
- `scripts/analyze.py` — statistical analysis

We welcome contributions: if you know of a system we missed or have better data for an existing entry, please open an issue or PR.

---

*This analysis was inspired by [METR's task horizon work](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) and their [cross-domain extension](https://metr.org/blog/2025-07-14-how-does-time-horizon-vary-across-domains/). We thank the robotics research community for publishing the benchmarks and evaluations that made this analysis possible.*
