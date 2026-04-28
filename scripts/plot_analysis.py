#!/usr/bin/env python3
"""
Three exploratory analyses:
  1. Hardware trends — task complexity and success by hardware class over time
  2. Subtask complexity — growth of num_subtasks over time, correlation with duration
  3. Sim-to-real gap — success rate comparisons stratified by task complexity
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'manipulation_horizons.csv')
FIGURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(FIGURES_DIR, exist_ok=True)

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
})

DURATION_TICKS = [4, 10, 30, 60, 300, 600, 1800, 3600]
DURATION_LABELS = ['4s', '10s', '30s', '1m', '5m', '10m', '30m', '1hr']

# ── Hardware classification ───────────────────────────────────────────────────

HARDWARE_GROUPS = {
    'Dexterous Hand':    ('#E91E63', 'D'),
    'Bimanual (ALOHA)':  ('#9C27B0', 's'),
    'Mobile Manipulator':('#FF9800', '^'),
    'Humanoid':          ('#4CAF50', 'P'),
    'Single Arm (Real)': ('#2196F3', 'o'),
    'Simulation':        ('#9E9E9E', 'X'),
}


def classify_hardware(row):
    hw = str(row.get('hardware', '')).lower()
    sr = str(row.get('sim_or_real', '')).lower()
    if sr == 'sim':
        return 'Simulation'
    if 'shadow' in hw or 'dexterous hand' in hw:
        return 'Dexterous Hand'
    if 'aloha' in hw:
        return 'Bimanual (ALOHA)'
    if 'humanoid' in hw or 'figure 02' in hw or 'gr-1' in hw:
        return 'Humanoid'
    if 'mobile' in hw or 'everyday robots' in hw or 'fetch' in hw:
        return 'Mobile Manipulator'
    return 'Single Arm (Real)'


def load():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['hardware_class'] = df.apply(classify_hardware, axis=1)
    # Drop the explicit teleoperation row
    df = df[df['success_rate'] > 0].copy()
    return df


def _save(fig, name):
    path = os.path.join(FIGURES_DIR, name)
    fig.savefig(path, dpi=160, bbox_inches='tight')
    print(f'  saved {path}')


# ══════════════════════════════════════════════════════════════════════════════
# 1. HARDWARE TRENDS
# ══════════════════════════════════════════════════════════════════════════════

def plot_hardware_trends(df):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # ── 1a. Task duration over time, colored by hardware class ─────────────────
    ax = axes[0]
    for hw_class, (color, marker) in HARDWARE_GROUPS.items():
        sub = df[df['hardware_class'] == hw_class]
        if len(sub) == 0:
            continue
        reliable = sub[sub['success_rate'] >= 50]
        unreliable = sub[sub['success_rate'] < 50]
        if len(reliable) > 0:
            ax.scatter(reliable['date'], reliable['human_time_seconds'],
                       c=color, marker=marker, s=80, alpha=0.8,
                       label=hw_class, edgecolors='white', linewidth=0.5, zorder=3)
        if len(unreliable) > 0:
            ax.scatter(unreliable['date'], unreliable['human_time_seconds'],
                       facecolors='none', edgecolors=color, marker=marker,
                       s=80, alpha=0.5, linewidth=1.5, zorder=2)
    ax.set_yscale('log')
    ax.set_yticks(DURATION_TICKS)
    ax.set_yticklabels(DURATION_LABELS)
    ax.set_ylim(3, 10000)
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_xlim(datetime(2015, 6, 1), datetime(2026, 3, 1))
    ax.set_xlabel('Date')
    ax.set_ylabel('Human-Equivalent Task Duration')
    ax.set_title('Task Duration Over Time\nby Hardware Class')
    ax.legend(fontsize=8, loc='upper left')

    # ── 1b. Mean success rate by hardware class (bar chart) ────────────────────
    ax = axes[1]
    hw_stats = (
        df.groupby('hardware_class')['success_rate']
        .agg(['mean', 'sem', 'count'])
        .reset_index()
        .sort_values('mean', ascending=False)
    )
    colors_ordered = [HARDWARE_GROUPS[h][0] for h in hw_stats['hardware_class']]
    bars = ax.bar(range(len(hw_stats)), hw_stats['mean'],
                  color=colors_ordered, edgecolor='white', linewidth=0.8, alpha=0.85)
    ax.errorbar(range(len(hw_stats)), hw_stats['mean'],
                yerr=hw_stats['sem'] * 1.96, fmt='none',
                color='#333', capsize=4, linewidth=1.2)
    ax.set_xticks(range(len(hw_stats)))
    ax.set_xticklabels(hw_stats['hardware_class'], rotation=30, ha='right', fontsize=9)
    for i, (_, row) in enumerate(hw_stats.iterrows()):
        ax.text(i, row['mean'] + row['sem'] * 1.96 + 1.5,
                f"n={int(row['count'])}", ha='center', va='bottom', fontsize=8, color='#555')
    ax.set_ylim(0, 115)
    ax.set_ylabel('Mean Success Rate (%)')
    ax.set_title('Mean Success Rate\nby Hardware Class (95% CI)')
    ax.axhline(50, color='#E91E63', linestyle='--', linewidth=1.2, alpha=0.7, label='50% threshold')
    ax.legend(fontsize=8)

    # ── 1c. Median task duration by hardware class ─────────────────────────────
    ax = axes[2]
    hw_dur = (
        df.groupby('hardware_class')['human_time_seconds']
        .agg(['median', 'max', 'count'])
        .reset_index()
        .sort_values('median', ascending=False)
    )
    colors_dur = [HARDWARE_GROUPS[h][0] for h in hw_dur['hardware_class']]
    ax.barh(range(len(hw_dur)), hw_dur['median'],
            color=colors_dur, edgecolor='white', alpha=0.85, label='Median')
    ax.barh(range(len(hw_dur)), hw_dur['max'],
            color=colors_dur, edgecolor='white', alpha=0.25, label='Max')
    ax.set_yticks(range(len(hw_dur)))
    ax.set_yticklabels(hw_dur['hardware_class'], fontsize=9)
    ax.set_xscale('log')
    ax.set_xticks(DURATION_TICKS)
    ax.set_xticklabels(DURATION_LABELS, fontsize=8)
    ax.set_xlabel('Human-Equivalent Task Duration')
    ax.set_title('Task Duration by Hardware Class\n(Median and Max, log scale)')
    ax.legend(fontsize=8)

    fig.suptitle('Hardware Platform Trends', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    _save(fig, 'analysis_hardware_trends.png')
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# 2. SUBTASK COMPLEXITY
# ══════════════════════════════════════════════════════════════════════════════

def plot_subtask_complexity(df):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    CAT_COLORS = {'tabletop': '#2196F3', 'mobile_manipulation': '#FF9800'}
    CAT_LABELS = {'tabletop': 'Tabletop', 'mobile_manipulation': 'Mobile'}

    # ── 2a. Num subtasks over time ─────────────────────────────────────────────
    ax = axes[0]
    for cat, color in CAT_COLORS.items():
        sub = df[df['category'] == cat]
        reliable = sub[sub['success_rate'] >= 50]
        unreliable = sub[sub['success_rate'] < 50]
        if len(reliable) > 0:
            ax.scatter(reliable['date'], reliable['num_subtasks'],
                       c=color, s=70, alpha=0.8, label=CAT_LABELS[cat],
                       edgecolors='white', linewidth=0.5)
        if len(unreliable) > 0:
            ax.scatter(unreliable['date'], unreliable['num_subtasks'],
                       facecolors='none', edgecolors=color, s=70,
                       alpha=0.5, linewidth=1.5)

    # Frontier: max num_subtasks at ≥50% success over time
    frontier_sub = (
        df[df['success_rate'] >= 50]
        .sort_values('date')
        .copy()
    )
    max_sub = 0
    front_rows = []
    for _, row in frontier_sub.iterrows():
        if row['num_subtasks'] >= max_sub:
            max_sub = row['num_subtasks']
            front_rows.append(row)
    if front_rows:
        fdf = pd.DataFrame(front_rows)
        ax.step(fdf['date'], fdf['num_subtasks'],
                color='#E91E63', linewidth=2, where='post', alpha=0.9,
                label='Max subtasks (≥50% success)')

    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_xlim(datetime(2015, 6, 1), datetime(2026, 3, 1))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Subtasks')
    ax.set_title('Subtask Count Over Time\n(hollow = <50% success)')
    ax.legend(fontsize=8)

    # ── 2b. Num subtasks vs task duration ─────────────────────────────────────
    ax = axes[1]
    for cat, color in CAT_COLORS.items():
        sub = df[df['category'] == cat]
        ax.scatter(sub['num_subtasks'], sub['human_time_seconds'],
                   c=color, s=70, alpha=0.7, label=CAT_LABELS[cat],
                   edgecolors='white', linewidth=0.5)

    # Regression line on log(duration) ~ subtasks
    valid = df.dropna(subset=['num_subtasks', 'human_time_seconds'])
    x = valid['num_subtasks'].values
    y = np.log(valid['human_time_seconds'].values)
    if len(x) > 2:
        coeffs = np.polyfit(x, y, 1)
        x_fit = np.linspace(x.min(), x.max(), 100)
        ax.plot(x_fit, np.exp(np.polyval(coeffs, x_fit)),
                color='#333', linewidth=1.5, linestyle='--', alpha=0.6,
                label=f'Log-linear fit (slope={coeffs[0]:.2f})')

    ax.set_yscale('log')
    ax.set_yticks(DURATION_TICKS)
    ax.set_yticklabels(DURATION_LABELS)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.set_xlabel('Number of Subtasks')
    ax.set_ylabel('Human-Equivalent Task Duration')
    ax.set_title('Subtask Count vs. Task Duration\n(log scale)')
    ax.legend(fontsize=8)

    # ── 2c. Success rate vs num subtasks ──────────────────────────────────────
    ax = axes[2]
    for cat, color in CAT_COLORS.items():
        sub = df[df['category'] == cat]
        ax.scatter(sub['num_subtasks'], sub['success_rate'],
                   c=color, s=70, alpha=0.7, label=CAT_LABELS[cat],
                   edgecolors='white', linewidth=0.5)

    # Bin-averaged success rate
    bins = [0.5, 2.5, 4.5, 7.5, 16]
    bin_labels = ['1–2', '3–4', '5–7', '8+']
    df['subtask_bin'] = pd.cut(df['num_subtasks'], bins=bins, labels=bin_labels)
    bin_means = df.groupby('subtask_bin', observed=False)['success_rate'].agg(['mean', 'sem'])
    bin_x = [1.5, 3.5, 6, 10]
    ax.plot(bin_x, bin_means['mean'].values, color='#E91E63',
            marker='D', markersize=8, linewidth=2, label='Bin mean', zorder=5)
    ax.fill_between(bin_x,
                    bin_means['mean'].values - bin_means['sem'].values * 1.96,
                    bin_means['mean'].values + bin_means['sem'].values * 1.96,
                    color='#E91E63', alpha=0.15)

    ax.axhline(50, color='#E91E63', linestyle='--', linewidth=1.2,
               alpha=0.5, label='50% threshold')
    ax.set_ylim(-5, 110)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.set_xlabel('Number of Subtasks')
    ax.set_ylabel('Success Rate (%)')
    ax.set_title('Success Rate vs. Subtask Count\n(binned mean ± 95% CI)')
    ax.legend(fontsize=8)

    fig.suptitle('Subtask Complexity Analysis', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    _save(fig, 'analysis_subtask_complexity.png')
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# 3. SIM-TO-REAL GAP
# ══════════════════════════════════════════════════════════════════════════════

def plot_sim_to_real(df):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    SIM_COLORS = {'sim': '#4CAF50', 'real': '#9C27B0'}
    SIM_LABELS = {'sim': 'Simulation', 'real': 'Real World'}

    # ── 3a. Success rate vs task duration, sim vs real ────────────────────────
    ax = axes[0]
    for sr, color in SIM_COLORS.items():
        sub = df[df['sim_or_real'] == sr]
        ax.scatter(sub['human_time_seconds'], sub['success_rate'],
                   c=color, s=80, alpha=0.75, label=SIM_LABELS[sr],
                   edgecolors='white', linewidth=0.5)

    ax.axhline(50, color='#E91E63', linestyle='--', linewidth=1.2,
               alpha=0.6, label='50% threshold')
    ax.set_xscale('log')
    ax.set_xticks(DURATION_TICKS)
    ax.set_xticklabels(DURATION_LABELS)
    ax.set_ylim(-5, 110)
    ax.set_xlabel('Human-Equivalent Task Duration')
    ax.set_ylabel('Success Rate (%)')
    ax.set_title('Success Rate vs. Duration\nSim vs. Real (log scale)')
    ax.legend(fontsize=9)

    # ── 3b. Success rate by sim/real, stratified by task duration bin ─────────
    ax = axes[1]
    dur_bins = [0, 15, 60, 300, 10000]
    dur_labels = ['≤15s\n(grasping)', '16s–1m\n(short tasks)',
                  '1m–5m\n(medium)', '>5m\n(long)']
    df['dur_bin'] = pd.cut(df['human_time_seconds'], bins=dur_bins, labels=dur_labels)

    x = np.arange(len(dur_labels))
    width = 0.35
    for i, (sr, color) in enumerate(SIM_COLORS.items()):
        means = []
        errs = []
        for lbl in dur_labels:
            sub = df[(df['sim_or_real'] == sr) & (df['dur_bin'] == lbl)]['success_rate']
            means.append(sub.mean() if len(sub) > 0 else np.nan)
            errs.append(sub.sem() * 1.96 if len(sub) > 1 else 0)
        offset = (i - 0.5) * width
        bars = ax.bar(x + offset, means, width, color=color, alpha=0.8,
                      edgecolor='white', label=SIM_LABELS[sr])
        ax.errorbar(x + offset, means, yerr=errs, fmt='none',
                    color='#333', capsize=4, linewidth=1.2)

    ax.set_xticks(x)
    ax.set_xticklabels(dur_labels, fontsize=9)
    ax.set_ylim(0, 120)
    ax.axhline(50, color='#E91E63', linestyle='--', linewidth=1.2, alpha=0.6)
    ax.set_ylabel('Mean Success Rate (%)')
    ax.set_title('Success Rate by Task Duration Bin\nSim vs. Real (mean ± 95% CI)')
    ax.legend(fontsize=9)

    # ── 3c. Success rate by sim/real, split by data quality tier ──────────────
    ax = axes[2]
    quality_order = ['benchmark', 'paper_demo', 'public_demo']
    quality_labels = ['Benchmark\n(N trials)', 'Paper Demo', 'Public Demo']

    x = np.arange(len(quality_order))
    for i, (sr, color) in enumerate(SIM_COLORS.items()):
        means = []
        errs = []
        counts = []
        for q in quality_order:
            sub = df[(df['sim_or_real'] == sr) & (df['data_quality'] == q)]['success_rate']
            means.append(sub.mean() if len(sub) > 0 else np.nan)
            errs.append(sub.sem() * 1.96 if len(sub) > 1 else 0)
            counts.append(len(sub))
        offset = (i - 0.5) * width
        ax.bar(x + offset, means, width, color=color, alpha=0.8,
               edgecolor='white', label=SIM_LABELS[sr])
        ax.errorbar(x + offset, means, yerr=errs, fmt='none',
                    color='#333', capsize=4, linewidth=1.2)
        for j, (m, c) in enumerate(zip(means, counts)):
            if not np.isnan(m) and c > 0:
                ax.text(x[j] + offset, (m or 0) + (errs[j] or 0) + 1.5,
                        f'n={c}', ha='center', va='bottom', fontsize=8, color='#555')

    ax.set_xticks(x)
    ax.set_xticklabels(quality_labels, fontsize=9)
    ax.set_ylim(0, 130)
    ax.axhline(50, color='#E91E63', linestyle='--', linewidth=1.2, alpha=0.6, label='50%')
    ax.set_ylabel('Mean Success Rate (%)')
    ax.set_title('Success Rate by Data Quality\nSim vs. Real (mean ± 95% CI)')
    ax.legend(fontsize=9)

    fig.suptitle('Sim-to-Real Gap Analysis', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    _save(fig, 'analysis_sim_to_real.png')
    plt.close(fig)


def main():
    print('Loading data...')
    df = load()
    print(f'  {len(df)} systems loaded')

    print('\n── Hardware class distribution ──')
    print(df['hardware_class'].value_counts().to_string())

    print('\nGenerating plots...')
    plot_hardware_trends(df)
    plot_subtask_complexity(df)
    plot_sim_to_real(df)
    print('Done.')


if __name__ == '__main__':
    main()
