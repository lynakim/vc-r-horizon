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


def compute_frontier(df, success_threshold=50):
    """Compute the frontier envelope: for each date, the longest task at >= threshold success."""
    filtered = df[df['success_rate'] >= success_threshold].copy()
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
    """Main METR-style plot: all data points + frontier line."""
    fig, ax = plt.subplots(figsize=(14, 8))

    # Plot all data points by category, splitting filled (≥50%) vs hollow (<50%)
    for cat, color in CATEGORY_COLORS.items():
        mask = df['category'] == cat
        cat_data = df[mask]
        if len(cat_data) == 0:
            continue

        # Reliable (≥50% success): filled markers
        reliable = cat_data[cat_data['success_rate'] >= 50]
        if len(reliable) > 0:
            ax.scatter(reliable['date'], reliable['human_time_seconds'],
                      c=color, marker='o', s=80, alpha=0.7,
                      label=f"{CATEGORY_LABELS[cat]} (≥50%)",
                      edgecolors='white', linewidth=0.5, zorder=3)

        # Unreliable (<50% success): hollow markers
        unreliable = cat_data[cat_data['success_rate'] < 50]
        if len(unreliable) > 0:
            ax.scatter(unreliable['date'], unreliable['human_time_seconds'],
                      facecolors='none', edgecolors=color, marker='o', s=80,
                      alpha=0.5, linewidth=1.5, zorder=2,
                      label=f"{CATEGORY_LABELS[cat]} (<50%, attempted)")

    # Plot frontier line
    if len(frontier_df) > 0:
        ax.plot(frontier_df['date'], frontier_df['human_time_seconds'],
                color='#E91E63', linewidth=2.5, alpha=0.8, zorder=4,
                label='Frontier (≥50% success)')
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

    # METR LLM agent data (approximate, from their publications)
    # 50% time horizon in seconds (human-equivalent time)
    metr_dates = [
        datetime(2019, 6, 1),   # GPT-2 era
        datetime(2020, 6, 1),   # GPT-3
        datetime(2021, 3, 1),   # Codex
        datetime(2022, 3, 1),   # text-davinci-002
        datetime(2022, 12, 1),  # ChatGPT
        datetime(2023, 3, 1),   # GPT-4
        datetime(2023, 11, 1),  # GPT-4 Turbo
        datetime(2024, 5, 1),   # GPT-4o / Claude 3
        datetime(2024, 12, 1),  # o1 / Claude 3.5
        datetime(2025, 6, 1),   # Claude 4 / GPT-5 era
    ]
    # Approximate 50% horizons from METR data (seconds)
    # ~1 min in 2019 doubling every 7 months → ~2-4 hours by 2025
    metr_horizons = [
        60,       # ~1 min
        120,      # ~2 min
        240,      # ~4 min
        480,      # ~8 min
        900,      # ~15 min
        1800,     # ~30 min
        2700,     # ~45 min
        5400,     # ~90 min
        10800,    # ~3 hr
        21600,    # ~6 hr
    ]

    ax.plot(metr_dates, metr_horizons, color='#9C27B0', linewidth=2, alpha=0.6,
            linestyle='--', label='METR LLM Agent Horizon (approx.)', zorder=2)
    ax.fill_between(metr_dates, [h * 0.5 for h in metr_horizons],
                    [h * 2 for h in metr_horizons],
                    color='#9C27B0', alpha=0.08, zorder=1)

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

    # All robot data points — filled (≥50%) vs hollow (<50%)
    frontier_names = set(frontier_df['system_name'].values) if len(frontier_df) > 0 else set()
    for cat, color in CATEGORY_COLORS.items():
        mask = df['category'] == cat
        cat_data = df[mask]

        reliable = cat_data[cat_data['success_rate'] >= 50]
        if len(reliable) > 0:
            ax.scatter(reliable['date'], reliable['human_time_seconds'],
                      c=color, s=50, alpha=0.4, edgecolors='white', linewidth=0.5,
                      label=CATEGORY_LABELS[cat], zorder=3)

        unreliable = cat_data[cat_data['success_rate'] < 50]
        if len(unreliable) > 0:
            ax.scatter(unreliable['date'], unreliable['human_time_seconds'],
                      facecolors='none', edgecolors=color, s=50, alpha=0.35,
                      linewidth=1.2, zorder=2,
                      label=f"{CATEGORY_LABELS[cat]} (<50%)")

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
    """Show how frontier changes at different success thresholds."""
    fig, ax = plt.subplots(figsize=(12, 7))

    thresholds = [30, 50, 80]
    colors = ['#4CAF50', '#E91E63', '#FF5722']
    alphas = [0.6, 1.0, 0.6]

    for thresh, color, alpha in zip(thresholds, colors, alphas):
        frontier = compute_frontier(df, success_threshold=thresh)
        if len(frontier) > 0:
            ax.plot(frontier['date'], frontier['human_time_seconds'],
                    color=color, linewidth=2, alpha=alpha,
                    label=f'≥{thresh}% success', marker='o', markersize=5)

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
    print("\nDone! Check the figures/ directory.")


if __name__ == '__main__':
    main()
