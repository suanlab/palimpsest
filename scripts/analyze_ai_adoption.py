#!/usr/bin/env python3
"""Analyze AI adoption dynamics across scientific fields.

This script reads AI adoption panel data, computes four analyses, writes structured
JSON results, and prints concise summary tables.
"""
# pyright: basic, reportMissingImports=false

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

INPUT_PATH = Path("data/processed/ai_adoption_by_field.parquet")
OUTPUT_PATH = Path("data/processed/ai_adoption_analysis.json")

ANALYSIS_START_YEAR = 2000
ANALYSIS_END_YEAR = 2024
EARLY_START = 2005
EARLY_END = 2014
RECENT_START = 2015
RECENT_END = 2024
ONSET_THRESHOLD_PCT_POINTS = 0.5

TREATMENT_FIELDS = {
    "Computer Science",
    "Mathematics",
    "Engineering",
}
CONTROL_FIELDS = {
    "Medicine",
    "Psychology",
    "Political Science",
}

DID_PRE_START = 2000
DID_PRE_END = 2014
DID_POST_START = 2015
DID_POST_END = 2024


def load_and_prepare_data(input_path: Path) -> pd.DataFrame:
    df = pd.read_parquet(input_path)

    required_columns = {
        "field_id",
        "field_name",
        "year",
        "total_count",
        "ai_count",
        "ai_fraction",
    }
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        missing_sorted = sorted(missing_columns)
        raise ValueError(f"Missing required columns: {missing_sorted}")

    df = df.copy()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df = df[df["year"].between(ANALYSIS_START_YEAR, ANALYSIS_END_YEAR)]
    df = df.dropna(subset=["year", "field_name", "field_id"]).copy()
    df["year"] = df["year"].astype(int)

    df["total_count"] = pd.to_numeric(df["total_count"], errors="coerce").fillna(0)
    df["ai_count"] = pd.to_numeric(df["ai_count"], errors="coerce").fillna(0)
    df["ai_fraction"] = pd.to_numeric(df["ai_fraction"], errors="coerce")

    fallback_fraction = np.where(
        df["total_count"] > 0,
        df["ai_count"] / df["total_count"],
        0.0,
    )
    df["ai_fraction"] = df["ai_fraction"].fillna(
        pd.Series(fallback_fraction, index=df.index)
    )
    df["ai_fraction"] = df["ai_fraction"].clip(lower=0.0, upper=1.0)

    year_index = pd.Index(
        range(ANALYSIS_START_YEAR, ANALYSIS_END_YEAR + 1), name="year"
    )
    panel_frames: list[pd.DataFrame] = []

    for (field_id, field_name), group in df.groupby(
        ["field_id", "field_name"], sort=True
    ):
        field_id_value = str(field_id)
        field_name_value = str(field_name)
        base = group.set_index("year").sort_index()
        reindexed = base.reindex(year_index)
        reindexed["field_id"] = field_id_value
        reindexed["field_name"] = field_name_value
        reindexed["total_count"] = reindexed["total_count"].fillna(0)
        reindexed["ai_count"] = reindexed["ai_count"].fillna(0)
        reindexed["ai_fraction"] = reindexed["ai_fraction"].fillna(0.0)
        panel_frames.append(reindexed.reset_index())

    panel_df = pd.concat(panel_frames, ignore_index=True)
    return panel_df


def analyze_adoption_acceleration(df: pd.DataFrame) -> dict[str, Any]:
    field_stats: list[dict[str, Any]] = []

    for field_name, group in df.groupby("field_name", sort=True):
        early_mask = group["year"].between(EARLY_START, EARLY_END)
        recent_mask = group["year"].between(RECENT_START, RECENT_END)

        early_avg = float(group.loc[early_mask, "ai_fraction"].mean())
        recent_avg = float(group.loc[recent_mask, "ai_fraction"].mean())
        absolute_change = recent_avg - early_avg

        if early_avg > 0:
            fold_increase = recent_avg / early_avg
        elif recent_avg > 0:
            fold_increase = None
        else:
            fold_increase = 0.0

        field_stats.append(
            {
                "field_name": field_name,
                "early_period_avg_ai_fraction": early_avg,
                "recent_period_avg_ai_fraction": recent_avg,
                "absolute_change": absolute_change,
                "fold_increase": fold_increase,
            },
        )

    ranked = sorted(field_stats, key=lambda row: row["absolute_change"], reverse=True)
    for rank, row in enumerate(ranked, start=1):
        row["rank_by_acceleration"] = rank

    return {
        "periods": {
            "early": [EARLY_START, EARLY_END],
            "recent": [RECENT_START, RECENT_END],
        },
        "ranked_fields": ranked,
    }


def analyze_adoption_onset(df: pd.DataFrame) -> dict[str, Any]:
    field_results: list[dict[str, Any]] = []

    for field_name, group in df.groupby("field_name", sort=True):
        series = group.sort_values("year")[["year", "ai_fraction"]].copy()
        series["yoy_change_pct_points"] = series["ai_fraction"].diff() * 100
        series["rolling_3y_avg_change_pct_points"] = (
            series["yoy_change_pct_points"].rolling(window=3, min_periods=3).mean()
        )

        onset_mask = (
            series["rolling_3y_avg_change_pct_points"] >= ONSET_THRESHOLD_PCT_POINTS
        )
        onset_year: int | None
        if onset_mask.any():
            onset_year = int(series.loc[onset_mask, "year"].iloc[0])
        else:
            onset_year = None

        max_rolling = float(series["rolling_3y_avg_change_pct_points"].max(skipna=True))
        if np.isnan(max_rolling):
            max_rolling = 0.0

        field_results.append(
            {
                "field_name": field_name,
                "inflection_year": onset_year,
                "threshold_pct_points_per_year": ONSET_THRESHOLD_PCT_POINTS,
                "max_rolling_3y_avg_change_pct_points": max_rolling,
            },
        )

    detected = [r for r in field_results if r["inflection_year"] is not None]
    detected_sorted = sorted(detected, key=lambda r: int(r["inflection_year"]))

    return {
        "method": "First year where 3-year rolling average of YoY AI-fraction change exceeds threshold.",
        "threshold_pct_points_per_year": ONSET_THRESHOLD_PCT_POINTS,
        "field_results": field_results,
        "detection_order": [
            {"field_name": r["field_name"], "inflection_year": r["inflection_year"]}
            for r in detected_sorted
        ],
    }


def _pearson_with_guard(
    x: np.ndarray, y: np.ndarray
) -> tuple[float | None, float | None]:
    if x.size < 2 or y.size < 2:
        return None, None
    if np.isclose(float(np.std(x)), 0.0) or np.isclose(float(np.std(y)), 0.0):
        return None, None

    corr, p_value = stats.pearsonr(x, y)
    return float(corr), float(p_value)


def analyze_cross_field_diffusion(df: pd.DataFrame) -> dict[str, Any]:
    pivot = df.pivot_table(index="year", columns="field_name", values="ai_fraction")
    pivot = pivot.sort_index().fillna(0.0)
    fields = pivot.columns.to_list()

    corr_matrix: dict[str, dict[str, float | None]] = {}
    pval_matrix: dict[str, dict[str, float | None]] = {}
    pairwise_rows: list[dict[str, Any]] = []

    for field_i in fields:
        corr_matrix[field_i] = {}
        pval_matrix[field_i] = {}
        for field_j in fields:
            x = pivot[field_i].to_numpy(dtype=float)
            y = pivot[field_j].to_numpy(dtype=float)
            corr, p_value = _pearson_with_guard(x, y)
            corr_matrix[field_i][field_j] = corr
            pval_matrix[field_i][field_j] = p_value

    for i, field_i in enumerate(fields):
        for j in range(i + 1, len(fields)):
            field_j = fields[j]
            corr = corr_matrix[field_i][field_j]
            p_value = pval_matrix[field_i][field_j]
            pairwise_rows.append(
                {
                    "field_a": field_i,
                    "field_b": field_j,
                    "pearson_correlation": corr,
                    "p_value": p_value,
                },
            )

    valid_corrs = [
        float(row["pearson_correlation"])
        for row in pairwise_rows
        if row["pearson_correlation"] is not None
    ]
    avg_corr = float(np.mean(valid_corrs)) if valid_corrs else None
    strong_corr_fraction = (
        float(np.mean([abs(v) >= 0.7 for v in valid_corrs])) if valid_corrs else None
    )

    pairwise_sorted = sorted(
        pairwise_rows,
        key=lambda row: (
            abs(row["pearson_correlation"])
            if row["pearson_correlation"] is not None
            else -1.0
        ),
        reverse=True,
    )

    return {
        "years": [ANALYSIS_START_YEAR, ANALYSIS_END_YEAR],
        "correlation_method": "pearson",
        "correlation_matrix": corr_matrix,
        "p_value_matrix": pval_matrix,
        "mean_pairwise_correlation": avg_corr,
        "fraction_strong_correlations_abs_ge_0_7": strong_corr_fraction,
        "top_correlated_pairs": pairwise_sorted[:10],
    }


def analyze_did_framework(df: pd.DataFrame) -> dict[str, Any]:
    subset = df[
        df["field_name"].isin(TREATMENT_FIELDS.union(CONTROL_FIELDS))
        & df["year"].between(DID_PRE_START, DID_POST_END)
    ].copy()
    subset["group"] = np.where(
        subset["field_name"].isin(TREATMENT_FIELDS),
        "treatment",
        "control",
    )
    subset["period"] = np.where(subset["year"] <= DID_PRE_END, "pre", "post")

    group_period_means = subset.groupby(["group", "period"], as_index=False)[
        "ai_fraction"
    ].mean()

    mean_lookup = {
        (str(row["group"]), str(row["period"])): float(row["ai_fraction"])
        for _, row in group_period_means.iterrows()
    }

    treat_pre = mean_lookup.get(("treatment", "pre"), 0.0)
    treat_post = mean_lookup.get(("treatment", "post"), 0.0)
    control_pre = mean_lookup.get(("control", "pre"), 0.0)
    control_post = mean_lookup.get(("control", "post"), 0.0)

    treat_change = treat_post - treat_pre
    control_change = control_post - control_pre
    att = treat_change - control_change

    per_field = subset.groupby(["field_name", "group", "period"], as_index=False)[
        "ai_fraction"
    ].mean()
    per_field_wide = per_field.pivot_table(
        index=["field_name", "group"],
        columns="period",
        values="ai_fraction",
    ).reset_index()
    per_field_wide["pre"] = per_field_wide["pre"].fillna(0.0)
    per_field_wide["post"] = per_field_wide["post"].fillna(0.0)
    per_field_wide["change"] = per_field_wide["post"] - per_field_wide["pre"]

    treat_changes = per_field_wide.loc[
        per_field_wide["group"] == "treatment", "change"
    ].to_numpy(dtype=float)
    control_changes = per_field_wide.loc[
        per_field_wide["group"] == "control", "change"
    ].to_numpy(dtype=float)

    t_stat: float | None
    p_value: float | None
    if treat_changes.size >= 2 and control_changes.size >= 2:
        ttest = stats.ttest_ind(treat_changes, control_changes, equal_var=False)
        t_stat = float(ttest.statistic)
        p_value = float(ttest.pvalue)
    else:
        t_stat = None
        p_value = None

    all_changes = np.concatenate([treat_changes, control_changes])
    if all_changes.size >= 2 and not np.isclose(
        float(np.std(all_changes, ddof=1)), 0.0
    ):
        se = float(np.std(all_changes, ddof=1) / np.sqrt(all_changes.size))
        t_crit = float(stats.t.ppf(0.975, df=all_changes.size - 1))
        ci_95 = [att - t_crit * se, att + t_crit * se]
    else:
        ci_95 = None

    per_field_rows = []
    for _, row in per_field_wide.sort_values(["group", "field_name"]).iterrows():
        per_field_rows.append(
            {
                "field_name": str(row["field_name"]),
                "group": str(row["group"]),
                "pre_mean_ai_fraction": float(row["pre"]),
                "post_mean_ai_fraction": float(row["post"]),
                "change": float(row["change"]),
            },
        )

    return {
        "treatment_fields": sorted(TREATMENT_FIELDS),
        "control_fields": sorted(CONTROL_FIELDS),
        "pre_period": [DID_PRE_START, DID_PRE_END],
        "post_period": [DID_POST_START, DID_POST_END],
        "group_period_means": {
            "treatment": {"pre": treat_pre, "post": treat_post, "change": treat_change},
            "control": {
                "pre": control_pre,
                "post": control_post,
                "change": control_change,
            },
        },
        "att": att,
        "att_pct_points": att * 100,
        "welch_t_test_on_field_level_changes": {
            "t_statistic": t_stat,
            "p_value": p_value,
        },
        "approx_att_95ci": ci_95,
        "field_level_changes": per_field_rows,
    }


def _to_native(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _to_native(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_native(v) for v in value]
    if isinstance(value, tuple):
        return tuple(_to_native(v) for v in value)
    if isinstance(value, np.floating | float):
        if np.isnan(value) or np.isinf(value):
            return None
        return float(value)
    if isinstance(value, np.integer | int):
        return int(value)
    if isinstance(value, np.bool_ | bool):
        return bool(value)
    return value


def print_summary(results: dict[str, Any]) -> None:
    acceleration = results["analysis_1_adoption_acceleration"]["ranked_fields"]
    onset = results["analysis_2_adoption_onset"]["field_results"]
    diffusion = results["analysis_3_cross_field_diffusion"]
    did = results["analysis_4_did_framework"]

    print("=" * 88)
    print("AI ADOPTION ANALYSIS (2000-2024)")
    print("=" * 88)

    accel_df = pd.DataFrame(acceleration)
    accel_display = accel_df[
        [
            "rank_by_acceleration",
            "field_name",
            "early_period_avg_ai_fraction",
            "recent_period_avg_ai_fraction",
            "absolute_change",
            "fold_increase",
        ]
    ].copy()
    for col in [
        "early_period_avg_ai_fraction",
        "recent_period_avg_ai_fraction",
        "absolute_change",
        "fold_increase",
    ]:
        accel_display[col] = (
            accel_display[col]
            .astype(float)
            .map(
                lambda x: f"{x:.4f}" if np.isfinite(x) else "NA",
            )
        )

    print("\n[1] Adoption acceleration (2005-2014 vs 2015-2024)")
    print(accel_display.to_string(index=False))

    onset_df = pd.DataFrame(onset)
    onset_df = onset_df.sort_values(
        by=["inflection_year", "field_name"],
        na_position="last",
    )
    print(
        "\n[2] Adoption onset detection "
        f"(threshold: {ONSET_THRESHOLD_PCT_POINTS:.2f} pct-points/year)"
    )
    print(
        onset_df[
            [
                "field_name",
                "inflection_year",
                "max_rolling_3y_avg_change_pct_points",
            ]
        ].to_string(index=False),
    )

    print("\n[3] Cross-field diffusion (Pearson correlations)")
    print(
        f"Mean pairwise correlation: {diffusion['mean_pairwise_correlation']:.4f}"
        if diffusion["mean_pairwise_correlation"] is not None
        else "Mean pairwise correlation: NA"
    )
    print(
        "Strong-correlation share (|r| >= 0.7): "
        f"{diffusion['fraction_strong_correlations_abs_ge_0_7']:.3f}"
        if diffusion["fraction_strong_correlations_abs_ge_0_7"] is not None
        else "Strong-correlation share (|r| >= 0.7): NA"
    )
    print("Top correlated field pairs:")
    top_pairs = pd.DataFrame(diffusion["top_correlated_pairs"])
    if not top_pairs.empty:
        top_pairs_display = top_pairs.copy()
        top_pairs_display["pearson_correlation"] = (
            top_pairs_display["pearson_correlation"]
            .astype(float)
            .map(lambda x: f"{x:.4f}" if np.isfinite(x) else "NA")
        )
        top_pairs_display["p_value"] = (
            top_pairs_display["p_value"]
            .astype(float)
            .map(
                lambda x: f"{x:.2e}" if np.isfinite(x) else "NA",
            )
        )
        print(top_pairs_display.to_string(index=False))

    print("\n[4] DID-style treatment vs control")
    print(f"Treatment fields: {', '.join(did['treatment_fields'])}")
    print(f"Control fields:   {', '.join(did['control_fields'])}")
    print(
        "ATT (fraction scale): "
        f"{did['att']:.4f}"
        f" ({did['att_pct_points']:.2f} pct-points)"
    )
    test_result = did["welch_t_test_on_field_level_changes"]
    if test_result["t_statistic"] is not None and test_result["p_value"] is not None:
        print(
            "Welch t-test on field-level pre/post changes: "
            f"t={test_result['t_statistic']:.4f}, p={test_result['p_value']:.4f}"
        )
    else:
        print("Welch t-test on field-level pre/post changes: NA")

    print("\nField-level DID inputs:")
    did_fields = pd.DataFrame(did["field_level_changes"])
    print(did_fields.to_string(index=False))
    print("=" * 88)
    print(f"Results saved to: {OUTPUT_PATH}")


def main() -> None:
    df = load_and_prepare_data(INPUT_PATH)

    results: dict[str, Any] = {
        "metadata": {
            "input_path": str(INPUT_PATH),
            "output_path": str(OUTPUT_PATH),
            "years_analyzed": [ANALYSIS_START_YEAR, ANALYSIS_END_YEAR],
            "excluded_years": [2025],
            "n_fields": int(df["field_name"].nunique()),
            "n_rows": len(df),
        },
        "analysis_1_adoption_acceleration": analyze_adoption_acceleration(df),
        "analysis_2_adoption_onset": analyze_adoption_onset(df),
        "analysis_3_cross_field_diffusion": analyze_cross_field_diffusion(df),
        "analysis_4_did_framework": analyze_did_framework(df),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(_to_native(results), f, indent=2)

    print_summary(results)


if __name__ == "__main__":
    main()
