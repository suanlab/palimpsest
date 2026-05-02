#!/usr/bin/env python3
"""[B-CORE-event] Hindawi event-study citation curve.

For each Hindawi 2023-batch retraction, compute citation count as a function
of years relative to the retraction event year (-5 to +5). Compare against
matched controls and against Wiley/Elsevier regular retractions for the
same time period. The event-study plot is the headline figure of the paper.

Outputs:
  data/processed/track3/event_study.json
  docs/submissions/track3_pnas/figures/fig_event_study.{pdf,png}
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
    "font.family": "serif",
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 9,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.8, "lines.linewidth": 1.2,
})

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "retraction_watch" / "retraction-watch-data" / "retraction_watch.csv"
DATA = ROOT / "data" / "processed" / "track3"
FIG = ROOT / "docs" / "submissions" / "track3_pnas" / "figures"
FIG.mkdir(parents=True, exist_ok=True)


def main() -> None:
    print("Loading...")
    rw = pd.read_csv(RAW, low_memory=False)
    rw["DOI_norm"] = rw.OriginalPaperDOI.astype(str).str.strip().str.lower()
    rw["publisher_norm"] = rw.Publisher.fillna("Unknown").str.strip()
    rw["retract_year"] = pd.to_datetime(rw.RetractionDate, errors="coerce").dt.year
    rw_unique = rw.drop_duplicates(subset=["DOI_norm"], keep="first")

    # Build "publisher × retract_year" lookup keyed by openalex id
    rp = pd.read_csv(DATA / "retracted_papers.tsv", sep=",", quotechar='"',
                     engine="python", on_bad_lines="skip")
    rp.columns = [c.strip() for c in rp.columns]
    rp["doi"] = rp.doi.astype(str).str.strip().str.strip('"').str.lower()
    rp["openalex_id"] = rp.openalex_id.astype(str).str.strip().str.strip('"')
    rp = rp.drop_duplicates(subset=["doi"], keep="first")
    rp = rp.merge(
        rw_unique[["DOI_norm", "publisher_norm", "retract_year"]].rename(
            columns={"DOI_norm": "doi"}),
        on="doi", how="left",
    ).drop_duplicates(subset=["openalex_id"], keep="first")

    # contamination_1hop.tsv has per-citation rows: citing_id, citing_year,
    # retracted_id, retracted_year, citing_field. Aggregate to (retracted_id,
    # citing_year) → citation count.
    print("Loading contamination_1hop...")
    rows = pd.read_csv(DATA / "contamination_1hop.tsv", sep=",", quotechar='"',
                        engine="python", on_bad_lines="skip")
    rows.columns = [c.strip() for c in rows.columns]
    rows["retracted_id"] = rows.retracted_id.astype(str).str.strip().str.strip('"')
    rows["citing_year"] = pd.to_numeric(rows.citing_year, errors="coerce")
    print(f"  rows: {len(rows):,}, cols: {list(rows.columns)}")

    # Aggregate per-paper per-year citation count
    ymat = (rows.dropna(subset=["citing_year"])
                .groupby(["retracted_id", "citing_year"]).size()
                .reset_index(name="citation_count"))
    ymat["openalex_id"] = ymat.retracted_id

    # Attach publisher + retract_year
    ymat = ymat.merge(
        rp[["openalex_id", "publisher_norm", "retract_year"]],
        on="openalex_id", how="left",
    ).dropna(subset=["publisher_norm", "retract_year"])
    ymat["event_time"] = ymat["citing_year"] - ymat["retract_year"]
    cite_year_col = "citing_year"
    cnt_col = "citation_count"
    print(f"Aggregated to {len(ymat):,} (retracted_id, citing_year) rows.")

    # Define publisher groups
    groups = {
        "Hindawi (batch 2023)": (ymat.publisher_norm == "Hindawi") & (ymat.retract_year >= 2022),
        "Hindawi (regular pre-2022)": (ymat.publisher_norm == "Hindawi") & (ymat.retract_year < 2022),
        "Wiley (regular)": ymat.publisher_norm == "Wiley",
        "Elsevier (regular)": ymat.publisher_norm == "Elsevier",
        "Springer (regular)": ymat.publisher_norm == "Springer",
        "IEEE (immediate)": ymat.publisher_norm.str.startswith("IEEE"),
    }
    colors = {
        "Hindawi (batch 2023)": "#c0392b",
        "Hindawi (regular pre-2022)": "#e67e22",
        "Wiley (regular)": "#2980b9",
        "Elsevier (regular)": "#16a085",
        "Springer (regular)": "#7f8c8d",
        "IEEE (immediate)": "#34495e",
    }
    # Mean citations per paper per event-time bucket
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    rows_out = []
    for label, flt in groups.items():
        sub = ymat[flt].copy()
        sub = sub[(sub.event_time >= -5) & (sub.event_time <= 5)]
        if len(sub) == 0: continue
        # Per-paper average: aggregate by retracted_id × event_time, then average across papers
        per_paper = (sub.groupby(["retracted_id", "event_time"])[cnt_col]
                          .sum().reset_index())
        avg = per_paper.groupby("event_time")[cnt_col].mean().reindex(range(-5, 6), fill_value=0)
        ax.plot(avg.index, avg.values, "-o", color=colors[label],
                label=f"{label} (n={sub.retracted_id.nunique():,})",
                markersize=3.5, linewidth=1.3)
        for et, v in avg.items():
            rows_out.append({"group": label, "event_time": int(et),
                              "mean_citations": float(v)})

    ax.axvline(0, color="black", linewidth=0.6, linestyle="--", alpha=0.5)
    ax.set_xlabel("Years relative to retraction event")
    ax.set_ylabel("Mean annual citations per retracted paper")
    ax.set_title("Citation event-study: Hindawi batch retraction vs. regular publisher flow",
                 loc="left", fontsize=9)
    ax.legend(frameon=False, fontsize=7, loc="upper right")
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_event_study.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote fig_event_study.{{pdf,png}}")

    pd.DataFrame(rows_out).to_csv(DATA / "tables" / "table_event_study.tsv",
                                    sep="\t", index=False)
    out = {"event_study_curves": rows_out}
    (DATA / "event_study.json").write_text(json.dumps(out, indent=2))
    print(f"Wrote event_study.json")


if __name__ == "__main__":
    main()
