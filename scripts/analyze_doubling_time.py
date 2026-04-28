#!/usr/bin/env python3
"""
Analyze the doubling time of the frontier task horizon.
Fits log(duration) ~ date (exponential growth model) and reports R², doubling time.
Compares: full frontier vs ≥80% success vs without Dactyl Rubik's Cube.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'manipulation_horizons.csv')


def load_data():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    # days since epoch for regression
    df['days'] = (df['date'] - pd.Timestamp('2016-01-01')).dt.days
    return df


def compute_frontier(df, success_threshold=50):
    filtered = df[df['success_rate'] >= success_threshold].copy()
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


def main():
    df = load_data()

    print("=" * 60)
    print("FRONTIER DOUBLING TIME ANALYSIS")
    print("Fitting: log(task_duration) ~ date (exponential growth model)")
    print("=" * 60)

    # 1. Standard frontier: ≥50% success
    f50 = compute_frontier(df, success_threshold=50)
    fit_exponential(f50, "All frontier points (≥50% success)")

    # 2. High-reliability frontier: ≥80% success
    f80 = compute_frontier(df, success_threshold=80)
    fit_exponential(f80, "High-reliability frontier (≥80% success)")

    # 3. ≥50% but without Dactyl Rubik's Cube
    df_no_dactyl = df[df['system_name'] != "OpenAI Dactyl - Rubik's Cube"].copy()
    f_no_dactyl = compute_frontier(df_no_dactyl, success_threshold=50)
    fit_exponential(f_no_dactyl, "≥50% success, Dactyl Rubik's Cube removed")

    # 4. ≥80% without Dactyl (it's 60% so already excluded, just confirm)
    print("\n\nNote: Dactyl Rubik's Cube has 60% success, so it is already")
    print("excluded from the ≥80% scenario above.")


if __name__ == '__main__':
    main()
