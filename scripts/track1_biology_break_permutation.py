#!/usr/bin/env python3
"""T1-B: Permutation test for Biology 2019 Chow structural break.

The original Chow test reported F = 11.11 as the maximum F across candidate
breakpoints with asymptotic p < 0.001. That asymptotic p assumes iid residuals
and a single pre-specified break year. When the break year is *selected* as
the maximum across candidates, the distribution of max-F under the null
(no break anywhere) differs from the single-point F distribution.

This script computes the empirical null distribution via:
  1. Circular block bootstrap on Biology's de-trended residuals (block size 3)
  2. Refit max-Chow-F on each bootstrap series
  3. Compare observed F = 11.11 against the empirical max-F distribution

Outputs:
  data/processed/track1_biology_break_permutation.json
  docs/submissions/track1_nhb/figures/fig_biology_break_permutation.{pdf,png}
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

mpl.rcParams.update({
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "font.family": "serif", "font.size": 8,
    "axes.labelsize": 8, "axes.titlesize": 9,
    "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.8,
})

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT_FIG = ROOT / "docs" / "submissions" / "track1_nhb" / "figures"
OUT_FIG.mkdir(parents=True, exist_ok=True)


def chow_maxF(y: np.ndarray, min_window: int = 5) -> tuple[float, int]:
    """Scan all candidate break years and return (max F, best break index)."""
    n = len(y)
    x_full = np.arange(n)
    # Pooled linear model
    X_pooled = sm.add_constant(x_full)
    rss_pooled = np.sum(sm.OLS(y, X_pooled).fit().resid ** 2)

    best_F = -np.inf
    best_k = -1
    for k in range(min_window, n - min_window):
        x1, y1 = x_full[:k], y[:k]
        x2, y2 = x_full[k:], y[k:]
        X1 = sm.add_constant(x1)
        X2 = sm.add_constant(x2)
        rss1 = np.sum(sm.OLS(y1, X1).fit().resid ** 2)
        rss2 = np.sum(sm.OLS(y2, X2).fit().resid ** 2)
        rss_split = rss1 + rss2
        # Chow F with df_num = 2 (two extra parameters), df_den = n - 4
        if rss_split <= 0 or n - 4 <= 0:
            continue
        F = ((rss_pooled - rss_split) / 2) / (rss_split / (n - 4))
        if F > best_F:
            best_F = F
            best_k = k
    return float(best_F), int(best_k)


def circular_block_bootstrap(y: np.ndarray, block_size: int, rng: np.random.Generator) -> np.ndarray:
    """Generate one bootstrap series of the same length via circular blocks."""
    n = len(y)
    n_blocks = int(np.ceil(n / block_size))
    starts = rng.integers(0, n, size=n_blocks)
    pieces = [np.take(y, np.arange(s, s + block_size) % n) for s in starts]
    return np.concatenate(pieces)[:n]


def main() -> None:
    df = pd.read_parquet(DATA / "ai_adoption_by_field.parquet")
    bio = df[(df.field_name == "Biology") & (df.year <= 2023)].sort_values("year").reset_index(drop=True)
    print(f"Biology panel: {len(bio)} years ({bio.year.min()}–{bio.year.max()}) "
          "— 2024 (23.2% AI fraction) excluded as extraction artefact; "
          "2025 excluded as incomplete coverage")
    y = bio.ai_fraction.values * 100  # pp
    years = bio.year.values

    # De-trend by linear fit (so bootstrap preserves no-break structure)
    X = sm.add_constant(np.arange(len(y)))
    fitted = sm.OLS(y, X).fit()
    resid = fitted.resid
    trend = fitted.fittedvalues

    # Observed max-F
    obs_F, obs_k = chow_maxF(y)
    obs_break_year = int(years[obs_k])
    print(f"Observed max-Chow-F = {obs_F:.3f} at break year {obs_break_year} (k={obs_k})")

    # Permutation: resample residuals, add trend back, recompute max-F
    n_boot = 2000
    rng = np.random.default_rng(2026)
    null_F = np.empty(n_boot)
    for b in range(n_boot):
        r_boot = circular_block_bootstrap(resid, block_size=3, rng=rng)
        y_boot = trend + r_boot
        F_b, _ = chow_maxF(y_boot)
        null_F[b] = F_b
    p_emp = float((null_F >= obs_F).sum() + 1) / (n_boot + 1)

    print(f"Empirical max-F null: mean {null_F.mean():.3f}, sd {null_F.std():.3f}, 95% {np.quantile(null_F, 0.95):.3f}, 99% {np.quantile(null_F, 0.99):.3f}")
    print(f"Empirical p-value for observed F = {obs_F:.3f}: p = {p_emp:.4f}")

    out = {
        "observed_F": obs_F,
        "observed_break_year": obs_break_year,
        "n_bootstrap": n_boot,
        "block_size": 3,
        "null_mean_F": float(null_F.mean()),
        "null_sd_F": float(null_F.std()),
        "null_q95": float(np.quantile(null_F, 0.95)),
        "null_q99": float(np.quantile(null_F, 0.99)),
        "empirical_p": p_emp,
        "interpretation": (
            f"Observed max-Chow-F = {obs_F:.2f} at break year {obs_break_year}. "
            f"Under 2,000 circular block-bootstrap resamples of de-trended "
            f"Biology residuals (block size 3, null hypothesis: no break), "
            f"the empirical max-F distribution has mean {null_F.mean():.2f} and "
            f"95% quantile {np.quantile(null_F, 0.95):.2f}. Empirical p-value "
            f"= {p_emp:.4f}. This stress-tests the reported asymptotic p < "
            "0.001, which was based on a single pre-specified break year; the "
            "empirical p incorporates the multiple-testing burden of scanning "
            "all candidate break years."
        ),
    }
    (DATA / "track1_biology_break_permutation.json").write_text(json.dumps(out, indent=2))
    print(f"\nwrote track1_biology_break_permutation.json")

    # Figure: null distribution of max-F + observed value
    fig, ax = plt.subplots(figsize=(3.5, 2.8))
    ax.hist(null_F, bins=40, color="#bbb", edgecolor="grey", linewidth=0.3)
    ax.axvline(obs_F, color="red", linewidth=1.2, label=f"Observed {obs_F:.2f}")
    ax.axvline(np.quantile(null_F, 0.95), color="black", linewidth=0.7, linestyle="--",
               label=f"Null 95% {np.quantile(null_F, 0.95):.2f}")
    ax.axvline(np.quantile(null_F, 0.99), color="black", linewidth=0.7, linestyle=":",
               label=f"Null 99% {np.quantile(null_F, 0.99):.2f}")
    ax.set_xlabel("max-Chow-F across candidate break years")
    ax.set_ylabel("Bootstrap count")
    ax.set_title(f"Biology 2019 break permutation (p = {p_emp:.3f})", loc="left")
    ax.legend(frameon=False, fontsize=6.5)
    fig.tight_layout()
    fig.savefig(OUT_FIG / "fig_biology_break_permutation.pdf", dpi=300, bbox_inches="tight")
    fig.savefig(OUT_FIG / "fig_biology_break_permutation.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote fig_biology_break_permutation.{{pdf,png}}")


if __name__ == "__main__":
    main()
