#!/usr/bin/env python3
"""
Hardware trends analysis:
  - Task duration over time, by hardware class
  - Median/max task duration by hardware class (real-world systems only)

Note on interpretation: the right panel shows what task complexity each form
factor has been *applied to*, not what it's capable of. Single-arm systems skew
short because most single-arm work targets simpler pick-and-place tasks;
bimanual and mobile platforms are deployed for longer, multi-step tasks by
design.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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

# Hardware groups — simulation is tracked but excluded from the duration bar chart
# since it's an evaluation environment, not a hardware form factor.
HARDWARE_GROUPS = {
    'Dexterous Hand':    ('#E91E63', 'D'),
    'Bimanual (ALOHA)':  ('#9C27B0', 's'),
    'Mobile Manipulator':('#FF9800', '^'),
    'Humanoid':          ('#4CAF50', 'P'),
    'Single Arm (Real)': ('#2196F3', 'o'),
    'Simulation':        ('#9E9E9E', 'X'),
}

# Classes to show in the duration-by-hardware bar chart (real hardware only)
REAL_HARDWARE_ORDER = [
    'Bimanual (ALOHA)',
    'Mobile Manipulator',
    'Humanoid',
    'Dexterous Hand',
    'Single Arm (Real)',
]


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
    df = df[df['success_rate'] > 0].copy()  # drop explicit teleoperation row
    return df


def _save(fig, name):
    path = os.path.join(FIGURES_DIR, name)
    fig.savefig(path, dpi=160, bbox_inches='tight')
    print(f'  saved {path}')


def plot_hardware_trends(df):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # ── Left: task duration over time, colored by hardware class ──────────────
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
            # hollow markers for <50% success — no separate legend entry
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
    ax.set_title('Task Duration Over Time by Hardware Class\n'
                 '(filled = ≥50% success, hollow = <50%)')
    ax.legend(fontsize=8, loc='upper left')

    # ── Right: median/max task duration by real hardware class ────────────────
    # Shows what complexity level each form factor has been applied to.
    # Simulation excluded — it's an evaluation environment, not a hardware class.
    ax = axes[1]
    real_df = df[df['hardware_class'].isin(REAL_HARDWARE_ORDER)].copy()
    hw_dur = (
        real_df.groupby('hardware_class')['human_time_seconds']
        .agg(['median', 'max', 'count'])
        .reindex(REAL_HARDWARE_ORDER)
        .dropna()
    )
    colors_dur = [HARDWARE_GROUPS[h][0] for h in hw_dur.index]

    y_pos = range(len(hw_dur))
    ax.barh(y_pos, hw_dur['max'], color=colors_dur, edgecolor='white',
            alpha=0.25, label='Max (any success rate)')
    ax.barh(y_pos, hw_dur['median'], color=colors_dur, edgecolor='white',
            alpha=0.85, label='Median (all systems)')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(
        [f"{h}  (n={int(hw_dur.loc[h, 'count'])})" for h in hw_dur.index],
        fontsize=9
    )
    ax.set_xscale('log')
    ax.set_xticks(DURATION_TICKS)
    ax.set_xticklabels(DURATION_LABELS, fontsize=9)
    ax.set_xlabel('Human-Equivalent Task Duration')
    ax.set_title('Task Duration by Hardware Class\n'
                 '(real-world systems only; median and max across all reported success rates)')
    ax.legend(fontsize=8)

    fig.suptitle('Hardware Platform Trends', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    _save(fig, 'analysis_hardware_trends.png')
    plt.close(fig)


def main():
    print('Loading data...')
    df = load()
    print(f'  {len(df)} systems loaded')

    print('\nHardware class distribution:')
    print(df['hardware_class'].value_counts().to_string())

    print('\nGenerating plots...')
    plot_hardware_trends(df)
    print('Done.')


if __name__ == '__main__':
    main()
