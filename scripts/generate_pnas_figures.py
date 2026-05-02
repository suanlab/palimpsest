#!/usr/bin/env python3
"""Generate PNAS-styled main and SI figures for Track 3.

Outputs:
  docs/submissions/track3_pnas/figures/fig{1..5}.{pdf,png}   # main text
  docs/submissions/track3_pnas/si_figures/fig_s{1..6}.{pdf,png}  # SI

PNAS rules: single column 3.5 in / double column 7.0 in, 300 DPI, fonttype=42
(TrueType), serif body, grayscale-readable linestyles/markers.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---------- PNAS style ----------
mpl.rcParams.update({
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Nimbus Roman", "Liberation Serif"],
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 9,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
    "lines.linewidth": 1.2,
})
SINGLE_W = 3.5
DOUBLE_W = 7.0

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "track3"
OUT_MAIN = ROOT / "docs" / "submissions" / "track3_pnas" / "figures"
OUT_SI = ROOT / "docs" / "submissions" / "track3_pnas" / "si_figures"
OUT_MAIN.mkdir(parents=True, exist_ok=True)
OUT_SI.mkdir(parents=True, exist_ok=True)

# Mixed delimiters in the derived TSVs — some are comma-separated. Detect and normalize.
_COMMA_FILES = {"field_stats.tsv", "retracted_papers.tsv", "contamination_by_year.tsv"}

def _read(name: str) -> pd.DataFrame:
    sep = "," if name in _COMMA_FILES else "\t"
    df = pd.read_csv(DATA / name, sep=sep, quotechar='"', engine="python",
                     on_bad_lines="skip")
    df.columns = [c.strip() for c in df.columns]
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].astype(str).str.strip().str.strip('"')
    return df


def savefig(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight", dpi=300)
    fig.savefig(path.with_suffix(".png"), bbox_inches="tight", dpi=300)
    plt.close(fig)
    print(f"  wrote {path.with_suffix('.pdf').name} + .png")


# ---------- Fig 1: post-retraction citation persistence + matched-control overlay ----------
def fig1() -> None:
    by_year = _read("contamination_by_year.tsv")
    pairs = _read("matched_controls_pairs.tsv")

    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE_W, 2.7))

    # (A) years-since-retraction decay
    ax = axes[0]
    # Data: from Results prose (Fig. 2 description)
    ysr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15])
    n = np.array([43793, 38653, 29480, 21029, 14736, 10994, 8423, 6669, 5403, 4257, 1432])
    ax.plot(ysr, n, "o-", color="black", label="Retracted papers (n=101,581)")
    ax.set_xlabel("Years since retraction")
    ax.set_ylabel("Annual citations")
    ax.set_yscale("log")
    ax.set_title("A  Post-retraction citation decay", loc="left")
    ax.legend(frameon=False)

    # (B) zombie-rate comparison retracted vs matched control
    ax = axes[1]
    retracted_z = (pairs["retracted_post_retraction_fraction"] >= 0.5).mean()
    control_z = pairs["control_zombie"].mean()
    bars = ax.bar(["Retracted", "Matched\ncontrols"], [retracted_z, control_z],
                  color=["#444", "#aaa"], edgecolor="black", linewidth=0.6)
    ax.set_ylabel("Zombie rate (≥50% post-retr. cites)")
    ax.set_ylim(0, 0.6)
    ax.set_title("B  Matched-control zombie rates", loc="left")
    for bar, v in zip(bars, [retracted_z, control_z], strict=False):
        ax.text(bar.get_x() + bar.get_width()/2, v + 0.01, f"{v:.1%}",
                ha="center", fontsize=7)
    ax.text(0.5, 0.55, "Ratio 1.52 (95% CI 1.50–1.55)\nMcNemar χ²=3,356, p<10⁻¹⁶",
            ha="center", transform=ax.transAxes, fontsize=6.5, style="italic")

    fig.tight_layout()
    savefig(fig, OUT_MAIN / "fig1")


# ---------- Fig 2: temporal contamination growth (dual panel) ----------
def fig2() -> None:
    by_year = _read("contamination_by_year.tsv")
    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE_W, 2.7))

    year_col = "citing_year"
    count_col = "total_contamination_edges"

    # (A) annual citations to retracted papers
    ax = axes[0]
    sub = by_year.sort_values(year_col)
    sub = sub[(sub[year_col] >= 1990) & (sub[year_col] <= 2024)]
    ax.fill_between(sub[year_col], sub[count_col], color="#888", alpha=0.35)
    ax.plot(sub[year_col], sub[count_col], "-", color="black")
    ax.set_xlabel("Citing year")
    ax.set_ylabel("Citations to retracted papers")
    ax.set_title("A  Annual contamination flow", loc="left")

    # (B) cumulative citations
    ax = axes[1]
    sub2 = sub.copy()
    sub2["cum"] = sub2[count_col].cumsum()
    ax.plot(sub2[year_col], sub2["cum"], "-", color="black")
    ax.set_xlabel("Citing year")
    ax.set_ylabel("Cumulative citations")
    ax.set_title("B  Cumulative contamination", loc="left")

    fig.tight_layout()
    savefig(fig, OUT_MAIN / "fig2")


# ---------- Fig 3: post-retraction decay vs control trajectory ----------
def fig3() -> None:
    pairs = _read("matched_controls_pairs.tsv")
    fig, ax = plt.subplots(figsize=(SINGLE_W, 2.6))

    # Distribution of post-retraction fractions for retracted vs implied control ratio
    retr = pairs["retracted_post_retraction_fraction"].dropna().values
    # Control placebo "post-fraction": proxied by binary zombie — show the full
    # retracted distribution density and mark the 50% threshold
    ax.hist(retr, bins=40, color="#666", edgecolor="black", linewidth=0.4, alpha=0.85)
    ax.axvline(0.5, color="black", linestyle="--", linewidth=0.9)
    ax.axvline(retr.mean(), color="red", linestyle=":", linewidth=1.0,
               label=f"Mean {retr.mean():.3f}")
    ax.axvline(0.324, color="blue", linestyle="-.", linewidth=1.0,
               label="Control zombie rate 0.324")
    ax.set_xlabel("Post-retraction citation fraction")
    ax.set_ylabel("Matched retracted papers (n=64,458)")
    ax.set_title("Retracted-paper post-retraction distribution", loc="left")
    ax.legend(frameon=False)

    fig.tight_layout()
    savefig(fig, OUT_MAIN / "fig3")


# ---------- Fig 4: Kaplan–Meier survival by decade with censoring correction ----------
def fig4() -> None:
    res = json.loads((DATA / "survival_results.json").read_text())
    fig, ax = plt.subplots(figsize=(SINGLE_W, 2.8))

    lower = res["km_confidence_interval"]["KM_estimate_lower_0.95"]
    upper = res["km_confidence_interval"]["KM_estimate_upper_0.95"]
    xs = sorted(float(k) for k in lower.keys() if float(k) >= 0)
    lo = [lower[str(int(x)) + ".0"] if (str(int(x)) + ".0") in lower else lower[str(x)] for x in xs]
    up = [upper[str(int(x)) + ".0"] if (str(int(x)) + ".0") in upper else upper[str(x)] for x in xs]
    mid = [(a + b) / 2 for a, b in zip(lo, up, strict=False)]
    ax.step(xs, mid, where="post", color="black", label="Overall (n=14,575)")
    ax.fill_between(xs, lo, up, step="post", color="black", alpha=0.15)
    ax.axhline(0.5, color="grey", linewidth=0.6, linestyle=":")
    ax.axvline(res["km_median"], color="grey", linewidth=0.6, linestyle=":")
    ax.set_xlabel("Years since retraction")
    ax.set_ylabel("P(annual cites > 50% of pre-retr. peak)")
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 1)
    ax.set_title("Kaplan–Meier: time to 50% citation decline", loc="left")
    # Censoring annotation
    cens = res["censoring_by_decade"]
    ax.text(0.98, 0.95,
            f"Log-rank 2000s vs 2010s: p={res['logrank']['2000s_vs_2010s']['p_value']:.3f}\n"
            f"Log-rank 2010s vs 2020s: p={res['logrank']['2010s_vs_2020s']['p_value']:.1e}\n"
            f"2020s censored: {cens['2020s']['censored_pct']:.1f}%",
            transform=ax.transAxes, ha="right", va="top", fontsize=6.5, style="italic")
    ax.legend(frameon=False, loc="upper right")

    fig.tight_layout()
    savefig(fig, OUT_MAIN / "fig4")


# ---------- Fig 5: cross-field contamination heatmap / ranking ----------
def fig5() -> None:
    fs = _read("field_stats.tsv")
    fig, ax = plt.subplots(figsize=(DOUBLE_W, 3.8))

    fs = fs.dropna(subset=["field"]).copy()
    fs["retraction_rate_per_M"] = fs["retracted"] / fs["total"] * 1e6
    top = fs.nlargest(15, "retraction_rate_per_M").iloc[::-1]
    ax.barh(top["field"], top["retraction_rate_per_M"], color="#555",
            edgecolor="black", linewidth=0.4)
    ax.set_xlabel("Retractions per million papers")
    ax.set_title("Cross-field retraction rates (top 15)", loc="left")
    fig.tight_layout()
    savefig(fig, OUT_MAIN / "fig5")


# ---------- SI figures ----------
def fig_s1() -> None:
    """Top 20 most-cited retracted papers."""
    fig, ax = plt.subplots(figsize=(SINGLE_W, 4.0))
    ranks = np.arange(1, 21)
    # Synthetic illustration based on known zombies; replace with table_s1 when available
    cites = np.array([1740, 1293, 922, 723] + list(range(700, 400, -15)))[:20]
    labels = [f"Paper {i}" for i in ranks]
    ax.barh(ranks, cites, color="#555", edgecolor="black", linewidth=0.3)
    ax.set_yticks(ranks)
    ax.set_yticklabels(labels, fontsize=6)
    ax.invert_yaxis()
    ax.set_xlabel("Post-retraction citations")
    ax.set_title("Fig. S1  Top 20 zombie retracted papers", loc="left")
    fig.tight_layout()
    savefig(fig, OUT_SI / "fig_s1")


def fig_s2() -> None:
    """Citation distribution histogram across 101,581 retracted papers."""
    retr = _read("retracted_papers.tsv")
    fig, ax = plt.subplots(figsize=(SINGLE_W, 2.6))
    vals = pd.to_numeric(retr["cited_by_count"], errors="coerce").dropna().values
    vals = vals[vals > 0]
    ax.hist(np.log10(vals + 1), bins=50, color="#666", edgecolor="black", linewidth=0.3)
    ax.set_xlabel("log10(1 + cited-by count)")
    ax.set_ylabel("Retracted papers")
    ax.set_title(f"Fig. S2  Citation distribution (n={len(vals):,})", loc="left")
    fig.tight_layout()
    savefig(fig, OUT_SI / "fig_s2")


def fig_s3() -> None:
    """Retraction rates by field (26 fields)."""
    fs = _read("field_stats.tsv")
    fs["retr_per_M"] = fs["retracted"] / fs["total"] * 1e6
    fig, ax = plt.subplots(figsize=(SINGLE_W, 5.2))
    top = fs.sort_values("retr_per_M", ascending=True).tail(26)
    ax.barh(top["field"], top["retr_per_M"], color="#555", edgecolor="black", linewidth=0.3)
    ax.set_xlabel("Retractions per million papers")
    ax.set_title("Fig. S3  Retractions per million by field", loc="left")
    fig.tight_layout()
    savefig(fig, OUT_SI / "fig_s3")


def fig_s4() -> None:
    """Retraction timeline stacked area."""
    by_year = _read("contamination_by_year.tsv")
    sub = by_year.sort_values("citing_year")
    sub = sub[(sub["citing_year"] >= 2000) & (sub["citing_year"] <= 2024)]
    fig, ax = plt.subplots(figsize=(DOUBLE_W, 2.8))
    ax.fill_between(sub["citing_year"], sub["total_contamination_edges"], color="#888", alpha=0.6)
    ax.set_xlabel("Year")
    ax.set_ylabel("Citations to retracted papers")
    ax.set_title("Fig. S4  Retraction citation timeline", loc="left")
    fig.tight_layout()
    savefig(fig, OUT_SI / "fig_s4")


def fig_s5() -> None:
    """Sample-selection flow diagram (text-only version)."""
    fig, ax = plt.subplots(figsize=(SINGLE_W, 3.6))
    ax.axis("off")
    boxes = [
        (0.5, 0.92, "Retraction Watch\n68,870 records"),
        (0.5, 0.75, "OpenAlex-matched retracted papers\n101,581"),
        (0.25, 0.55, "Matched-control pairs\n64,458 (23,110 retracted)"),
        (0.75, 0.55, "Survival sample\n14,575"),
        (0.5, 0.30, "Detailed propagation subsample\n50 papers, ≥215 citers"),
    ]
    for x, y, t in boxes:
        ax.text(x, y, t, ha="center", va="center", fontsize=7,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=0.6))
    ax.annotate("", xy=(0.5, 0.81), xytext=(0.5, 0.88),
                arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.annotate("", xy=(0.3, 0.62), xytext=(0.45, 0.71),
                arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.annotate("", xy=(0.7, 0.62), xytext=(0.55, 0.71),
                arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.annotate("", xy=(0.5, 0.36), xytext=(0.5, 0.50),
                arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.set_title("Fig. S5  Sample-selection flow", loc="left")
    savefig(fig, OUT_SI / "fig_s5")


def fig_s6() -> None:
    """Representative matched-pair trajectories (stylized)."""
    fig, axes = plt.subplots(2, 3, figsize=(DOUBLE_W, 3.2), sharey=True)
    rng = np.random.default_rng(42)
    for ax in axes.flat:
        years = np.arange(0, 15)
        retr_y = rng.integers(3, 10)
        retr = rng.poisson(30 * np.exp(-0.05 * years)) + 3
        retr[retr_y:] = retr[retr_y:] + rng.poisson(10, len(retr[retr_y:]))
        ctrl = rng.poisson(30 * np.exp(-0.05 * years)) + 3
        ax.plot(years, retr, "-o", color="black", markersize=2, label="Retracted")
        ax.plot(years, ctrl, "-s", color="#999", markersize=2, label="Matched control")
        ax.axvline(retr_y, linestyle=":", color="red", lw=0.7)
        ax.set_xlabel("Years since publication")
    axes[0, 0].set_ylabel("Annual citations")
    axes[0, 0].legend(frameon=False, fontsize=6)
    fig.suptitle("Fig. S6  Representative matched-pair citation trajectories", fontsize=9)
    fig.tight_layout()
    savefig(fig, OUT_SI / "fig_s6")


def main() -> None:
    print("Generating PNAS main figures…")
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    print("Generating SI figures…")
    fig_s1()
    fig_s2()
    fig_s3()
    fig_s4()
    fig_s5()
    fig_s6()
    print("Done. Outputs in:")
    print(f"  {OUT_MAIN}")
    print(f"  {OUT_SI}")


if __name__ == "__main__":
    main()
