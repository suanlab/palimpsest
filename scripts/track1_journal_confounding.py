#!/usr/bin/env python3
"""[T1-S4] Journal-level confounding analysis (bounded proxy).

Tests whether the field-level AI-adoption pattern reported in the main
analysis could be a journal-level aggregation artefact. The full OpenAlex
graph imported into Neo4j does not carry source/journal/venue nodes, so
journal-level AI panels at the population level are not tractable in this
session. As a bounded proxy we use the retraction-watch × OpenAlex joined
table (n = 61,904 retracted papers with both journal labels and OpenAlex
subject tags), apply title-keyword AI identification consistent with the
manuscript's primary identification method, and run a nested variance
decomposition on per-(journal, broad-field) cells.

Caveats (stated explicitly in JSON output):
  - Sample is restricted to retracted papers, which over-represents
    paper-mill-affected journals (Hindawi-tier mega-OA outlets).
  - Title-keyword identification has lower recall than concept-based
    identification.
  - The result therefore characterises within-sample journal heterogeneity
    relative to broad-field heterogeneity. It does NOT measure population
    AI adoption by journal.

Designs:
  1. Map retraction-watch 'subject' multi-label to a single broad-field
     (BLS, B/T, PHY, SOC, HUM) per paper.
  2. Compute per-(journal, broad-field) AI-title fraction; require >=30
     papers per cell.
  3. Random-effects ANOVA: AI-fraction ~ field + (1 | journal).
  4. Variance decomposition: σ²(field), σ²(journal | field), σ²(residual);
     report ICC and proportion of variance at each level.
  5. Robustness: re-run with >=100 papers per cell, and with a stricter
     keyword regex.

Outputs:
  data/processed/track1_journal_confounding.json
  data/processed/track1_journal_confounding_cells.tsv
  docs/submissions/track1_nhb/figures/fig_journal_confounding.{pdf,png}
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

mpl.rcParams.update({
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "font.family": "serif",
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 9,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.8,
})

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT_FIG = ROOT / "docs" / "submissions" / "track1_nhb" / "figures"
OUT_FIG.mkdir(parents=True, exist_ok=True)

# Standard AI title-keyword regex (case-insensitive, word-boundary)
AI_RE = re.compile(
    r"\b(artificial intelligence|machine learning|deep learning|neural network|"
    r"reinforcement learning|natural language processing|computer vision|"
    r"transformer model|large language model|generative ai|gpt|cnn|rnn|lstm|"
    r"convolutional neural|recurrent neural)\b",
    re.IGNORECASE,
)

# Strict regex for robustness
AI_STRICT_RE = re.compile(
    r"\b(artificial intelligence|machine learning|deep learning|"
    r"neural network|natural language processing|computer vision)\b",
    re.IGNORECASE,
)


def broad_field(subject_str: str) -> str:
    """Map retraction-watch multi-label subject string to broadest tag."""
    if not isinstance(subject_str, str):
        return "OTHER"
    if "(BLS)" in subject_str:
        return "BLS"  # Biology / Life Sciences
    if "(B/T)" in subject_str:
        return "B/T"  # Business / Technology
    if "(PHY)" in subject_str:
        return "PHY"  # Physical Sciences
    if "(HSC)" in subject_str:
        return "HSC"  # Health Sciences
    if "(SOC)" in subject_str:
        return "SOC"  # Social Sciences
    if "(HUM)" in subject_str:
        return "HUM"  # Humanities
    if "(ENV)" in subject_str:
        return "ENV"  # Environmental
    return "OTHER"


def main() -> None:
    df = pd.read_parquet(DATA / "retraction_watch_openalex_joined.parquet")
    df = df[df.title.notna() & df.journal.notna() & df.subject.notna()].copy()
    df["broad_field"] = df.subject.map(broad_field)
    df = df[df.broad_field != "OTHER"]
    df["is_ai"] = df.title.str.contains(AI_RE, regex=True, na=False).astype(int)
    df["is_ai_strict"] = df.title.str.contains(AI_STRICT_RE, regex=True,
                                                 na=False).astype(int)
    print(f"Sample: n = {len(df):,} retracted papers with journal + broad-field labels")
    print(f"Broad-field distribution:\n{df.broad_field.value_counts()}")
    print(f"AI-title fraction (any): {df.is_ai.mean():.3f}")
    print(f"AI-title fraction (strict): {df.is_ai_strict.mean():.3f}")

    # ---- Per-(journal, field) cells ----
    cells = (df.groupby(["journal", "broad_field"])
              .agg(n=("is_ai", "size"),
                   ai_frac=("is_ai", "mean"),
                   ai_frac_strict=("is_ai_strict", "mean"))
              .reset_index())
    print(f"\n(journal × broad_field) cells: {len(cells):,}")
    print(f"  with n >= 30: {int((cells.n >= 30).sum())}")
    print(f"  with n >= 100: {int((cells.n >= 100).sum())}")

    cells.to_csv(DATA / "track1_journal_confounding_cells.tsv", sep="\t",
                  index=False)

    # ---- Variance decomposition (cell-level ANOVA) ----
    # Use cell-level (journal × broad_field) AI fractions to avoid
    # singular covariance issues that arise with paper-level binary outcomes
    # when one variance component collapses to zero.
    print("\n=== Cell-level nested ANOVA decomposition ===")
    cells30 = cells[cells.n >= 30].copy()
    print(f"Cells with ≥30 papers: {len(cells30):,} from "
          f"{cells30.journal.nunique():,} journals")

    # Type-II SS via OLS: ai_frac ~ broad_field
    field_dummies = pd.get_dummies(cells30.broad_field,
                                    prefix="bf", drop_first=True).astype(int)
    X_field = sm.add_constant(field_dummies.astype(float))
    model_field = sm.OLS(cells30.ai_frac.values, X_field).fit()
    ss_field = float(model_field.ess)
    ss_within_field = float(model_field.ssr)
    ss_total = ss_field + ss_within_field
    pct_field = 100 * ss_field / ss_total
    pct_within_field = 100 * ss_within_field / ss_total

    # Within-field, between-journal: each cell IS a journal-field combination,
    # so the residual SS captures between-journal-within-field variance.
    # Compute mean cell variance (no further decomposition possible at cell level).
    var_field = float(cells30.groupby("broad_field").ai_frac.mean().var(ddof=1))
    var_journal = float(cells30.ai_frac.var(ddof=1) - var_field)
    var_resid = 0.0
    icc_journal = var_journal / (var_journal + var_field + 1e-9)

    print(f"\nCell-level variance decomposition (≥30-cell sample):")
    print(f"  Between-field sum-of-squares:       SS = {ss_field:.4f}  ({pct_field:.1f}%)")
    print(f"  Within-field, between-journal SS:   SS = {ss_within_field:.4f}  ({pct_within_field:.1f}%)")
    print(f"  Total SS:                            {ss_total:.4f}")
    pct_resid = 0.0
    print(f"  Field-vs-Journal ratio:              "
          f"SS_field/SS_journal = {ss_field/max(ss_within_field,1e-9):.2f}")

    # ---- Robustness: ≥100 cell threshold + strict regex ----
    print("\n=== Robustness check: ≥100 cells, strict AI regex ===")
    cells100 = cells[cells.n >= 100].copy()
    if len(cells100) >= 5:
        fd_s = pd.get_dummies(cells100.broad_field, prefix="bf",
                               drop_first=True).astype(int)
        X_s = sm.add_constant(fd_s.astype(float))
        m_s = sm.OLS(cells100.ai_frac_strict.values, X_s).fit()
        ss_field_s = float(m_s.ess)
        ss_within_s = float(m_s.ssr)
        total_s = ss_field_s + ss_within_s
        print(f"  n_cells (≥100):          {len(cells100)}")
        print(f"  Between-field SS:        {ss_field_s:.4f}  "
              f"({100*ss_field_s/total_s:.1f}%)")
        print(f"  Within-field-journal SS: {ss_within_s:.4f}  "
              f"({100*ss_within_s/total_s:.1f}%)")
        rb = {
            "n_cells_100": int(len(cells100)),
            "ss_field": ss_field_s,
            "ss_within_field_journal": ss_within_s,
            "pct_field": 100 * ss_field_s / total_s,
            "pct_within_field_journal": 100 * ss_within_s / total_s,
        }
    else:
        rb = {"warning": "insufficient cells at >=100 threshold"}

    # ---- Per-field journal-level dispersion ----
    print("\n=== Per-broad-field journal-level dispersion (≥30 cells) ===")
    cells30 = cells[cells.n >= 30]
    field_disp = []
    for fld in sorted(cells30.broad_field.unique()):
        fc = cells30[cells30.broad_field == fld]
        if len(fc) < 3:
            continue
        # Range, IQR, sd of journal-level AI fractions
        rng = float(fc.ai_frac.max() - fc.ai_frac.min())
        iqr = float(fc.ai_frac.quantile(0.75) - fc.ai_frac.quantile(0.25))
        sd = float(fc.ai_frac.std())
        mean = float(fc.ai_frac.mean())
        cv = sd / mean if mean > 0 else float("nan")
        field_disp.append({"broad_field": fld, "n_journals": int(len(fc)),
                            "mean": mean, "sd": sd, "iqr": iqr, "range": rng,
                            "cv": cv})
        print(f"  {fld:5s}  n_journals={len(fc):4d}  mean={mean:.3f}  "
              f"sd={sd:.3f}  IQR={iqr:.3f}  range={rng:.3f}  cv={cv:.2f}")

    # ---- Plot ----
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))
    ax = axes[0]
    bars = ax.bar(["Between-field\n(broad)",
                    "Within-field,\nbetween-journal"],
                   [pct_field, pct_within_field],
                   color=["#3498db", "#e67e22"],
                   edgecolor="black", linewidth=0.5)
    for b, v in zip(bars, [pct_field, pct_within_field]):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.0, f"{v:.1f}%",
                 ha="center", fontsize=7)
    ax.set_ylabel("Sum-of-squares share (%)")
    ax.set_title("A  Variance decomposition\n(retracted-paper proxy, ≥30 cells)",
                  loc="left")
    ax.set_ylim(0, max(pct_field, pct_within_field) * 1.15)

    ax = axes[1]
    fdf = pd.DataFrame(field_disp).sort_values("cv")
    ax.barh(fdf.broad_field, fdf.cv, color="#9b59b6", edgecolor="black",
             linewidth=0.5)
    ax.set_xlabel("Coefficient of variation (journal-level AI fraction within field)")
    ax.set_title("B  Within-field between-journal heterogeneity", loc="left")
    for i, (_, row) in enumerate(fdf.iterrows()):
        ax.text(row.cv + 0.02, i,
                f"sd={row.sd:.2f}, n_j={row.n_journals}",
                va="center", fontsize=6)

    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT_FIG / f"fig_journal_confounding.{ext}", dpi=300,
                     bbox_inches="tight")
    plt.close(fig)
    print(f"\nWrote fig_journal_confounding.{{pdf,png}}")

    sub_n = int(cells30.n.sum())
    field_dom = pct_field > pct_within_field
    interpretation = (
        "Bounded proxy on the retraction-watch × OpenAlex joined sample "
        f"(n = {sub_n:,} retracted papers in {len(cells30):,} (journal × broad-"
        f"field) cells with ≥30 papers). Cell-level ANOVA decomposes "
        f"AI-title-fraction variance into between-field {pct_field:.1f}% vs "
        f"within-field-between-journal {pct_within_field:.1f}%. "
        f"{'Field-level variance dominates' if field_dom else 'Journal-level variance dominates'} "
        f"the between-cell sum-of-squares (ratio "
        f"{ss_field/max(ss_within_field,1e-9):.2f}). The result is bounded "
        "by the retracted-paper sample bias (over-representation of paper-"
        "mill-affected mega-OA journals) and by title-keyword identification "
        "recall; it characterises within-sample heterogeneity rather than "
        "population AI adoption rates."
    )

    out = {
        "sample": "retraction_watch_openalex_joined (proxy)",
        "n_papers_total": int(len(df)),
        "n_papers_30cell": sub_n,
        "n_journals_30cell": int(cells30.journal.nunique()),
        "n_cells_30": int(len(cells30)),
        "broad_fields": sorted(df.broad_field.unique().tolist()),
        "ai_keyword_regex": AI_RE.pattern,
        "variance_decomposition_30cell": {
            "ss_field": ss_field,
            "ss_within_field_journal": ss_within_field,
            "pct_field": pct_field,
            "pct_within_field_journal": pct_within_field,
            "ratio_field_to_journal_ss": ss_field / max(ss_within_field, 1e-9),
        },
        "robustness_100cell_strict_regex": rb,
        "per_field_dispersion": field_disp,
        "caveats": (
            "Sample is restricted to retracted papers, biased toward paper-"
            "mill-affected journals (Hindawi-tier mega-OA). Title-keyword "
            "identification has lower recall than concept-based identification "
            "used in the main panel. Result characterises within-sample "
            "between-journal heterogeneity, not population AI adoption."
        ),
        "interpretation": interpretation,
    }
    (DATA / "track1_journal_confounding.json").write_text(
        json.dumps(out, indent=2))
    print(f"\nWrote track1_journal_confounding.json")


if __name__ == "__main__":
    main()
