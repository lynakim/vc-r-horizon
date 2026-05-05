#!/usr/bin/env python3
"""
Analyze the doubling time of the frontier task horizon.
Fits log(duration) ~ date (exponential growth model) and reports R², doubling time.
Compares: ≥50% (canonical) vs ≥80% high-reliability vs sim-included sensitivity.

Also fits non-exponential alternatives (linear, logarithmic, power, quadratic)
and reports R² + AIC for each, on both raw-y and log-y residual scales.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'manipulation_horizons.csv')

# All time variables are years measured from this anchor. Chosen earlier than
# the first frontier point so t > 0 everywhere — required for log(t) and t^b
# to be defined.
T_ANCHOR = pd.Timestamp('2015-06-01')


def load_data():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    df['days'] = (df['date'] - pd.Timestamp('2016-01-01')).dt.days
    df['t_years'] = (df['date'] - T_ANCHOR).dt.days / 365.25
    return df


def compute_frontier(df, success_threshold=50, real_only=True):
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


def fit_exponential(frontier_df, label):
    """Fit log(duration) ~ date and compute R², doubling time."""
    x = frontier_df['days'].values.astype(float)
    y = np.log(frontier_df['human_time_seconds'].values.astype(float))

    n = len(x)
    if n < 3:
        print(f"\n{label}: only {n} points — can't fit meaningfully")
        return

    # OLS: y = a + b*x
    x_mean = x.mean()
    y_mean = y.mean()
    b = np.dot(x - x_mean, y - y_mean) / np.dot(x - x_mean, x - x_mean)
    a = y_mean - b * x_mean

    y_pred = a + b * x
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y_mean) ** 2)
    r2 = 1 - ss_res / ss_tot

    # Doubling time: log(2) / b (in days), convert to years
    doubling_days = np.log(2) / b
    doubling_years = doubling_days / 365.25

    print(f"\n{'─'*60}")
    print(f"Scenario: {label}")
    print(f"  N frontier points : {n}")
    print(f"  Points used:")
    for _, row in frontier_df.iterrows():
        print(f"    {row['date'].strftime('%Y-%m')}  {row['system_name']:<35s}  "
              f"{row['human_time_seconds']:>6.0f}s  {row['success_rate']:.0f}%")
    print(f"  R²                : {r2:.4f}")
    print(f"  Doubling time     : {doubling_years:.2f} years  ({doubling_days:.0f} days)")
    print(f"  Slope (log-scale) : {b*365.25:.4f} log-seconds/year")

    return {'label': label, 'n': n, 'r2': r2, 'doubling_years': doubling_years}


def _score(y, log_y, y_pred, k):
    """Compute R² and Gaussian-likelihood AIC on both raw-y and log-y scales.

    Comparing AIC across linear-y vs log-y fits is meaningful only when both
    are evaluated against the same response, so every model gets scored on
    *both* — the user picks which residual scale they care about.
    """
    n = len(y)
    y_pred_clip = np.maximum(y_pred, 1e-9)  # for log of any negative predictions
    log_y_pred = np.log(y_pred_clip)

    sse_y = np.sum((y - y_pred) ** 2)
    sse_logy = np.sum((log_y - log_y_pred) ** 2)
    sst_y = np.sum((y - y.mean()) ** 2)
    sst_logy = np.sum((log_y - log_y.mean()) ** 2)

    r2_y = 1 - sse_y / sst_y if sst_y > 0 else float('nan')
    r2_logy = 1 - sse_logy / sst_logy if sst_logy > 0 else float('nan')

    # AIC up to additive constant: n*ln(SSE/n) + 2k
    aic_y = n * np.log(sse_y / n) + 2 * k
    aic_logy = n * np.log(sse_logy / n) + 2 * k

    return r2_y, r2_logy, aic_y, aic_logy


def fit_alternative_shapes(frontier_df, label):
    """Fit several functional forms to the frontier and tabulate R²/AIC.

    Models (k = free params):
      1. Exponential   log(y) = a + b·t            (k=2)  ← current default
      2. Linear        y     = a + b·t             (k=2)
      3. Logarithmic   y     = a + b·log(t)        (k=2)
      4. Power         log(y) = a + b·log(t)       (k=2)  → y = α·t^b
      5. Quadratic-log log(y) = a + b·t + c·t²     (k=3)
      6. Quadratic-raw y     = a + b·t + c·t²      (k=3)
    """
    if len(frontier_df) < 4:
        print(f"\n[{label}] only {len(frontier_df)} points — skipping shape comparison")
        return

    t = frontier_df['t_years'].values.astype(float)
    y = frontier_df['human_time_seconds'].values.astype(float)
    log_y = np.log(y)
    log_t = np.log(t)
    n = len(t)

    fits = []

    # 1. Exponential — fit in log space
    b, a = np.polyfit(t, log_y, 1)
    yhat = np.exp(a + b * t)
    doubling_yr = np.log(2) / b if b > 0 else float('inf')
    fits.append(('Exponential   log y ~ t',        2, yhat, f'doubling = {doubling_yr*12:.1f} mo'))

    # 2. Linear — fit in raw space
    b, a = np.polyfit(t, y, 1)
    yhat = a + b * t
    fits.append(('Linear        y ~ t',            2, yhat, f'slope = {b:.0f} s/yr'))

    # 3. Logarithmic — fit in raw space
    b, a = np.polyfit(log_t, y, 1)
    yhat = a + b * log_t
    fits.append(('Logarithmic   y ~ log t',        2, yhat, f'slope = {b:.0f} s per log-yr'))

    # 4. Power — fit in log space
    b, a = np.polyfit(log_t, log_y, 1)
    yhat = np.exp(a + b * log_t)
    fits.append(('Power         log y ~ log t',    2, yhat, f'exponent = {b:.2f}'))

    # 5. Quadratic on log
    c, b, a = np.polyfit(t, log_y, 2)
    yhat = np.exp(a + b * t + c * t * t)
    fits.append(('Quadratic-log log y ~ t + t²',   3, yhat, f't² coef = {c:+.4f}'))

    # 6. Quadratic on raw
    c, b, a = np.polyfit(t, y, 2)
    yhat = a + b * t + c * t * t
    fits.append(('Quadratic-raw y ~ t + t²',       3, yhat, f't² coef = {c:+.1f}'))

    rows = []
    for name, k, yhat, extra in fits:
        r2_y, r2_logy, aic_y, aic_logy = _score(y, log_y, yhat, k)
        rows.append((name, k, r2_y, r2_logy, aic_y, aic_logy, extra))

    aic_y_min = min(r[4] for r in rows)
    aic_logy_min = min(r[5] for r in rows)

    print(f"\n{'='*102}")
    print(f"Shape comparison — {label}   (n = {n})")
    print(f"{'='*102}")
    print(f"{'Model':<32} {'k':>2}  {'R²(y)':>7} {'R²(log y)':>10}  "
          f"{'ΔAIC(y)':>9} {'ΔAIC(log y)':>12}   notes")
    print('-' * 102)
    for name, k, r2_y, r2_logy, aic_y, aic_logy, extra in rows:
        d_y = aic_y - aic_y_min
        d_logy = aic_logy - aic_logy_min
        print(f"{name:<32} {k:>2}  {r2_y:>7.3f} {r2_logy:>10.3f}  "
              f"{d_y:>9.2f} {d_logy:>12.2f}   {extra}")

    best_y = min(rows, key=lambda r: r[4])[0].strip()
    best_logy = min(rows, key=lambda r: r[5])[0].strip()
    print(f"\n  Best by AIC on raw seconds : {best_y}")
    print(f"  Best by AIC on log seconds : {best_logy}")
    print(f"  (ΔAIC < 2 ≈ indistinguishable; 2–7 weak preference; >10 strong)")


def main():
    df = load_data()

    print("=" * 60)
    print("FRONTIER DOUBLING TIME ANALYSIS")
    print("Fitting: log(task_duration) ~ date (exponential growth model)")
    print("Canonical frontier = real-world systems only.")
    print("=" * 60)

    # 1. Canonical frontier: real-world, ≥50% success
    f50 = compute_frontier(df, success_threshold=50, real_only=True)
    fit_exponential(f50, "Real-world frontier (≥50% success)")

    # 2. High-reliability frontier: real-world, ≥80% success
    f80 = compute_frontier(df, success_threshold=80, real_only=True)
    fit_exponential(f80, "Real-world high-reliability frontier (≥80% success)")

    # 3. Sensitivity: include sim systems at ≥50%
    f_sim = compute_frontier(df, success_threshold=50, real_only=False)
    fit_exponential(f_sim, "Sensitivity: ≥50% incl. sim systems")

    # 4. Binary-only frontier (mixed binary+rubric is the canonical;
    #    binary-only matters because Entry 9 of research_log.md notes the
    #    two diverge at the post-2024 tail)
    f_binary = compute_frontier(
        df[df['success_type'] == 'binary'], success_threshold=50, real_only=True
    )

    # Shape comparisons — does exponential actually beat the alternatives?
    print("\n\n" + "#" * 102)
    print("# Non-exponential shape comparisons")
    print("#" * 102)
    fit_alternative_shapes(f50, "Real-world ≥50% (canonical, binary + rubric)")
    fit_alternative_shapes(f_binary, "Real-world ≥50%, binary-only")
    fit_alternative_shapes(f80, "Real-world ≥80% high-reliability")


if __name__ == '__main__':
    main()
