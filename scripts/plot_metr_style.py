#!/usr/bin/env python3
"""
METR-style time-horizon plot for robotic manipulation.

Mirrors the visual language of https://metr.org/time-horizons/:
  - log-y task duration vs. release date
  - every system as a point, colored by measured success rate
  - a single dotted exponential fit through the per-date frontier
    at the 70% reliability threshold, with a 95% bootstrap CI band

CI methodology: METR's three-level hierarchical bootstrap (task
families → tasks → runs, 10k samples; arxiv 2503.14499 §3.2) is
not portable here — our rows are already aggregated success rates
with no per-run data. We use the closest analog, which is METR's
"Bootstrap (models)" ablation: resample the frontier systems with
replacement, refit log(y) = a + b·t each draw, and take pointwise
2.5/97.5 percentiles of the resulting curves. This captures
system-selection uncertainty, not run-to-run variance.

Data lives in data/manipulation_horizons.csv. This is scaffolding —
the curve and band will move as that CSV evolves.
"""

import os
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'manipulation_horizons.csv')
FIGURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(FIGURES_DIR, exist_ok=True)

EPOCH = pd.Timestamp('2015-01-01')

# Y-axis tick marks reused across panels.
Y_TICKS = [1, 5, 10, 30, 60, 300, 600, 1800, 3600, 7200, 21600]
Y_LABELS = ['1s', '5s', '10s', '30s', '1min', '5min', '10min', '30min', '1hr', '2hr', '6hr']

# Systems to call out by name. Other points stay unlabeled to keep the plot legible.
LABELED_SYSTEMS = {
    'Levine et al. Grasping',
    'OpenAI Dactyl - Block',
    'RT-1',
    'RT-2',
    'Mobile ALOHA',
    'HIL-SERL',
    'π0 (laundry folding)',
    'π0.5 (bedroom cleanup)',
    'π0.6 (espresso)',
    'π0.6 (diverse laundry)',
    'Gemini Robotics - Lunch Box',
    'Figure 02 at BMW',
}


def load_data():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    df['days_since_epoch'] = (df['date'] - EPOCH).dt.days
    df['years_since_epoch'] = df['days_since_epoch'] / 365.25
    return df


def fit_exponential(dates, durations):
    """OLS in log-space: log(y) = a + b * t.

    Returns (intercept_a, slope_b_per_year, doubling_months).
    """
    t = np.array([(d - EPOCH).days / 365.25 for d in dates])
    log_y = np.log(durations)
    b, a = np.polyfit(t, log_y, 1)  # polyfit returns highest-order first
    doubling_months = 12 * np.log(2) / b if b > 0 else float('inf')
    return a, b, doubling_months


def bootstrap_ci(dates, durations, t_grid, n_boot=10000, ci=95, seed=7):
    """System-level bootstrap CI for the exponential fit.

    Resamples the input rows with replacement n_boot times, refits
    log(y) = a + b·t per draw, and returns:
      - lo, hi: pointwise percentile band on the fit curve (seconds)
      - doubling_lo, doubling_hi: percentile CI on doubling time (months)
    """
    rng = np.random.default_rng(seed)
    t = np.array([(d - EPOCH).days / 365.25 for d in dates])
    log_y = np.log(durations)
    n = len(t)
    if n < 3:
        return None, None, None, None

    preds = np.empty((n_boot, len(t_grid)))
    slopes = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        if len(np.unique(t[idx])) < 2:
            preds[i] = np.nan
            slopes[i] = np.nan
            continue
        b, a = np.polyfit(t[idx], log_y[idx], 1)
        preds[i] = np.exp(a + b * t_grid)
        slopes[i] = b

    alpha = (100 - ci) / 2
    lo = np.nanpercentile(preds, alpha, axis=0)
    hi = np.nanpercentile(preds, 100 - alpha, axis=0)

    # Doubling time CI: hi-slope draws give the *short* doubling time.
    valid = slopes[np.isfinite(slopes) & (slopes > 0)]
    doubling_months = 12 * np.log(2) / valid
    doubling_lo = np.percentile(doubling_months, alpha)
    doubling_hi = np.percentile(doubling_months, 100 - alpha)
    return lo, hi, doubling_lo, doubling_hi


def horizon_frontier(df, threshold):
    """Per-date running max of human_time_seconds for points >= threshold.

    Real-world only (sim-only systems are shown as faint points but don't
    define the horizon). One representative point per date — the longest
    task that cleared the threshold on that date.
    """
    real = df[(df['sim_or_real'] == 'real') & (df['success_rate'] >= threshold)].copy()
    real = real.sort_values('date')
    keep = []
    running_max = -1.0
    for _, row in real.iterrows():
        if row['human_time_seconds'] > running_max:
            running_max = row['human_time_seconds']
            keep.append(row)
    return pd.DataFrame(keep)


def plot_metr_style(df, save=True):
    fig, ax = plt.subplots(figsize=(13, 7.5))

    # --- background scatter, all points, colored by success rate ---
    cmap = plt.get_cmap('viridis')
    norm = Normalize(vmin=0, vmax=100)

    real = df[df['sim_or_real'] == 'real']
    sim = df[df['sim_or_real'] == 'sim']

    ax.scatter(real['date'], real['human_time_seconds'],
               c=real['success_rate'], cmap=cmap, norm=norm,
               s=70, alpha=0.85, edgecolors='white', linewidths=0.6,
               zorder=3, label='Real-world systems')

    if len(sim) > 0:
        ax.scatter(sim['date'], sim['human_time_seconds'],
                   c=sim['success_rate'], cmap=cmap, norm=norm,
                   s=55, alpha=0.4, marker='^',
                   edgecolors='white', linewidths=0.4,
                   zorder=2, label='Sim-only')

    # --- 70% horizon: single dotted exponential fit ---
    horizon_70 = horizon_frontier(df, threshold=70)

    # Time grid spanning the data plus a bit of room.
    t_min = (df['date'].min() - pd.Timedelta(days=120) - EPOCH).days / 365.25
    t_max = (df['date'].max() + pd.Timedelta(days=120) - EPOCH).days / 365.25
    t_grid = np.linspace(t_min, t_max, 200)
    grid_dates = [EPOCH + pd.Timedelta(days=365.25 * t) for t in t_grid]

    if len(horizon_70) >= 3:
        a, b, doubling_70 = fit_exponential(horizon_70['date'].tolist(),
                                            horizon_70['human_time_seconds'].values)
        fit_curve = np.exp(a + b * t_grid)

        lo, hi, dlo, dhi = bootstrap_ci(horizon_70['date'].tolist(),
                                        horizon_70['human_time_seconds'].values,
                                        t_grid)
        if lo is not None:
            ax.fill_between(grid_dates, lo, hi, color='#E91E63',
                            alpha=0.10, zorder=1, linewidth=0,
                            label='70% horizon — 95% CI (system bootstrap)')
            ci_str = f' [95% CI {dlo:.1f}–{dhi:.1f} mo]'
        else:
            ci_str = ''

        ax.plot(grid_dates, fit_curve, color='#E91E63', linewidth=2.0,
                linestyle=':', alpha=0.9, zorder=4,
                label=f'70% horizon fit — doubles every {doubling_70:.1f} mo{ci_str}')

    # --- annotations for a curated subset ---
    for _, row in df.iterrows():
        if row['system_name'] in LABELED_SYSTEMS:
            ax.annotate(row['system_name'],
                        (row['date'], row['human_time_seconds']),
                        textcoords='offset points', xytext=(7, 7),
                        fontsize=7.5, color='#333',
                        arrowprops=dict(arrowstyle='-', color='#bbb', lw=0.5))

    # --- axes ---
    ax.set_yscale('log')
    ax.set_yticks(Y_TICKS)
    ax.set_yticklabels(Y_LABELS)
    ax.set_ylim(1, 30000)

    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_xlim(datetime(2015, 6, 1), datetime(2026, 6, 1))

    ax.grid(True, which='major', alpha=0.3, linestyle='--')
    ax.grid(True, which='minor', axis='y', alpha=0.1, linestyle=':')

    ax.set_xlabel('Release date')
    ax.set_ylabel('Human-equivalent task duration (log scale)')
    ax.set_title('Robotic manipulation time horizon\n'
                 'Task length a robot completes at ≥70% success rate',
                 fontsize=13)

    # --- colorbar for success rate ---
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, pad=0.01, fraction=0.035)
    cbar.set_label('Success rate (%)')

    ax.legend(loc='upper left', fontsize=8.5, framealpha=0.92)

    plt.tight_layout()
    if save:
        out_png = os.path.join(FIGURES_DIR, 'metr_style_horizon.png')
        out_svg = os.path.join(FIGURES_DIR, 'metr_style_horizon.svg')
        fig.savefig(out_png, dpi=200, bbox_inches='tight')
        fig.savefig(out_svg, bbox_inches='tight')
        print(f'Saved {out_png}')
    return fig, ax


def main():
    df = load_data()
    print(f'Loaded {len(df)} rows; {df["date"].min().date()} → {df["date"].max().date()}')
    plot_metr_style(df)


if __name__ == '__main__':
    main()
