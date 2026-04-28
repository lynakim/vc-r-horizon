#!/usr/bin/env python3
"""
Success rate vs. task duration curves, one line per system.
Models success(t) = exp(-t/tau) with tau fitted from observed data points.
Solid line up to observed anchor; dashed extrapolation beyond.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'manipulation_horizons.csv')
FIGURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'figures')

# Multi-point data for systems where we have per-task breakdowns
# (task_duration_seconds, success_rate_fraction)
MULTI_POINT_DATA = {
    'Mobile ALOHA': [
        (10,  0.95),   # wipe wine
        (20,  0.95),   # call elevator
        (45,  0.80),   # rinse pan
        (90,  0.85),   # use two-door cabinet (the frontier entry)
        (180, 0.40),   # cook shrimp (fails our 50% threshold)
    ],
    'Pi0.6': [
        (240, 0.90),   # espresso (grind+tamp+extract+clean)
        (300, 0.97),   # laundry folding on 50 novel items
        (600, 0.20),   # box assembly
    ],
}

# Systems to show — frontier systems get labels; others are context
FRONTIER_SYSTEMS = {
    'OpenAI Dactyl - Rubik\'s Cube',
    'SayCan',
    'ACT / ALOHA',
    'Mobile ALOHA',
    'Pi0',
    'Pi0.5',
    'Pi0.6',
}

# A few non-frontier reference systems to show range
REFERENCE_SYSTEMS = {
    'RT-1',
    'FurnitureBench',
    'Levine et al. Grasping',
    'Diffusion Policy',
}

SYSTEM_LABELS = {
    'OpenAI Dactyl - Rubik\'s Cube': "Dactyl Rubik's (2019)",
    'SayCan': 'SayCan (2022)',
    'ACT / ALOHA': 'ACT/ALOHA (2023)',
    'Mobile ALOHA': 'Mobile ALOHA (2024)',
    'Pi0': 'π0 (2024)',
    'Pi0.5': 'π0.5 (2025)',
    'Pi0.6': 'π0.6 (2025)',
    'RT-1': 'RT-1 (2022)',
    'FurnitureBench': 'FurnitureBench (2023)',
    'Levine et al. Grasping': 'Levine (2016)',
    'Diffusion Policy': 'Diffusion Policy (2023)',
}


def fit_tau_single(t0, s0):
    """Fit tau from one (duration, success_rate) data point."""
    if s0 <= 0 or s0 >= 1:
        return None
    return -t0 / np.log(s0)


def fit_tau_multi(points):
    """Fit tau from multiple (duration, success_rate) pairs via log-linear regression."""
    ts = np.array([p[0] for p in points if 0 < p[1] < 1])
    ss = np.array([p[1] for p in points if 0 < p[1] < 1])
    if len(ts) < 2:
        return fit_tau_single(ts[0], ss[0]) if len(ts) == 1 else None
    # log(s) = -t/tau  => regress log(s) on t, intercept=0
    tau = -np.dot(ts, ts) / np.dot(ts, np.log(ss))
    return tau if tau > 0 else None


def horizon_at_50(tau):
    return tau * np.log(2) if tau else None


def make_colormap_for_years(year_min, year_max):
    cmap = plt.cm.plasma
    norm = mcolors.Normalize(vmin=year_min, vmax=year_max)
    return cmap, norm


def plot_curves():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year

    # Filter to systems we want to show
    shown = df[df['system_name'].isin(FRONTIER_SYSTEMS | REFERENCE_SYSTEMS)].copy()
    shown = shown.sort_values('date')

    year_min = shown['year'].min()
    year_max = shown['year'].max()
    cmap, norm = make_colormap_for_years(year_min, year_max)

    fig, ax = plt.subplots(figsize=(13, 7))

    t_fine = np.logspace(np.log10(2), np.log10(15000), 800)

    for _, row in shown.iterrows():
        name = row['system_name']
        year = row['year']
        color = cmap(norm(year))
        is_frontier = name in FRONTIER_SYSTEMS
        lw = 2.2 if is_frontier else 1.2
        alpha_solid = 0.9 if is_frontier else 0.55
        alpha_dash = 0.35 if is_frontier else 0.2
        label = SYSTEM_LABELS.get(name)

        # Get data points
        if name in MULTI_POINT_DATA:
            points = MULTI_POINT_DATA[name]
            tau = fit_tau_multi(points)
            t_anchor = max(p[0] for p in points)   # rightmost observed point
        else:
            s0 = row['success_rate'] / 100
            t0 = row['human_time_seconds']
            tau = fit_tau_single(t0, s0)
            t_anchor = t0
            points = [(t0, s0)]

        if tau is None or tau <= 0:
            # 100% success — just plot point, can't fit curve
            ax.scatter(
                [row['human_time_seconds']], [row['success_rate']],
                color=color, s=90, marker='D', zorder=6,
                label=label,
            )
            continue

        # Solid curve: 0 → t_anchor
        t_solid = t_fine[t_fine <= t_anchor * 1.05]
        if len(t_solid) == 0:
            t_solid = np.array([t_anchor])
        ax.plot(
            t_solid, np.exp(-t_solid / tau) * 100,
            color=color, linewidth=lw, alpha=alpha_solid,
            label=label,
        )

        # Dashed extrapolation: t_anchor → right edge (while >5%)
        t_dash = t_fine[(t_fine > t_anchor) & (np.exp(-t_fine / tau) > 0.05)]
        if len(t_dash) > 0:
            ax.plot(
                t_dash, np.exp(-t_dash / tau) * 100,
                color=color, linewidth=lw, linestyle='--', alpha=alpha_dash,
            )

        # Mark observed data points
        for t_pt, s_pt in points:
            ax.scatter(
                [t_pt], [s_pt * 100],
                color=color, s=55 if is_frontier else 35,
                edgecolors='white', linewidths=0.6,
                zorder=7,
            )

        # Mark 50% horizon with a small tick on the x-axis
        t50 = horizon_at_50(tau)
        if t50 and 2 < t50 < 15000:
            ax.axvline(t50, color=color, linewidth=0.7, alpha=0.25, linestyle=':')

    # Reference lines
    ax.axhline(50, color='#444', linestyle='--', linewidth=1.2, alpha=0.7, label='50% threshold')

    # Annotations for a few key systems
    annotations = {
        'OpenAI Dactyl - Rubik\'s Cube': (245, 62, "Dactyl\nRubik's"),
        'Pi0.6': (620, 99, 'π0.6'),
        'Pi0.5': (620, 72, 'π0.5'),
        'Mobile ALOHA': (95, 87, 'Mobile\nALOHA'),
        'SayCan': (93, 76, 'SayCan'),
    }
    for name, (tx, ty, txt) in annotations.items():
        row = df[df['system_name'] == name]
        if len(row) == 0:
            continue
        year = row.iloc[0]['year']
        color = cmap(norm(year))
        ax.annotate(
            txt, xy=(tx, ty), fontsize=7.5, color=color,
            fontweight='bold', va='bottom',
        )

    ax.set_xscale('log')
    ax.set_xlim(3, 12000)
    ax.set_ylim(0, 110)
    ax.set_xlabel('Task Duration — human-equivalent time (seconds)', fontsize=11)
    ax.set_ylabel('Success Rate (%)', fontsize=11)
    ax.set_title(
        'Robot Manipulation: Success Rate vs. Task Duration\n'
        r'Fitted exponential model  $\mathrm{success}(t) = e^{-t/\tau}$ — '
        'solid = observed range, dashed = extrapolation',
        fontsize=11,
    )

    # x-axis tick labels in human-readable time
    xticks = [5, 10, 30, 60, 300, 600, 3600]
    xlabels = ['5s', '10s', '30s', '1 min', '5 min', '10 min', '1 hr']
    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels)

    ax.legend(fontsize=8, loc='upper right', framealpha=0.85, ncol=2)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, shrink=0.7, pad=0.01)
    cb.set_label('Year', fontsize=10)
    cb.set_ticks([2016, 2018, 2020, 2022, 2024, 2025])

    plt.tight_layout()
    out_path = os.path.join(FIGURES_DIR, 'success_vs_duration_curves.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    print(f'Saved {out_path}')
    plt.close()


if __name__ == '__main__':
    plot_curves()
