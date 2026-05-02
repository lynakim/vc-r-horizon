#!/usr/bin/env python3
"""Rebuild manipulation_horizons.csv from audited data.

Applies the inclusion criteria in inclusion_criteria.md:
  1. Real hardware, autonomously evaluated
  2. Systematic evaluation (documented protocol)
  3. N >= 10 real-world end-to-end trials
  4. Same task for rate and duration
  5. Grounded human time (4-value source)

Adds the success_type column (binary | rubric_progress).
Recomputes is_frontier programmatically from the canonical envelope:
real-world rows, success_rate >= 50, monotonic non-decreasing.
"""

import csv
import os
from datetime import datetime

OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'manipulation_horizons.csv')

COLS = [
    'date', 'system_name', 'paper_url', 'task_description',
    'human_time_seconds', 'human_time_source', 'confidence',
    'success_rate', 'num_trials', 'num_subtasks',
    'category', 'sim_or_real', 'hardware', 'data_quality',
    'is_frontier', 'success_type', 'notes',
]

# Each row is a dict matching the columns above (minus is_frontier, computed).
ROWS = [
    # ============================================================
    # 2016 — early grasping era
    # ============================================================
    dict(date='2016-03-01', system_name='Levine et al. Grasping',
         paper_url='https://arxiv.org/abs/1603.02199',
         task_description='Grasp single object from bin',
         human_time_seconds=4, human_time_source='defended_estimate',
         confidence='high', success_rate=80, num_trials=800000, num_subtasks=1,
         category='tabletop', sim_or_real='real',
         hardware='Custom 7-DoF arms (14 robots)', data_quality='benchmark',
         success_type='binary',
         notes='800k grasp attempts across 14 robots over 2 months; ~80% grasp success'),

    # NOTE: All sim-only rows removed in May 2026 audit. The horizon analysis
    # is a real-world capability story; sim results don't anchor the frontier
    # and add visual noise without informing the doubling-time question.
    # Dropped: HER (2017), IKEA Furniture (2019, sim), ACRONYM (2020),
    # TransporterNet (2021), CLIPort (2021), PerAct (2022), RoboCerebra (2025),
    # VLABench (2025). FurnitureBench (real, 2023) and RT-X (real dataset
    # paper, 2023) are kept because their evaluations are real.

    # ============================================================
    # 2018 — grasping scaled, in-hand RL begins
    # ============================================================
    dict(date='2018-01-01', system_name='Dex-Net 2.0/4.0',
         paper_url='https://arxiv.org/abs/1703.09312',
         task_description='Bin picking - grasp novel objects',
         human_time_seconds=4, human_time_source='defended_estimate',
         confidence='high', success_rate=93, num_trials=40, num_subtasks=1,
         category='tabletop', sim_or_real='real',
         hardware='ABB YuMi', data_quality='benchmark',
         success_type='binary',
         notes='93% grasp success on novel objects from bin'),

    dict(date='2018-06-27', system_name='QT-Opt',
         paper_url='https://arxiv.org/abs/1806.10293',
         task_description='Vision-based closed-loop bin grasping of diverse objects',
         human_time_seconds=4, human_time_source='defended_estimate',
         confidence='high', success_rate=96, num_trials=580000, num_subtasks=1,
         category='tabletop', sim_or_real='real',
         hardware='7x KUKA LBR IIWA + parallel-jaw gripper', data_quality='benchmark',
         success_type='binary',
         notes='96% grasp success on unseen objects; 580k+ real grasp attempts; learns regrasping strategies'),

    dict(date='2018-07-01', system_name='OpenAI Dactyl - Block',
         paper_url='https://arxiv.org/abs/1808.00177',
         task_description='Reorient block to target face using in-hand manipulation',
         human_time_seconds=10, human_time_source='defended_estimate',
         confidence='high', success_rate=80, num_trials=100, num_subtasks=1,
         category='tabletop', sim_or_real='real',
         hardware='Shadow Dexterous Hand', data_quality='benchmark',
         success_type='binary',
         notes='Sim-to-real via ADR. Median ~13 / mean ~26.4 consecutive successful rotations per trial; 50-rotation cap. ~80% reflects share of trials achieving >=1 successful rotation under best ADR config'),

    # ============================================================
    # 2019 — long-horizon dexterity, grasping novelty
    # ============================================================
    dict(date='2019-04-01', system_name='TossingBot',
         paper_url='https://arxiv.org/abs/1903.11239',
         task_description='Pick object and toss into target bin',
         human_time_seconds=5, human_time_source='defended_estimate',
         confidence='high', success_rate=85, num_trials=10000, num_subtasks=2,
         category='tabletop', sim_or_real='real',
         hardware='UR5 + vacuum gripper', data_quality='benchmark',
         success_type='binary',
         notes='85% success grasping+tossing; self-supervised; 10k+ real trials'),

    # ============================================================
    # 2022 — VLA precursors and LLM-as-planner
    # ============================================================
    dict(date='2022-02-04', system_name='BC-Z',
         paper_url='https://arxiv.org/abs/2202.02005',
         task_description='Multi-task manipulation: pick; wipe; knock (24 unseen tasks)',
         human_time_seconds=8, human_time_source='defended_estimate',
         confidence='high', success_rate=44, num_trials=100, num_subtasks=1,
         category='tabletop', sim_or_real='real',
         hardware='Everyday Robots (12 robots)', data_quality='benchmark',
         success_type='binary',
         notes='44% avg on 24 unseen zero-shot tasks; 25.8k demos + 18.7k human videos'),

    dict(date='2022-04-01', system_name='SayCan',
         paper_url='https://arxiv.org/abs/2204.01691',
         task_description='Multi-step kitchen task: fetch and place (6-step end-to-end)',
         human_time_seconds=90, human_time_source='defended_estimate',
         confidence='medium', success_rate=50, num_trials=120, num_subtasks=6,
         category='mobile_manipulation', sim_or_real='real',
         hardware='Everyday Robots mobile manipulator', data_quality='benchmark',
         success_type='binary',
         notes='Headline rate is END-TO-END for 6-step task. Paper reports 74% planning success * per-step execution = ~50% end-to-end. Earlier CSV had 74% (planning only) — that conflated subtask rate with full-task duration, criterion #4 violation'),

    dict(date='2022-08-01', system_name='Inner Monologue',
         paper_url='https://arxiv.org/abs/2207.05608',
         task_description='Multi-step kitchen tasks with language feedback',
         human_time_seconds=90, human_time_source='defended_estimate',
         confidence='medium', success_rate=69, num_trials=100, num_subtasks=5,
         category='mobile_manipulation', sim_or_real='real',
         hardware='Everyday Robots mobile manipulator', data_quality='benchmark',
         success_type='binary',
         notes='69% overall success on multi-step tasks with embodied reasoning'),

    dict(date='2022-09-01', system_name='Code as Policies',
         paper_url='https://arxiv.org/abs/2209.07753',
         task_description='LLM-planned multi-step manipulation; 5+ step tabletop tasks',
         human_time_seconds=120, human_time_source='defended_estimate',
         confidence='medium', success_rate=63, num_trials=100, num_subtasks=5,
         category='tabletop', sim_or_real='real',
         hardware='UR5 + Robotiq gripper', data_quality='benchmark',
         success_type='binary',
         notes='63% on compositional tabletop tasks; LLM writes manipulation code'),

    dict(date='2022-12-13', system_name='RT-1',
         paper_url='https://arxiv.org/abs/2212.06817',
         task_description='Single-step pick/place/move',
         human_time_seconds=8, human_time_source='defended_estimate',
         confidence='high', success_rate=97, num_trials=3000, num_subtasks=1,
         category='tabletop', sim_or_real='real',
         hardware='Everyday Robots', data_quality='benchmark',
         success_type='binary',
         notes='97% on seen tasks; 76% on unseen; 700+ task instructions'),

    # ============================================================
    # 2023 — diffusion, ACT, RT-2
    # ============================================================
    dict(date='2023-02-01', system_name='Diffusion Policy',
         paper_url='https://arxiv.org/abs/2303.04137',
         task_description='Multi-step manipulation: push-T / can sorting / square nut',
         human_time_seconds=45, human_time_source='defended_estimate',
         confidence='medium', success_rate=88, num_trials=50, num_subtasks=3,
         category='tabletop', sim_or_real='real',
         hardware='UR5 / Franka', data_quality='benchmark',
         success_type='binary',
         notes='Diffusion-based policy; 88% on push-T'),

    # ACT/ALOHA: actual tasks are 8-14s human time per paper §V-B (paper-read agent confirmed).
    # Headline: slot battery 96% on N=25 at ~14s. Previous CSV row had 85% at 120s — that combined
    # the slot-battery rate with a guessed threading duration; criterion #4 violation.
    dict(date='2023-03-01', system_name='ACT / ALOHA',
         paper_url='https://arxiv.org/abs/2304.13705',
         task_description='Slot battery into device (bimanual, ALOHA)',
         human_time_seconds=14, human_time_source='published_baseline',
         confidence='high', success_rate=96, num_trials=25, num_subtasks=3,
         category='tabletop', sim_or_real='real',
         hardware='ALOHA bimanual setup (ViperX 300)', data_quality='benchmark',
         success_type='binary',
         notes='96% on slot battery (paper Tab. I, N=25). Other tasks at same ~14s human time per paper §V-B: slide ziploc 88%, open cup 84%, prep tape 64%, put on shoe 92%, thread velcro 20%'),

    dict(date='2023-05-01', system_name='CLEANing Robot (TidyBot)',
         paper_url='https://arxiv.org/abs/2305.09560',
         task_description='Pick subtask of multi-object sort (per-pick rate, not full task)',
         human_time_seconds=10, human_time_source='defended_estimate',
         confidence='medium', success_rate=85, num_trials=20, num_subtasks=1,
         category='mobile_manipulation', sim_or_real='real',
         hardware='Mobile Fetch robot', data_quality='paper_demo',
         success_type='binary',
         notes='85% is per-pick rate (subtask), not end-to-end multi-object sort task. Duration adjusted to per-pick (~10s), not full sort. Earlier CSV had 85% at 60s (full task) — that was an aggregate-rate issue'),

    dict(date='2023-07-28', system_name='RT-2',
         paper_url='https://arxiv.org/abs/2307.15818',
         task_description='Single-step manipulation with semantic reasoning',
         human_time_seconds=8, human_time_source='defended_estimate',
         confidence='high', success_rate=62, num_trials=6000, num_subtasks=1,
         category='tabletop', sim_or_real='real',
         hardware='Everyday Robots', data_quality='benchmark',
         success_type='binary',
         notes='62% on novel/emergent tasks; 3x better than baselines'),

    dict(date='2023-08-01', system_name='FurnitureBench',
         paper_url='https://arxiv.org/abs/2305.12821',
         task_description='Real furniture assembly (one-leg table)',
         human_time_seconds=900, human_time_source='published_baseline',
         confidence='high', success_rate=15, num_trials=50, num_subtasks=8,
         category='tabletop', sim_or_real='real',
         hardware='Franka Panda with custom grippers', data_quality='benchmark',
         success_type='binary',
         notes='Best IL method ~15% on easiest assembly; below 50% threshold'),

    dict(date='2023-10-01', system_name='RT-X / Open X-Embodiment',
         paper_url='https://arxiv.org/abs/2310.08864',
         task_description='Single-step multi-robot manipulation across 22 embodiments',
         human_time_seconds=8, human_time_source='defended_estimate',
         confidence='high', success_rate=70, num_trials=1000, num_subtasks=1,
         category='tabletop', sim_or_real='real',
         hardware='22 different robot platforms', data_quality='benchmark',
         success_type='binary',
         notes='1M+ trajectories; 527 skills; 50% improvement over single-embodiment'),

    # ============================================================
    # 2024 — VLA generalists, mobile bimanual, dexterous RL
    # ============================================================
    # Mobile ALOHA: per-task durations from paper §5.2 (paper-read agent confirmed).
    # Previous CSV had 85% at 90s — 90s is the cabinet teleop time, but headline rate
    # was for cabinet at 85% / 30s. Updated to longest-task-at->=50% rule:
    # call elevator 95% at 45s human-teleop time.
    dict(date='2024-01-04', system_name='Mobile ALOHA',
         paper_url='https://arxiv.org/abs/2401.02117',
         task_description='Mobile bimanual: call elevator (full task, autonomous)',
         human_time_seconds=45, human_time_source='published_baseline',
         confidence='high', success_rate=95, num_trials=20, num_subtasks=4,
         category='mobile_manipulation', sim_or_real='real',
         hardware='Mobile ALOHA (Trossen ViperX on AgileX base)', data_quality='paper_demo',
         success_type='binary',
         notes='Call elevator 95% at 45s. Other tasks (paper Tab. 1): wipe wine 95%/26s, cabinet 85%/30s, high five 85%/40s, rinse pan 80%/22s, push chairs 80%/40s. Cook shrimp 40% on N=5 dropped (below N=10 bar)'),

    dict(date='2024-01-04', system_name='Mobile ALOHA Cooking (Teleop)',
         paper_url='https://arxiv.org/abs/2401.02117',
         task_description='3-course Cantonese meal via TELEOPERATION (not autonomous)',
         human_time_seconds=3600, human_time_source='observed_demo',
         confidence='low', success_rate=0, num_trials=1, num_subtasks=15,
         category='mobile_manipulation', sim_or_real='real',
         hardware='Mobile ALOHA', data_quality='public_demo',
         success_type='binary',
         notes='Reference only — teleoperated, not autonomous (disqualified by criterion 1). Included to flag the gap between viral demos and autonomous capability'),

    dict(date='2024-03-01', system_name='GR-1 Humanoid Manipulation',
         paper_url='https://arxiv.org/abs/2312.15496',
         task_description='Humanoid pick and place + pour water + wipe table',
         human_time_seconds=60, human_time_source='defended_estimate',
         confidence='medium', success_rate=70, num_trials=20, num_subtasks=3,
         category='mobile_manipulation', sim_or_real='real',
         hardware='Fourier GR-1 humanoid', data_quality='paper_demo',
         success_type='binary',
         notes='Early humanoid manipulation demos; 3-step household tasks'),

    dict(date='2024-05-01', system_name='Octo',
         paper_url='https://arxiv.org/abs/2405.12213',
         task_description='Single-step generalist manipulation: pick/place/push',
         human_time_seconds=8, human_time_source='defended_estimate',
         confidence='high', success_rate=55, num_trials=100, num_subtasks=1,
         category='tabletop', sim_or_real='real',
         hardware='WidowX / Franka', data_quality='benchmark',
         success_type='binary',
         notes='Open-source generalist; 93M params; pretrained on 800k Open X-Embodiment episodes'),

    dict(date='2024-06-01', system_name='OpenVLA',
         paper_url='https://arxiv.org/abs/2406.09246',
         task_description='Single-step manipulation: pick; place; push',
         human_time_seconds=8, human_time_source='defended_estimate',
         confidence='high', success_rate=65, num_trials=100, num_subtasks=1,
         category='tabletop', sim_or_real='real',
         hardware='WidowX / Franka', data_quality='benchmark',
         success_type='binary',
         notes='7B parameter VLA; 20.4% improvement over baselines on fine-tuned setups'),

    # HIL-SERL: paper-read agent confirmed N=100 (not 20 as previously) and per-task cycle times.
    # Use object handover as representative task: longest cycle at 100% with N=100.
    dict(date='2024-10-29', system_name='HIL-SERL',
         paper_url='https://arxiv.org/abs/2410.21845',
         task_description='Object handover (bimanual)',
         human_time_seconds=14, human_time_source='published_baseline',
         confidence='high', success_rate=100, num_trials=100, num_subtasks=2,
         category='tabletop', sim_or_real='real',
         hardware='Franka Panda', data_quality='benchmark',
         success_type='binary',
         notes='Tab. 1a: 100% on N=100, RL cycle 13.6s, BC baseline 16.1s (~human time). All 13 tasks at 100% incl. RAM insert (4.8s), USB grasp (6.7s), timing belt (7.2s), IKEA whole assembly (10/10 N=10, multi-stage)'),

    # ALOHA Unleashed (NEW): paper-read agent confirmed N=20 per task, 80-120s timeouts, binary.
    # Multiple rows for the spread of capability.
    dict(date='2024-10-13', system_name='ALOHA Unleashed - Hang Shirt',
         paper_url='https://arxiv.org/abs/2410.13126',
         task_description='Hang shirt on hanger from messy initial state',
         human_time_seconds=120, human_time_source='published_baseline',
         confidence='high', success_rate=70, num_trials=20, num_subtasks=4,
         category='tabletop', sim_or_real='real',
         hardware='ALOHA 2', data_quality='benchmark',
         success_type='binary',
         notes='ShirtMessy task, paper Tab. 1, 120s timeout. Longest >=50% task in the paper'),

    dict(date='2024-10-13', system_name='ALOHA Unleashed - Tie Shoelace',
         paper_url='https://arxiv.org/abs/2410.13126',
         task_description='Tie shoelaces (easy initial state)',
         human_time_seconds=80, human_time_source='published_baseline',
         confidence='high', success_rate=70, num_trials=20, num_subtasks=5,
         category='tabletop', sim_or_real='real',
         hardware='ALOHA 2', data_quality='benchmark',
         success_type='binary',
         notes='LaceEasy task, paper Tab. 1, 80s timeout'),

    dict(date='2024-10-13', system_name='ALOHA Unleashed - Gear Insert',
         paper_url='https://arxiv.org/abs/2410.13126',
         task_description='Insert at least one of three robot gears',
         human_time_seconds=80, human_time_source='published_baseline',
         confidence='high', success_rate=95, num_trials=20, num_subtasks=3,
         category='tabletop', sim_or_real='real',
         hardware='ALOHA 2', data_quality='benchmark',
         success_type='binary',
         notes='GearInsert-1 task, paper Tab. 1. Full 3-gear task only 40% (below threshold)'),

    # π0: paper-read agent confirmed all tasks rubric scoring at N=10 / 5-min timeout.
    # Replaces previous "75% at 300s binary" — that conflated rubric with binary.
    dict(date='2024-10-31', system_name='π0 (laundry folding)',
         paper_url='https://arxiv.org/abs/2410.24164',
         task_description='Post-train laundry folding (5-min episode timeout)',
         human_time_seconds=300, human_time_source='published_baseline',
         confidence='medium', success_rate=70, num_trials=10, num_subtasks=4,
         category='tabletop', sim_or_real='real',
         hardware='Franka / ALOHA / UR5 (8 embodiments)', data_quality='paper_demo',
         success_type='rubric_progress',
         notes='Paper §VI-D, Fig 13. 4-point rubric (avg progress ~0.7), N=10. Episode 5-min timeout. Authors report tasks "take 5-20 min". This row is rubric_progress, not binary success'),

    dict(date='2024-12-01', system_name='ALOHA 2 (hardware platform)',
         paper_url='https://aloha-2.github.io/',
         task_description='Hardware platform paper — no quantitative manipulation evaluation',
         human_time_seconds=0, human_time_source='defended_estimate',
         confidence='low', success_rate=0, num_trials=0, num_subtasks=0,
         category='tabletop', sim_or_real='real',
         hardware='ALOHA 2 bimanual platform', data_quality='public_demo',
         success_type='binary',
         notes='REFERENCE ONLY — ALOHA 2 is a hardware paper with no per-task evaluations. Benchmark numbers attributed to ALOHA 2 actually come from ALOHA Unleashed and Gemini Robotics. Excluded from frontier'),

    # ============================================================
    # 2025 — generalist VLAs, π series, humanoid
    # ============================================================
    dict(date='2025-02-01', system_name='UMI - Dish Washing',
         paper_url='https://arxiv.org/abs/2402.10329',
         task_description='Dish washing (7-step long horizon, hand-held gripper data)',
         human_time_seconds=60, human_time_source='defended_estimate',
         confidence='medium', success_rate=70, num_trials=20, num_subtasks=7,
         category='tabletop', sim_or_real='real',
         hardware='UR5 / Franka (cross-platform)', data_quality='benchmark',
         success_type='binary',
         notes='Paper §V-D Fig 8: 14/20 = 70% on 7-step dish wash. Other tasks: cup arrange 100%, dynamic toss 87.5%, cloth folding 70%'),

    dict(date='2025-03-12', system_name='Gemini Robotics - Lunch Box',
         paper_url='https://arxiv.org/abs/2503.20020',
         task_description='Pack lunch-box (multi-item, multi-step)',
         human_time_seconds=120, human_time_source='published_baseline',
         confidence='high', success_rate=100, num_trials=20, num_subtasks=6,
         category='tabletop', sim_or_real='real',
         hardware='ALOHA 2', data_quality='benchmark',
         success_type='binary',
         notes='Specialist (fine-tuned) model, paper §4.1 / Fig 23, "over 2 minutes". 100% on N=20. Other tasks: scoop nuts 100%, cards 90%, spelling 83% (N=12), snap peas 55%, origami 45%'),

    dict(date='2025-03-01', system_name='Figure 02 at BMW',
         paper_url='https://www.figure.ai/news/production-at-bmw',
         task_description='Sheet metal loading: 3 parts per 84s cycle over 10-hour shifts',
         human_time_seconds=84, human_time_source='observed_demo',
         confidence='medium', success_rate=99, num_trials=90000, num_subtasks=3,
         category='mobile_manipulation', sim_or_real='real',
         hardware='Figure 02 humanoid', data_quality='public_demo',
         success_type='binary',
         notes='>99% placement accuracy per shift (5mm tolerance); 90k+ parts; 1250+ hours; narrow industrial task. 11-month deployment concluded Nov 2025'),

    dict(date='2025-04-22', system_name='π0.5 (bedroom cleanup)',
         paper_url='https://arxiv.org/abs/2504.16054',
         task_description='Bedroom cleanup in novel home (laundry-in-basket + make bed)',
         human_time_seconds=720, human_time_source='published_baseline',
         confidence='medium', success_rate=70, num_trials=30, num_subtasks=8,
         category='mobile_manipulation', sim_or_real='real',
         hardware='Franka + mobile base / ALOHA', data_quality='paper_demo',
         success_type='rubric_progress',
         notes='Paper §V-A Fig 7. Rubric scoring (5/8-pt rubric depending on task). N=10 per home x 3 homes = 30. Total task duration 10-15 min per Fig 1. Some episodes dropped post-hoc (cancelled due to robot failures). rubric_progress, not binary'),

    # ============================================================
    # Round 2 additions (May 2026 audit). All seven verified against the
    # 3-criterion bar by paper-reading agent. None push the ≥50% frontier
    # past π0.5's 720s cap; all fill in the 2024–2026 cluster below it.
    # ============================================================

    dict(date='2024-11-01', system_name='BiDex - Lift Pot',
         paper_url='https://arxiv.org/abs/2411.13677',
         task_description='Lift pot (autonomous bimanual dexterous policy on LEAP V2)',
         human_time_seconds=12, human_time_source='defended_estimate',
         confidence='medium', success_rate=75, num_trials=20, num_subtasks=2,
         category='tabletop', sim_or_real='real',
         hardware='Bimanual LEAP V2 dexterous hands', data_quality='benchmark',
         success_type='binary',
         notes='CoRL 2024. Autonomous ACT policy trained from BiDex teleop demos. Tab. 4 (LEAP V2): 15/20. Most of the paper is teleop infrastructure; the policy results in Tab. 3-4 are the autonomous component'),

    dict(date='2025-03-05', system_name='BEHAVIOR Robot Suite - Put Items onto Shelves',
         paper_url='https://arxiv.org/abs/2503.05652',
         task_description='Put items onto shelves (single-stage household)',
         human_time_seconds=60, human_time_source='published_baseline',
         confidence='high', success_rate=93, num_trials=15, num_subtasks=2,
         category='mobile_manipulation', sim_or_real='real',
         hardware='Galaxea R1 (bimanual + mobile + torso)', data_quality='benchmark',
         success_type='binary',
         notes='Paper Tab. A.IX-A.XIII, x/15 binary entire-task (ET) success. Highest-success household task in the BRS suite'),

    dict(date='2025-03-05', system_name='BEHAVIOR Robot Suite - Take Trash Outside',
         paper_url='https://arxiv.org/abs/2503.05652',
         task_description='Take trash outside (mobile bimanual multi-stage)',
         human_time_seconds=130, human_time_source='published_baseline',
         confidence='high', success_rate=53, num_trials=15, num_subtasks=4,
         category='mobile_manipulation', sim_or_real='real',
         hardware='Galaxea R1', data_quality='benchmark',
         success_type='binary',
         notes='Paper Tab. A.IX-A.XIII, 8/15 ET success. Just above 50% threshold. Notable as one of the few binary multi-minute results in 2025'),

    dict(date='2025-03-05', system_name='BEHAVIOR Robot Suite - Clean House After a Wild Party',
         paper_url='https://arxiv.org/abs/2503.05652',
         task_description='Clean house after wild party (6-stage household)',
         human_time_seconds=210, human_time_source='published_baseline',
         confidence='high', success_rate=40, num_trials=15, num_subtasks=6,
         category='mobile_manipulation', sim_or_real='real',
         hardware='Galaxea R1', data_quality='benchmark',
         success_type='binary',
         notes='Longest task in BRS suite. 6/15 ET = 40% — below 50% threshold. Included as a sub-50% reference point showing where binary multi-minute is in 2025'),

    dict(date='2025-03-10', system_name='AgiBot World / GO-1 - Fold Shorts',
         paper_url='https://arxiv.org/abs/2503.06669',
         task_description='Fold shorts (humanoid bimanual)',
         human_time_seconds=30, human_time_source='defended_estimate',
         confidence='medium', success_rate=66, num_trials=30, num_subtasks=4,
         category='mobile_manipulation', sim_or_real='real',
         hardware='G1 humanoid (AgiBot fleet)', data_quality='benchmark',
         success_type='rubric_progress',
         notes='Paper Sec. V-A1, Fig 5/6: GO-1 generalist scores 0.66 in-distribution rubric, 0.51 out-of-distribution avg. 10 rollouts × 3 scenarios. IROS 2025 best paper finalist'),

    dict(date='2025-03-02', system_name='Reactive Diffusion Policy - Bimanual Lifting',
         paper_url='https://arxiv.org/abs/2503.02881',
         task_description='Bimanual lifting (clamp + lift coordinated, soft and hard cups)',
         human_time_seconds=15, human_time_source='defended_estimate',
         confidence='medium', success_rate=70, num_trials=20, num_subtasks=2,
         category='tabletop', sim_or_real='real',
         hardware='Bimanual Flexiv Rizon 4', data_quality='benchmark',
         success_type='rubric_progress',
         notes='RSS 2025 outstanding student paper. RDP Force rubric score 0.70 (0/0.5/1). Binary lift sub-metric: 90% on each cup type. Slow-fast diffusion + visuotactile'),

    dict(date='2025-05-21', system_name='DexUMI - Kitchen',
         paper_url='https://arxiv.org/abs/2505.21864',
         task_description='Kitchen 4-stage: turn off knob → pick-place pan → pick salt → sprinkle',
         human_time_seconds=45, human_time_source='defended_estimate',
         confidence='medium', success_rate=75, num_trials=20, num_subtasks=4,
         category='tabletop', sim_or_real='real',
         hardware='Inspire Hand / XHand (12-DoF dexterous)', data_quality='benchmark',
         success_type='binary',
         notes='CoRL 2025 oral. Stage-wise accumulated success (best config Rel/Yes/Inpaint): knob 1.00, pan 0.85, salt 0.95, sprinkle 0.75. Final-stage = 75% binary'),

    dict(date='2025-07-05', system_name='TRI LBM - CutAppleInSlices',
         paper_url='https://arxiv.org/abs/2507.05331',
         task_description='Cut apple into slices (longest LBM task: corer + knife + slice + wipe)',
         human_time_seconds=180, human_time_source='published_baseline',
         confidence='medium', success_rate=30, num_trials=50, num_subtasks=7,
         category='tabletop', sim_or_real='real',
         hardware='Bimanual Franka FR3', data_quality='benchmark',
         success_type='rubric_progress',
         notes='TRI Large Behavior Models. Paper §IV-A2, Fig S6b: "longest horizon task in benchmark, up to 3 minutes". Binary fully-completed ~0%, but task-completion (TC) rubric is meaningful (~30% partial credit estimated). 50 rollouts/task — strongest stats methodology in the field'),

    dict(date='2025-10-14', system_name='RL-100 - Box Folding',
         paper_url='https://arxiv.org/abs/2510.14830',
         task_description='Box folding (long-horizon contact-rich, RL-100 CM)',
         human_time_seconds=42, human_time_source='observed_demo',
         confidence='high', success_rate=100, num_trials=50, num_subtasks=4,
         category='tabletop', sim_or_real='real',
         hardware='Multi-embodiment (paper has 8 tasks)', data_quality='benchmark',
         success_type='binary',
         notes='RL-100 paper. 50/50 box folding. Robot wall-clock 41.4s (CM) / 45.6s (DDIM). Paper also reports 7-hour mall juicing run with 1000/1000 trials. 2025 standout for binary reliability at this horizon'),

    # π0.6: split into binary single-shirt + rubric espresso + rubric box assembly per paper §VI.
    dict(date='2025-11-17', system_name='π0.6 (single-shirt fold)',
         paper_url='https://arxiv.org/abs/2511.14759',
         task_description='Fold single orange t-shirt collar-up (failure-mode-removal ablation)',
         human_time_seconds=200, human_time_source='published_baseline',
         confidence='high', success_rate=97, num_trials=50, num_subtasks=4,
         category='mobile_manipulation', sim_or_real='real',
         hardware='Mobile bimanual robot', data_quality='paper_demo',
         success_type='binary',
         notes='Paper §VI-C-1 last paragraph: 97% on strict failure-mode-removal ablation (single shirt, fixed orientation). 200s timeout. Binary success. The clean comparable number from this paper'),

    dict(date='2025-11-17', system_name='π0.6 (espresso)',
         paper_url='https://arxiv.org/abs/2511.14759',
         task_description='Make espresso (grind+tamp+extract+clean), 200s timeout',
         human_time_seconds=200, human_time_source='published_baseline',
         confidence='medium', success_rate=90, num_trials=414, num_subtasks=5,
         category='mobile_manipulation', sim_or_real='real',
         hardware='Mobile bimanual robot', data_quality='paper_demo',
         success_type='rubric_progress',
         notes='Paper §VI-A, Fig 8: "90%+ range" with RECAP. Multi-stage rubric. Continuous 5:30 AM-11:30 PM operation in real shop'),

    dict(date='2025-11-17', system_name='π0.6 (diverse laundry)',
         paper_url='https://arxiv.org/abs/2511.14759',
         task_description='Diverse laundry items (11 categories) including button-up shirt',
         human_time_seconds=500, human_time_source='published_baseline',
         confidence='medium', success_rate=75, num_trials=450, num_subtasks=5,
         category='mobile_manipulation', sim_or_real='real',
         hardware='Mobile bimanual robot', data_quality='paper_demo',
         success_type='rubric_progress',
         notes='Paper §VI-A: "more than 2x reduction in failure rates" with RECAP, ~70-80% range. 500s timeout. Hardest item is button-up shirt'),
]


def compute_is_frontier(rows):
    """Mark rows on the canonical real-world >=50% frontier.

    Frontier = real-world rows with success_rate >= 50, sorted by date,
    monotonic non-decreasing in human_time_seconds (ties allowed).
    """
    eligible = [r for r in rows
                if r['sim_or_real'] == 'real'
                and r['success_rate'] >= 50
                and r['num_trials'] >= 10]  # criterion 3: N>=10

    eligible.sort(key=lambda r: r['date'])
    max_time = 0
    frontier_keys = set()
    for r in eligible:
        if r['human_time_seconds'] >= max_time:
            max_time = r['human_time_seconds']
            frontier_keys.add((r['date'], r['system_name']))

    for r in rows:
        r['is_frontier'] = (r['date'], r['system_name']) in frontier_keys


def main():
    compute_is_frontier(ROWS)

    with open(OUT, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=COLS)
        writer.writeheader()
        for r in ROWS:
            r['is_frontier'] = 'TRUE' if r['is_frontier'] else 'FALSE'
            writer.writerow({c: r.get(c, '') for c in COLS})

    n_frontier = sum(1 for r in ROWS if r['is_frontier'] == 'TRUE')
    n_real = sum(1 for r in ROWS if r['sim_or_real'] == 'real')
    n_sim = sum(1 for r in ROWS if r['sim_or_real'] == 'sim')
    n_rubric = sum(1 for r in ROWS if r.get('success_type') == 'rubric_progress')

    print(f'Wrote {len(ROWS)} rows to {OUT}')
    print(f'  real: {n_real}  sim: {n_sim}')
    print(f'  on frontier: {n_frontier}')
    print(f'  rubric_progress: {n_rubric}')
    print()
    print('Frontier (chronological):')
    for r in ROWS:
        if r['is_frontier'] == 'TRUE':
            print(f"  {r['date']}  {r['system_name']:35s}  {r['human_time_seconds']:>5d}s  {r['success_rate']:>3}%  ({r.get('success_type','binary')})")


if __name__ == '__main__':
    main()
