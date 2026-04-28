#!/usr/bin/env python3
"""Basic distribution plots for the manipulation_horizons dataset."""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

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

CAT_COLORS = {'tabletop': '#2196F3', 'mobile_manipulation': '#FF9800'}
CAT_LABELS = {'tabletop': 'Tabletop', 'mobile_manipulation': 'Mobile'}

DURATION_TICKS = [4, 10, 30, 60, 300, 600, 1800, 3600, 7200]
DURATION_LABELS = ['4s', '10s', '30s', '1m', '5m', '10m', '30m', '1h', '2h']


def load():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    return df


def _save(fig, name):
    path = os.path.join(FIGURES_DIR, name)
    fig.savefig(path, dpi=160, bbox_inches='tight')
    print(f"  saved {path}")


# ── 1. Success rate histogram ─────────────────────────────────────────────────
def plot_success_rate_hist(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    bins = np.arange(0, 105, 10)
    for cat, color in CAT_COLORS.items():
        sub = df[df['category'] == cat]['success_rate']
        ax.hist(sub, bins=bins, color=color, alpha=0.65, label=CAT_LABELS[cat], edgecolor='white')
    ax.axvline(50, color='#E91E63', linestyle='--', linewidth=1.5, label='50% threshold')
    ax.set_xlabel('Success Rate (%)')
    ax.set_ylabel('Number of Systems')
    ax.set_title('Distribution of Success Rates')
    ax.legend()
    plt.tight_layout()
    _save(fig, 'dist_success_rate.png')
    plt.close(fig)


# ── 2. Task duration histogram (log scale) ────────────────────────────────────
def plot_duration_hist(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    log_bins = np.logspace(np.log10(3), np.log10(8000), 20)
    for cat, color in CAT_COLORS.items():
        sub = df[df['category'] == cat]['human_time_seconds']
        ax.hist(sub, bins=log_bins, color=color, alpha=0.65, label=CAT_LABELS[cat], edgecolor='white')
    ax.set_xscale('log')
    ax.set_xticks(DURATION_TICKS)
    ax.set_xticklabels(DURATION_LABELS)
    ax.set_xlabel('Human-Equivalent Task Duration')
    ax.set_ylabel('Number of Systems')
    ax.set_title('Distribution of Task Durations (log scale)')
    ax.legend()
    plt.tight_layout()
    _save(fig, 'dist_duration.png')
    plt.close(fig)


# ── 3. Success rate vs duration scatter ───────────────────────────────────────
def plot_success_vs_duration(df):
    fig, ax = plt.subplots(figsize=(9, 6))
    for cat, color in CAT_COLORS.items():
        sub = df[df['category'] == cat]
        ax.scatter(sub['human_time_seconds'], sub['success_rate'],
                   c=color, alpha=0.7, s=70, edgecolors='white',
                   linewidth=0.5, label=CAT_LABELS[cat])
    ax.axhline(50, color='#E91E63', linestyle='--', linewidth=1.2, label='50% threshold')
    ax.set_xscale('log')
    ax.set_xticks(DURATION_TICKS)
    ax.set_xticklabels(DURATION_LABELS)
    ax.set_ylim(-5, 105)
    ax.set_xlabel('Human-Equivalent Task Duration')
    ax.set_ylabel('Success Rate (%)')
    ax.set_title('Success Rate vs. Task Duration')
    ax.legend()
    plt.tight_layout()
    _save(fig, 'dist_success_vs_duration.png')
    plt.close(fig)


# ── 4. Breakdown bar charts (category / sim-real / quality / frontier) ─────────
def plot_breakdowns(df):
    fig, axes = plt.subplots(1, 4, figsize=(15, 5))

    def bar(ax, counts, colors, title, rotation=0):
        bars = ax.bar(range(len(counts)), counts.values,
                      color=colors, edgecolor='white', linewidth=0.8)
        ax.set_xticks(range(len(counts)))
        ax.set_xticklabels(counts.index, rotation=rotation, ha='right' if rotation else 'center')
        ax.set_ylabel('Count')
        ax.set_title(title)
        for b in bars:
            h = b.get_height()
            ax.text(b.get_x() + b.get_width() / 2, h + 0.2, str(int(h)),
                    ha='center', va='bottom', fontsize=9)
        ax.set_ylim(0, counts.max() * 1.25)
        ax.grid(axis='x', alpha=0)

    # Category
    cat_counts = df['category'].map(CAT_LABELS).value_counts()
    bar(axes[0], cat_counts, ['#2196F3', '#FF9800'], 'By Category')

    # Sim vs Real
    sim_counts = df['sim_or_real'].value_counts()
    bar(axes[1], sim_counts, ['#4CAF50', '#9C27B0'], 'Sim vs Real')

    # Data quality
    qual_counts = df['data_quality'].value_counts()
    bar(axes[2], qual_counts, ['#E91E63', '#FF9800', '#607D8B'],
        'Data Quality', rotation=15)

    # Frontier flag
    front_counts = df['is_frontier'].map({True: 'Frontier', False: 'Non-frontier'}).value_counts()
    bar(axes[3], front_counts, ['#E91E63', '#BDBDBD'], 'Frontier Systems')

    fig.suptitle('Dataset Composition', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    _save(fig, 'dist_breakdowns.png')
    plt.close(fig)


# ── 5. Papers per year ────────────────────────────────────────────────────────
def plot_papers_per_year(df):
    fig, ax = plt.subplots(figsize=(9, 5))
    year_counts = df.groupby(['year', 'category']).size().unstack(fill_value=0)
    years = year_counts.index.astype(str)
    x = np.arange(len(years))
    width = 0.4
    for i, (cat, color) in enumerate(CAT_COLORS.items()):
        col = year_counts.get(cat, pd.Series(0, index=year_counts.index))
        ax.bar(x + (i - 0.5) * width, col, width, color=color,
               alpha=0.8, label=CAT_LABELS[cat], edgecolor='white')
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=45, ha='right')
    ax.set_ylabel('Number of Systems')
    ax.set_title('Systems Published per Year')
    ax.legend()
    plt.tight_layout()
    _save(fig, 'dist_papers_per_year.png')
    plt.close(fig)


# ── 6. Number of subtasks histogram ───────────────────────────────────────────
def plot_subtasks(df):
    fig, ax = plt.subplots(figsize=(7, 5))
    max_sub = int(df['num_subtasks'].max())
    bins = np.arange(0.5, max_sub + 1.5, 1)
    for cat, color in CAT_COLORS.items():
        sub = df[df['category'] == cat]['num_subtasks']
        ax.hist(sub, bins=bins, color=color, alpha=0.65, label=CAT_LABELS[cat], edgecolor='white')
    ax.set_xlabel('Number of Subtasks')
    ax.set_ylabel('Number of Systems')
    ax.set_title('Distribution of Subtask Count')
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.legend()
    plt.tight_layout()
    _save(fig, 'dist_subtasks.png')
    plt.close(fig)


# ── 7. Success rate by sim vs real (box plot) ─────────────────────────────────
def plot_success_by_sim_real(df):
    fig, ax = plt.subplots(figsize=(7, 5))
    groups = [df[df['sim_or_real'] == g]['success_rate'].dropna()
              for g in ['sim', 'real']]
    bp = ax.boxplot(groups, patch_artist=True, widths=0.4,
                    medianprops=dict(color='white', linewidth=2))
    colors = ['#4CAF50', '#9C27B0']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_xticklabels(['Simulation', 'Real World'])
    ax.set_ylabel('Success Rate (%)')
    ax.set_title('Success Rate: Sim vs Real World')
    plt.tight_layout()
    _save(fig, 'dist_success_sim_vs_real.png')
    plt.close(fig)


def main():
    print("Loading data...")
    df = load()
    # Drop the teleoperation row (explicitly not autonomous)
    df = df[df['success_rate'] > 0].copy()
    print(f"  {len(df)} systems after dropping zero-success rows")

    print("Generating distribution plots...")
    plot_success_rate_hist(df)
    plot_duration_hist(df)
    plot_success_vs_duration(df)
    plot_breakdowns(df)
    plot_papers_per_year(df)
    plot_subtasks(df)
    plot_success_by_sim_real(df)
    print("Done.")


if __name__ == '__main__':
    main()
