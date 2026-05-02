#!/usr/bin/env python3
"""Perform deep AI adoption analysis for Track 1 scientific fields.

This script reads AI adoption panel data, executes five deep analyses, writes
structured JSON output, and prints concise summary tables for quick inspection.
"""
# pyright: basic, reportMissingImports=false

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import optimize, stats
from scipy.cluster import hierarchy
from scipy.spatial import distance

try:
    import statsmodels.api as sm

    HAS_STATSMODELS = True
except ModuleNotFoundError:
    sm = None
    HAS_STATSMODELS = False

INPUT_PATH = Path("data/processed/ai_adoption_by_field.parquet")
OUTPUT_PATH = Path("data/processed/ai_adoption_deep_analysis.json")

ANALYSIS_START_YEAR = 2000
ANALYSIS_END_YEAR = 2024

SCURVE_BOUNDS = ([0.01, 0.01, 1995.0], [1.0, 2.0, 2030.0])
SCURVE_MAX_EVALS = 20000

TYPE_A_K_THRESHOLD = 0.12
TYPE_A_T0_THRESHOLD = 2016.0
TYPE_C_R2_THRESHOLD = 0.90
TYPE_D_K_THRESHOLD = 0.05
TYPE_D_R_THRESHOLD = 0.015

BREAK_MIN_WINDOW = 5
BREAK_F_PARAMS = 2

PREDICTOR_COLUMNS = [
    "math_intensity",
    "data_availability",
    "experimental",
    "regulatory",
]
OUTCOME_COLUMNS = [
    "ai_fraction_2024",
    "growth_rate_2010_2024",
    "acceleration",
    "onset_year",
]

DID_SPECS: dict[str, dict[str, tuple[str, ...]]] = {
    "spec_a_top_accelerators": {
        "treatment": (
            "Computer Science",
            "Biology",
            "Geology",
            "Environmental Science",
            "Materials Science",
        ),
        "control": (
            "Medicine",
            "Psychology",
            "Political Science",
            "Economics",
            "Business",
        ),
    },
    "spec_b_recent_accelerators": {
        "treatment": (
            "Biology",
            "Geology",
            "Environmental Science",
        ),
        "control": (
            "Medicine",
            "Psychology",
            "Political Science",
        ),
    },
}

FIELD_CHARACTERISTICS: dict[str, dict[str, float]] = {
    "Biology": {
        "math_intensity": 0.50,
        "data_availability": 0.80,
        "experimental": 0.90,
        "regulatory": 0.30,
    },
    "Business": {
        "math_intensity": 0.45,
        "data_availability": 0.70,
        "experimental": 0.40,
        "regulatory": 0.40,
    },
    "Chemistry": {
        "math_intensity": 0.65,
        "data_availability": 0.70,
        "experimental": 0.85,
        "regulatory": 0.40,
    },
    "Computer Science": {
        "math_intensity": 0.90,
        "data_availability": 0.95,
        "experimental": 0.30,
        "regulatory": 0.10,
    },
    "Economics": {
        "math_intensity": 0.75,
        "data_availability": 0.70,
        "experimental": 0.25,
        "regulatory": 0.35,
    },
    "Engineering": {
        "math_intensity": 0.80,
        "data_availability": 0.78,
        "experimental": 0.70,
        "regulatory": 0.35,
    },
    "Environmental Science": {
        "math_intensity": 0.60,
        "data_availability": 0.82,
        "experimental": 0.85,
        "regulatory": 0.45,
    },
    "Geography": {
        "math_intensity": 0.55,
        "data_availability": 0.72,
        "experimental": 0.60,
        "regulatory": 0.40,
    },
    "Geology": {
        "math_intensity": 0.58,
        "data_availability": 0.75,
        "experimental": 0.88,
        "regulatory": 0.35,
    },
    "Materials Science": {
        "math_intensity": 0.72,
        "data_availability": 0.70,
        "experimental": 0.80,
        "regulatory": 0.35,
    },
    "Mathematics": {
        "math_intensity": 0.95,
        "data_availability": 0.55,
        "experimental": 0.10,
        "regulatory": 0.05,
    },
    "Medicine": {
        "math_intensity": 0.40,
        "data_availability": 0.85,
        "experimental": 0.70,
        "regulatory": 0.95,
    },
    "Physics": {
        "math_intensity": 0.85,
        "data_availability": 0.68,
        "experimental": 0.50,
        "regulatory": 0.20,
    },
    "Political Science": {
        "math_intensity": 0.50,
        "data_availability": 0.60,
        "experimental": 0.25,
        "regulatory": 0.55,
    },
    "Psychology": {
        "math_intensity": 0.45,
        "data_availability": 0.76,
        "experimental": 0.65,
        "regulatory": 0.75,
    },
}


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
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    working = df.copy()
    working["year"] = pd.to_numeric(working["year"], errors="coerce").astype("Int64")
    working = working[
        working["year"].between(ANALYSIS_START_YEAR, ANALYSIS_END_YEAR)
    ].copy()
    working = working.dropna(subset=["field_id", "field_name", "year"])
    working["year"] = working["year"].astype(int)

    working["total_count"] = pd.to_numeric(working["total_count"], errors="coerce")
    working["total_count"] = working["total_count"].fillna(0.0)

    working["ai_count"] = pd.to_numeric(working["ai_count"], errors="coerce")
    working["ai_count"] = working["ai_count"].fillna(0.0)

    working["ai_fraction"] = pd.to_numeric(working["ai_fraction"], errors="coerce")
    fallback_fraction = np.where(
        working["total_count"] > 0,
        working["ai_count"] / working["total_count"],
        0.0,
    )
    working["ai_fraction"] = working["ai_fraction"].fillna(
        pd.Series(fallback_fraction, index=working.index),
    )
    working["ai_fraction"] = working["ai_fraction"].clip(lower=0.0, upper=1.0)

    year_index = pd.Index(
        range(ANALYSIS_START_YEAR, ANALYSIS_END_YEAR + 1),
        name="year",
    )
    panel_frames: list[pd.DataFrame] = []

    for (field_id, field_name), group in working.groupby(
        ["field_id", "field_name"], sort=True
    ):
        panel = group.set_index("year").sort_index().reindex(year_index)
        panel["field_id"] = str(field_id)
        panel["field_name"] = str(field_name)
        panel["total_count"] = panel["total_count"].fillna(0.0)
        panel["ai_count"] = panel["ai_count"].fillna(0.0)
        panel["ai_fraction"] = panel["ai_fraction"].fillna(0.0)
        panel_frames.append(panel.reset_index())

    if not panel_frames:
        raise ValueError("No rows available after filtering and balancing panel data.")

    return pd.concat(panel_frames, ignore_index=True)


def logistic_growth_model(
    years: np.ndarray,
    k: float,
    r: float,
    t0: float,
) -> np.ndarray:
    return k / (1.0 + np.exp(-r * (years - t0)))


def _compute_r_squared(y_true: np.ndarray, y_pred: np.ndarray) -> float | None:
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    if np.isclose(ss_tot, 0.0):
        return 1.0 if np.isclose(ss_res, 0.0) else None
    return float(1.0 - (ss_res / ss_tot))


def classify_adoption_type(
    k: float | None,
    r: float | None,
    t0: float | None,
    r_squared: float | None,
) -> str:
    if k is None or r is None:
        return "Type C"
    if k < TYPE_D_K_THRESHOLD or r < TYPE_D_R_THRESHOLD:
        return "Type D"
    if r_squared is None or r_squared < TYPE_C_R2_THRESHOLD:
        return "Type C"
    if t0 is not None and k >= TYPE_A_K_THRESHOLD and t0 <= TYPE_A_T0_THRESHOLD:
        return "Type A"
    return "Type B"


def analyze_s_curve_fitting(df: pd.DataFrame) -> dict[str, Any]:
    field_results: list[dict[str, Any]] = []

    bounds_lower = np.array(SCURVE_BOUNDS[0], dtype=float)
    bounds_upper = np.array(SCURVE_BOUNDS[1], dtype=float)

    for field_name, group in df.groupby("field_name", sort=True):
        ordered = group.sort_values("year")
        years = ordered["year"].to_numpy(dtype=float)
        values = ordered["ai_fraction"].to_numpy(dtype=float)

        initial_guess = np.array(
            [
                np.clip(max(float(values.max()) * 1.10, 0.02), bounds_lower[0], 0.95),
                0.20,
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
            with warnings.catch_warnings():
                warnings.simplefilter("error", optimize.OptimizeWarning)
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
        except (RuntimeError, ValueError, optimize.OptimizeWarning) as exc:
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
            "Type A": "Early adopter/saturating (high K, early t0)",
            "Type B": "Accelerating/mid-phase S-curve",
            "Type C": "Linear/slow growth (R^2 < 0.9 or failed fit)",
            "Type D": "Flat/resistant (K < 0.05 or near-zero r)",
        },
        "field_results": field_results,
        "type_counts": {str(k): int(v) for k, v in type_counts.items()},
    }


def _pearson_with_guard(
    x: np.ndarray,
    y: np.ndarray,
) -> tuple[float | None, float | None]:
    if x.size < 2 or y.size < 2:
        return None, None
    if np.isclose(float(np.std(x)), 0.0) or np.isclose(float(np.std(y)), 0.0):
        return None, None
    corr_raw, p_value_raw = stats.pearsonr(x, y)
    corr = float(np.asarray(corr_raw).item())
    p_value = float(np.asarray(p_value_raw).item())
    return corr, p_value


def _linear_fit_with_sse(
    years: np.ndarray,
    values: np.ndarray,
) -> tuple[float, float, float]:
    if years.size == 0:
        return 0.0, 0.0, 0.0

    if np.unique(years).size < 2:
        intercept = float(np.mean(values))
        residuals = values - intercept
        return 0.0, intercept, float(np.sum(residuals**2))

    slope, intercept = np.polyfit(years, values, deg=1)
    predicted = (slope * years) + intercept
    sse = float(np.sum((values - predicted) ** 2))
    return float(slope), float(intercept), sse


def detect_structural_breaks(
    series: pd.DataFrame,
    min_window: int = BREAK_MIN_WINDOW,
) -> dict[str, Any]:
    years = series["year"].to_numpy(dtype=float)
    values = series["ai_fraction"].to_numpy(dtype=float)

    if years.size < (2 * min_window + 1):
        return {
            "status": "insufficient_data",
            "min_window": min_window,
            "candidates": [],
            "best_break": None,
            "best_break_2018_2021": None,
        }

    _, _, pooled_sse = _linear_fit_with_sse(years, values)
    candidates: list[dict[str, Any]] = []

    for split_idx in range(min_window, len(series) - min_window):
        pre_years = years[:split_idx]
        pre_values = values[:split_idx]
        post_years = years[split_idx:]
        post_values = values[split_idx:]

        pre_slope, _, pre_sse = _linear_fit_with_sse(pre_years, pre_values)
        post_slope, _, post_sse = _linear_fit_with_sse(post_years, post_values)
        split_sse = pre_sse + post_sse

        n1 = pre_values.size
        n2 = post_values.size
        df_denom = n1 + n2 - (2 * BREAK_F_PARAMS)

        f_stat = 0.0
        p_value = 1.0
        if df_denom > 0 and split_sse > 0 and pooled_sse >= split_sse:
            numerator = (pooled_sse - split_sse) / BREAK_F_PARAMS
            denominator = split_sse / df_denom
            if denominator > 0:
                f_stat = max(float(numerator / denominator), 0.0)
                p_value = float(stats.f.sf(f_stat, BREAK_F_PARAMS, df_denom))

        candidates.append(
            {
                "break_year": int(years[split_idx]),
                "f_statistic": float(f_stat),
                "p_value": float(p_value),
                "pre_slope": float(pre_slope),
                "post_slope": float(post_slope),
                "slope_change": float(post_slope - pre_slope),
            },
        )

    best_break = max(candidates, key=lambda row: row["f_statistic"])
    candidate_window = [
        row for row in candidates if 2018 <= int(row["break_year"]) <= 2021
    ]
    best_window_break = (
        max(candidate_window, key=lambda row: row["f_statistic"])
        if candidate_window
        else None
    )

    return {
        "status": "ok",
        "min_window": min_window,
        "best_break": best_break,
        "best_break_2018_2021": best_window_break,
        "candidates": candidates,
    }


def _field_series(df: pd.DataFrame, field_name: str) -> pd.DataFrame:
    return (
        df[df["field_name"] == field_name][["year", "ai_fraction"]]
        .sort_values("year")
        .copy()
    )


def _trajectory_summary(series: pd.DataFrame) -> dict[str, Any]:
    years = series["year"].to_numpy(dtype=float)
    values = series["ai_fraction"].to_numpy(dtype=float)

    start_value = float(values[0])
    end_value = float(values[-1])
    slope, _, _ = _linear_fit_with_sse(years, values)
    span = max(int(years[-1] - years[0]), 1)

    if start_value > 0:
        fold_growth = float(end_value / start_value)
        annualized_growth = float((end_value / start_value) ** (1.0 / span) - 1.0)
    else:
        fold_growth = None
        annualized_growth = None

    return {
        "start_year": int(years[0]),
        "end_year": int(years[-1]),
        "start_ai_fraction": start_value,
        "end_ai_fraction": end_value,
        "absolute_change": end_value - start_value,
        "fold_growth": fold_growth,
        "annualized_growth": annualized_growth,
        "linear_slope_per_year": float(slope),
    }


def analyze_biology_deep_dive(df: pd.DataFrame) -> dict[str, Any]:
    biology = _field_series(df, "Biology")
    geology = _field_series(df, "Geology")
    env_science = _field_series(df, "Environmental Science")

    biology["yoy_change"] = biology["ai_fraction"].diff()
    biology["yoy_acceleration"] = biology["yoy_change"].diff()

    eps = 1e-6
    biology["rolling_3y_growth_rate"] = (
        biology["ai_fraction"] / biology["ai_fraction"].shift(3).clip(lower=eps) - 1.0
    )

    growth_values = biology["rolling_3y_growth_rate"].dropna().to_numpy(dtype=float)
    if growth_values.size > 0:
        max_growth = float(np.max(growth_values))
        median_growth = float(np.median(growth_values))
        if np.isclose(median_growth, 0.0):
            breakout_score = None
        else:
            breakout_score = float(max_growth / median_growth)
    else:
        max_growth = None
        median_growth = None
        breakout_score = None

    break_results = detect_structural_breaks(biology)

    biology_values = biology["ai_fraction"].to_numpy(dtype=float)
    comparisons: list[dict[str, Any]] = []
    for comparator_name, comparator in [
        ("Geology", geology),
        ("Environmental Science", env_science),
    ]:
        comparator_values = comparator["ai_fraction"].to_numpy(dtype=float)
        corr, p_value = _pearson_with_guard(biology_values, comparator_values)

        biology_2024 = float(
            biology.loc[biology["year"] == ANALYSIS_END_YEAR, "ai_fraction"].iloc[0],
        )
        comparator_2024 = float(
            comparator.loc[
                comparator["year"] == ANALYSIS_END_YEAR,
                "ai_fraction",
            ].iloc[0],
        )

        comparisons.append(
            {
                "field_name": comparator_name,
                "trajectory_summary": _trajectory_summary(comparator),
                "pearson_vs_biology": corr,
                "p_value_vs_biology": p_value,
                "gap_vs_biology_2024": biology_2024 - comparator_2024,
            },
        )

    return {
        "target_field": "Biology",
        "proxy_note": (
            "No external API calls: this section uses trajectory proxies "
            "(YoY acceleration, structural break tests, and peer comparisons)."
        ),
        "biology_trajectory_summary": _trajectory_summary(biology),
        "rolling_3y_growth": {
            "definition": "(ai_fraction_t / ai_fraction_(t-3)) - 1",
            "max_rolling_3y_growth_rate": max_growth,
            "median_rolling_3y_growth_rate": median_growth,
            "breakout_score": breakout_score,
        },
        "yearly_proxy_table": biology.to_dict(orient="records"),
        "structural_break_detection": break_results,
        "comparative_fields": comparisons,
    }


def build_field_outcomes(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for field_name, group in df.groupby("field_name", sort=True):
        series = group.sort_values("year")[["year", "ai_fraction"]].copy()

        value_2010 = float(series.loc[series["year"] == 2010, "ai_fraction"].iloc[0])
        value_2024 = float(series.loc[series["year"] == 2024, "ai_fraction"].iloc[0])

        growth_rate = (
            float((value_2024 / value_2010) - 1.0) if value_2010 > 0 else np.nan
        )

        series["yoy_change"] = series["ai_fraction"].diff()
        early_yoy = series.loc[series["year"].between(2010, 2016), "yoy_change"].mean()
        late_yoy = series.loc[series["year"].between(2018, 2024), "yoy_change"].mean()
        acceleration = float(late_yoy - early_yoy)

        onset_threshold = 0.5 * value_2024
        onset_candidates = series.loc[
            series["ai_fraction"] >= onset_threshold,
            "year",
        ]
        onset_year = (
            int(onset_candidates.iloc[0])
            if not onset_candidates.empty
            else ANALYSIS_END_YEAR + 1
        )

        rows.append(
            {
                "field_name": str(field_name),
                "ai_fraction_2024": value_2024,
                "growth_rate_2010_2024": growth_rate,
                "acceleration": acceleration,
                "onset_year": onset_year,
            },
        )

    return pd.DataFrame(rows)


def _add_constant(x_matrix: pd.DataFrame) -> pd.DataFrame:
    if HAS_STATSMODELS and sm is not None:
        return sm.add_constant(x_matrix, has_constant="add")

    if "const" in x_matrix.columns:
        return x_matrix.copy()

    constant = pd.Series(1.0, index=x_matrix.index, name="const")
    return pd.concat([constant, x_matrix], axis=1)


def _fit_ols_numpy(y_vector: pd.Series, x_matrix: pd.DataFrame) -> dict[str, Any]:
    x_values = x_matrix.to_numpy(dtype=float)
    y_values = y_vector.to_numpy(dtype=float)

    n_obs, n_params = x_values.shape
    params, _, _, _ = np.linalg.lstsq(x_values, y_values, rcond=None)
    fitted_values = x_values @ params
    residuals = y_values - fitted_values

    rss = float(np.sum(residuals**2))
    tss = float(np.sum((y_values - np.mean(y_values)) ** 2))
    r_squared = None if np.isclose(tss, 0.0) else float(1.0 - (rss / tss))

    df_resid = n_obs - n_params
    if df_resid > 0:
        sigma_sq = rss / df_resid
        xtx_inv = np.linalg.pinv(x_values.T @ x_values)
        cov_params = sigma_sq * xtx_inv
        std_errors = np.sqrt(np.diag(cov_params))
        with np.errstate(divide="ignore", invalid="ignore"):
            t_values = params / std_errors
        p_values = 2.0 * stats.t.sf(np.abs(t_values), df=df_resid)

        if r_squared is not None:
            adj_r_squared = float(1.0 - ((1.0 - r_squared) * (n_obs - 1) / df_resid))
        else:
            adj_r_squared = None
    else:
        std_errors = np.full(n_params, np.nan, dtype=float)
        p_values = np.full(n_params, np.nan, dtype=float)
        adj_r_squared = None

    if n_obs > 0 and rss > 0:
        log_like = -0.5 * n_obs * (np.log(2.0 * np.pi) + 1.0 + np.log(rss / n_obs))
        aic = float((2.0 * n_params) - (2.0 * log_like))
        bic = float((np.log(n_obs) * n_params) - (2.0 * log_like))
    else:
        aic = None
        bic = None

    names = [str(name) for name in x_matrix.columns]
    return {
        "nobs": float(n_obs),
        "rsquared": r_squared,
        "rsquared_adj": adj_r_squared,
        "aic": aic,
        "bic": bic,
        "params": {name: float(params[idx]) for idx, name in enumerate(names)},
        "pvalues": {name: float(p_values[idx]) for idx, name in enumerate(names)},
        "bse": {name: float(std_errors[idx]) for idx, name in enumerate(names)},
    }


def _fit_ols(y_vector: pd.Series, x_matrix: pd.DataFrame) -> dict[str, Any]:
    x_numeric = x_matrix.astype(float)
    y_numeric = y_vector.astype(float)

    if HAS_STATSMODELS and sm is not None:
        fitted = sm.OLS(y_numeric, x_numeric).fit()
        return {
            "nobs": float(fitted.nobs),
            "rsquared": float(fitted.rsquared),
            "rsquared_adj": float(fitted.rsquared_adj),
            "aic": float(fitted.aic),
            "bic": float(fitted.bic),
            "params": {str(k): float(v) for k, v in fitted.params.items()},
            "pvalues": {str(k): float(v) for k, v in fitted.pvalues.items()},
            "bse": {str(k): float(v) for k, v in fitted.bse.items()},
        }

    return _fit_ols_numpy(y_numeric, x_numeric)


def _run_ols_regression(data: pd.DataFrame, outcome_column: str) -> dict[str, Any]:
    model_data = data[[*PREDICTOR_COLUMNS, outcome_column]].dropna().copy()
    if model_data.shape[0] <= len(PREDICTOR_COLUMNS):
        return {
            "outcome": outcome_column,
            "status": "insufficient_data",
            "n_obs": int(model_data.shape[0]),
            "coefficients": None,
            "p_values": None,
            "r_squared": None,
            "adj_r_squared": None,
        }

    x_matrix = _add_constant(model_data[PREDICTOR_COLUMNS])
    y_vector = model_data[outcome_column].astype(float)

    fitted = _fit_ols(y_vector, x_matrix)

    return {
        "outcome": outcome_column,
        "status": "ok",
        "n_obs": int(fitted["nobs"]),
        "r_squared": fitted["rsquared"],
        "adj_r_squared": fitted["rsquared_adj"],
        "aic": fitted["aic"],
        "bic": fitted["bic"],
        "coefficients": fitted["params"],
        "p_values": fitted["pvalues"],
        "std_errors": fitted["bse"],
    }


def analyze_field_characteristics_predictors(
    field_outcomes: pd.DataFrame,
) -> dict[str, Any]:
    characteristics = (
        pd.DataFrame.from_dict(FIELD_CHARACTERISTICS, orient="index")
        .reset_index()
        .rename(columns={"index": "field_name"})
    )

    merged = field_outcomes.merge(characteristics, on="field_name", how="left")
    missing_characteristics = merged.loc[
        merged[PREDICTOR_COLUMNS].isna().any(axis=1),
        "field_name",
    ].tolist()
    if missing_characteristics:
        raise ValueError(
            "Missing field characteristics for: "
            f"{sorted(set(str(v) for v in missing_characteristics))}",
        )

    regression_results = {
        outcome: _run_ols_regression(merged, outcome) for outcome in OUTCOME_COLUMNS
    }

    predictor_correlations = (
        merged[PREDICTOR_COLUMNS].corr().round(4).to_dict(orient="index")
    )

    return {
        "model": (
            "adoption_metric ~ math_intensity + data_availability + experimental "
            "+ regulatory"
        ),
        "field_characteristics": FIELD_CHARACTERISTICS,
        "field_outcomes": merged[
            ["field_name", *OUTCOME_COLUMNS, *PREDICTOR_COLUMNS]
        ].to_dict(orient="records"),
        "predictor_correlations": predictor_correlations,
        "regression_results": regression_results,
    }


def build_inflection_year_lookup(
    s_curve_analysis: dict[str, Any],
    field_outcomes: pd.DataFrame,
) -> dict[str, int]:
    onset_lookup: dict[str, int] = {}
    for _, row in field_outcomes[["field_name", "onset_year"]].iterrows():
        onset_lookup[str(row["field_name"])] = int(float(row["onset_year"]))

    inflection_lookup: dict[str, int] = {}
    for row in s_curve_analysis["field_results"]:
        field_name = str(row["field_name"])
        t0_value = row["t0"]
        if t0_value is None:
            entry_year = onset_lookup.get(field_name, 2016)
        else:
            entry_year = round(float(t0_value))

        clipped_entry = int(
            np.clip(
                entry_year,
                ANALYSIS_START_YEAR + 3,
                ANALYSIS_END_YEAR - 3,
            ),
        )
        inflection_lookup[field_name] = clipped_entry

    return inflection_lookup


def _welch_ci(
    treated: np.ndarray,
    control: np.ndarray,
) -> tuple[float | None, float | None]:
    if treated.size < 2 or control.size < 2:
        return None, None

    mean_diff = float(np.mean(treated) - np.mean(control))
    var_treated = float(np.var(treated, ddof=1))
    var_control = float(np.var(control, ddof=1))

    se_sq = (var_treated / treated.size) + (var_control / control.size)
    if se_sq <= 0:
        return None, None

    numerator = se_sq**2
    denom_left = (var_treated / treated.size) ** 2 / max(treated.size - 1, 1)
    denom_right = (var_control / control.size) ** 2 / max(control.size - 1, 1)
    denominator = denom_left + denom_right
    if denominator <= 0:
        return None, None

    df_welch = numerator / denominator
    t_crit = float(stats.t.ppf(0.975, df_welch))
    se = float(np.sqrt(se_sq))
    return mean_diff - (t_crit * se), mean_diff + (t_crit * se)


def _fit_did_panel_regression(panel_df: pd.DataFrame) -> dict[str, Any]:
    working = panel_df.copy()
    core_terms = working[["treatment_group", "post_treatment", "interaction"]]
    core_terms = core_terms.astype(float)

    field_dummies = pd.get_dummies(
        working["field_name"],
        prefix="field",
        drop_first=True,
        dtype=float,
    )
    year_dummies = pd.get_dummies(
        working["year"].astype(str),
        prefix="year",
        drop_first=True,
        dtype=float,
    )

    x_matrix = pd.concat([core_terms, field_dummies, year_dummies], axis=1)
    x_matrix = _add_constant(x_matrix)
    y_vector = working["ai_fraction"].astype(float)

    fitted = _fit_ols(y_vector, x_matrix)
    key_terms = ["const", "treatment_group", "post_treatment", "interaction"]

    return {
        "formula": "ai_fraction ~ post_treatment * treatment_group + field_FE + year_FE",
        "n_obs": int(fitted["nobs"]),
        "r_squared": fitted["rsquared"],
        "adj_r_squared": fitted["rsquared_adj"],
        "coefficients": {term: fitted["params"].get(term) for term in key_terms},
        "p_values": {term: fitted["pvalues"].get(term) for term in key_terms},
        "std_errors": {term: fitted["bse"].get(term) for term in key_terms},
    }


def run_refined_did_spec(
    df: pd.DataFrame,
    treatment_fields: tuple[str, ...],
    control_fields: tuple[str, ...],
    inflection_lookup: dict[str, int],
) -> dict[str, Any]:
    included_fields = sorted(set(treatment_fields).union(control_fields))
    subset = df[df["field_name"].isin(included_fields)].copy()

    treated_entries = [
        int(inflection_lookup[field])
        for field in treatment_fields
        if field in inflection_lookup
    ]
    if not treated_entries:
        raise ValueError("No valid treatment-entry years available for DID spec.")

    control_entry_year = round(float(np.median(treated_entries)))
    control_entry_year = int(
        np.clip(
            control_entry_year,
            ANALYSIS_START_YEAR + 3,
            ANALYSIS_END_YEAR - 3,
        ),
    )

    entry_year_lookup: dict[str, int] = {}
    for field in included_fields:
        if field in treatment_fields:
            entry_year_lookup[field] = int(inflection_lookup[field])
        else:
            entry_year_lookup[field] = control_entry_year

    subset["treatment_group"] = subset["field_name"].isin(treatment_fields).astype(int)
    subset["entry_year"] = subset["field_name"].map(entry_year_lookup).astype(int)
    subset["post_treatment"] = (subset["year"] >= subset["entry_year"]).astype(int)
    subset["interaction"] = subset["treatment_group"] * subset["post_treatment"]

    field_changes: list[dict[str, Any]] = []
    for field_name, group in subset.groupby("field_name", sort=True):
        entry_year = int(entry_year_lookup[str(field_name)])
        pre = group.loc[group["year"] < entry_year, "ai_fraction"]
        post = group.loc[group["year"] >= entry_year, "ai_fraction"]
        if pre.empty or post.empty:
            continue

        pre_mean = float(pre.mean())
        post_mean = float(post.mean())
        field_changes.append(
            {
                "field_name": str(field_name),
                "group": (
                    "treatment"
                    if str(field_name) in set(treatment_fields)
                    else "control"
                ),
                "entry_year": entry_year,
                "pre_mean_ai_fraction": pre_mean,
                "post_mean_ai_fraction": post_mean,
                "change": post_mean - pre_mean,
            },
        )

    changes_df = pd.DataFrame(field_changes)
    treat_changes = changes_df.loc[
        changes_df["group"] == "treatment",
        "change",
    ].to_numpy(dtype=float)
    control_changes = changes_df.loc[
        changes_df["group"] == "control",
        "change",
    ].to_numpy(dtype=float)

    if treat_changes.size > 0 and control_changes.size > 0:
        att = float(np.mean(treat_changes) - np.mean(control_changes))
    else:
        att = None

    if treat_changes.size >= 2 and control_changes.size >= 2:
        t_stat_raw, p_value_raw = stats.ttest_ind(
            treat_changes,
            control_changes,
            equal_var=False,
        )
        t_stat = float(np.asarray(t_stat_raw).item())
        p_value = float(np.asarray(p_value_raw).item())
    else:
        t_stat = None
        p_value = None

    ci_low, ci_high = _welch_ci(treat_changes, control_changes)
    panel_regression = _fit_did_panel_regression(subset)

    return {
        "treatment_fields": list(treatment_fields),
        "control_fields": list(control_fields),
        "staggered_treatment_years": {
            field: entry_year_lookup[field] for field in treatment_fields
        },
        "control_post_reference_year": control_entry_year,
        "att": att,
        "att_pct_points": (att * 100.0) if att is not None else None,
        "welch_t_test": {
            "t_statistic": t_stat,
            "p_value": p_value,
        },
        "att_95_ci": [ci_low, ci_high] if ci_low is not None else None,
        "field_level_changes": field_changes,
        "panel_regression": panel_regression,
    }


def analyze_refined_did(
    df: pd.DataFrame,
    inflection_lookup: dict[str, int],
) -> dict[str, Any]:
    spec_results: dict[str, Any] = {}
    for spec_name, spec in DID_SPECS.items():
        spec_results[spec_name] = run_refined_did_spec(
            df=df,
            treatment_fields=spec["treatment"],
            control_fields=spec["control"],
            inflection_lookup=inflection_lookup,
        )

    return {
        "method": (
            "Staggered-treatment DID with field-specific treatment-entry years, "
            "Welch tests on field-level changes, and FE panel regressions."
        ),
        "all_field_inflection_years": inflection_lookup,
        "specifications": spec_results,
    }


def _zscore_series(series: pd.Series) -> pd.Series:
    values = series.to_numpy(dtype=float)
    std = float(np.std(values))
    if np.isclose(std, 0.0):
        return pd.Series(np.zeros_like(values), index=series.index)
    mean = float(np.mean(values))
    return (series - mean) / std


def _mean_or_none(values: list[float | None]) -> float | None:
    valid = [float(v) for v in values if v is not None]
    if not valid:
        return None
    return float(np.mean(valid))


def analyze_adoption_trajectory_clustering(
    df: pd.DataFrame,
    s_curve_analysis: dict[str, Any],
) -> dict[str, Any]:
    pivot = df.pivot_table(index="year", columns="field_name", values="ai_fraction")
    pivot = pivot.sort_index().fillna(0.0)

    normalized = pivot.apply(_zscore_series, axis=0)
    corr_matrix = normalized.corr()
    fields = corr_matrix.columns.to_list()

    corr_values = corr_matrix.to_numpy(dtype=float)
    distance_values = np.clip(1.0 - corr_values, 0.0, 2.0)
    np.fill_diagonal(distance_values, 0.0)

    condensed = distance.squareform(distance_values, checks=False)
    linkage_matrix = hierarchy.linkage(condensed, method="average")
    cluster_labels = hierarchy.fcluster(linkage_matrix, t=4, criterion="maxclust")

    assignment_df = pd.DataFrame(
        {
            "field_name": fields,
            "cluster_id": cluster_labels,
        },
    ).sort_values(["cluster_id", "field_name"])
    assignment_df["cluster_id"] = assignment_df["cluster_id"].astype(int)

    scurve_lookup = {
        str(row["field_name"]): row for row in s_curve_analysis["field_results"]
    }

    cluster_type_lookup: dict[int, str] = {}
    cluster_summaries: list[dict[str, Any]] = []
    cluster_ids = sorted(assignment_df["cluster_id"].unique().tolist())
    for cluster_id_int in cluster_ids:
        group = assignment_df[assignment_df["cluster_id"] == cluster_id_int]
        cluster_fields = [str(v) for v in group["field_name"].tolist()]
        k_mean = _mean_or_none(
            [
                scurve_lookup[field].get("K")
                for field in cluster_fields
                if field in scurve_lookup
            ],
        )
        r_mean = _mean_or_none(
            [
                scurve_lookup[field].get("r")
                for field in cluster_fields
                if field in scurve_lookup
            ],
        )
        t0_mean = _mean_or_none(
            [
                scurve_lookup[field].get("t0")
                for field in cluster_fields
                if field in scurve_lookup
            ],
        )
        r2_mean = _mean_or_none(
            [
                scurve_lookup[field].get("r_squared")
                for field in cluster_fields
                if field in scurve_lookup
            ],
        )

        cluster_type = classify_adoption_type(
            k=k_mean,
            r=r_mean,
            t0=t0_mean,
            r_squared=r2_mean,
        )
        cluster_type_lookup[cluster_id_int] = cluster_type

        cluster_summaries.append(
            {
                "cluster_id": cluster_id_int,
                "cluster_type": cluster_type,
                "n_fields": len(cluster_fields),
                "fields": cluster_fields,
                "cluster_mean_K": k_mean,
                "cluster_mean_r": r_mean,
                "cluster_mean_t0": t0_mean,
                "cluster_mean_r_squared": r2_mean,
            },
        )

    assignments: list[dict[str, Any]] = []
    for field_name, cluster_id in zip(
        assignment_df["field_name"].tolist(),
        assignment_df["cluster_id"].tolist(),
        strict=True,
    ):
        cluster_id_int = int(cluster_id)
        assignments.append(
            {
                "field_name": str(field_name),
                "cluster_id": cluster_id_int,
                "cluster_type": cluster_type_lookup[cluster_id_int],
                "s_curve_type": scurve_lookup.get(
                    str(field_name),
                    {},
                ).get("adoption_type"),
            },
        )

    dendrogram = hierarchy.dendrogram(
        linkage_matrix,
        labels=fields,
        no_plot=True,
    )
    leaves = dendrogram.get("leaves") or []
    labels = dendrogram.get("ivl") or []
    icoord = dendrogram.get("icoord") or []
    dcoord = dendrogram.get("dcoord") or []
    color_list = dendrogram.get("color_list") or []

    dendrogram_data = {
        "leaves": [int(v) for v in leaves],
        "labels": [str(v) for v in labels],
        "icoord": [[float(x) for x in row] for row in icoord],
        "dcoord": [[float(x) for x in row] for row in dcoord],
        "color_list": [str(v) for v in color_list],
    }

    return {
        "normalization": "z_score",
        "distance": "1 - correlation",
        "linkage_method": "average",
        "n_clusters": 4,
        "cluster_summaries": cluster_summaries,
        "cluster_assignments": assignments,
        "correlation_matrix": corr_matrix.to_dict(orient="index"),
        "dendrogram": dendrogram_data,
    }


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
    if isinstance(value, np.bool_ | bool):
        return bool(value)
    if isinstance(value, np.integer | int):
        return int(value)
    if value is None:
        return None
    if pd.isna(value):
        return None
    return value


def _format_metric(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not np.isfinite(numeric):
        return "NA"
    return f"{numeric:.{digits}f}"


def print_summary(results: dict[str, Any]) -> None:
    print("=" * 88)
    print("AI ADOPTION DEEP ANALYSIS (TRACK 1, 2000-2024)")
    print("=" * 88)

    analysis_1 = results["analysis_1_s_curve_fitting"]
    analysis_2 = results["analysis_2_biology_deep_dive"]
    analysis_3 = results["analysis_3_field_characteristics_predictors"]
    analysis_4 = results["analysis_4_refined_did"]
    analysis_5 = results["analysis_5_trajectory_clustering"]

    print("\n[1] S-curve fitting by field")
    s_curve_df = pd.DataFrame(analysis_1["field_results"])
    for col in ["K", "r", "t0", "r_squared"]:
        s_curve_df[col] = s_curve_df[col].map(_format_metric)
    print(
        s_curve_df[
            [
                "field_name",
                "K",
                "r",
                "t0",
                "r_squared",
                "adoption_type",
                "fit_status",
            ]
        ].to_string(index=False),
    )

    print("\n[2] Biology deep-dive proxy metrics")
    breakout = analysis_2["rolling_3y_growth"]
    print(
        "Breakout score = max(3y growth) / median(3y growth): "
        f"{_format_metric(breakout['breakout_score'])}"
    )
    best_break = analysis_2["structural_break_detection"]["best_break"]
    if best_break is not None:
        print(
            "Best structural break: "
            f"{best_break['break_year']} "
            f"(F={_format_metric(best_break['f_statistic'])}, "
            f"p={_format_metric(best_break['p_value'])})"
        )

    compare_df = pd.DataFrame(analysis_2["comparative_fields"])
    compare_df["pearson_vs_biology"] = compare_df["pearson_vs_biology"].map(
        _format_metric,
    )
    compare_df["gap_vs_biology_2024"] = compare_df["gap_vs_biology_2024"].map(
        _format_metric,
    )
    print(
        compare_df[
            ["field_name", "pearson_vs_biology", "gap_vs_biology_2024"]
        ].to_string(index=False),
    )

    print("\n[3] Field-characteristics predictor regressions")
    regression_rows: list[dict[str, Any]] = []
    for outcome, details in analysis_3["regression_results"].items():
        coeffs = details.get("coefficients")
        pvals = details.get("p_values")
        regression_rows.append(
            {
                "outcome": outcome,
                "r_squared": _format_metric(details.get("r_squared")),
                "coef_math": _format_metric(
                    coeffs.get("math_intensity") if isinstance(coeffs, dict) else None
                ),
                "p_math": _format_metric(
                    pvals.get("math_intensity") if isinstance(pvals, dict) else None
                ),
                "coef_data": _format_metric(
                    coeffs.get("data_availability")
                    if isinstance(coeffs, dict)
                    else None
                ),
                "p_data": _format_metric(
                    pvals.get("data_availability") if isinstance(pvals, dict) else None
                ),
            },
        )
    print(pd.DataFrame(regression_rows).to_string(index=False))

    print("\n[4] Refined DID (staggered timing)")
    for spec_name, spec in analysis_4["specifications"].items():
        print(
            f"{spec_name}: ATT={_format_metric(spec['att'])} "
            f"({_format_metric(spec['att_pct_points'])} pct-points), "
            f"Welch p={_format_metric(spec['welch_t_test']['p_value'])}"
        )
        interaction_coef = spec["panel_regression"]["coefficients"].get("interaction")
        interaction_p = spec["panel_regression"]["p_values"].get("interaction")
        print(
            "  FE interaction coef="
            f"{_format_metric(interaction_coef)}, "
            f"p={_format_metric(interaction_p)}"
        )

    print("\n[5] Adoption trajectory clustering")
    cluster_df = pd.DataFrame(analysis_5["cluster_assignments"])
    print(cluster_df.sort_values(["cluster_id", "field_name"]).to_string(index=False))

    print("=" * 88)
    print(f"Results saved to: {OUTPUT_PATH}")


def main() -> None:
    df = load_and_prepare_data(INPUT_PATH)

    analysis_1 = analyze_s_curve_fitting(df)
    biology_deep_dive = analyze_biology_deep_dive(df)
    field_outcomes = build_field_outcomes(df)
    analysis_3 = analyze_field_characteristics_predictors(field_outcomes)

    inflection_lookup = build_inflection_year_lookup(
        s_curve_analysis=analysis_1,
        field_outcomes=field_outcomes,
    )
    analysis_4 = analyze_refined_did(df, inflection_lookup)
    analysis_5 = analyze_adoption_trajectory_clustering(df, analysis_1)

    results: dict[str, Any] = {
        "metadata": {
            "input_path": str(INPUT_PATH),
            "output_path": str(OUTPUT_PATH),
            "years_analyzed": [ANALYSIS_START_YEAR, ANALYSIS_END_YEAR],
            "n_fields": int(df["field_name"].nunique()),
            "n_rows": len(df),
            "statsmodels_available": HAS_STATSMODELS,
        },
        "analysis_1_s_curve_fitting": analysis_1,
        "analysis_2_biology_deep_dive": biology_deep_dive,
        "analysis_3_field_characteristics_predictors": analysis_3,
        "analysis_4_refined_did": analysis_4,
        "analysis_5_trajectory_clustering": analysis_5,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(_to_native(results), indent=2, ensure_ascii=True),
        encoding="utf-8",
    )

    print_summary(results)


if __name__ == "__main__":
    main()
