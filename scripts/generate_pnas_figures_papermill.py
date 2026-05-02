#!/usr/bin/env python3
"""PNAS paper-mill-focused figures for Track 3 resubmission.

Fig 1: A=Paper-mill retraction volume by year (log scale), B=Field concentration
Fig 2: A=Zombie rate by reason (bar chart + CI), B=Mill vs non-mill head-to-head
Fig 3: Post-retraction citation volume attributable by reason (stacked area)
Fig 4: KM survival by reason + matched-window 2000s vs 2010s null
Fig 5: Field × reason heatmap

Outputs (PNAS format: 3.5" single / 7" double, 300 DPI, fonttype=42):
  docs/submissions/track3_pnas/figures/fig1.{pdf,png}
  docs/submissions/track3_pnas/figures/fig2.{pdf,png}
  docs/submissions/track3_pnas/figures/fig3.{pdf,png}
  docs/submissions/track3_pnas/figures/fig4.{pdf,png}
  docs/submissions/track3_pnas/figures/fig5.{pdf,png}
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

mpl.rcParams.update({
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Liberation Serif"],
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 9,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.8, "lines.linewidth": 1.1,
})

SINGLE = 3.5
DOUBLE = 7.0

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "track3"
TABLES = DATA / "tables"
FIG = ROOT / "docs" / "submissions" / "track3_pnas" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# Color palette, reason-coded
COLOR = {
    "Paper mill": "#c0392b",   # strong red
    "Other":       "#7f8c8d",  # slate
    "Error":       "#f39c12",  # amber
    "Misconduct":  "#2980b9",  # blue
    "Unknown":     "#bdc3c7",  # light grey
}
ORDER = ["Misconduct", "Error", "Other", "Paper mill"]  # increasing zombie ratio


def save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight", dpi=300)
    fig.savefig(path.with_suffix(".png"), bbox_inches="tight", dpi=300)
    plt.close(fig)
    print(f"  wrote {path.name}.{{pdf,png}}")


def fig1() -> None:
    """Fig 1. A: paper-mill retraction volume timeline (log scale) with year-by-reason stacked
       B: field concentration (top 15 paper-mill share)."""
    timeline = pd.read_csv(TABLES / "table_papermill_timeline.tsv", sep="\t", index_col=0)
    fields = pd.read_csv(TABLES / "table_papermill_fields.tsv", sep="\t")

    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE, 2.8))

    # (A) Stacked timeline, 2000-2024, top reasons
    ax = axes[0]
    timeline = timeline.loc[2000:2024]
    cats_present = [c for c in ORDER if c in timeline.columns]
    bottom = np.zeros(len(timeline))
    for c in cats_present:
        vals = timeline[c].values
        ax.bar(timeline.index, vals, bottom=bottom, color=COLOR[c], label=c,
               width=0.85, edgecolor="white", linewidth=0.2)
        bottom += vals
    ax.set_xlabel("Retraction year")
    ax.set_ylabel("Retractions (count)")
    ax.set_title("A  Retraction volume by reason, 2000–2024", loc="left")
    ax.legend(frameon=False, loc="upper left", fontsize=6.5)
    # Annotate 2020+ paper-mill explosion
    ax.annotate("Paper-mill\nexplosion\n2020+",
                xy=(2022, timeline.loc[2022].sum()*0.9),
                xytext=(2015, timeline.max().max()*0.7),
                arrowprops=dict(arrowstyle="->", color="#c0392b", lw=0.7),
                fontsize=6.5, color="#c0392b", ha="center")

    # (B) Field concentration (top 15)
    ax = axes[1]
    top = fields.sort_values("paper_mill_share", ascending=True)
    # Short field labels
    short = {
        "Decision Sciences": "Decision Sci.",
        "Computer Science": "Computer Sci.",
        "Social Sciences": "Social Sci.",
        "Health Professions": "Health Prof.",
        "Immunology and Microbiology": "Immuno/Micro",
        "Agricultural and Biological Sciences": "Agri/Bio Sci.",
        "Environmental Science": "Environ. Sci.",
        "Arts and Humanities": "Arts/Humani.",
    }
    labels = [short.get(f, f[:14]) for f in top.field]
    colors_bar = ["#c0392b" if s >= 0.15 else "#7f8c8d" for s in top.paper_mill_share]
    ax.barh(labels, top.paper_mill_share * 100, color=colors_bar,
            edgecolor="white", linewidth=0.3)
    for i, (_, row) in enumerate(top.iterrows()):
        ax.text(row.paper_mill_share * 100 + 0.5, i,
                f"{row.paper_mill_share*100:.1f}%",
                va="center", fontsize=6.5, color="#333")
    ax.set_xlabel("Paper-mill share of retractions (%)")
    ax.set_title("B  Field concentration (fields ≥100 retractions)", loc="left")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, top.paper_mill_share.max() * 100 * 1.15)

    fig.tight_layout()
    save(fig, FIG / "fig1")


def fig2() -> None:
    """Fig 2. A: zombie rate by reason with 95% CI; B: mill vs non-mill direct comparison."""
    stats = pd.read_csv(TABLES / "table_papermill_stats.tsv", sep="\t")
    stats = stats[stats.reason != "Unknown"].copy()
    stats["reason"] = pd.Categorical(stats.reason, categories=ORDER, ordered=True)
    stats = stats.sort_values("reason")

    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE, 2.8))

    # (A) Zombie rate by reason
    ax = axes[0]
    x = np.arange(len(stats))
    w = 0.38
    retr = stats.retracted_zombie_rate.values
    ctrl = stats.control_zombie_rate.values
    retr_err = np.vstack([retr - stats.retracted_CI_low,
                          stats.retracted_CI_high - retr])
    ctrl_err = np.vstack([ctrl - stats.control_CI_low,
                          stats.control_CI_high - ctrl])
    ax.bar(x - w/2, retr, w, yerr=retr_err, color="#2c3e50",
           edgecolor="white", linewidth=0.3, label="Retracted",
           error_kw=dict(elinewidth=0.6, capsize=1.5, ecolor="black"))
    ax.bar(x + w/2, ctrl, w, yerr=ctrl_err, color="#bdc3c7",
           edgecolor="white", linewidth=0.3, label="Matched control",
           error_kw=dict(elinewidth=0.6, capsize=1.5, ecolor="black"))
    # Annotate odds ratios above bars
    for i, (_, row) in enumerate(stats.iterrows()):
        ax.text(i, max(row.retracted_CI_high, row.control_CI_high) + 0.03,
                f"OR={row.odds_ratio:.1f}", ha="center", fontsize=6.5,
                color="#c0392b" if row.odds_ratio > 7 else "#333")
    ax.set_xticks(x)
    ax.set_xticklabels(stats.reason, rotation=15, ha="right")
    ax.set_ylabel("Zombie rate (≥50% post-retraction cites)")
    ax.set_ylim(0, 1.0)
    ax.set_title("A  Zombie rate by retraction reason (n=34,126 pairs)", loc="left")
    ax.legend(frameon=False, loc="upper left", fontsize=6.5)

    # (B) Mill vs non-mill direct comparison
    ax = axes[1]
    mill_rate = stats.loc[stats.reason == "Paper mill", "retracted_zombie_rate"].values[0]
    nonmill = stats[stats.reason.isin(["Misconduct", "Error", "Other"])]
    # Pooled non-mill rate (weighted by n)
    nonmill_n = nonmill.n_pairs.sum()
    nonmill_zombies = (nonmill.n_pairs * nonmill.retracted_zombie_rate).sum()
    nonmill_rate = nonmill_zombies / nonmill_n
    labels = ["Paper\nmill\n(n=9,094)", "Non-mill\nretracted\n(n=25,032)", "Matched\ncontrols\n(n=34,126)"]
    # pooled control rate
    ctrl_n = stats[stats.reason.isin(ORDER)].n_pairs.sum()
    ctrl_zombies = (stats[stats.reason.isin(ORDER)].n_pairs
                    * stats[stats.reason.isin(ORDER)].control_zombie_rate).sum()
    ctrl_rate = ctrl_zombies / ctrl_n
    values = [mill_rate, nonmill_rate, ctrl_rate]
    colors = ["#c0392b", "#34495e", "#bdc3c7"]
    bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=0.3)
    for b, v in zip(bars, values, strict=True):
        ax.text(b.get_x() + b.get_width()/2, v + 0.02, f"{v:.1%}",
                ha="center", fontsize=7, color="#333")
    ax.axhline(0.5, color="grey", linewidth=0.5, linestyle=":")
    ax.set_ylabel("Zombie rate")
    ax.set_ylim(0, 0.9)
    ax.set_title("B  Paper mill vs non-mill (OR=1.32, Fisher p<10⁻²²)", loc="left")

    fig.tight_layout()
    save(fig, FIG / "fig2")


def fig3() -> None:
    """Fig 3. Post-retraction citation volume attributable by reason (stacked share)."""
    cites = pd.read_csv(TABLES / "table_papermill_citations.tsv", sep="\t")
    cites = cites[cites.reason_category != "Unknown"].copy()
    cites["reason_category"] = pd.Categorical(
        cites.reason_category, categories=ORDER, ordered=True)
    cites = cites.sort_values("reason_category")

    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE, 2.8))

    # (A) Post-retraction citation volume
    ax = axes[0]
    total = cites.total_post_cites.sum()
    shares = cites.total_post_cites / total * 100
    colors = [COLOR[r] for r in cites.reason_category]
    # Horizontal stacked bar
    left = 0
    for share, color, reason in zip(shares, colors, cites.reason_category, strict=True):
        ax.barh(0, share, left=left, color=color, edgecolor="white",
                linewidth=0.5, height=0.4)
        ax.text(left + share/2, 0, f"{reason}\n{share:.1f}%",
                ha="center", va="center", fontsize=7, color="white")
        left += share
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.6, 0.6)
    ax.set_yticks([])
    ax.set_xlabel("Share of total post-retraction citation volume (%)")
    ax.set_title(f"A  Post-retraction citations by reason (total = {int(total):,})",
                 loc="left")

    # (B) Absolute citation volume comparison
    ax = axes[1]
    y = np.arange(len(cites))
    ax.barh(y, cites.total_post_cites, color=[COLOR[r] for r in cites.reason_category],
            edgecolor="white", linewidth=0.3)
    for i, (_, row) in enumerate(cites.iterrows()):
        ax.text(row.total_post_cites * 1.01, i,
                f"{int(row.total_post_cites):,}", va="center", fontsize=7)
    ax.set_yticks(y)
    ax.set_yticklabels(cites.reason_category)
    ax.set_xlabel("Post-retraction citations (absolute)")
    ax.set_title("B  Absolute post-retraction citation volume", loc="left")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, cites.total_post_cites.max() * 1.25)

    fig.tight_layout()
    save(fig, FIG / "fig3")


def fig4() -> None:
    """Fig 4. KM survival: (A) by reason, (B) matched-window 2000s vs 2010s null."""
    surv = pd.read_csv(DATA / "survival_analysis.tsv", sep="\t")

    # Merge reasons
    rp = pd.read_csv(DATA / "retracted_papers.tsv", sep=",", quotechar='"',
                     engine="python", on_bad_lines="skip")
    rp.columns = [c.strip() for c in rp.columns]
    rp["openalex_id_clean"] = rp.openalex_id.astype(str).str.strip().str.strip('"')
    rp["doi"] = rp.doi.astype(str).str.strip().str.strip('"').str.lower()

    # Classify reason via RW
    rw = pd.read_csv(ROOT / "data" / "raw" / "retraction_watch" /
                     "retraction-watch-data" / "retraction_watch.csv",
                     low_memory=False)
    rw["OriginalPaperDOI"] = rw.OriginalPaperDOI.astype(str).str.strip().str.lower()
    # Reuse classifier
    def cls(s):
        if pd.isna(s) or not s: return "Unknown"
        r = s.lower()
        if "paper mill" in r: return "Paper mill"
        if any(k in r for k in ["fabrication","falsification","plagiari","misconduct","fake peer","image manipulation"]):
            return "Misconduct"
        if any(k in r for k in ["error","calculat","reproducib","statistical","methodolog"]):
            return "Error"
        return "Other"
    rw["reason_category"] = rw.Reason.apply(cls)
    rp = rp.merge(rw[["OriginalPaperDOI", "reason_category"]].rename(
        columns={"OriginalPaperDOI": "doi"}), on="doi", how="left")
    rp["reason_category"] = rp.reason_category.fillna("Unknown")

    surv["retracted_id"] = surv.retracted_id.astype(str).str.strip()
    surv = surv.merge(rp[["openalex_id_clean", "reason_category"]].rename(
        columns={"openalex_id_clean": "retracted_id"}), on="retracted_id", how="left")
    surv["reason_category"] = surv.reason_category.fillna("Unknown")

    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE, 2.8))

    # (A) KM by reason (excluding Unknown)
    ax = axes[0]
    for reason in ORDER:
        grp = surv[surv.reason_category == reason]
        if len(grp) < 200: continue
        km = KaplanMeierFitter().fit(grp.time, grp.event,
                                      label=f"{reason} (n={len(grp):,})")
        km.plot_survival_function(ax=ax, ci_show=False,
                                   color=COLOR[reason], linewidth=1.1)
    ax.axhline(0.5, color="grey", linewidth=0.5, linestyle=":")
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Years since retraction")
    ax.set_ylabel("S(t): P(cites > 50% pre-retr. peak)")
    ax.set_title("A  Kaplan–Meier by reason", loc="left")
    ax.legend(frameon=False, loc="upper right", fontsize=6.5)

    # (B) Matched-window 2000s vs 2010s
    ax = axes[1]
    s2000 = surv[surv.decade == "2000s"].copy()
    s2010m = surv[(surv.decade == "2010s") & (surv.retraction_year <= 2015)].copy()
    # Cap at 10 years
    for d in [s2000, s2010m]:
        too_late = d.time > 10
        d.loc[too_late, "event"] = 0
        d.loc[too_late, "time"] = 10
    km1 = KaplanMeierFitter().fit(s2000.time, s2000.event,
                                    label=f"2000s (n={len(s2000)})")
    km1.plot_survival_function(ax=ax, color="#2c3e50", ci_show=True, linewidth=1.1)
    km2 = KaplanMeierFitter().fit(s2010m.time, s2010m.event,
                                    label=f"2010s mature (n={len(s2010m)})")
    km2.plot_survival_function(ax=ax, color="#c0392b", linestyle="--", ci_show=True, linewidth=1.1)
    res = logrank_test(s2000.time, s2010m.time, s2000.event, s2010m.event)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Years since retraction (10-yr matched window)")
    ax.set_ylabel("S(t)")
    ax.axhline(0.5, color="grey", linewidth=0.5, linestyle=":")
    ax.set_title(f"B  2000s vs 2010s: no acceleration (log-rank p={res.p_value:.3f})",
                 loc="left")
    ax.legend(frameon=False, loc="upper right", fontsize=6.5)

    fig.tight_layout()
    save(fig, FIG / "fig4")


def fig5() -> None:
    """Fig 5. Cross-field post-retraction citation rates (top 15) with paper-mill share overlay."""
    import csv
    # Field stats — try both possible separators
    try:
        fs = pd.read_csv(DATA / "field_stats.tsv", sep=",", engine="python")
    except Exception:
        fs = pd.read_csv(DATA / "field_stats.tsv", sep="\t", engine="python")
    fs.columns = [c.strip() for c in fs.columns]
    fs["field"] = fs["field"].astype(str).str.strip().str.strip('"')

    # Paper-mill share by field (from table_papermill_fields)
    pm = pd.read_csv(TABLES / "table_papermill_fields.tsv", sep="\t")
    pm["field"] = pm.field.str.strip()

    merged = fs.merge(pm[["field", "paper_mill_share"]], on="field", how="left")
    merged["retr_per_M"] = merged.retracted / merged.total * 1e6
    merged["paper_mill_share"] = merged.paper_mill_share.fillna(0)
    top = merged.nlargest(15, "retr_per_M").sort_values("retr_per_M").reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(DOUBLE, 3.8))
    # Horizontal bars: retraction rate
    y = np.arange(len(top))
    ax.barh(y, top.retr_per_M, color="#34495e", alpha=0.6,
            edgecolor="white", linewidth=0.3, label="Retractions per million papers")
    # Overlay paper-mill share as red segment (proportional)
    mill_counts = top.retr_per_M * top.paper_mill_share
    ax.barh(y, mill_counts, color="#c0392b", edgecolor="white", linewidth=0.3,
            label="Paper-mill component")

    for i, (_, row) in enumerate(top.iterrows()):
        ax.text(row.retr_per_M + 8, i,
                f"{int(row.retr_per_M)} ({row.paper_mill_share*100:.0f}% mill)",
                va="center", fontsize=6.5, color="#333")
    ax.set_yticks(y)
    ax.set_yticklabels(top.field, fontsize=7)
    ax.set_xlabel("Retractions per million papers (red = paper-mill share)")
    ax.set_title("Cross-field retraction rates with paper-mill decomposition (top 15)",
                 loc="left")
    ax.legend(frameon=False, loc="lower right", fontsize=7)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, top.retr_per_M.max() * 1.3)

    fig.tight_layout()
    save(fig, FIG / "fig5")


def main() -> None:
    print("Generating paper-mill PNAS figures…")
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    print("Done.")


if __name__ == "__main__":
    main()
