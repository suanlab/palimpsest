#!/usr/bin/env python3
"""T1-C: Biology subfield decomposition.

The original "Biology" in Track 1 main analysis is a Level-0 concept that
maps to four OpenAlex primary fields available in neo4j_field_panel:
  - Agricultural and Biological Sciences
  - Biochemistry, Genetics and Molecular Biology
  - Immunology and Microbiology
  - Neuroscience

We test whether the 2019 slope acceleration is concentrated in a specific
biology sub-community (e.g., Biochemistry/Genetics, where AlphaFold's
structural-biology impact is most direct) or diffused across all
biology-adjacent fields.

Outputs:
  data/processed/track1_biology_subfield.json
  docs/submissions/track1_nhb/figures/fig_biology_subfield.{pdf,png}
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
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.8,
})

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT_FIG = ROOT / "docs" / "submissions" / "track1_nhb" / "figures"
OUT_FIG.mkdir(parents=True, exist_ok=True)

BIO_SUBFIELDS = [
    "Agricultural and Biological Sciences",
    "Biochemistry, Genetics and Molecular Biology",
    "Immunology and Microbiology",
    "Neuroscience",
]
BREAK_YEAR = 2019
END_YEAR = 2023  # exclude 2024 (extraction artefact) and 2025 (incomplete)


def slope(x: np.ndarray, y: np.ndarray) -> dict:
    X = sm.add_constant(x)
    m = sm.OLS(y, X).fit()
    params = np.asarray(m.params)
    bse = np.asarray(m.bse)
    pv = np.asarray(m.pvalues)
    return {
        "slope": float(params[1]),
        "se": float(bse[1]),
        "p": float(pv[1]),
        "r2": float(m.rsquared),
        "n": int(len(y)),
    }


def main() -> None:
    df = pd.read_parquet(DATA / "neo4j_field_panel.parquet")
    df = df[df.year <= END_YEAR].copy()
    # Use concept-based AI fraction (broader, more complete)
    df["ai_pct"] = df.ai_concept_fraction * 100
    print(f"Panel: {len(df)} field-year obs across {df.field_name.nunique()} fields")

    fig, axes = plt.subplots(2, 2, figsize=(7.0, 5.2), sharey=False)
    fig.suptitle("Biology subfield decomposition: AI adoption before vs. after 2019",
                 fontsize=9, y=1.00)

    results = {}
    for ax, sub in zip(axes.flat, BIO_SUBFIELDS, strict=True):
        s = df[df.field_name == sub].sort_values("year").reset_index(drop=True)
        if len(s) < 10:
            ax.set_visible(False)
            continue
        y = s.ai_pct.values
        pre = s[s.year < BREAK_YEAR]
        post = s[s.year >= BREAK_YEAR]
        sl_pre = slope(np.arange(len(pre)), pre.ai_pct.values)
        sl_post = slope(np.arange(len(post)), post.ai_pct.values)
        ratio = sl_post["slope"] / sl_pre["slope"] if abs(sl_pre["slope"]) > 1e-6 else float("inf")

        ax.plot(s.year, y, "o-", color="black", markersize=3, linewidth=0.9)
        ax.axvline(BREAK_YEAR - 0.5, color="red", linewidth=0.7, linestyle="--")
        # Fit and plot pre/post linear trends
        xpre = pre.year.values
        xpost = post.year.values
        ax.plot(xpre, np.polyval(np.polyfit(range(len(pre)), pre.ai_pct, 1),
                                   range(len(pre))) if len(pre) >= 2 else [pre.ai_pct.mean()] * len(pre),
                color="#0077cc", linewidth=0.8, alpha=0.7)
        ax.plot(xpost, np.polyval(np.polyfit(range(len(post)), post.ai_pct, 1),
                                    range(len(post))) if len(post) >= 2 else [post.ai_pct.mean()] * len(post),
                color="#cc0000", linewidth=0.8, alpha=0.7)
        ax.set_title(f"{sub}\npre={sl_pre['slope']:.3f} pp/yr, post={sl_post['slope']:.3f} pp/yr ({ratio:.1f}×)",
                     loc="left", fontsize=7)
        ax.set_xlabel("Year")
        ax.set_ylabel("AI fraction (%)")

        results[sub] = {
            "pre_slope_pp_yr": sl_pre["slope"],
            "pre_p": sl_pre["p"],
            "post_slope_pp_yr": sl_post["slope"],
            "post_p": sl_post["p"],
            "acceleration_ratio": float(ratio),
            "n_pre": int(sl_pre["n"]),
            "n_post": int(sl_post["n"]),
        }
        print(f"{sub:45s} pre={sl_pre['slope']:+.3f} post={sl_post['slope']:+.3f} "
              f"ratio={ratio:+.2f}x")

    fig.tight_layout()
    fig.savefig(OUT_FIG / "fig_biology_subfield.pdf", dpi=300, bbox_inches="tight")
    fig.savefig(OUT_FIG / "fig_biology_subfield.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"\nwrote fig_biology_subfield.{{pdf,png}}")

    # Determine if acceleration is concentrated or diffused
    accel_ratios = {k: v["acceleration_ratio"] for k, v in results.items()}
    sorted_by_accel = sorted(accel_ratios.items(), key=lambda kv: -kv[1])
    diffused = all(v > 1.5 for v in accel_ratios.values())
    concentrated = (sorted_by_accel[0][1] / sorted_by_accel[-1][1]) > 3 if sorted_by_accel[-1][1] > 0 else True

    out = {
        "break_year": BREAK_YEAR,
        "subfield_slopes": results,
        "pattern": (
            "diffused" if diffused else
            "concentrated" if concentrated else
            "mixed"
        ),
        "interpretation": (
            "Post-2019 slope accelerations across biology-adjacent OpenAlex primary "
            "fields. Ratios compare (post-2019 slope) / (pre-2019 slope). A ratio >1 "
            "indicates acceleration; ratios near 1 indicate continuation; negative "
            "ratios indicate deceleration. The pattern determines whether the 2019 "
            "Biology acceleration is diffused (all subfields accelerate similarly) "
            "or concentrated (only specific subfields, e.g., Biochemistry/Genetics "
            "& Molecular Biology, accelerate, consistent with an AlphaFold-localised "
            "effect)."
        ),
    }
    (DATA / "track1_biology_subfield.json").write_text(json.dumps(out, indent=2))
    print(f"wrote track1_biology_subfield.json")


if __name__ == "__main__":
    main()
