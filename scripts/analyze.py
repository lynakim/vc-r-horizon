#!/usr/bin/env python3
"""
Statistical analysis of robotic manipulation task horizons.
Fits exponential growth models and estimates doubling times.
"""

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import pearsonr
from datetime import datetime
import os
import json

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'manipulation_horizons.csv')
FIGURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(FIGURES_DIR, exist_ok=True)


def load_data():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    df['days_since_2015'] = (df['date'] - pd.Timestamp('2015-01-01')).dt.days
    df['years_since_2015'] = df['days_since_2015'] / 365.25
    return df


def compute_frontier(df, success_threshold=50):
    """Compute frontier envelope at given success threshold."""
    filtered = df[df['success_rate'] >= success_threshold].copy()
    filtered = filtered.sort_values('date')
    frontier_points = []
    max_time = 0
    for _, row in filtered.iterrows():
        if row['human_time_seconds'] >= max_time:
            max_time = row['human_time_seconds']
            frontier_points.append(row)
    return pd.DataFrame(frontier_points)


def exponential_model(x, a, b):
    """Exponential: y = a * exp(b * x)"""
    return a * np.exp(b * x)


def fit_exponential(frontier_df):
    """Fit exponential to frontier data and compute doubling time."""
    if len(frontier_df) < 3:
        print("Not enough frontier points for exponential fit (need ≥3)")
        return None

    x = frontier_df['years_since_2015'].values
    y = frontier_df['human_time_seconds'].values

    # Fit in log space for stability
    log_y = np.log(y)
    coeffs = np.polyfit(x, log_y, 1)
    growth_rate = coeffs[0]  # per year
    intercept = np.exp(coeffs[1])

    # Doubling time
    doubling_time_years = np.log(2) / growth_rate if growth_rate > 0 else float('inf')
    doubling_time_months = doubling_time_years * 12

    # R-squared
    y_pred = intercept * np.exp(growth_rate * x)
    log_y_pred = np.log(y_pred)
    ss_res = np.sum((log_y - log_y_pred) ** 2)
    ss_tot = np.sum((log_y - np.mean(log_y)) ** 2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    # Confidence interval on growth rate via bootstrap
    n_bootstrap = 1000
    growth_rates_boot = []
    rng = np.random.RandomState(42)
    for _ in range(n_bootstrap):
        idx = rng.choice(len(x), size=len(x), replace=True)
        x_boot = x[idx]
        log_y_boot = log_y[idx]
        try:
            c = np.polyfit(x_boot, log_y_boot, 1)
            growth_rates_boot.append(c[0])
        except:
            pass

    growth_rate_ci = (np.percentile(growth_rates_boot, 2.5),
                      np.percentile(growth_rates_boot, 97.5)) if growth_rates_boot else (None, None)

    doubling_ci = None
    if growth_rate_ci[0] and growth_rate_ci[1]:
        dt_high = np.log(2) / growth_rate_ci[0] * 12 if growth_rate_ci[0] > 0 else float('inf')
        dt_low = np.log(2) / growth_rate_ci[1] * 12 if growth_rate_ci[1] > 0 else float('inf')
        doubling_ci = (min(dt_low, dt_high), max(dt_low, dt_high))

    results = {
        'growth_rate_per_year': growth_rate,
        'intercept': intercept,
        'doubling_time_months': doubling_time_months,
        'doubling_time_years': doubling_time_years,
        'r_squared': r_squared,
        'growth_rate_95ci': growth_rate_ci,
        'doubling_time_95ci_months': doubling_ci,
        'n_points': len(frontier_df),
    }

    return results


def analyze_by_category(df):
    """Analyze each category separately."""
    results = {}
    for cat in df['category'].unique():
        cat_data = df[df['category'] == cat]
        frontier = compute_frontier(cat_data, success_threshold=50)
        if len(frontier) >= 3:
            fit = fit_exponential(frontier)
            results[cat] = fit
        else:
            results[cat] = {'error': f'Only {len(frontier)} frontier points, need ≥3'}
    return results


def compare_with_metr():
    """Compare robotics doubling time with METR's LLM agent findings."""
    metr_findings = {
        'overall_2019_2025': {'doubling_months': 7, 'note': 'METR overall finding'},
        'recent_2024_2025': {'doubling_months': 4, 'note': 'METR accelerating trend'},
        'web_arena': {'doubling_months': 7, 'note': 'WebArena agentic tasks, ~50x behind software'},
        'self_driving_fsd': {'doubling_months': 20, 'note': 'Tesla FSD, slowest domain'},
    }
    return metr_findings


def print_results(results, category_results, metr_comparison):
    """Print formatted analysis results."""
    print("=" * 70)
    print("ROBOTIC MANIPULATION TASK HORIZON ANALYSIS")
    print("=" * 70)

    if results:
        print(f"\n--- Overall Frontier (all categories combined) ---")
        print(f"  Growth rate: {results['growth_rate_per_year']:.3f} /year")
        print(f"  Doubling time: {results['doubling_time_months']:.1f} months")
        if results['doubling_time_95ci_months']:
            lo, hi = results['doubling_time_95ci_months']
            print(f"  Doubling time 95% CI: ({lo:.1f}, {hi:.1f}) months")
        print(f"  R² (log-linear fit): {results['r_squared']:.3f}")
        print(f"  Frontier data points: {results['n_points']}")
    else:
        print("\n  Insufficient data for overall fit.")

    print(f"\n--- By Category ---")
    for cat, res in category_results.items():
        print(f"\n  {cat}:")
        if 'error' in res:
            print(f"    {res['error']}")
        else:
            print(f"    Doubling time: {res['doubling_time_months']:.1f} months")
            print(f"    R²: {res['r_squared']:.3f}")
            print(f"    Points: {res['n_points']}")

    print(f"\n--- Comparison with METR LLM Agent Findings ---")
    for domain, info in metr_comparison.items():
        print(f"  {domain}: {info['doubling_months']} months ({info['note']})")

    if results:
        print(f"\n  Robot manipulation doubling: {results['doubling_time_months']:.1f} months")
        ratio = results['doubling_time_months'] / 7
        print(f"  Ratio vs METR overall (7mo): {ratio:.1f}x slower")


def save_results(results, category_results):
    """Save analysis results to JSON."""
    output = {
        'overall': results if results else None,
        'by_category': {},
        'generated_at': datetime.now().isoformat(),
    }
    for cat, res in category_results.items():
        serializable = {}
        for k, v in res.items():
            if isinstance(v, (np.floating, np.integer)):
                serializable[k] = float(v)
            elif isinstance(v, tuple):
                serializable[k] = [float(x) if x is not None else None for x in v]
            else:
                serializable[k] = v
        output['by_category'][cat] = serializable

    # Convert numpy types in overall results
    if output['overall']:
        for k, v in output['overall'].items():
            if isinstance(v, (np.floating, np.integer)):
                output['overall'][k] = float(v)
            elif isinstance(v, tuple):
                output['overall'][k] = [float(x) if x is not None else None for x in v]

    path = os.path.join(FIGURES_DIR, '..', 'data', 'analysis_results.json')
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved analysis results to {path}")


def main():
    print("Loading data...")
    df = load_data()
    print(f"Loaded {len(df)} data points")

    if len(df) == 0:
        print("No data. Populate data/manipulation_horizons.csv first.")
        return

    # Compute frontier
    frontier = compute_frontier(df, success_threshold=50)
    print(f"Frontier points: {len(frontier)}")

    # Fit exponential
    results = fit_exponential(frontier) if len(frontier) >= 3 else None

    # By category
    category_results = analyze_by_category(df)

    # METR comparison data
    metr_comparison = compare_with_metr()

    # Print and save
    print_results(results, category_results, metr_comparison)
    save_results(results, category_results)


if __name__ == '__main__':
    main()
