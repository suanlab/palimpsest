#!/usr/bin/env python3
"""Run full statistical analysis for Neo4j-extracted 26-field AI adoption data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import optimize, stats

INPUT_PANEL_PATH = Path("data/processed/neo4j_field_panel.parquet")
INPUT_SUMMARY_PATH = Path("data/processed/neo4j_field_summary.parquet")
INPUT_RETRACTION_PATH = Path("data/processed/neo4j_retraction_by_field_year.parquet")
OUTPUT_JSON_PATH = Path("data/processed/neo4j_field_analysis.json")

ANALYSIS_START_YEAR = 2000
ANALYSIS_END_YEAR = 2024

EARLY_PERIOD = (2005, 2014)
RECENT_PERIOD = (2015, 2024)

SCURVE_BOUNDS = ([0.001, 0.01, 1995.0], [1.0, 2.0, 2030.0])
SCURVE_MAX_EVALS = 20_000

ONSET_ROLLING_WINDOW = 3
ONSET_THRESHOLD = 0.005
STRONG_CORRELATION_THRESHOLD = 0.70

METHOD_SPECS = {
    "title": {
        "fraction_column": "ai_title_fraction",
        "count_column": "ai_title_count",
        "label": "title-based",
    },
    "concept": {
        "fraction_column": "ai_concept_fraction",
        "count_column": "ai_concept_count",
        "label": "concept-based",
    },
}


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = required - set(df.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"{name} missing required columns: {missing_text}")


def _to_native(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _to_native(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_native(v) for v in value]
    if isinstance(value, tuple):
        return tuple(_to_native(v) for v in value)
    if isinstance(value, np.ndarray):
        return [_to_native(v) for v in value.tolist()]
    if isinstance(value, np.floating | float):
        if np.isnan(value) or np.isinf(value):
            return None
        return float(value)
    if isinstance(value, np.integer | int):
        return int(value)
    if isinstance(value, np.bool_ | bool):
        return bool(value)
    if value is None:
        return None
    if pd.isna(value):
        return None
    return value


def _compute_r_squared(y_true: np.ndarray, y_pred: np.ndarray) -> float | None:
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    if np.isclose(ss_tot, 0.0):
        return 1.0 if np.isclose(ss_res, 0.0) else None
    return float(1.0 - (ss_res / ss_tot))


def _pearson_with_guard(
    x: np.ndarray, y: np.ndarray
) -> tuple[float | None, float | None]:
    if x.size < 2 or y.size < 2:
        return None, None
    if np.isclose(float(np.std(x)), 0.0) or np.isclose(float(np.std(y)), 0.0):
        return None, None
    corr_raw, p_value_raw = stats.pearsonr(x, y)
    corr = float(np.asarray(corr_raw).item())
    p_value = float(np.asarray(p_value_raw).item())
    return corr, p_value


def logistic_growth_model(
    years: np.ndarray, k: float, r: float, t0: float
) -> np.ndarray:
    return k / (1.0 + np.exp(-r * (years - t0)))


def classify_adoption_type(
    k: float | None,
    r: float | None,
    t0: float | None,
    r_squared: float | None,
) -> str:
    if k is None or r is None or t0 is None or r_squared is None:
        return "C"
    if k < 0.03 or r < 0.03 or r_squared < 0.50:
        return "D"
    if k >= 0.10 and t0 <= 2014.0 and r_squared >= 0.80:
        return "A"
    if r >= 0.12 and t0 <= 2024.0 and r_squared >= 0.75:
        return "B"
    return "C"


def load_panel_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing panel data file: {path}")

    panel_df = pd.read_parquet(path)
    _require_columns(
        panel_df,
        {
            "field_id",
            "field_name",
            "year",
            "total_count",
            "ai_title_count",
            "ai_concept_count",
            "ai_title_fraction",
            "ai_concept_fraction",
        },
        "neo4j_field_panel",
    )

    working = panel_df.copy()
    working["year"] = pd.to_numeric(working["year"], errors="coerce").astype("Int64")
    working = working.dropna(subset=["field_id", "field_name", "year"]).copy()
    working["year"] = working["year"].astype(int)

    for column in [
        "total_count",
        "ai_title_count",
        "ai_concept_count",
        "ai_title_fraction",
        "ai_concept_fraction",
    ]:
        working[column] = pd.to_numeric(working[column], errors="coerce").fillna(0.0)

    working["ai_title_fraction"] = working["ai_title_fraction"].clip(0.0, 1.0)
    working["ai_concept_fraction"] = working["ai_concept_fraction"].clip(0.0, 1.0)
    return working


def analyze_s_curve_fitting(df: pd.DataFrame, fraction_column: str) -> dict[str, Any]:
    field_results: list[dict[str, Any]] = []

    bounds_lower = np.array(SCURVE_BOUNDS[0], dtype=float)
    bounds_upper = np.array(SCURVE_BOUNDS[1], dtype=float)

    for field_name, group in df.groupby("field_name", sort=True):
        ordered = group.sort_values("year")
        years = ordered["year"].to_numpy(dtype=float)
        values = ordered[fraction_column].to_numpy(dtype=float)

        initial_guess = np.array(
            [
                np.clip(max(float(values.max()) * 1.15, 0.01), bounds_lower[0], 0.95),
                0.15,
                np.clip(float(np.median(years)), bounds_lower[2], bounds_upper[2]),
            ],
            dtype=float,
        )

        k_hat: float | None
        r_hat: float | None
        t0_hat: float | None
        r_squared: float | None
        fit_status: str

        try:
            params, _ = optimize.curve_fit(
                logistic_growth_model,
                years,
                values,
                p0=initial_guess,
                bounds=SCURVE_BOUNDS,
                maxfev=SCURVE_MAX_EVALS,
            )
            k_hat = float(params[0])
            r_hat = float(params[1])
            t0_hat = float(params[2])
            fitted_values = logistic_growth_model(years, k_hat, r_hat, t0_hat)
            r_squared = _compute_r_squared(values, fitted_values)
            fit_status = "ok"
        except (RuntimeError, ValueError) as exc:
            k_hat = None
            r_hat = None
            t0_hat = None
            r_squared = None
            fit_status = f"fit_failed: {exc.__class__.__name__}"

        adoption_type = classify_adoption_type(
            k=k_hat,
            r=r_hat,
            t0=t0_hat,
            r_squared=r_squared,
        )

        field_results.append(
            {
                "field_name": str(field_name),
                "K": k_hat,
                "r": r_hat,
                "t0": t0_hat,
                "r_squared": r_squared,
                "adoption_type": adoption_type,
                "fit_status": fit_status,
            },
        )

    type_counts = (
        pd.Series([row["adoption_type"] for row in field_results])
        .value_counts()
        .to_dict()
    )

    return {
        "model": "y(t) = K / (1 + exp(-r*(t - t0)))",
        "parameter_bounds": {
            "K": [SCURVE_BOUNDS[0][0], SCURVE_BOUNDS[1][0]],
            "r": [SCURVE_BOUNDS[0][1], SCURVE_BOUNDS[1][1]],
            "t0": [SCURVE_BOUNDS[0][2], SCURVE_BOUNDS[1][2]],
        },
        "classification_rules": {
            "A": "early adopter, high carrying capacity",
            "B": "accelerating adoption",
            "C": "moderate or mixed trajectory",
            "D": "flat/resistant trajectory",
        },
        "field_results": field_results,
        "type_counts": {str(key): int(val) for key, val in type_counts.items()},
    }


def analyze_adoption_onset(df: pd.DataFrame, fraction_column: str) -> dict[str, Any]:
    onset_rows: list[dict[str, Any]] = []

    for field_name, group in df.groupby("field_name", sort=True):
        ordered = group.sort_values("year")[["year", fraction_column]].copy()
        ordered["yoy_change"] = ordered[fraction_column].diff()
        ordered["rolling_3y_change"] = (
            ordered["yoy_change"]
            .rolling(ONSET_ROLLING_WINDOW, min_periods=ONSET_ROLLING_WINDOW)
            .mean()
        )

        onset_candidates = ordered[ordered["rolling_3y_change"] > ONSET_THRESHOLD]
        onset_year = (
            int(onset_candidates["year"].iloc[0])
            if not onset_candidates.empty
            else None
        )
        max_rolling = ordered["rolling_3y_change"].max(skipna=True)

        onset_rows.append(
            {
                "field_name": str(field_name),
                "onset_year": onset_year,
                "max_rolling_change": (
                    float(max_rolling) if pd.notna(max_rolling) else None
                ),
            },
        )

    ranked = sorted(
        onset_rows,
        key=lambda row: (
            row["max_rolling_change"] if row["max_rolling_change"] is not None else -1.0
        ),
        reverse=True,
    )
    return {
        "rolling_window_years": ONSET_ROLLING_WINDOW,
        "threshold_fraction": ONSET_THRESHOLD,
        "threshold_pct_points": ONSET_THRESHOLD * 100,
        "field_results": onset_rows,
        "ranked_by_max_rolling_change": ranked,
    }


def analyze_cross_field_correlations(
    df: pd.DataFrame, fraction_column: str
) -> dict[str, Any]:
    pivot = (
        df.pivot_table(index="year", columns="field_name", values=fraction_column)
        .sort_index(axis=1)
        .sort_index()
    )
    corr = pivot.corr(method="pearson")
    fields = corr.columns.tolist()

    pair_rows: list[dict[str, Any]] = []
    corr_values: list[float] = []

    for i, field_i in enumerate(fields):
        for j in range(i + 1, len(fields)):
            field_j = fields[j]
            value = corr.iloc[i, j]
            if pd.isna(value):
                continue
            corr_float = float(np.asarray(value, dtype=float).item())
            corr_values.append(corr_float)
            pair_rows.append(
                {
                    "field_a": field_i,
                    "field_b": field_j,
                    "correlation": corr_float,
                },
            )

    strong_pairs = [
        row
        for row in pair_rows
        if abs(row["correlation"]) >= STRONG_CORRELATION_THRESHOLD
    ]
    pair_rows = sorted(pair_rows, key=lambda row: abs(row["correlation"]), reverse=True)

    return {
        "n_fields": len(fields),
        "n_pairs": len(pair_rows),
        "mean_correlation": float(np.mean(corr_values)) if corr_values else None,
        "fraction_strong_pairs": (
            float(len(strong_pairs) / len(pair_rows)) if pair_rows else None
        ),
        "strong_threshold_abs_r": STRONG_CORRELATION_THRESHOLD,
        "top_strong_pairs": strong_pairs[:20],
        "correlation_matrix": corr.to_dict(),
    }


def analyze_period_comparison(df: pd.DataFrame, fraction_column: str) -> dict[str, Any]:
    early = (
        df[df["year"].between(EARLY_PERIOD[0], EARLY_PERIOD[1])]
        .groupby("field_name")[fraction_column]
        .mean()
        .rename("early_mean")
    )
    recent = (
        df[df["year"].between(RECENT_PERIOD[0], RECENT_PERIOD[1])]
        .groupby("field_name")[fraction_column]
        .mean()
        .rename("recent_mean")
    )
    joined = early.to_frame().join(recent, how="outer").fillna(0.0)
    joined["absolute_change"] = joined["recent_mean"] - joined["early_mean"]
    joined["fold_change"] = np.where(
        joined["early_mean"] > 0,
        joined["recent_mean"] / joined["early_mean"],
        np.nan,
    )

    field_results = joined.reset_index().to_dict(orient="records")

    abs_rank = joined.sort_values("absolute_change", ascending=False).reset_index()
    fold_rank = joined.sort_values("fold_change", ascending=False).reset_index()

    return {
        "early_period": list(EARLY_PERIOD),
        "recent_period": list(RECENT_PERIOD),
        "field_results": field_results,
        "rank_by_absolute_change": abs_rank.to_dict(orient="records"),
        "rank_by_fold_change": fold_rank.to_dict(orient="records"),
    }


def analyze_retractions(
    panel_df: pd.DataFrame,
    retraction_df: pd.DataFrame,
    fraction_column: str,
) -> dict[str, Any]:
    totals = panel_df[
        ["field_id", "field_name", "year", "total_count", fraction_column]
    ].copy()
    joined = totals.merge(
        retraction_df[["field_id", "field_name", "year", "retracted_count"]],
        on=["field_id", "field_name", "year"],
        how="left",
    )
    joined["retracted_count"] = joined["retracted_count"].fillna(0.0)
    joined["retraction_rate"] = np.where(
        joined["total_count"] > 0,
        joined["retracted_count"] / joined["total_count"],
        np.nan,
    )

    field_summary = (
        joined.groupby(["field_id", "field_name"], as_index=False)
        .agg(
            total_papers=("total_count", "sum"),
            total_retractions=("retracted_count", "sum"),
            mean_ai_fraction=(fraction_column, "mean"),
            mean_retraction_rate=("retraction_rate", "mean"),
        )
        .sort_values("total_retractions", ascending=False)
    )
    field_summary["retraction_rate"] = np.where(
        field_summary["total_papers"] > 0,
        field_summary["total_retractions"] / field_summary["total_papers"],
        np.nan,
    )
    field_summary["retraction_per_million"] = (
        field_summary["retraction_rate"] * 1_000_000
    )

    yearly = (
        joined.groupby("year", as_index=False)
        .agg(
            total_papers=("total_count", "sum"),
            total_retractions=("retracted_count", "sum"),
            weighted_ai_count=(
                fraction_column,
                lambda s: float(np.sum(s * joined.loc[s.index, "total_count"])),
            ),
        )
        .sort_values("year")
    )
    yearly["retraction_rate"] = np.where(
        yearly["total_papers"] > 0,
        yearly["total_retractions"] / yearly["total_papers"],
        np.nan,
    )
    yearly["ai_fraction_weighted"] = np.where(
        yearly["total_papers"] > 0,
        yearly["weighted_ai_count"] / yearly["total_papers"],
        np.nan,
    )

    field_corr, field_corr_p = _pearson_with_guard(
        field_summary["mean_ai_fraction"].to_numpy(dtype=float),
        field_summary["retraction_rate"].to_numpy(dtype=float),
    )
    panel_corr, panel_corr_p = _pearson_with_guard(
        joined[fraction_column].to_numpy(dtype=float),
        joined["retraction_rate"].fillna(0.0).to_numpy(dtype=float),
    )
    yearly_corr, yearly_corr_p = _pearson_with_guard(
        yearly["ai_fraction_weighted"].fillna(0.0).to_numpy(dtype=float),
        yearly["retraction_rate"].fillna(0.0).to_numpy(dtype=float),
    )

    return {
        "field_summary": field_summary.to_dict(orient="records"),
        "yearly_trend": yearly.to_dict(orient="records"),
        "correlation_with_ai_adoption": {
            "field_level_mean": {
                "pearson_r": field_corr,
                "p_value": field_corr_p,
            },
            "field_year_panel": {
                "pearson_r": panel_corr,
                "p_value": panel_corr_p,
            },
            "yearly_aggregate": {
                "pearson_r": yearly_corr,
                "p_value": yearly_corr_p,
            },
        },
    }


def print_summary(results: dict[str, Any]) -> None:
    print("=" * 96)
    print("NEO4J FIELD ANALYSIS (26 fields, 2000-2024)")
    print("=" * 96)

    for method_key, method_result in results["methods"].items():
        print(f"\n[{method_key.upper()}] {method_result['label']}")

        s_curve_df = pd.DataFrame(
            method_result["analysis_1_s_curve_fitting"]["field_results"]
        )
        print(
            "- S-curve type counts:",
            method_result["analysis_1_s_curve_fitting"]["type_counts"],
        )
        print(
            s_curve_df[["field_name", "K", "r", "t0", "r_squared", "adoption_type"]]
            .sort_values("K", ascending=False)
            .head(8)
            .to_string(index=False)
        )

        onset_df = pd.DataFrame(
            method_result["analysis_2_adoption_onset"]["field_results"]
        )
        print("- Earliest onset fields:")
        print(
            onset_df.sort_values(
                ["onset_year", "max_rolling_change"], na_position="last"
            )
            .head(8)
            .to_string(index=False)
        )

        period_df = pd.DataFrame(
            method_result["analysis_4_period_comparison"]["field_results"]
        )
        print("- Largest absolute change (pct-points):")
        preview = (
            period_df.sort_values("absolute_change", ascending=False).head(8).copy()
        )
        for col in ["early_mean", "recent_mean", "absolute_change"]:
            preview[col] = preview[col] * 100
        print(
            preview[
                ["field_name", "early_mean", "recent_mean", "absolute_change"]
            ].to_string(index=False)
        )

        retract_df = pd.DataFrame(
            method_result["analysis_5_retraction_rate"]["field_summary"]
        )
        print("- Highest retraction rates per million papers:")
        print(
            retract_df.sort_values("retraction_per_million", ascending=False)
            .head(8)[["field_name", "retraction_per_million", "mean_ai_fraction"]]
            .to_string(index=False)
        )

    print("\nOutput JSON:", OUTPUT_JSON_PATH)


def main() -> None:
    panel_df = load_panel_data(INPUT_PANEL_PATH)
    summary_df = pd.read_parquet(INPUT_SUMMARY_PATH)
    retraction_df = pd.read_parquet(INPUT_RETRACTION_PATH)

    _require_columns(
        summary_df,
        {
            "field_id",
            "field_name",
            "paper_count",
            "ai_title_count",
            "ai_concept_count",
            "ai_title_fraction",
            "ai_concept_fraction",
        },
        "neo4j_field_summary",
    )
    _require_columns(
        retraction_df,
        {"field_id", "field_name", "year", "retracted_count"},
        "neo4j_retraction_by_field_year",
    )
    retraction_df = retraction_df.copy()
    retraction_df["year"] = pd.to_numeric(
        retraction_df["year"], errors="coerce"
    ).astype("Int64")
    retraction_df = retraction_df.dropna(subset=["year"]).copy()
    retraction_df["year"] = retraction_df["year"].astype(int)
    retraction_df["retracted_count"] = pd.to_numeric(
        retraction_df["retracted_count"],
        errors="coerce",
    ).fillna(0.0)

    panel_main = panel_df[
        panel_df["year"].between(ANALYSIS_START_YEAR, ANALYSIS_END_YEAR)
    ].copy()

    methods_output: dict[str, Any] = {}
    for method_key, spec in METHOD_SPECS.items():
        fraction_column = str(spec["fraction_column"])
        method_panel = panel_main[
            ["field_id", "field_name", "year", "total_count", fraction_column]
        ].copy()

        methods_output[method_key] = {
            "label": str(spec["label"]),
            "fraction_column": fraction_column,
            "analysis_1_s_curve_fitting": analyze_s_curve_fitting(
                method_panel, fraction_column
            ),
            "analysis_2_adoption_onset": analyze_adoption_onset(
                method_panel, fraction_column
            ),
            "analysis_3_cross_field_correlation": analyze_cross_field_correlations(
                method_panel, fraction_column
            ),
            "analysis_4_period_comparison": analyze_period_comparison(
                method_panel, fraction_column
            ),
            "analysis_5_retraction_rate": analyze_retractions(
                panel_df=method_panel,
                retraction_df=retraction_df,
                fraction_column=fraction_column,
            ),
        }

    results: dict[str, Any] = {
        "metadata": {
            "input_panel_path": str(INPUT_PANEL_PATH),
            "input_summary_path": str(INPUT_SUMMARY_PATH),
            "input_retraction_path": str(INPUT_RETRACTION_PATH),
            "output_json_path": str(OUTPUT_JSON_PATH),
            "years_analyzed": [ANALYSIS_START_YEAR, ANALYSIS_END_YEAR],
            "fields_total": int(panel_df["field_name"].nunique()),
            "rows_total": len(panel_df),
            "rows_main_window": len(panel_main),
        },
        "field_summary": summary_df.sort_values("field_name").to_dict(orient="records"),
        "methods": methods_output,
    }

    OUTPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON_PATH.write_text(
        json.dumps(_to_native(results), indent=2, ensure_ascii=True),
        encoding="utf-8",
    )

    print_summary(results)


if __name__ == "__main__":
    main()
