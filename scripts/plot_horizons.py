#!/usr/bin/env python3
"""
Plot the task-completion time horizon for robotic manipulation systems.
Analogous to METR's time horizon plots for LLM agents.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import LogLocator, LogFormatter
from datetime import datetime
import os

# Paths
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'manipulation_horizons.csv')
FIGURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(FIGURES_DIR, exist_ok=True)

# Style
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
})

CATEGORY_COLORS = {
    'tabletop': '#2196F3',
    'mobile_manipulation': '#FF9800',
}
CATEGORY_LABELS = {
    'tabletop': 'Tabletop / Fixed-base',
    'mobile_manipulation': 'Mobile Manipulation',
}
QUALITY_MARKERS = {
    'benchmark': 'o',
    'paper_demo': 's',
    'public_demo': '^',
}

# Notable non-frontier systems to label on the main plot.
# Maps system_name → (x_offset, y_offset) for annotation placement.
NOTABLE_SYSTEMS = {
    'RT-1': (10, -14),
    'RT-2': (10, 10),
    'SayCan': (-60, 12),
    'Mobile ALOHA': (10, -14),
    'FurnitureBench': (-85, -14),
    'Diffusion Policy': (-95, 8),
    'QT-Opt': (8, -14),
    'HIL-SERL': (10, -14),
    'Figure 02 at BMW': (-110, -14),
}


def load_data():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    df['human_time_minutes'] = df['human_time_seconds'] / 60.0
    df['human_time_hours'] = df['human_time_seconds'] / 3600.0
    return df


def compute_frontier(df, success_threshold=50, real_only=True):
    """Compute the frontier envelope.

    Canonical frontier is real-world only (sim results are tracked but
    don't anchor the envelope). Pass real_only=False for sensitivity.
    """
    filtered = df[df['success_rate'] >= success_threshold].copy()
    if real_only:
        filtered = filtered[filtered['sim_or_real'] == 'real']
    filtered = filtered.sort_values('date')

    frontier_points = []
    max_time = 0
    for _, row in filtered.iterrows():
        if row['human_time_seconds'] >= max_time:
            max_time = row['human_time_seconds']
            frontier_points.append(row)

    return pd.DataFrame(frontier_points)


def format_duration(seconds):
    """Format seconds into human-readable duration."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.0f}min"
    else:
        return f"{seconds/3600:.1f}hr"


def plot_main(df, frontier_df, save=True):
    """Main METR-style plot: all data points + frontier line.

    Real-world systems use category-colored circles. Sim-only systems
    use gray triangles to flag that they don't anchor the frontier.
    """
    fig, ax = plt.subplots(figsize=(14, 8))

    real_df = df[df['sim_or_real'] == 'real']
    sim_df = df[df['sim_or_real'] == 'sim']

    # Real systems by category, ≥50% filled, <50% hollow
    for cat, color in CATEGORY_COLORS.items():
        cat_data = real_df[real_df['category'] == cat]
        if len(cat_data) == 0:
            continue

        reliable = cat_data[cat_data['success_rate'] >= 50]
        if len(reliable) > 0:
            ax.scatter(reliable['date'], reliable['human_time_seconds'],
                      c=color, marker='o', s=80, alpha=0.75,
                      label=f"{CATEGORY_LABELS[cat]} (real, ≥50%)",
                      edgecolors='white', linewidth=0.5, zorder=3)

        unreliable = cat_data[cat_data['success_rate'] < 50]
        if len(unreliable) > 0:
            ax.scatter(unreliable['date'], unreliable['human_time_seconds'],
                      facecolors='none', edgecolors=color, marker='o', s=80,
                      alpha=0.5, linewidth=1.5, zorder=2,
                      label=f"{CATEGORY_LABELS[cat]} (real, <50%)")

    # Sim-only systems: gray triangles, distinct from real markers
    if len(sim_df) > 0:
        sim_reliable = sim_df[sim_df['success_rate'] >= 50]
        sim_unreliable = sim_df[sim_df['success_rate'] < 50]
        if len(sim_reliable) > 0:
            ax.scatter(sim_reliable['date'], sim_reliable['human_time_seconds'],
                      c='#9E9E9E', marker='^', s=80, alpha=0.6,
                      label='Sim-only (≥50%, not on frontier)',
                      edgecolors='white', linewidth=0.5, zorder=3)
        if len(sim_unreliable) > 0:
            ax.scatter(sim_unreliable['date'], sim_unreliable['human_time_seconds'],
                      facecolors='none', edgecolors='#9E9E9E', marker='^', s=80,
                      alpha=0.5, linewidth=1.2, zorder=2,
                      label='Sim-only (<50%)')

    # Plot frontier line (real-world ≥50% only)
    if len(frontier_df) > 0:
        ax.plot(frontier_df['date'], frontier_df['human_time_seconds'],
                color='#E91E63', linewidth=2.5, alpha=0.85, zorder=4,
                label='Frontier (real-world, ≥50%)')
        ax.scatter(frontier_df['date'], frontier_df['human_time_seconds'],
                  color='#E91E63', s=120, zorder=5, edgecolors='white',
                  linewidth=1.5)

    # Label frontier points
    frontier_names = set(frontier_df['system_name'].values) if len(frontier_df) > 0 else set()
    for _, row in frontier_df.iterrows():
        label = row['system_name']
        offset = (10, 10)
        ax.annotate(label, (row['date'], row['human_time_seconds']),
                   textcoords="offset points", xytext=offset,
                   fontsize=8, fontweight='bold', color='#333',
                   arrowprops=dict(arrowstyle='->', color='#999', lw=0.8))

    # Label notable non-frontier systems
    for _, row in df.iterrows():
        name = row['system_name']
        # Check if this system (or a prefix of it) matches a notable entry
        matched_key = None
        for key in NOTABLE_SYSTEMS:
            if key in name:
                matched_key = key
                break
        if matched_key is None:
            continue
        if name in frontier_names:
            continue  # already labeled as frontier
        offset = NOTABLE_SYSTEMS[matched_key]
        ax.annotate(matched_key, (row['date'], row['human_time_seconds']),
                   textcoords="offset points", xytext=offset,
                   fontsize=7, fontstyle='italic', color='#666',
                   arrowprops=dict(arrowstyle='->', color='#bbb', lw=0.6))

    # Y-axis: log scale with human-readable labels
    ax.set_yscale('log')
    y_ticks = [5, 10, 30, 60, 300, 600, 1800, 3600, 7200]
    y_labels = ['5s', '10s', '30s', '1min', '5min', '10min', '30min', '1hr', '2hr']
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_ylim(3, 10000)

    # X-axis
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_xlim(datetime(2015, 6, 1), datetime(2026, 1, 1))

    ax.set_xlabel('Date')
    ax.set_ylabel('Human-Equivalent Task Duration')
    ax.set_title('Robotic Manipulation Task Horizon Over Time\n'
                 '(Longest task completed at ≥50% success rate, measured in human-equivalent time)',
                 fontsize=13)

    # Legend
    handles, labels = ax.get_legend_handles_labels()
    # Deduplicate
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(),
              loc='upper left', fontsize=9, framealpha=0.9)

    plt.tight_layout()
    if save:
        fig.savefig(os.path.join(FIGURES_DIR, 'main_horizon_plot.png'), dpi=200, bbox_inches='tight')
        fig.savefig(os.path.join(FIGURES_DIR, 'main_horizon_plot.svg'), bbox_inches='tight')
        print(f"Saved main plot to {FIGURES_DIR}/main_horizon_plot.png")
    return fig, ax


def plot_by_category(df, save=True):
    """Separate plots for tabletop vs mobile manipulation."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=True)

    for idx, (cat, color) in enumerate(CATEGORY_COLORS.items()):
        ax = axes[idx]
        mask = df['category'] == cat
        cat_data = df[mask]

        # Filter for >=50% success
        reliable = cat_data[cat_data['success_rate'] >= 50]

        if len(cat_data) > 0:
            ax.scatter(cat_data['date'], cat_data['human_time_seconds'],
                      c=color, s=60, alpha=0.5, edgecolors='white', linewidth=0.5)

        # Frontier for this category
        frontier = compute_frontier(cat_data, success_threshold=50)
        if len(frontier) > 0:
            ax.plot(frontier['date'], frontier['human_time_seconds'],
                    color=color, linewidth=2.5, alpha=0.9)
            for _, row in frontier.iterrows():
                ax.annotate(row['system_name'],
                           (row['date'], row['human_time_seconds']),
                           textcoords="offset points", xytext=(8, 8),
                           fontsize=7, fontweight='bold')

        ax.set_yscale('log')
        y_ticks = [5, 10, 30, 60, 300, 600, 1800, 3600]
        y_labels = ['5s', '10s', '30s', '1min', '5min', '10min', '30min', '1hr']
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)
        ax.set_ylim(3, 10000)
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.set_xlim(datetime(2015, 6, 1), datetime(2026, 1, 1))
        ax.set_title(CATEGORY_LABELS[cat], fontsize=13, color=color)
        ax.set_xlabel('Date')
        ax.grid(True, alpha=0.3, linestyle='--')

    axes[0].set_ylabel('Human-Equivalent Task Duration')
    fig.suptitle('Task Horizon by Category', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save:
        fig.savefig(os.path.join(FIGURES_DIR, 'category_comparison.png'), dpi=200, bbox_inches='tight')
        print(f"Saved category plot to {FIGURES_DIR}/category_comparison.png")
    return fig, axes


def plot_with_metr_overlay(df, frontier_df, save=True):
    """Overlay approximate METR LLM agent horizon for comparison."""
    fig, ax = plt.subplots(figsize=(14, 8))

    # METR LLM agent trend line.
    # We avoid hand-eyeballing per-model points (the original version of this
    # plot did that and the values didn't match METR's published numbers).
    # Instead we anchor on METR's one explicitly stated value and propagate
    # their published doubling time:
    #   - Claude 3.7 Sonnet, Feb 2025: ~60 min (3600s) at 50% success
    #     Source: METR, "Measuring AI Ability to Complete Long Tasks",
    #             https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/
    #   - Doubling time: ~7 months (METR overall finding, same post)
    metr_anchor_date = datetime(2025, 2, 1)
    metr_anchor_seconds = 3600.0
    metr_doubling_months = 7.0
    metr_growth_per_day = np.log(2) / (metr_doubling_months * 30.4375)

    line_dates = [datetime(2019, 1, 1), datetime(2025, 6, 1)]
    line_horizons = [
        metr_anchor_seconds * np.exp(
            metr_growth_per_day * ((d - metr_anchor_date).days)
        )
        for d in line_dates
    ]
    ax.plot(line_dates, line_horizons, color='#9C27B0', linewidth=2, alpha=0.7,
            linestyle='--',
            label='METR LLM agents (50% horizon, ~7-mo doubling)',
            zorder=2)
    # Anchor point so readers see what the line is pinned to
    ax.scatter([metr_anchor_date], [metr_anchor_seconds],
               color='#9C27B0', s=80, marker='*', zorder=3,
               edgecolors='white', linewidth=0.7,
               label='Claude 3.7 Sonnet (METR-stated, Feb 2025)')

    # Plot robot frontier
    if len(frontier_df) > 0:
        ax.plot(frontier_df['date'], frontier_df['human_time_seconds'],
                color='#E91E63', linewidth=2.5, alpha=0.9, zorder=4,
                label='Robot Manipulation Frontier')
        ax.scatter(frontier_df['date'], frontier_df['human_time_seconds'],
                  color='#E91E63', s=100, zorder=5, edgecolors='white', linewidth=1.5)

        for _, row in frontier_df.iterrows():
            ax.annotate(row['system_name'],
                       (row['date'], row['human_time_seconds']),
                       textcoords="offset points", xytext=(10, 10),
                       fontsize=8, fontweight='bold', color='#333',
                       arrowprops=dict(arrowstyle='->', color='#999', lw=0.8))

    # All robot data points — real (colored circles) vs sim (gray triangles)
    frontier_names = set(frontier_df['system_name'].values) if len(frontier_df) > 0 else set()
    real_df = df[df['sim_or_real'] == 'real']
    sim_df = df[df['sim_or_real'] == 'sim']
    for cat, color in CATEGORY_COLORS.items():
        cat_data = real_df[real_df['category'] == cat]
        reliable = cat_data[cat_data['success_rate'] >= 50]
        if len(reliable) > 0:
            ax.scatter(reliable['date'], reliable['human_time_seconds'],
                      c=color, marker='o', s=50, alpha=0.5, edgecolors='white', linewidth=0.5,
                      label=f"{CATEGORY_LABELS[cat]} (real)", zorder=3)
        unreliable = cat_data[cat_data['success_rate'] < 50]
        if len(unreliable) > 0:
            ax.scatter(unreliable['date'], unreliable['human_time_seconds'],
                      facecolors='none', edgecolors=color, marker='o', s=50, alpha=0.35,
                      linewidth=1.2, zorder=2,
                      label=f"{CATEGORY_LABELS[cat]} (real, <50%)")
    if len(sim_df) > 0:
        ax.scatter(sim_df['date'], sim_df['human_time_seconds'],
                  c='#9E9E9E', marker='^', s=45, alpha=0.5,
                  edgecolors='white', linewidth=0.4,
                  label='Sim-only', zorder=2)

    # Label notable non-frontier systems on comparison plot too
    for _, row in df.iterrows():
        name = row['system_name']
        matched_key = None
        for key in NOTABLE_SYSTEMS:
            if key in name:
                matched_key = key
                break
        if matched_key is None or name in frontier_names:
            continue
        offset = NOTABLE_SYSTEMS[matched_key]
        ax.annotate(matched_key, (row['date'], row['human_time_seconds']),
                   textcoords="offset points", xytext=offset,
                   fontsize=7, fontstyle='italic', color='#666',
                   arrowprops=dict(arrowstyle='->', color='#bbb', lw=0.6))

    ax.set_yscale('log')
    y_ticks = [5, 10, 30, 60, 300, 600, 1800, 3600, 7200, 21600]
    y_labels = ['5s', '10s', '30s', '1min', '5min', '10min', '30min', '1hr', '2hr', '6hr']
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_ylim(3, 50000)

    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_xlim(datetime(2015, 6, 1), datetime(2026, 1, 1))

    ax.set_xlabel('Date')
    ax.set_ylabel('Human-Equivalent Task Duration (log scale)')
    ax.set_title('Robot Manipulation vs. LLM Agent Task Horizons\n'
                 '(50% reliability threshold, human-equivalent time)',
                 fontsize=13)

    ax.legend(loc='upper left', fontsize=9, framealpha=0.9)
    plt.tight_layout()

    if save:
        fig.savefig(os.path.join(FIGURES_DIR, 'robot_vs_llm_comparison.png'), dpi=200, bbox_inches='tight')
        print(f"Saved comparison plot to {FIGURES_DIR}/robot_vs_llm_comparison.png")
    return fig, ax


def plot_sensitivity(df, save=True):
    """Show how frontier changes at different success thresholds.

    Small-multiples view: one panel per threshold so each frontier is
    readable on its own axes, with the underlying scatter as faint
    background. A sixth panel overlays all five for comparison.
    """
    thresholds = [50, 70, 90]
    colors = ['#E91E63', '#FF9800', '#2196F3']

    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharey=True)
    axes = axes.flatten()

    real_df = df[df['sim_or_real'] == 'real']

    def style_axis(ax):
        ax.set_yscale('log')
        y_ticks = [5, 10, 30, 60, 300, 600, 1800, 3600]
        y_labels = ['5s', '10s', '30s', '1min', '5min', '10min', '30min', '1hr']
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)
        ax.set_ylim(3, 10000)
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.set_xlim(datetime(2015, 6, 1), datetime(2026, 1, 1))
        ax.grid(True, alpha=0.3, linestyle='--')

    # One panel per threshold
    for i, (thresh, color) in enumerate(zip(thresholds, colors)):
        ax = axes[i]
        # Faint scatter of all real-world rows >= threshold
        eligible = real_df[real_df['success_rate'] >= thresh]
        if len(eligible) > 0:
            ax.scatter(eligible['date'], eligible['human_time_seconds'],
                       c='#999', s=30, alpha=0.4, zorder=1)
        # Frontier line
        frontier = compute_frontier(df, success_threshold=thresh)
        if len(frontier) > 0:
            ax.plot(frontier['date'], frontier['human_time_seconds'],
                    color=color, linewidth=2.5, alpha=0.9, zorder=3,
                    marker='o', markersize=6)
            # Label only the last point
            last = frontier.iloc[-1]
            ax.annotate(last['system_name'],
                        (last['date'], last['human_time_seconds']),
                        textcoords='offset points', xytext=(8, 8),
                        fontsize=8, fontweight='bold', color=color)
        style_axis(ax)
        ax.set_title(f'≥{thresh}% success  (N={len(frontier)})',
                     fontsize=12, color=color, fontweight='bold')

    # Fourth panel: all three overlaid
    ax = axes[3]
    for thresh, color in zip(thresholds, colors):
        frontier = compute_frontier(df, success_threshold=thresh)
        if len(frontier) > 0:
            ax.plot(frontier['date'], frontier['human_time_seconds'],
                    color=color, linewidth=2, alpha=0.85,
                    label=f'≥{thresh}% (N={len(frontier)})',
                    marker='o', markersize=4)
    style_axis(ax)
    ax.set_title('All thresholds overlaid', fontsize=12, fontweight='bold')
    ax.legend(loc='upper left', fontsize=9, framealpha=0.9)

    for ax in axes[2:]:
        ax.set_xlabel('Date')
    axes[0].set_ylabel('Human-Equivalent Task Duration')
    axes[2].set_ylabel('Human-Equivalent Task Duration')

    fig.suptitle('Frontier Sensitivity to Success Rate Threshold',
                 fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()

    ax.set_yscale('log')
    y_ticks = [5, 10, 30, 60, 300, 600, 1800, 3600]
    y_labels = ['5s', '10s', '30s', '1min', '5min', '10min', '30min', '1hr']
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_ylim(3, 10000)

    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_xlim(datetime(2015, 6, 1), datetime(2026, 1, 1))

    ax.set_xlabel('Date')
    ax.set_ylabel('Human-Equivalent Task Duration')
    ax.set_title('Frontier Sensitivity to Success Rate Threshold', fontsize=13)
    ax.legend(fontsize=10)
    plt.tight_layout()

    if save:
        fig.savefig(os.path.join(FIGURES_DIR, 'sensitivity_thresholds.png'), dpi=200, bbox_inches='tight')
        print(f"Saved sensitivity plot to {FIGURES_DIR}/sensitivity_thresholds.png")
    return fig, ax


def plot_binary_vs_mixed_frontier(df, save=True):
    """Plot the canonical (binary + rubric) frontier and the binary-only
    frontier on the same axes. The two tell different stories about the
    2019–2024 plateau.
    """
    fig, ax = plt.subplots(figsize=(14, 8))

    # Background scatter: all real-world rows
    real_df = df[df['sim_or_real'] == 'real']
    binary_pts = real_df[real_df['success_type'] == 'binary']
    rubric_pts = real_df[real_df['success_type'] == 'rubric_progress']

    if len(binary_pts) > 0:
        ax.scatter(binary_pts['date'], binary_pts['human_time_seconds'],
                   c='#bbb', s=35, alpha=0.45, marker='o', zorder=1,
                   label='All real-world (binary)')
    if len(rubric_pts) > 0:
        ax.scatter(rubric_pts['date'], rubric_pts['human_time_seconds'],
                   facecolors='none', edgecolors='#bbb', s=50, alpha=0.5,
                   marker='D', linewidth=1, zorder=1,
                   label='All real-world (rubric)')

    # Mixed frontier (canonical: binary + rubric, ≥50%)
    mixed = compute_frontier(df, success_threshold=50, real_only=True)
    if len(mixed) > 0:
        ax.plot(mixed['date'], mixed['human_time_seconds'],
                color='#E91E63', linewidth=2.5, alpha=0.9, zorder=4,
                label=f'Mixed frontier — binary + rubric (N={len(mixed)})',
                marker='o', markersize=8)

    # Binary-only frontier
    df_binary = df[df['success_type'] == 'binary']
    binary_frontier = compute_frontier(df_binary, success_threshold=50, real_only=True)
    if len(binary_frontier) > 0:
        ax.plot(binary_frontier['date'], binary_frontier['human_time_seconds'],
                color='#2196F3', linewidth=2.5, alpha=0.9, zorder=5,
                label=f'Binary-only frontier (N={len(binary_frontier)})',
                marker='s', markersize=7, linestyle='--')

    # Annotate key divergence points
    for _, r in mixed.iterrows():
        if r['success_type'] == 'rubric_progress':
            ax.annotate(f"{r['system_name']}\n(rubric)",
                        (r['date'], r['human_time_seconds']),
                        textcoords='offset points', xytext=(10, 10),
                        fontsize=8, fontweight='bold', color='#E91E63',
                        arrowprops=dict(arrowstyle='->', color='#E91E63', lw=0.7))

    # Annotate the tail of the binary frontier
    if len(binary_frontier) > 0:
        last_binary = binary_frontier.iloc[-1]
        ax.annotate(f"{last_binary['system_name']}\n(binary)",
                    (last_binary['date'], last_binary['human_time_seconds']),
                    textcoords='offset points', xytext=(-110, -25),
                    fontsize=8, fontweight='bold', color='#2196F3',
                    arrowprops=dict(arrowstyle='->', color='#2196F3', lw=0.7))

    # Y-axis: log
    ax.set_yscale('log')
    y_ticks = [5, 10, 30, 60, 300, 600, 1800, 3600]
    y_labels = ['5s', '10s', '30s', '1min', '5min', '10min', '30min', '1hr']
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_ylim(3, 10000)

    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_xlim(datetime(2015, 6, 1), datetime(2026, 1, 1))

    ax.set_xlabel('Date')
    ax.set_ylabel('Human-Equivalent Task Duration')
    ax.set_title('Two frontiers tell different stories\n'
                 'Mixed (binary + rubric): 14.1mo doubling, R² = 0.78, with 5-year plateau\n'
                 'Binary-only: 17.8mo doubling, R² = 0.91, no plateau',
                 fontsize=12)
    ax.legend(loc='upper left', fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()
    if save:
        fig.savefig(os.path.join(FIGURES_DIR, 'binary_vs_mixed_frontier.png'),
                    dpi=200, bbox_inches='tight')
        print(f"Saved binary-vs-mixed plot to {FIGURES_DIR}/binary_vs_mixed_frontier.png")
    return fig, ax


def main():
    print("Loading data...")
    df = load_data()
    print(f"Loaded {len(df)} data points")

    if len(df) == 0:
        print("No data points found. Please populate data/manipulation_horizons.csv first.")
        return

    # Summary stats
    print(f"\nCategories: {df['category'].value_counts().to_dict()}")
    print(f"Sim vs Real: {df['sim_or_real'].value_counts().to_dict()}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Human time range: {format_duration(df['human_time_seconds'].min())} to {format_duration(df['human_time_seconds'].max())}")

    # Compute frontier
    frontier_df = compute_frontier(df, success_threshold=50)
    print(f"\nFrontier points (≥50% success): {len(frontier_df)}")
    if len(frontier_df) > 0:
        print("\nFrontier systems:")
        for _, row in frontier_df.iterrows():
            print(f"  {row['date'].strftime('%Y-%m')} | {row['system_name']:25s} | "
                  f"{format_duration(row['human_time_seconds']):>6s} | "
                  f"{row['success_rate']:.0f}% success | {row['task_description'][:60]}")

    # Generate all plots
    print("\nGenerating plots...")
    plot_main(df, frontier_df)
    plot_by_category(df)
    plot_with_metr_overlay(df, frontier_df)
    plot_sensitivity(df)
    plot_binary_vs_mixed_frontier(df)
    print("\nDone! Check the figures/ directory.")


if __name__ == '__main__':
    main()
