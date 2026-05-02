#!/usr/bin/env python3
"""
Scatter plot of all (task duration, success rate) data points, colored by year.
No model fitting — shows the raw data distribution and how it shifts over time.
"""

import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.lines as mlines
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'manipulation_horizons.csv')
FIGURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'figures')

# Notable systems to label, keyed on the exact `system_name` from the CSV.
# (label_text, x_nudge_factor, y_nudge)
# A warning is emitted if any key here is missing from the CSV — keeps the figure
# from silently dropping labels after dataset renames.
FRONTIER_LABELS = {
    'Levine et al. Grasping':        ('Levine (2016)',         1.15, -7.0),
    'OpenAI Dactyl - Block':         ('Dactyl Block (2018)',   1.12,  2.0),
    "OpenAI Dactyl - Rubik's Cube":  ("Dactyl Rubik's (2019)", 1.10, -7.0),
    'SayCan':                        ('SayCan (2022)',         1.12,  2.0),
    'ACT / ALOHA':                   ('ACT/ALOHA (2023)',      1.10,  2.0),
    'Mobile ALOHA':                  ('Mobile ALOHA (2024)',   1.10, -7.5),
    'π0 (laundry folding)':          ('π0 (2024)',             1.12,  2.0),
    'π0.5 (bedroom cleanup)':        ('π0.5 (2025)',           1.10, -7.0),
    'π0.6 (single-shirt fold)':      ('π0.6 (2025)',           1.10,  2.0),
}


def plot_scatter():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year

    # Exclude teleoperated/non-autonomous rows (recorded with success_rate=0)
    df = df[df['success_rate'] > 0].copy()

    year_min, year_max = df['year'].min(), df['year'].max()
    cmap = plt.cm.plasma
    norm = mcolors.Normalize(vmin=year_min, vmax=year_max)

    fig, ax = plt.subplots(figsize=(11, 7))

    real = df[df['sim_or_real'] == 'real']
    sim = df[df['sim_or_real'] == 'sim']

    # Sim points (open circles, smaller)
    ax.scatter(
        sim['human_time_seconds'], sim['success_rate'],
        c=sim['year'], cmap=cmap, norm=norm,
        s=55, marker='o', facecolors='none',
        linewidths=1.2, alpha=0.7, zorder=3,
    )

    # Real points (filled circles)
    ax.scatter(
        real['human_time_seconds'], real['success_rate'],
        c=real['year'], cmap=cmap, norm=norm,
        s=70, marker='o',
        alpha=0.85, zorder=4,
    )

    # Frontier systems: larger markers + labels
    missing = [n for n in FRONTIER_LABELS if (df['system_name'] == n).sum() == 0]
    if missing:
        warnings.warn(
            f"FRONTIER_LABELS keys not found in CSV (label dropped silently otherwise): {missing}",
            stacklevel=2,
        )

    for name, (label, xf, dy) in FRONTIER_LABELS.items():
        row = df[df['system_name'] == name]
        if len(row) == 0:
            continue
        r = row.iloc[0]
        color = cmap(norm(r['year']))
        ax.scatter(
            r['human_time_seconds'], r['success_rate'],
            s=160, marker='o', color=color,
            edgecolors='white', linewidths=1.0,
            zorder=5,
        )
        ax.annotate(
            label,
            xy=(r['human_time_seconds'], r['success_rate']),
            xytext=(r['human_time_seconds'] * xf, r['success_rate'] + dy),
            fontsize=7.5, color=color, fontweight='bold',
            va='bottom',
        )

    # 50% reference line
    ax.axhline(50, color='#555', linestyle='--', linewidth=1.2, alpha=0.6, label='50% threshold')

    ax.set_xscale('log')
    ax.set_xlim(2, 8000)
    ax.set_ylim(0, 108)

    xticks = [5, 10, 30, 60, 300, 600, 3600]
    xlabels = ['5s', '10s', '30s', '1 min', '5 min', '10 min', '1 hr']
    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels)

    ax.set_xlabel('Task Duration — human-equivalent time', fontsize=11)
    ax.set_ylabel('Success Rate (%)', fontsize=11)
    ax.set_title(
        'Robot Manipulation: Task Duration vs. Success Rate (all systems, 2016–2025)\n'
        'Filled = real-world  ·  Open = sim-only  ·  Large = frontier systems',
        fontsize=11,
    )

    # Proxy artists so the legend shows marker style, not colormap colors
    legend_real = mlines.Line2D([], [], color='gray', marker='o', linestyle='None',
                                markersize=7, label='Real-world')
    legend_sim = mlines.Line2D([], [], color='gray', marker='o', linestyle='None',
                               markersize=7, markerfacecolor='none', label='Sim-only')
    legend_50 = mlines.Line2D([], [], color='#555', linestyle='--', linewidth=1.2,
                              label='50% threshold')
    ax.legend(handles=[legend_real, legend_sim, legend_50],
              fontsize=9, loc='lower left', framealpha=0.85)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, shrink=0.75, pad=0.01)
    cb.set_label('Year', fontsize=10)
    cb.set_ticks([2016, 2018, 2020, 2022, 2024, 2025])

    plt.tight_layout()
    out_path = os.path.join(FIGURES_DIR, 'scatter_duration_success.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    print(f'Saved {out_path}')
    plt.close()


if __name__ == '__main__':
    plot_scatter()
