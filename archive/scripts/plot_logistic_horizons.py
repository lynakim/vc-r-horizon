#!/usr/bin/env python3
"""
METR-style per-paper logistic fit, as a test alongside the existing plot.

For papers with multi-task evaluations (data/per_task_evaluations.csv) we
fit a logistic of success on log(human_time):

    P(success | t) = sigmoid(alpha + beta * log(t))

and read off the time-horizon at a chosen reliability threshold p*:

    horizon(p*) = exp((logit(p*) - alpha) / beta)

A within-paper bootstrap over tasks gives a 95% CI on each horizon.

Two new test plots are written to figures/, NOTHING is overwritten:
  - figures/logistic_horizon_test.png
        side-by-side: original CSV points (left), logistic-replaced (right)
  - figures/logistic_per_paper_curves.png
        each paper's logistic fit overlaid on its task points

Rubric scoring is treated as continuous: we use the rubric mean as a
fractional success rate and weight by num_trials in the binomial likelihood.
This is the same approximation METR uses for "continuous scoring" in their
Appendix H. Rubric vs binary rows are flagged in the data file.
"""

import os
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from scipy.optimize import minimize

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
FIGURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'figures')
MAIN_CSV = os.path.join(DATA_DIR, 'manipulation_horizons.csv')
PER_TASK_CSV = os.path.join(DATA_DIR, 'per_task_evaluations.csv')

# Threshold for the time horizon. 70% to match the previous plot.
THRESHOLD = 0.70

EPOCH = pd.Timestamp('2015-01-01')

Y_TICKS = [1, 5, 10, 30, 60, 300, 600, 1800, 3600, 7200, 21600]
Y_LABELS = ['1s', '5s', '10s', '30s', '1min', '5min', '10min', '30min', '1hr', '2hr', '6hr']


# --------- data loading ---------

def load_main():
    df = pd.read_csv(MAIN_CSV)
    df['date'] = pd.to_datetime(df['date'])
    return df


def load_per_task():
    df = pd.read_csv(PER_TASK_CSV)
    df['paper_date'] = pd.to_datetime(df['paper_date'])
    df['rate'] = df['success_rate'] / 100.0
    return df


# --------- logistic fit ---------

def logit(p, eps=1e-6):
    p = np.clip(p, eps, 1 - eps)
    return np.log(p / (1 - p))


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def fit_logistic(times, rates, ns):
    """Maximum-likelihood fit of P = sigmoid(alpha + beta * log(t)).

    Treats each row as `n` Bernoulli trials with empirical rate `rate`,
    so the log-likelihood is sum_i n_i [r_i log p_i + (1 - r_i) log(1 - p_i)].
    Rubric rates use the same form (continuous scoring).

    Returns (alpha, beta) or (None, None) if the fit is degenerate.
    """
    log_t = np.log(times)
    rates = np.clip(rates, 1e-6, 1 - 1e-6)
    ns = np.asarray(ns, dtype=float)

    def neg_log_lik(params):
        a, b = params
        z = a + b * log_t
        log_p = -np.logaddexp(0, -z)        # log sigmoid(z)
        log_1mp = -np.logaddexp(0, z)       # log (1 - sigmoid(z))
        ll = np.sum(ns * (rates * log_p + (1 - rates) * log_1mp))
        return -ll

    # Sensible initial guess: pivot near median t, slope mildly negative.
    a0 = 0.0
    b0 = -0.5
    res = minimize(neg_log_lik, x0=[a0, b0], method='Nelder-Mead',
                   options={'xatol': 1e-6, 'fatol': 1e-6, 'maxiter': 5000})
    if not res.success:
        return None, None
    a, b = res.x
    if not np.isfinite(a) or not np.isfinite(b):
        return None, None
    return a, b


def horizon_from_fit(alpha, beta, threshold=THRESHOLD):
    """Time at which the logistic crosses `threshold`.

    Returns None if beta is non-negative (rate doesn't fall with duration —
    horizon is unbounded / extrapolation is meaningless).
    """
    if beta is None or beta >= -1e-3:
        return None
    return float(np.exp((logit(threshold) - alpha) / beta))


def bootstrap_horizon(times, rates, ns, n_boot=2000, seed=0,
                      threshold=THRESHOLD):
    """Within-paper task-level bootstrap CI on the horizon."""
    rng = np.random.default_rng(seed)
    horizons = []
    n = len(times)
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        if len(np.unique(times[idx])) < 2:
            continue
        a, b = fit_logistic(times[idx], rates[idx], ns[idx])
        h = horizon_from_fit(a, b, threshold)
        if h is not None and 1e-2 < h < 1e6:
            horizons.append(h)
    if len(horizons) < 50:
        return None, None, None
    horizons = np.array(horizons)
    return (np.median(horizons),
            np.percentile(horizons, 2.5),
            np.percentile(horizons, 97.5))


# --------- per-paper summary ---------

def per_paper_horizons(per_task, threshold=THRESHOLD):
    """For each paper, fit logistic, compute horizon + bootstrap CI."""
    rows = []
    for pid, grp in per_task.groupby('paper_id'):
        t = grp['human_time_seconds'].values.astype(float)
        r = grp['rate'].values.astype(float)
        n = grp['num_trials'].values.astype(float)
        a, b = fit_logistic(t, r, n)
        h = horizon_from_fit(a, b, threshold)
        h_med, h_lo, h_hi = bootstrap_horizon(t, r, n, threshold=threshold,
                                              seed=hash(pid) & 0xffff)
        rows.append({
            'paper_id': pid,
            'date': grp['paper_date'].iloc[0],
            'paper_url': grp['paper_url'].iloc[0],
            'n_tasks': len(grp),
            'alpha': a,
            'beta': b,
            'horizon_pt': h,
            'horizon_med': h_med,
            'horizon_lo': h_lo,
            'horizon_hi': h_hi,
        })
    return pd.DataFrame(rows)


# --------- plotting ---------

def base_axes(ax):
    ax.set_yscale('log')
    ax.set_yticks(Y_TICKS)
    ax.set_yticklabels(Y_LABELS)
    ax.set_ylim(1, 30000)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_xlim(datetime(2015, 6, 1), datetime(2026, 6, 1))
    ax.grid(True, which='major', alpha=0.3, linestyle='--')
    ax.grid(True, which='minor', axis='y', alpha=0.1, linestyle=':')


def plot_comparison(main_df, fit_df, threshold=THRESHOLD, save=True):
    """Side-by-side: original CSV points (left) vs. logistic-replaced (right).

    For papers with a per-paper logistic fit, swap that paper's row(s) in the
    main scatter for a single point at (paper_date, fitted_horizon) with a
    vertical CI bar.
    """
    cmap = plt.get_cmap('viridis')
    norm = Normalize(vmin=0, vmax=100)

    fig, axes = plt.subplots(1, 2, figsize=(18, 7.5), sharey=True)

    # --- panel 1: original ---
    real = main_df[main_df['sim_or_real'] == 'real']
    sim = main_df[main_df['sim_or_real'] == 'sim']
    axes[0].scatter(real['date'], real['human_time_seconds'],
                    c=real['success_rate'], cmap=cmap, norm=norm,
                    s=70, alpha=0.85, edgecolors='white', linewidths=0.6,
                    label='Real-world')
    axes[0].scatter(sim['date'], sim['human_time_seconds'],
                    c=sim['success_rate'], cmap=cmap, norm=norm,
                    s=55, alpha=0.4, marker='^',
                    edgecolors='white', linewidths=0.4, label='Sim-only')
    axes[0].set_title('Original: one row per (system, task)', fontsize=12)
    base_axes(axes[0])
    axes[0].set_ylabel('Human-equivalent task duration (log scale)')
    axes[0].set_xlabel('Release date')

    # --- panel 2: logistic-swapped ---
    # Drop the rows for papers we have logistic fits for.
    swap_urls = set(fit_df['paper_url'].dropna()) if 'paper_url' in fit_df else set()
    kept = main_df[~main_df['paper_url'].isin(swap_urls)]
    kept_real = kept[kept['sim_or_real'] == 'real']
    kept_sim = kept[kept['sim_or_real'] == 'sim']
    axes[1].scatter(kept_real['date'], kept_real['human_time_seconds'],
                    c=kept_real['success_rate'], cmap=cmap, norm=norm,
                    s=70, alpha=0.6, edgecolors='white', linewidths=0.5,
                    label='Real-world (CSV)')
    axes[1].scatter(kept_sim['date'], kept_sim['human_time_seconds'],
                    c=kept_sim['success_rate'], cmap=cmap, norm=norm,
                    s=55, alpha=0.3, marker='^',
                    edgecolors='white', linewidths=0.4)

    # Logistic-replaced points + CI bars + paper label.
    valid = fit_df[fit_df['horizon_med'].notna()]
    for _, row in valid.iterrows():
        d = row['date']
        med, lo, hi = row['horizon_med'], row['horizon_lo'], row['horizon_hi']
        axes[1].errorbar([d], [med], yerr=[[med - lo], [hi - med]],
                         fmt='D', color='#E91E63', markersize=9,
                         elinewidth=1.5, capsize=4, zorder=5,
                         markeredgecolor='white', markeredgewidth=0.8)
        axes[1].annotate(row['paper_id'], (d, med),
                         textcoords='offset points', xytext=(8, 8),
                         fontsize=8.5, color='#333', fontweight='bold')

    # Papers where the fit didn't converge (e.g. all rates above threshold)
    flat = fit_df[fit_df['horizon_med'].isna()]
    for _, row in flat.iterrows():
        axes[1].annotate(f"{row['paper_id']} (no horizon — saturated)",
                         (row['date'], 1.5),
                         textcoords='offset points', xytext=(0, 0),
                         fontsize=8, color='#999')

    axes[1].set_title(
        f'Logistic-replaced: per-paper {int(THRESHOLD * 100)}% horizon '
        f'with within-paper bootstrap CI', fontsize=12)
    base_axes(axes[1])
    axes[1].set_xlabel('Release date')

    # Shared colorbar
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=axes, pad=0.01, fraction=0.025)
    cbar.set_label('Success rate (%)')

    fig.suptitle(
        'Robotic manipulation horizon — per-paper logistic-fit test',
        fontsize=14, y=0.995)

    if save:
        out = os.path.join(FIGURES_DIR, 'logistic_horizon_test.png')
        fig.savefig(out, dpi=200, bbox_inches='tight')
        print(f'Saved {out}')
    return fig


def plot_per_paper_curves(per_task, fit_df, threshold=THRESHOLD, save=True):
    """One small panel per paper: tasks + fitted logistic + horizon line."""
    papers = list(per_task['paper_id'].unique())
    n = len(papers)
    cols = 2
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(11, 3.2 * rows))
    axes = np.array(axes).reshape(-1)

    for ax, pid in zip(axes, papers):
        grp = per_task[per_task['paper_id'] == pid]
        fit_row = fit_df[fit_df['paper_id'] == pid].iloc[0]
        a, b = fit_row['alpha'], fit_row['beta']

        ax.scatter(grp['human_time_seconds'], grp['rate'] * 100,
                   s=np.sqrt(grp['num_trials']) * 8, alpha=0.7,
                   color='#1976D2', edgecolors='white', linewidths=0.5)
        for _, r in grp.iterrows():
            ax.annotate(r['task_name'],
                        (r['human_time_seconds'], r['rate'] * 100),
                        textcoords='offset points', xytext=(5, 4),
                        fontsize=6.5, color='#444')

        if a is not None and b is not None:
            t_grid = np.logspace(
                np.log10(grp['human_time_seconds'].min() * 0.5),
                np.log10(grp['human_time_seconds'].max() * 2),
                200)
            ax.plot(t_grid, sigmoid(a + b * np.log(t_grid)) * 100,
                    color='#E91E63', linewidth=2)
            h = fit_row['horizon_pt']
            if h is not None and np.isfinite(h):
                ax.axvline(h, color='#E91E63', linestyle=':', alpha=0.6)
                ax.axhline(threshold * 100, color='#999',
                           linestyle=':', alpha=0.6)
                ax.text(h, 5, f'  {h:.0f}s', color='#E91E63',
                        fontsize=8, fontweight='bold')

        ax.set_xscale('log')
        ax.set_xlabel('Task human time (s, log)')
        ax.set_ylabel('Success rate (%)')
        ax.set_ylim(-5, 105)
        ax.set_title(f'{pid} — N tasks={len(grp)}', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')

    for ax in axes[len(papers):]:
        ax.set_visible(False)

    fig.suptitle(
        f'Per-paper logistic fits at {int(threshold * 100)}% threshold',
        fontsize=13, y=1.0)
    fig.tight_layout()

    if save:
        out = os.path.join(FIGURES_DIR, 'logistic_per_paper_curves.png')
        fig.savefig(out, dpi=200, bbox_inches='tight')
        print(f'Saved {out}')
    return fig


def main():
    main_df = load_main()
    per_task = load_per_task()
    print(f'Main CSV: {len(main_df)} rows')
    print(f'Per-task CSV: {len(per_task)} rows across '
          f'{per_task["paper_id"].nunique()} papers')

    fit_df = per_paper_horizons(per_task)
    print('\nPer-paper fits:')
    for _, r in fit_df.iterrows():
        if r['horizon_med'] is not None:
            print(f'  {r["paper_id"]:18s}  n={r["n_tasks"]:2d}  '
                  f'beta={r["beta"]:+.2f}  '
                  f'horizon={r["horizon_pt"]:7.1f}s  '
                  f'CI=[{r["horizon_lo"]:.1f}, {r["horizon_hi"]:.1f}]s')
        else:
            print(f'  {r["paper_id"]:18s}  n={r["n_tasks"]:2d}  '
                  f'beta={r["beta"]}  '
                  f'(fit non-decreasing or bootstrap unstable)')

    plot_comparison(main_df, fit_df)
    plot_per_paper_curves(per_task, fit_df)


if __name__ == '__main__':
    main()
