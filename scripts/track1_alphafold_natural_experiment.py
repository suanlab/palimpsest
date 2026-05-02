#!/usr/bin/env python3
"""[T1-S2] AlphaFold 2020 natural experiment.

Tests whether the July 2020 AlphaFold2 announcement at CASP14 (and the
subsequent July 2021 *Nature* publication) produced a Biology-subfield-
specific surge in AI adoption that is not shared by quantitative
comparator fields. The Biochemistry/Genetics & Molecular Biology subfield
should be the most directly affected (protein-structure prediction is
its core methodology); Agricultural/Biological Sciences, Immunology, and
Neuroscience are progressively further from AlphaFold's core; Chemistry
and Physics are quantitative-methodology controls with no AlphaFold
dependence.

Designs:
  1. Subfield-stratified DID with event year 2020:
     - Treatment intensity ranked by AlphaFold proximity:
       * High: Biochemistry, Genetics and Molecular Biology
       * Medium: Agricultural and Biological Sciences (incl. plant biology)
       * Low: Immunology and Microbiology, Neuroscience
       * Control: Chemistry, Physics and Astronomy
     - Two-way FE DID; predicted ordering: high > medium > low > 0 ≈ control
  2. Event-study DID with k = -10..+3 to test parallel-trends.
  3. Synthetic Biochemistry control from {Chemistry, Physics, Mathematics}
     to construct counterfactual; effect = actual - synthetic.
  4. Triple-difference: (Biochem - Chemistry) post-2020 - (Biochem - Chemistry) pre-2020.
  5. Falsification: assign Chemistry as treated; verify null effect.

Outputs:
  data/processed/track1_alphafold_natural_experiment.json
  data/processed/track1_alphafold_panel.tsv
  docs/submissions/track1_nhb/figures/fig_alphafold_naturalexp.{pdf,png}
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.optimize import minimize

mpl.rcParams.update({
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "font.family": "serif",
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 9,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.8, "lines.linewidth": 1.2,
})

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT_FIG = ROOT / "docs" / "submissions" / "track1_nhb" / "figures"
OUT_FIG.mkdir(parents=True, exist_ok=True)

EVENT_YEAR = 2020  # July 2020: AlphaFold2 wins CASP14
YEAR_LO = 2005
YEAR_HI = 2023  # exclude 2024 (extraction artefact) + 2025

# Treatment intensity ranking
TREAT_HIGH = ["Biochemistry, Genetics and Molecular Biology"]
TREAT_MED = ["Agricultural and Biological Sciences"]
TREAT_LOW = ["Immunology and Microbiology", "Neuroscience"]
CTRL = ["Chemistry", "Physics and Astronomy"]
PLACEBO_TREAT = "Chemistry"


def slope_change(yrs: np.ndarray, vals: np.ndarray, brk: int) -> dict:
    pre = vals[yrs < brk]
    post = vals[yrs >= brk]
    pre_yrs = yrs[yrs < brk]
    post_yrs = yrs[yrs >= brk]
    pre_slope = np.polyfit(pre_yrs, pre, 1)[0] if len(pre) >= 2 else 0.0
    post_slope = np.polyfit(post_yrs, post, 1)[0] if len(post) >= 2 else 0.0
    return {"pre_slope": float(pre_slope), "post_slope": float(post_slope),
            "ratio": float(post_slope / pre_slope) if abs(pre_slope) > 1e-9
                    else float("inf")}


def did_two_way_fe(panel: pd.DataFrame, treat_set: list[str],
                    event_year: int, ctrl_set: list[str]) -> dict:
    sub = panel[panel.field_name.isin(treat_set + ctrl_set)].copy()
    sub["treat"] = sub.field_name.isin(treat_set).astype(int)
    sub["post"] = (sub.year >= event_year).astype(int)
    sub["did"] = sub.treat * sub.post
    f_d = pd.get_dummies(sub.field_name, prefix="f", drop_first=True).astype(int)
    y_d = pd.get_dummies(sub.year, prefix="y", drop_first=True).astype(int)
    X = pd.concat([sub[["did"]], f_d, y_d], axis=1)
    X = sm.add_constant(X.astype(float))
    m = sm.OLS(sub.ai_pct, X).fit(cov_type="HC3")
    return {
        "did_pp": float(m.params["did"]),
        "se_pp": float(m.bse["did"]),
        "p": float(m.pvalues["did"]),
        "ci_lo": float(m.params["did"] - 1.96 * m.bse["did"]),
        "ci_hi": float(m.params["did"] + 1.96 * m.bse["did"]),
        "n_obs": int(len(sub)),
    }


def main() -> None:
    df = pd.read_parquet(DATA / "neo4j_field_panel.parquet")
    df = df[(df.year >= YEAR_LO) & (df.year <= YEAR_HI)].copy()
    df["ai_pct"] = df.ai_concept_fraction * 100

    use_fields = TREAT_HIGH + TREAT_MED + TREAT_LOW + CTRL + ["Mathematics"]
    panel = df[df.field_name.isin(use_fields)].copy()
    print(f"Panel: {len(panel)} field-year obs across {panel.field_name.nunique()} fields, "
          f"{YEAR_LO}-{YEAR_HI}")
    panel.to_csv(DATA / "track1_alphafold_panel.tsv", sep="\t", index=False)

    # ---- 1. Slope change per intensity level ----
    print("\n=== Pre/post-2020 slope changes per AlphaFold intensity tier ===")
    intensity_results = {}
    for tier_name, fields in [("HIGH", TREAT_HIGH), ("MEDIUM", TREAT_MED),
                                ("LOW", TREAT_LOW), ("CONTROL", CTRL)]:
        tier_rows = []
        for fld in fields:
            s = panel[panel.field_name == fld].sort_values("year")
            sl = slope_change(s.year.values, s.ai_pct.values, EVENT_YEAR)
            sl["field"] = fld
            tier_rows.append(sl)
            print(f"  [{tier_name:7s}] {fld:50s} pre={sl['pre_slope']:+.3f} pp/yr  "
                  f"post={sl['post_slope']:+.3f} pp/yr  ratio={sl['ratio']:+.2f}×")
        intensity_results[tier_name] = tier_rows

    # ---- 2. Two-way FE DID per intensity tier vs control ----
    print("\n=== Two-way FE DID per tier vs Chemistry+Physics control ===")
    tier_dids = {}
    for tier_name, fields in [("HIGH", TREAT_HIGH), ("MEDIUM", TREAT_MED),
                                ("LOW", TREAT_LOW)]:
        d = did_two_way_fe(panel, fields, EVENT_YEAR, CTRL)
        tier_dids[tier_name] = d
        print(f"  [{tier_name:7s}] DID = {d['did_pp']:+.3f} pp "
              f"(SE {d['se_pp']:.3f}, p {d['p']:.4f}, "
              f"95% CI [{d['ci_lo']:+.3f}, {d['ci_hi']:+.3f}], n={d['n_obs']})")

    # Combined Biology-vs-control DID (high+med+low pooled)
    pooled = TREAT_HIGH + TREAT_MED + TREAT_LOW
    d_pool = did_two_way_fe(panel, pooled, EVENT_YEAR, CTRL)
    print(f"  [POOLED ] DID = {d_pool['did_pp']:+.3f} pp (p {d_pool['p']:.4f})")

    # ---- 3. Event-study (Biochem vs Chemistry+Physics) ----
    print("\n=== Event-study DID (Biochem vs Chemistry+Physics, year-by-year) ===")
    es = (panel[panel.field_name.isin(TREAT_HIGH + CTRL)]
          .groupby(["field_name", "year"])["ai_pct"].mean().reset_index())
    es_pivot = es.pivot(index="year", columns="field_name", values="ai_pct")
    biochem_col = TREAT_HIGH[0]
    es_pivot["control_mean"] = es_pivot[CTRL].mean(axis=1)
    es_pivot["diff"] = es_pivot[biochem_col] - es_pivot["control_mean"]
    es_pivot["years_from_event"] = es_pivot.index - EVENT_YEAR
    es_rows = [{"year": int(y),
                "years_from_event": int(y - EVENT_YEAR),
                "biochem_rate": float(es_pivot.loc[y, biochem_col]),
                "control_rate": float(es_pivot.loc[y, "control_mean"]),
                "diff": float(es_pivot.loc[y, "diff"])}
                for y in es_pivot.index]
    es_df = pd.DataFrame(es_rows)
    print(es_df.to_string(index=False, float_format="%.3f"))
    pre = es_df[es_df.years_from_event < 0]
    pre_slope = np.polyfit(pre.years_from_event.values, pre["diff"].values, 1)[0]
    print(f"\nPre-2020 trend slope (Biochem - control): {pre_slope:+.4f} pp/yr "
          "(should be ~0 if parallel-trends)")

    # ---- 4. Synthetic Biochemistry control ----
    print("\n=== Synthetic Biochemistry control ===")
    pivot = (panel[panel.field_name.isin([biochem_col] + CTRL + ["Mathematics"])]
                  .pivot(index="year", columns="field_name", values="ai_pct"))
    bio_actual = pivot[biochem_col]
    donor_cols = [c for c in pivot.columns if c != biochem_col]
    donors = pivot[donor_cols].ffill().bfill()
    pre_yrs = [y for y in pivot.index if y < EVENT_YEAR
                and not np.isnan(bio_actual.loc[y])]

    def loss(w, donor_pre, b_pre):
        return float(np.sum((donor_pre @ w - b_pre) ** 2))

    n_donors = donors.shape[1]
    res = minimize(loss, np.ones(n_donors) / n_donors,
                   args=(donors.loc[pre_yrs].values, bio_actual.loc[pre_yrs].values),
                   method="SLSQP",
                   bounds=[(0.0, 1.0)] * n_donors,
                   constraints=({"type": "eq",
                                  "fun": lambda w: np.sum(w) - 1.0},))
    weights = res.x
    synth_series = pd.Series(donors.values @ weights, index=donors.index,
                              name="synthetic")
    print("Weights:")
    for d, w in zip(donors.columns, weights):
        if w > 0.005:
            print(f"  {d:30s} {w:.3f}")
    pre_rmse = float(np.sqrt(np.mean(
        (synth_series.loc[pre_yrs].values - bio_actual.loc[pre_yrs].values) ** 2)))
    print(f"Pre-event RMSE: {pre_rmse:.4f} pp")

    eff_rows = []
    for py in [y for y in pivot.index if y >= EVENT_YEAR]:
        if py in bio_actual.index:
            eff = float(bio_actual.loc[py] - synth_series.loc[py])
            eff_rows.append({"year": int(py),
                              "actual_biochem": float(bio_actual.loc[py]),
                              "synthetic": float(synth_series.loc[py]),
                              "effect_pp": eff})
            print(f"  {py}: actual {bio_actual.loc[py]:.3f}, "
                  f"synthetic {synth_series.loc[py]:.3f}, "
                  f"effect {eff:+.3f} pp")
    mean_post_eff = float(np.mean([r["effect_pp"] for r in eff_rows]))
    final_year_eff = eff_rows[-1]["effect_pp"] if eff_rows else 0.0

    # ---- 5. Falsification: Chemistry as treated ----
    print(f"\n=== Falsification: assign {PLACEBO_TREAT} as treated ===")
    p_ctrl = [c for c in CTRL if c != PLACEBO_TREAT] + ["Mathematics"]
    placebo_d = did_two_way_fe(panel, [PLACEBO_TREAT], EVENT_YEAR, p_ctrl)
    print(f"  Placebo DID = {placebo_d['did_pp']:+.3f} pp "
          f"(p {placebo_d['p']:.4f}, n {placebo_d['n_obs']})")

    # ---- Plot ----
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))

    # Panel A: trajectories
    ax = axes[0]
    palette = {biochem_col: "#c0392b",
                TREAT_MED[0]: "#e67e22",
                TREAT_LOW[0]: "#f1c40f",
                TREAT_LOW[1]: "#9b59b6",
                CTRL[0]: "#3498db",
                CTRL[1]: "#1abc9c"}
    for fld in TREAT_HIGH + TREAT_MED + TREAT_LOW + CTRL:
        s = panel[panel.field_name == fld].sort_values("year")
        col = palette.get(fld, "grey")
        lw = 1.8 if fld == biochem_col else 0.9
        ax.plot(s.year, s.ai_pct, "-", color=col, linewidth=lw,
                label=fld[:30] + ("…" if len(fld) > 30 else ""))
    ax.plot(synth_series.index, synth_series.values, "--", color="black",
            linewidth=1.2, label="Synthetic Biochem")
    ax.axvline(EVENT_YEAR - 0.5, color="grey", linestyle=":", linewidth=0.6)
    ax.set_xlabel("Year")
    ax.set_ylabel("AI fraction (%)")
    ax.set_title("A  AlphaFold 2020: subfield trajectories", loc="left")
    ax.legend(frameon=False, fontsize=5.5, loc="upper left")

    # Panel B: tier-DID dose-response
    ax = axes[1]
    tiers = ["HIGH", "MEDIUM", "LOW"]
    dids = [tier_dids[t]["did_pp"] for t in tiers]
    errs = [1.96 * tier_dids[t]["se_pp"] for t in tiers]
    ps = [tier_dids[t]["p"] for t in tiers]
    bars = ax.bar(tiers, dids, yerr=errs, capsize=4,
                   color=["#c0392b", "#e67e22", "#f1c40f"], alpha=0.85,
                   edgecolor="black", linewidth=0.5)
    ax.axhline(0, color="grey", linewidth=0.5, linestyle=":")
    # Annotate p-values
    for b, p, d in zip(bars, ps, dids):
        ax.text(b.get_x() + b.get_width() / 2, d + (0.15 if d >= 0 else -0.15),
                f"p={p:.3f}", ha="center", va="bottom" if d >= 0 else "top",
                fontsize=6.5)
    # Add placebo line
    ax.axhline(placebo_d["did_pp"], color="black", linestyle="--",
                linewidth=0.6,
                label=f"Placebo ({PLACEBO_TREAT}): {placebo_d['did_pp']:+.3f} pp")
    ax.set_xlabel("AlphaFold proximity tier")
    ax.set_ylabel("DID coefficient (pp)")
    ax.set_title("B  Dose–response by AlphaFold proximity", loc="left")
    ax.legend(frameon=False, loc="upper right", fontsize=6)
    ax.text(0.02, 0.96,
            f"Synth Biochem 2023 effect = {final_year_eff:+.3f} pp\n"
            f"Pre-2020 (Biochem−ctrl) slope = {pre_slope:+.3f} pp/yr",
            transform=ax.transAxes, va="top", fontsize=6,
            bbox=dict(facecolor="white", edgecolor="grey", lw=0.4))

    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT_FIG / f"fig_alphafold_naturalexp.{ext}",
                    dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"\nWrote fig_alphafold_naturalexp.{{pdf,png}}")

    # ---- Determine pattern ----
    high_did = tier_dids["HIGH"]["did_pp"]
    med_did = tier_dids["MEDIUM"]["did_pp"]
    low_did = tier_dids["LOW"]["did_pp"]
    monotonic = high_did >= med_did >= low_did
    high_sig = tier_dids["HIGH"]["p"] < 0.05
    pattern = (
        "supports AlphaFold-causal hypothesis: monotonic dose-response "
        "with significant high-tier effect"
        if (monotonic and high_sig) else
        "partial support: monotonic but non-significant high-tier"
        if monotonic else
        "does not support AlphaFold-causal hypothesis: "
        "non-monotonic across proximity tiers"
    )

    out = {
        "event_year": EVENT_YEAR,
        "treatment_intensity_tiers": {
            "HIGH": TREAT_HIGH,
            "MEDIUM": TREAT_MED,
            "LOW": TREAT_LOW,
            "CONTROL": CTRL,
        },
        "slope_changes": intensity_results,
        "tier_did": tier_dids,
        "pooled_biology_did": d_pool,
        "event_study_yearly": es_rows,
        "pre_2020_slope_diff_pp_per_yr": float(pre_slope),
        "synthetic_biochem_weights": {
            col: float(w) for col, w in zip(donors.columns, weights)
        },
        "synthetic_pre_event_rmse_pp": pre_rmse,
        "synthetic_mean_post_effect_pp": mean_post_eff,
        "synthetic_2023_effect_pp": float(final_year_eff),
        "synthetic_yearly_effects": eff_rows,
        "placebo_chemistry_did": placebo_d,
        "monotonic_dose_response": bool(monotonic),
        "pattern": pattern,
        "interpretation": (
            f"AlphaFold 2020 natural experiment with treatment-intensity "
            f"ranking (HIGH=Biochem, MED=Ag/Bio, LOW=Immunology/Neuroscience) "
            f"vs Chemistry+Physics control. Tier DIDs: HIGH={high_did:+.3f} "
            f"(p={tier_dids['HIGH']['p']:.3f}), MED={med_did:+.3f} "
            f"(p={tier_dids['MEDIUM']['p']:.3f}), LOW={low_did:+.3f} "
            f"(p={tier_dids['LOW']['p']:.3f}). Synthetic Biochemistry control "
            f"(weights: {', '.join(f'{d}={w:.2f}' for d, w in zip(donors.columns, weights) if w > 0.05)}) "
            f"projects 2023 effect of {final_year_eff:+.3f} pp. Placebo "
            f"(Chemistry as treated) yields {placebo_d['did_pp']:+.3f} pp "
            f"(p={placebo_d['p']:.3f}). Pattern: {pattern}."
        ),
    }
    (DATA / "track1_alphafold_natural_experiment.json").write_text(
        json.dumps(out, indent=2))
    print(f"\nWrote track1_alphafold_natural_experiment.json")


if __name__ == "__main__":
    main()
