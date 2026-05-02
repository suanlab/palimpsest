#!/usr/bin/env python3
"""Figure redesign v2 — publication-grade figures for all three papers.

Design principles:
  - Sans-serif headers (Helvetica-family), serif body for body text
  - Color-blind-friendly palette (viridis-derived)
  - Direct labelling instead of legend boxes where possible
  - Fewer axis ticks, larger labels
  - 300 DPI PDF + PNG; fonttype=42 (TrueType)
  - Consistent 3.5" single / 7.0" double column widths
  - Grayscale-robust linestyles

Outputs (regenerates selected figures only; rest left to generate_pnas_figures.py):
  docs/submissions/track3_pnas/figures/fig3_v2.{pdf,png}
  docs/submissions/track3_pnas/figures/fig5_v2.{pdf,png}
  docs/submissions/track1_nhb/figures/fig_great_divergence.{pdf,png}
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

mpl.rcParams.update({
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "font.family": ["DejaVu Sans", "Liberation Sans", "Arial"],
    "font.size": 9, "axes.labelsize": 9, "axes.titlesize": 10,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.9, "xtick.major.size": 3, "ytick.major.size": 3,
    "xtick.major.width": 0.8, "ytick.major.width": 0.8,
    "lines.linewidth": 1.4, "patch.linewidth": 0.5,
})

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
T3_FIG = ROOT / "docs" / "submissions" / "track3_pnas" / "figures"
T1_FIG = ROOT / "docs" / "submissions" / "track1_nhb" / "figures"
for d in (T3_FIG, T1_FIG):
    d.mkdir(parents=True, exist_ok=True)

# Viridis-derived palette (color-blind friendly)
PAL = {"primary": "#222831", "accent1": "#1b7837", "accent2": "#762a83",
       "accent3": "#d95f0e", "grey": "#888888", "light": "#cccccc"}


def save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path.with_suffix(".pdf"), dpi=300, bbox_inches="tight")
    fig.savefig(path.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {path.name}.{{pdf,png}}")


def _read_comma(name: str) -> pd.DataFrame:
    df = pd.read_csv(DATA / "track3" / name, sep=",", quotechar='"',
                      engine="python", on_bad_lines="skip")
    df.columns = [c.strip() for c in df.columns]
    return df


def fig3_v2() -> None:
    """Track 3 Fig 3 — matched-control zombie distribution, redesigned."""
    pairs = pd.read_csv(DATA / "track3" / "matched_controls_pairs.tsv", sep="\t")
    fig, ax = plt.subplots(figsize=(3.5, 2.7))

    retr_frac = pairs.retracted_post_retraction_fraction.dropna().values
    ax.hist(retr_frac, bins=40, color=PAL["primary"], edgecolor="white",
            linewidth=0.3, alpha=0.85)
    mean_retr = retr_frac.mean()
    ctrl_mean = pairs.control_zombie.mean()
    ax.axvline(mean_retr, color=PAL["accent3"], linewidth=1.4)
    ax.axvline(ctrl_mean, color=PAL["accent1"], linewidth=1.4, linestyle="--")
    # Direct labels (no legend)
    ax.text(mean_retr + 0.02, ax.get_ylim()[1] * 0.90,
            f"Retracted mean\n{mean_retr:.2f}", color=PAL["accent3"], fontsize=7.5, va="top")
    ax.text(ctrl_mean - 0.15, ax.get_ylim()[1] * 0.70,
            f"Control\nzombie rate\n{ctrl_mean:.2f}", color=PAL["accent1"], fontsize=7.5, va="top")
    ax.axvline(0.5, color=PAL["grey"], linewidth=0.6, linestyle=":")
    ax.set_xlim(0, 1)
    ax.set_xlabel("Post-retraction citation fraction")
    ax.set_ylabel("Matched pairs (of 64,458)")
    ax.set_title("Retracted-paper distribution diverges from matched controls",
                 loc="left", fontsize=9)
    save(fig, T3_FIG / "fig3_v2")


def fig5_v2() -> None:
    """Track 3 Fig 5 — cross-field contamination, redesigned."""
    fs = _read_comma("field_stats.tsv")
    fs["retr_per_M"] = fs.retracted / fs.total * 1e6
    top = fs.nlargest(15, "retr_per_M").sort_values("retr_per_M").reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    colors = [PAL["accent3"] if r.retr_per_M >= 500 else
              PAL["primary"] if r.retr_per_M >= 300 else PAL["grey"]
              for _, r in top.iterrows()]
    ax.barh(top.field, top.retr_per_M, color=colors, edgecolor="white",
            linewidth=0.4)
    for i, r in top.iterrows():
        ax.text(r.retr_per_M + 5, i, f"{int(r.retr_per_M)}", va="center",
                fontsize=7.5, color=PAL["primary"])
    ax.set_xlabel("Retractions per million papers")
    ax.set_title("Cross-field retraction rates (top 15 fields, 2000–2024)",
                 loc="left", fontsize=10)
    ax.set_xlim(0, top.retr_per_M.max() * 1.12)
    # Remove y-axis spine
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    save(fig, T3_FIG / "fig5_v2")


def fig_great_divergence() -> None:
    """Track 1 headline figure — AI adoption timeline, 4 groups, direct-labelled."""
    df = pd.read_parquet(DATA / "ai_adoption_by_field.parquet")
    df = df[df.year <= 2023].copy()
    df["ai_pct"] = df.ai_fraction * 100

    groups = {
        "High baseline (22–22%)": (["Computer Science", "Mathematics"], PAL["accent2"]),
        "Moderate: fast-growing": (["Biology", "Physics", "Geology"], PAL["accent1"]),
        "Moderate: slow": (["Psychology", "Economics", "Engineering"], PAL["primary"]),
        "Low: stagnant": (["Medicine", "Chemistry", "Environmental Science",
                            "Materials Science"], PAL["accent3"]),
    }

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.2))

    # Left: all 15 fields colored by group
    ax = axes[0]
    for label, (fields, color) in groups.items():
        for f in fields:
            s = df[df.field_name == f].sort_values("year")
            ax.plot(s.year, s.ai_pct, color=color, alpha=0.85, linewidth=1.2)
    # Direct-label the outlier at right edge
    ymax_field_year = {}
    for label, (fields, color) in groups.items():
        for f in fields:
            s = df[df.field_name == f].sort_values("year").tail(1)
            if not s.empty:
                ymax_field_year[f] = (int(s.year.iloc[0]), float(s.ai_pct.iloc[0]), color)
    for f in ["Computer Science", "Biology", "Medicine", "Environmental Science"]:
        yr, v, c = ymax_field_year[f]
        ax.text(yr + 0.5, v, f, color=c, fontsize=7, va="center")

    ax.set_xlabel("Year")
    ax.set_ylabel("AI publication fraction (%)")
    ax.set_xlim(2000, 2026)
    ax.set_title("A  15 fields, 2000–2023", loc="left")

    # Right: four-group summary bar
    ax = axes[1]
    labels_list, recents, early_list, colors_list = [], [], [], []
    for label, (fields, color) in groups.items():
        recent_vals = [df[(df.field_name == f) & (df.year >= 2015) & (df.year <= 2023)].ai_pct.mean()
                        for f in fields]
        early_vals = [df[(df.field_name == f) & (df.year >= 2005) & (df.year < 2015)].ai_pct.mean()
                       for f in fields]
        labels_list.append(label)
        recents.append(np.nanmean(recent_vals))
        early_list.append(np.nanmean(early_vals))
        colors_list.append(color)

    y_pos = np.arange(len(labels_list))
    h = 0.35
    ax.barh(y_pos - h/2, early_list, h, color=colors_list,
            edgecolor="white", linewidth=0.3, alpha=0.55, label="2005–2014")
    ax.barh(y_pos + h/2, recents, h, color=colors_list,
            edgecolor="white", linewidth=0.3, label="2015–2023")
    for i, (e, r) in enumerate(zip(early_list, recents, strict=False)):
        ax.text(r + 0.3, i + h/2, f"{r:.1f}%", fontsize=7.5, va="center",
                color=PAL["primary"])
        ax.text(e + 0.3, i - h/2, f"{e:.1f}%", fontsize=7.5, va="center",
                color=PAL["grey"])
    ax.set_yticks(y_pos); ax.set_yticklabels(labels_list, fontsize=7.5)
    ax.set_xlabel("Mean AI fraction (%)")
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    ax.set_title("B  Group means: early vs. recent period", loc="left")

    fig.tight_layout()
    save(fig, T1_FIG / "fig_great_divergence")


def main() -> None:
    print("Regenerating key figures with v2 design...")
    fig3_v2()
    fig5_v2()
    fig_great_divergence()
    print("Done.")


if __name__ == "__main__":
    main()
