#!/usr/bin/env python3
"""
Scatter of (task duration, success rate) split by success_type.

The plot answers a specific question: how does the cloud of (duration, success)
points move over time, and how does that movement differ for binary task
completion vs. partial-credit rubric scoring? Through 2025 the binary cloud
above 50% does not pass ~200s, while the rubric cloud extends to 5–12 minutes.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.lines as mlines
import matplotlib.patheffects as pe

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'manipulation_horizons.csv')
FIGURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'figures')

# (label_text, dx_points, dy_points, ha)
BINARY_LABELS = {
    'Levine et al. Grasping':       ('Levine (2016)',            16,  -2, 'left'),
    'OpenAI Dactyl - Block':        ('Dactyl Block (2018)',      16,   8, 'left'),
    'ACT / ALOHA':                  ('ACT/ALOHA (2023)',         16,   8, 'left'),
    'Mobile ALOHA':                 ('Mobile ALOHA (2024)',       0, -20, 'center'),
    'Figure 02 at BMW':             ('Figure 02 @ BMW (2025)',    0,  20, 'center'),
    'π0.6 (single-shirt fold)':     ('π0.6 single-shirt (2025)', 16,  -2, 'left'),
}

RUBRIC_LABELS = {
    'π0 (laundry folding)':         ('π0 laundry (2024)',         0, -22, 'center'),
    'π0.5 (bedroom cleanup)':       ('π0.5 bedroom',              8, -22, 'left'),
    'π0.6 (espresso)':              ('π0.6 espresso (2025)',     16,   4, 'left'),
    'π0.6 (diverse laundry)':       ('π0.6 diverse laundry (2025)', -8, 22, 'right'),
    'TRI LBM - CutAppleInSlices':   ('TRI LBM apple-cut (2025)', 16,  -2, 'left'),
}


def _draw_panel(ax, df_panel, labels, cmap, norm, title, subtitle):
    # Reference shading for the <50% region — grounds the threshold visually
    ax.axhspan(0, 50, color='#f2f2f2', zorder=0)
    ax.axhline(50, color='#888', linestyle='--', linewidth=1.0, alpha=0.7, zorder=2)

    real = df_panel[df_panel['sim_or_real'] == 'real']
    sim = df_panel[df_panel['sim_or_real'] == 'sim']

    ax.scatter(
        sim['human_time_seconds'], sim['success_rate'],
        c=sim['year'], cmap=cmap, norm=norm,
        s=55, marker='o', facecolors='none', linewidths=1.2,
        alpha=0.75, zorder=3,
    )
    ax.scatter(
        real['human_time_seconds'], real['success_rate'],
        c=real['year'], cmap=cmap, norm=norm,
        s=70, marker='o', alpha=0.85, zorder=4,
    )

    for name, (label, dx, dy, ha) in labels.items():
        row = df_panel[df_panel['system_name'] == name]
        if len(row) == 0:
            continue
        r = row.iloc[0]
        color = cmap(norm(r['year']))
        ax.scatter(
            r['human_time_seconds'], r['success_rate'],
            s=160, marker='o', color=color,
            edgecolors='white', linewidths=1.0, zorder=5,
        )
        ax.annotate(
            label,
            xy=(r['human_time_seconds'], r['success_rate']),
            xytext=(dx, dy), textcoords='offset points',
            fontsize=7.8, color=color, fontweight='bold',
            ha=ha, va='center', zorder=6,
            path_effects=[pe.withStroke(linewidth=2.5, foreground='white')],
        )

    ax.set_xscale('log')
    ax.set_xlim(2, 8000)
    ax.set_ylim(0, 108)

    xticks = [5, 10, 30, 60, 300, 600, 3600]
    xlabels = ['5s', '10s', '30s', '1 min', '5 min', '10 min', '1 hr']
    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels)
    ax.set_xlabel('Task Duration — human-equivalent time', fontsize=10)

    ax.set_title(title, fontsize=11, fontweight='bold', loc='left', pad=18)
    ax.text(0.0, 1.01, subtitle, transform=ax.transAxes, fontsize=8.5,
            color='#444', ha='left', va='bottom')


def plot_scatter():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year

    # Drop reference-only rows (success_rate = 0 or num_trials = 0) and teleop
    df = df[df['num_trials'] > 0].copy()
    df = df[df['success_rate'] > 0].copy()
    df = df[df['system_name'] != 'Mobile ALOHA Cooking (Teleop)'].copy()

    year_min, year_max = df['year'].min(), df['year'].max()
    cmap = plt.cm.plasma
    norm = mcolors.Normalize(vmin=year_min, vmax=year_max)

    df_binary = df[df['success_type'] == 'binary']
    df_rubric = df[df['success_type'] == 'rubric_progress']

    fig, (ax_left, ax_right) = plt.subplots(
        1, 2, figsize=(15, 6.8), sharey=True,
        gridspec_kw={'width_ratios': [1, 1], 'wspace': 0.06},
    )

    _draw_panel(
        ax_left, df_binary, BINARY_LABELS, cmap, norm,
        title='Binary task completion',
        subtitle=f'n = {len(df_binary)}  ·  Through 2025, the longest binary ≥50% point is π0.6\'s 200s single-shirt fold',
    )
    ax_left.set_ylabel('Success Rate (%)', fontsize=10)

    _draw_panel(
        ax_right, df_rubric, RUBRIC_LABELS, cmap, norm,
        title='Rubric (partial-credit) progress',
        subtitle=f'n = {len(df_rubric)}  ·  The 2024–25 cluster (π0 / π0.5 / π0.6 / TRI LBM) pushes rubric progress to 5–12 min',
    )

    legend_real = mlines.Line2D([], [], color='gray', marker='o', linestyle='None',
                                markersize=7, label='Real-world')
    legend_sim = mlines.Line2D([], [], color='gray', marker='o', linestyle='None',
                               markersize=7, markerfacecolor='none', label='Sim-only')
    legend_50 = mlines.Line2D([], [], color='#888', linestyle='--', linewidth=1.0,
                              label='50% threshold')
    ax_left.legend(handles=[legend_real, legend_sim, legend_50],
                   fontsize=8.5, loc='lower left', framealpha=0.9)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cb = fig.colorbar(sm, ax=[ax_left, ax_right], shrink=0.7, pad=0.025,
                      fraction=0.02)
    cb.set_label('Year', fontsize=9)
    cb.set_ticks([2016, 2018, 2020, 2022, 2024, 2025])

    fig.suptitle(
        'How the cloud of (duration, success) points moves — split by success type',
        fontsize=13, fontweight='bold', y=0.995, x=0.42, ha='center',
    )
    fig.text(
        0.42, 0.945,
        'Each paper reports either binary completion ("did the full task succeed?") or rubric progress '
        '("how much of the task was completed on average?"). The two metrics are not interchangeable, and '
        'they tell different stories about 2024–2025.',
        fontsize=9, color='#444', ha='center', va='top', wrap=True,
    )

    plt.subplots_adjust(top=0.86, bottom=0.10, left=0.055, right=0.93)
    out_path = os.path.join(FIGURES_DIR, 'scatter_duration_success.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    print(f'Saved {out_path}')
    plt.close()


if __name__ == '__main__':
    plot_scatter()
