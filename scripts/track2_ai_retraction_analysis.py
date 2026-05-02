#!/usr/bin/env python3
"""Track 2 (companion): AI adoption × retraction correlation, deeper analysis.

Extends the Extended Data Table 9 cross-sectional finding (r = 0.489) with
panel-level and causality-directed tests:
  1. Panel fixed-effects regression of retraction rate on lagged AI fraction
  2. Panel Granger causality test (field-year)
  3. Per-field time-series cross-correlation
  4. Placebo (pre-2015 retraction rate vs post-2015 AI adoption)

Outputs:
  data/processed/track2_ai_retraction_analysis.json
  docs/submissions/track2_note/fig_ai_retraction.{pdf,png}
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import pearsonr, spearmanr

mpl.rcParams.update({
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "font.family": "serif", "font.size": 8,
    "axes.labelsize": 8, "axes.titlesize": 9,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.8,
})

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT_DIR = ROOT / "docs" / "submissions" / "track2_note"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def build_panel() -> pd.DataFrame:
    """Merge AI-adoption panel with retraction-count panel by field × year."""
    ai = pd.read_parquet(DATA / "neo4j_field_panel.parquet")
    ai = ai[(ai.year >= 2000) & (ai.year <= 2023)].copy()
    ai["ai_pct"] = ai.ai_concept_fraction * 100

    # Build retraction rate per field × year from Retraction Watch
    rw = pd.read_csv(ROOT / "data" / "raw" / "retraction_watch" /
                      "retraction-watch-data" / "retraction_watch.csv",
                      low_memory=False)
    rw["year"] = pd.to_datetime(rw.OriginalPaperDate, errors="coerce").dt.year
    rw = rw.dropna(subset=["year"])
    rw["year"] = rw.year.astype(int)

    # Subject field mapping to OpenAlex primary fields is messy; use Retraction Watch Subject
    # heuristically: take first `(xx)` field token
    import re
    def first_subject(s):
        if pd.isna(s): return None
        m = re.search(r"\(([^)]+)\)\s*([^;]+)", s)
        return m.group(2).strip() if m else None
    rw["primary_subject"] = rw.Subject.apply(first_subject)

    # Aggregate retraction counts by subject×year
    rw_counts = rw.groupby(["primary_subject", "year"]).size().reset_index(name="retractions")

    # Total publication counts come from ai panel total_count
    ai = ai.rename(columns={"total_count": "papers"})
    # Map RW subjects to OpenAlex field names (imperfect — cover the main ones)
    subject_to_field = {
        "Biological Sciences": "Agricultural and Biological Sciences",
        "Biology": "Agricultural and Biological Sciences",
        "Environmental Sciences": "Environmental Science",
        "Computer Science": "Computer Science",
        "Engineering": "Engineering",
        "Chemistry": "Chemistry",
        "Physics": "Physics and Astronomy",
        "Astronomy": "Physics and Astronomy",
        "Mathematics": "Mathematics",
        "Materials Science": "Materials Science",
        "Neuroscience": "Neuroscience",
        "Medicine": "Medicine",
        "Clinical Medicine": "Medicine",
        "Social Sciences": "Social Sciences",
        "Psychology": "Psychology",
        "Psychiatry": "Psychology",
        "Economics": "Economics, Econometrics and Finance",
        "Business": "Business, Management and Accounting",
        "Earth Sciences": "Earth and Planetary Sciences",
        "Humanities": "Arts and Humanities",
        "Biochemistry": "Biochemistry, Genetics and Molecular Biology",
        "Genetics": "Biochemistry, Genetics and Molecular Biology",
        "Molecular Biology": "Biochemistry, Genetics and Molecular Biology",
        "Immunology": "Immunology and Microbiology",
        "Microbiology": "Immunology and Microbiology",
        "Pharmacology": "Pharmacology, Toxicology and Pharmaceutics",
        "Energy": "Energy",
    }
    rw_counts["field_name"] = rw_counts.primary_subject.map(subject_to_field)
    rw_counts = rw_counts.dropna(subset=["field_name"])
    rw_counts = rw_counts.groupby(["field_name", "year"]).retractions.sum().reset_index()

    panel = ai.merge(rw_counts, on=["field_name", "year"], how="left")
    panel["retractions"] = panel.retractions.fillna(0).astype(int)
    panel["retraction_rate_per_M"] = panel.retractions / panel.papers * 1e6
    return panel.sort_values(["field_name", "year"]).reset_index(drop=True)


def granger_field_panel(panel: pd.DataFrame, lag: int = 3) -> dict:
    """Panel Granger: retraction_t on AI_{t-1..t-lag} with field+year FE."""
    # Build lagged AI fraction per field
    p = panel.copy()
    p = p.sort_values(["field_name", "year"])
    for l in range(1, lag + 1):
        p[f"ai_lag{l}"] = p.groupby("field_name").ai_pct.shift(l)
    p = p.dropna()
    field_d = pd.get_dummies(p.field_name, prefix="f", drop_first=True).astype(int)
    year_d  = pd.get_dummies(p.year, prefix="y", drop_first=True).astype(int)
    lag_cols = [f"ai_lag{l}" for l in range(1, lag + 1)]
    X = pd.concat([p[lag_cols], field_d, year_d], axis=1)
    X = sm.add_constant(X).astype(float)
    y = p.retraction_rate_per_M
    m = sm.OLS(y, X).fit(cov_type="HC3")
    # Joint F-test on lag coefficients
    ftest = m.f_test(" = ".join(lag_cols) + " = 0")
    return {
        "n_obs": int(len(p)),
        "lag_coefs": {c: float(m.params[c]) for c in lag_cols},
        "lag_pvals": {c: float(m.pvalues[c]) for c in lag_cols},
        "joint_F": float(ftest.fvalue),
        "joint_p": float(ftest.pvalue),
        "R2": float(m.rsquared),
    }


def main() -> None:
    panel = build_panel()
    print(f"Panel: {len(panel)} field-year obs, {panel.field_name.nunique()} fields matched")

    # Cross-sectional correlation (field-level means over 2015-2023)
    agg = panel[(panel.year >= 2015)].groupby("field_name").agg(
        ai_pct_mean=("ai_pct", "mean"),
        retr_per_M_mean=("retraction_rate_per_M", "mean"),
    ).dropna().reset_index()
    rp, pp = pearsonr(agg.ai_pct_mean, agg.retr_per_M_mean)
    print(f"\nCross-sectional (2015-2023 means): r = {rp:.3f}, p = {pp:.4f}, n = {len(agg)}")

    # Panel correlation field×year (pooled)
    rf, pf = pearsonr(panel.ai_pct, panel.retraction_rate_per_M)
    print(f"Panel pooled: r = {rf:.3f}, p = {pf:.2e}, n = {len(panel)}")

    # Per-field time-series correlation
    per_field_r = {}
    for field, grp in panel.groupby("field_name"):
        if len(grp) < 10:
            continue
        r, _ = pearsonr(grp.ai_pct, grp.retraction_rate_per_M)
        per_field_r[field] = float(r)
    print(f"\nPer-field time-series correlations (n={len(per_field_r)} fields):")
    for f, r in sorted(per_field_r.items(), key=lambda kv: -kv[1])[:10]:
        print(f"  {f:<45s} r = {r:+.3f}")

    # Granger
    print("\n[3] Panel Granger test: retraction_t ~ AI_{t-1..t-3} + field FE + year FE")
    gr = granger_field_panel(panel, lag=3)
    print(f"  joint F = {gr['joint_F']:.3f}, p = {gr['joint_p']:.4f}, R² = {gr['R2']:.3f}")
    for c, coef in gr["lag_coefs"].items():
        print(f"    {c}: β = {coef:+.4f}, p = {gr['lag_pvals'][c]:.3f}")

    # Placebo: reverse direction (does retraction_{t-1} predict AI_t?)
    print("\n[4] Reverse-direction placebo: AI_t ~ retraction_{t-1..t-3} + FEs")
    p = panel.copy().sort_values(["field_name", "year"])
    for l in range(1, 4):
        p[f"retr_lag{l}"] = p.groupby("field_name").retraction_rate_per_M.shift(l)
    p = p.dropna()
    lag_cols = [f"retr_lag{l}" for l in range(1, 4)]
    field_d = pd.get_dummies(p.field_name, prefix="f", drop_first=True).astype(int)
    year_d  = pd.get_dummies(p.year, prefix="y", drop_first=True).astype(int)
    X = pd.concat([p[lag_cols], field_d, year_d], axis=1)
    X = sm.add_constant(X).astype(float)
    m = sm.OLS(p.ai_pct, X).fit(cov_type="HC3")
    ftest = m.f_test(" = ".join(lag_cols) + " = 0")
    reverse = {
        "joint_F": float(ftest.fvalue),
        "joint_p": float(ftest.pvalue),
        "R2": float(m.rsquared),
    }
    print(f"  reverse joint F = {reverse['joint_F']:.3f}, p = {reverse['joint_p']:.4f}")

    # Figure: scatter + Granger coefs
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8))

    ax = axes[0]
    ax.scatter(agg.ai_pct_mean, agg.retr_per_M_mean, s=25, c="black",
                edgecolor="white", linewidth=0.3)
    for _, r in agg.iterrows():
        if r.retr_per_M_mean > 200 or r.ai_pct_mean > 3:
            ax.annotate(r.field_name[:13], (r.ai_pct_mean, r.retr_per_M_mean),
                         fontsize=6, alpha=0.7)
    # OLS fit
    b, a = np.polyfit(agg.ai_pct_mean, agg.retr_per_M_mean, 1)
    xs = np.linspace(agg.ai_pct_mean.min(), agg.ai_pct_mean.max(), 50)
    ax.plot(xs, b * xs + a, "k--", linewidth=0.6, alpha=0.5)
    ax.set_xlabel("AI fraction 2015–2023 mean (%)")
    ax.set_ylabel("Retraction rate per million papers")
    ax.set_title(f"A  Cross-sectional (r={rp:.3f}, p={pp:.3f})", loc="left")

    ax = axes[1]
    lag_labels = list(gr["lag_coefs"].keys())
    coefs = [gr["lag_coefs"][c] for c in lag_labels]
    ax.bar(range(len(lag_labels)), coefs, color="#555", edgecolor="black", linewidth=0.3)
    ax.set_xticks(range(len(lag_labels)))
    ax.set_xticklabels([f"{-i}yr" for i in range(1, len(lag_labels) + 1)])
    ax.axhline(0, color="black", linewidth=0.4)
    ax.set_xlabel("AI fraction lag")
    ax.set_ylabel("Panel FE coefficient")
    ax.set_title(f"B  Granger F={gr['joint_F']:.2f}, p={gr['joint_p']:.3f}", loc="left")

    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig_ai_retraction.pdf", dpi=300, bbox_inches="tight")
    fig.savefig(OUT_DIR / "fig_ai_retraction.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    out = {
        "cross_sectional": {"r": float(rp), "p": float(pp), "n": int(len(agg))},
        "panel_pooled": {"r": float(rf), "p": float(pf), "n": int(len(panel))},
        "per_field_correlations": per_field_r,
        "panel_granger": gr,
        "reverse_direction_placebo": reverse,
        "interpretation": (
            f"Cross-sectional correlation r = {rp:.3f} (p = {pp:.3f}) replicates the "
            f"previously reported association at the field level. The panel Granger "
            f"test on lagged AI adoption predicting retraction rate yields F = "
            f"{gr['joint_F']:.2f}, p = {gr['joint_p']:.3f}; the reverse-direction "
            f"placebo (retractions predicting subsequent AI adoption) yields F = "
            f"{reverse['joint_F']:.2f}, p = {reverse['joint_p']:.3f}. Comparing "
            "forward versus reverse F-statistics indicates which temporal direction "
            "carries stronger predictive signal. Causal interpretation still "
            "requires ruling out common shocks (publication volume, paper-mill "
            "cycles, field-specific editorial policy changes) that this "
            "specification cannot identify."
        ),
    }
    (DATA / "track2_ai_retraction_analysis.json").write_text(json.dumps(out, indent=2))
    print(f"\nwrote track2_ai_retraction_analysis.json")
    print(f"wrote fig_ai_retraction.{{pdf,png}}")


if __name__ == "__main__":
    main()
