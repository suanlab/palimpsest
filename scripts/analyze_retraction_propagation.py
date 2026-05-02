#!/usr/bin/env python3
"""Analyze retraction contamination propagation from collected citation data."""
# pyright: reportAny=false, reportExplicitAny=false, reportUnknownArgumentType=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportCallIssue=false, reportArgumentType=false, reportOperatorIssue=false, reportUnusedCallResult=false

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

DATA_DIR = Path("data/processed")

RETRACTED_PATH = DATA_DIR / "retracted_papers.parquet"
CITERS_PATH = DATA_DIR / "retraction_citers.parquet"
STATS_PATH = DATA_DIR / "retraction_propagation_stats.parquet"
REFERENCES_PATH = DATA_DIR / "retraction_references.parquet"

OUTPUT_JSON_PATH = DATA_DIR / "retraction_analysis.json"

PERCENTILES: tuple[float, ...] = (0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95)


def _to_python_native(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _to_python_native(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_to_python_native(v) for v in value]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if pd.isna(value):
        return None
    return value


def _safe_int_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0).astype(int)


def _safe_float_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def load_data() -> dict[str, pd.DataFrame]:
    return {
        "retracted": pd.read_parquet(RETRACTED_PATH),
        "citers": pd.read_parquet(CITERS_PATH),
        "stats": pd.read_parquet(STATS_PATH),
        "references": pd.read_parquet(REFERENCES_PATH),
    }


def _distribution_stats(values: pd.Series) -> dict[str, Any]:
    cleaned = _safe_float_series(values).dropna()
    if cleaned.empty:
        return {
            "count": 0,
            "mean": 0.0,
            "median": 0.0,
            "max": 0.0,
            "min": 0.0,
            "std": 0.0,
            "percentiles": {f"p{int(p * 100)}": 0.0 for p in PERCENTILES},
        }

    percentile_values = {
        f"p{int(p * 100)}": float(cleaned.quantile(p)) for p in PERCENTILES
    }
    return {
        "count": int(cleaned.shape[0]),
        "mean": float(cleaned.mean()),
        "median": float(cleaned.median()),
        "max": float(cleaned.max()),
        "min": float(cleaned.min()),
        "std": float(cleaned.std(ddof=0)),
        "percentiles": percentile_values,
    }


def analyze_contamination_scale(
    citers_df: pd.DataFrame,
) -> tuple[dict[str, Any], pd.DataFrame]:
    working = citers_df.copy()
    working["citing_cited_by_count"] = _safe_int_series(
        working["citing_cited_by_count"]
    )

    total_direct_rows = len(working)
    total_unique_direct_citers = int(working["citing_openalex_id"].nunique(dropna=True))

    per_retracted = (
        working.groupby(["retracted_openalex_id", "retracted_doi"], as_index=False)
        .agg(
            direct_citers_count=("citing_openalex_id", "nunique"),
            two_hop_reach_estimate=("citing_cited_by_count", "sum"),
            avg_citer_citations=("citing_cited_by_count", "mean"),
        )
        .sort_values("direct_citers_count", ascending=False)
    )
    per_retracted["avg_citer_citations"] = (
        _safe_float_series(per_retracted["avg_citer_citations"]).fillna(0.0).round(3)
    )

    distribution = _distribution_stats(per_retracted["direct_citers_count"])
    total_two_hop_reach_estimate = int(per_retracted["two_hop_reach_estimate"].sum())

    analysis = {
        "total_direct_citation_rows": total_direct_rows,
        "total_unique_direct_citers": total_unique_direct_citers,
        "retracted_papers_with_citers": int(per_retracted.shape[0]),
        "direct_citers_distribution": distribution,
        "total_two_hop_reach_estimate": total_two_hop_reach_estimate,
        "mean_two_hop_reach_estimate_per_retracted": float(
            per_retracted["two_hop_reach_estimate"].mean()
        )
        if not per_retracted.empty
        else 0.0,
        "top_retracted_by_two_hop_reach": per_retracted.nlargest(
            10,
            "two_hop_reach_estimate",
        ).to_dict(orient="records"),
    }
    return analysis, per_retracted


def _build_5y_windows(years_since_pub: pd.Series) -> pd.Series:
    cleaned = _safe_int_series(years_since_pub)
    bins = cleaned // 5
    return bins


def _half_life_year(citation_years: pd.Series, publication_year: int) -> int | None:
    cleaned = pd.to_numeric(citation_years, errors="coerce").dropna().astype(int)
    if cleaned.empty:
        return None

    yearly_counts = cleaned.value_counts().sort_index()
    cumulative = yearly_counts.cumsum()
    threshold = cumulative.iloc[-1] * 0.5
    reached_year = int(cumulative[cumulative >= threshold].index[0])
    return reached_year - publication_year


def analyze_temporal_self_correction(
    citers_df: pd.DataFrame,
    stats_df: pd.DataFrame,
) -> tuple[dict[str, Any], pd.DataFrame]:
    stats_51 = stats_df[stats_df["doi"] != "__ALL__"].copy()
    stats_51["publication_year"] = _safe_int_series(stats_51["publication_year"])

    temporal_rows: list[dict[str, Any]] = []
    for row in stats_51.itertuples(index=False):
        paper_citers = citers_df[
            citers_df["retracted_openalex_id"] == row.openalex_id
        ].copy()
        if paper_citers.empty:
            temporal_rows.append(
                {
                    "retracted_openalex_id": row.openalex_id,
                    "doi": row.doi,
                    "publication_year": int(row.publication_year),
                    "total_observed_citations": 0,
                    "half_life_years": None,
                    "window_counts": {},
                    "window_slope": 0.0,
                    "recent_vs_previous_ratio": None,
                    "decline_signal": False,
                },
            )
            continue

        paper_citers["citing_year"] = pd.to_numeric(
            paper_citers["citing_year"],
            errors="coerce",
        )
        paper_citers = paper_citers.dropna(subset=["citing_year"])
        paper_citers["citing_year"] = paper_citers["citing_year"].astype(int)

        if paper_citers.empty:
            temporal_rows.append(
                {
                    "retracted_openalex_id": row.openalex_id,
                    "doi": row.doi,
                    "publication_year": int(row.publication_year),
                    "total_observed_citations": 0,
                    "half_life_years": None,
                    "window_counts": {},
                    "window_slope": 0.0,
                    "recent_vs_previous_ratio": None,
                    "decline_signal": False,
                },
            )
            continue

        pub_year = int(row.publication_year)
        paper_citers["years_since_publication"] = paper_citers["citing_year"] - pub_year

        windows = _build_5y_windows(paper_citers["years_since_publication"])
        window_counts = windows.value_counts().sort_index()
        window_labels = {
            f"{int(window) * 5}-{int(window) * 5 + 4}": int(count)
            for window, count in window_counts.items()
        }

        if len(window_counts) >= 2:
            x = window_counts.index.to_numpy(dtype=float)
            y = window_counts.to_numpy(dtype=float)
            slope = float(np.polyfit(x, y, 1)[0])
        else:
            slope = 0.0

        if len(window_counts) >= 4:
            previous = float(window_counts.iloc[-4:-2].sum())
            recent = float(window_counts.iloc[-2:].sum())
            recent_ratio = (recent / previous) if previous > 0 else None
        elif len(window_counts) >= 2:
            previous = float(window_counts.iloc[:-1].sum())
            recent = float(window_counts.iloc[-1])
            recent_ratio = (recent / previous) if previous > 0 else None
        else:
            recent_ratio = None

        half_life = _half_life_year(paper_citers["citing_year"], pub_year)
        decline_signal = bool(
            (slope < 0) and (recent_ratio is not None) and (recent_ratio < 1.0)
        )

        temporal_rows.append(
            {
                "retracted_openalex_id": row.openalex_id,
                "doi": row.doi,
                "publication_year": pub_year,
                "total_observed_citations": len(paper_citers),
                "half_life_years": half_life,
                "window_counts": window_labels,
                "window_slope": slope,
                "recent_vs_previous_ratio": recent_ratio,
                "decline_signal": decline_signal,
            },
        )

    temporal_df = pd.DataFrame(temporal_rows)
    half_life_distribution = _distribution_stats(temporal_df["half_life_years"])

    analysis = {
        "papers_analyzed": len(temporal_df),
        "papers_with_decline_signal": int(temporal_df["decline_signal"].sum()),
        "decline_signal_rate": float(temporal_df["decline_signal"].mean())
        if not temporal_df.empty
        else 0.0,
        "half_life_distribution_years": half_life_distribution,
        "fastest_half_life_papers": temporal_df.sort_values(
            "half_life_years",
            na_position="last",
        )
        .head(10)
        .to_dict(orient="records"),
        "slowest_half_life_papers": temporal_df.sort_values(
            "half_life_years",
            na_position="last",
            ascending=False,
        )
        .head(10)
        .to_dict(orient="records"),
    }
    return analysis, temporal_df


def analyze_contamination_severity(
    per_retracted_scale_df: pd.DataFrame,
) -> tuple[dict[str, Any], pd.DataFrame]:
    severity_df = per_retracted_scale_df.copy()
    severity_df["severity"] = _safe_float_series(
        severity_df["direct_citers_count"]
    ) * _safe_float_series(severity_df["avg_citer_citations"])
    severity_df["severity"] = _safe_float_series(severity_df["severity"]).fillna(0.0)

    ranked = severity_df.sort_values("severity", ascending=False).reset_index(drop=True)
    ranked["rank"] = np.arange(1, len(ranked) + 1)

    analysis = {
        "severity_formula": "direct_citers_count * avg_citer_citations",
        "severity_distribution": _distribution_stats(ranked["severity"]),
        "top_20_by_severity": ranked.head(20).to_dict(orient="records"),
    }
    return analysis, ranked


def analyze_field_distribution_proxy(
    citers_df: pd.DataFrame,
    retracted_df: pd.DataFrame,
) -> dict[str, Any]:
    citing_year_counts = (
        pd.to_numeric(citers_df["citing_year"], errors="coerce")
        .dropna()
        .astype(int)
        .value_counts()
        .sort_index()
    )

    retracted_year_counts = (
        pd.to_numeric(retracted_df["publication_year"], errors="coerce")
        .dropna()
        .astype(int)
        .value_counts()
        .sort_index()
    )

    citing_decade_counts = (
        pd.DataFrame(
            {
                "citing_year": citing_year_counts.index,
                "count": citing_year_counts.values,
            }
        )
        .assign(decade=lambda d: (d["citing_year"] // 10) * 10)
        .groupby("decade", as_index=False)["count"]
        .sum()
        .sort_values("count", ascending=False)
    )

    retracted_decade_counts = (
        pd.DataFrame(
            {
                "publication_year": retracted_year_counts.index,
                "count": retracted_year_counts.values,
            },
        )
        .assign(decade=lambda d: (d["publication_year"] // 10) * 10)
        .groupby("decade", as_index=False)["count"]
        .sum()
        .sort_values("count", ascending=False)
    )

    return {
        "note": (
            "Field labels are unavailable in current Track 3 files; this section uses "
            "temporal distribution proxies to locate where contamination pressure is concentrated."
        ),
        "citing_year_distribution": {
            str(int(year)): int(count) for year, count in citing_year_counts.items()
        },
        "citing_decade_distribution": citing_decade_counts.to_dict(orient="records"),
        "retracted_publication_year_distribution": {
            str(int(year)): int(count) for year, count in retracted_year_counts.items()
        },
        "retracted_publication_decade_distribution": retracted_decade_counts.to_dict(
            orient="records"
        ),
    }


def _build_velocity_rows(
    citers_df: pd.DataFrame,
    stats_df: pd.DataFrame,
) -> pd.DataFrame:
    stats_51 = stats_df[stats_df["doi"] != "__ALL__"].copy()
    stats_51["publication_year"] = _safe_int_series(stats_51["publication_year"])

    rows: list[dict[str, Any]] = []
    for row in stats_51.itertuples(index=False):
        paper_citers = citers_df[
            citers_df["retracted_openalex_id"] == row.openalex_id
        ].copy()
        paper_citers["citing_year"] = pd.to_numeric(
            paper_citers["citing_year"],
            errors="coerce",
        )
        paper_citers = paper_citers.dropna(subset=["citing_year"])

        if paper_citers.empty:
            rows.append(
                {
                    "retracted_openalex_id": row.openalex_id,
                    "doi": row.doi,
                    "publication_year": int(row.publication_year),
                    "observed_citations": 0,
                    "max_age": 0,
                    "early_5y_fraction": 0.0,
                    "avg_annual_velocity": 0.0,
                    "velocity_curve": {},
                },
            )
            continue

        paper_citers["citing_year"] = paper_citers["citing_year"].astype(int)
        publication_year = int(row.publication_year)
        paper_citers["age"] = paper_citers["citing_year"] - publication_year

        paper_citers = paper_citers[paper_citers["age"] >= 0]
        if paper_citers.empty:
            rows.append(
                {
                    "retracted_openalex_id": row.openalex_id,
                    "doi": row.doi,
                    "publication_year": publication_year,
                    "observed_citations": 0,
                    "max_age": 0,
                    "early_5y_fraction": 0.0,
                    "avg_annual_velocity": 0.0,
                    "velocity_curve": {},
                },
            )
            continue

        age_counts = paper_citers["age"].value_counts().sort_index()
        cumulative = age_counts.cumsum()
        total = int(cumulative.iloc[-1])
        cumulative_fraction = (cumulative / total).to_dict()

        early_count = int(age_counts[age_counts.index <= 5].sum())
        max_age = int(age_counts.index.max())
        years_active = max_age + 1
        avg_annual_velocity = float(total / years_active) if years_active > 0 else 0.0

        rows.append(
            {
                "retracted_openalex_id": row.openalex_id,
                "doi": row.doi,
                "publication_year": publication_year,
                "observed_citations": total,
                "max_age": max_age,
                "early_5y_fraction": float(early_count / total) if total > 0 else 0.0,
                "avg_annual_velocity": avg_annual_velocity,
                "velocity_curve": {
                    str(int(age)): float(frac)
                    for age, frac in sorted(
                        cumulative_fraction.items(), key=lambda x: x[0]
                    )
                },
            },
        )

    return pd.DataFrame(rows)


def _compute_reference_velocity_curve(velocity_df: pd.DataFrame) -> dict[str, float]:
    points: dict[int, list[float]] = {}
    for curve in velocity_df["velocity_curve"]:
        if not isinstance(curve, dict):
            continue
        for age_str, frac in curve.items():
            try:
                age = int(age_str)
                value = float(frac)
            except (TypeError, ValueError):
                continue
            points.setdefault(age, []).append(value)

    median_curve = {
        str(age): float(np.median(values)) for age, values in sorted(points.items())
    }
    return median_curve


def analyze_citation_velocity(
    citers_df: pd.DataFrame,
    stats_df: pd.DataFrame,
) -> tuple[dict[str, Any], pd.DataFrame]:
    velocity_df = _build_velocity_rows(citers_df=citers_df, stats_df=stats_df)
    reference_curve = _compute_reference_velocity_curve(velocity_df)

    early_stats = _distribution_stats(velocity_df["early_5y_fraction"])
    velocity_stats = _distribution_stats(velocity_df["avg_annual_velocity"])

    early_mean = (
        float(velocity_df["early_5y_fraction"].mean()) if not velocity_df.empty else 0.0
    )
    early_std = (
        float(velocity_df["early_5y_fraction"].std(ddof=0))
        if not velocity_df.empty
        else 0.0
    )
    if early_std > 0:
        velocity_df["early_5y_zscore"] = (
            velocity_df["early_5y_fraction"] - early_mean
        ) / early_std
    else:
        velocity_df["early_5y_zscore"] = 0.0

    unusually_fast = velocity_df[velocity_df["early_5y_zscore"] >= 2.0].copy()
    unusually_slow = velocity_df[velocity_df["early_5y_zscore"] <= -2.0].copy()

    analysis = {
        "reference_median_cumulative_curve": reference_curve,
        "early_5y_fraction_distribution": early_stats,
        "avg_annual_velocity_distribution": velocity_stats,
        "unusually_fast_early_citation_papers": unusually_fast.sort_values(
            "early_5y_zscore",
            ascending=False,
        )
        .head(20)
        .to_dict(orient="records"),
        "unusually_slow_early_citation_papers": unusually_slow.sort_values(
            "early_5y_zscore",
            ascending=True,
        )
        .head(20)
        .to_dict(orient="records"),
    }
    return analysis, velocity_df


def _print_section(title: str) -> None:
    print(f"\n{'=' * 24} {title} {'=' * 24}")


def print_summary_tables(
    contamination_scale: dict[str, Any],
    severity_df: pd.DataFrame,
    temporal_df: pd.DataFrame,
    velocity_df: pd.DataFrame,
) -> None:
    _print_section("Analysis 1: Contamination Scale")
    summary_rows = [
        {
            "metric": "total_direct_citation_rows",
            "value": contamination_scale["total_direct_citation_rows"],
        },
        {
            "metric": "total_unique_direct_citers",
            "value": contamination_scale["total_unique_direct_citers"],
        },
        {
            "metric": "total_two_hop_reach_estimate",
            "value": contamination_scale["total_two_hop_reach_estimate"],
        },
    ]
    print(pd.DataFrame(summary_rows).to_string(index=False))

    dist = contamination_scale["direct_citers_distribution"]
    percentile_rows = [
        {"stat": "mean", "value": dist["mean"]},
        {"stat": "median", "value": dist["median"]},
        {"stat": "max", "value": dist["max"]},
    ] + [{"stat": k, "value": v} for k, v in dist["percentiles"].items()]
    print("\nDirect citers per retracted paper distribution:")
    print(pd.DataFrame(percentile_rows).to_string(index=False))

    _print_section("Analysis 3: Contamination Severity (Top 15)")
    cols = [
        "rank",
        "retracted_doi",
        "direct_citers_count",
        "avg_citer_citations",
        "severity",
    ]
    print(severity_df[cols].head(15).to_string(index=False))

    _print_section("Analysis 2: Temporal Self-Correction")
    temporal_cols = [
        "doi",
        "publication_year",
        "total_observed_citations",
        "half_life_years",
        "window_slope",
        "recent_vs_previous_ratio",
        "decline_signal",
    ]
    print(
        temporal_df[temporal_cols]
        .sort_values("half_life_years")
        .head(15)
        .to_string(index=False)
    )

    _print_section("Analysis 5: Citation Velocity")
    velocity_cols = [
        "doi",
        "publication_year",
        "observed_citations",
        "max_age",
        "early_5y_fraction",
        "avg_annual_velocity",
        "early_5y_zscore",
    ]
    print(
        velocity_df[velocity_cols]
        .sort_values("early_5y_fraction", ascending=False)
        .head(15)
        .to_string(index=False),
    )


def build_analysis_payload(
    data_frames: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    retracted_df = data_frames["retracted"]
    citers_df = data_frames["citers"]
    stats_df = data_frames["stats"]
    references_df = data_frames["references"]

    contamination_scale, per_retracted_scale_df = analyze_contamination_scale(citers_df)
    temporal_analysis, temporal_df = analyze_temporal_self_correction(
        citers_df, stats_df
    )
    severity_analysis, severity_df = analyze_contamination_severity(
        per_retracted_scale_df
    )
    field_proxy_analysis = analyze_field_distribution_proxy(citers_df, retracted_df)
    velocity_analysis, velocity_df = analyze_citation_velocity(citers_df, stats_df)

    print_summary_tables(
        contamination_scale=contamination_scale,
        severity_df=severity_df,
        temporal_df=temporal_df,
        velocity_df=velocity_df,
    )

    payload = {
        "meta": {
            "data_files": {
                "retracted_papers": str(RETRACTED_PATH),
                "retraction_citers": str(CITERS_PATH),
                "retraction_propagation_stats": str(STATS_PATH),
                "retraction_references": str(REFERENCES_PATH),
            },
            "row_counts": {
                "retracted_papers": len(retracted_df),
                "retraction_citers": len(citers_df),
                "retraction_propagation_stats": len(stats_df),
                "retraction_references": len(references_df),
            },
        },
        "analysis_1_contamination_scale": contamination_scale,
        "analysis_2_temporal_self_correction": temporal_analysis,
        "analysis_3_contamination_severity": severity_analysis,
        "analysis_4_field_distribution_proxy": field_proxy_analysis,
        "analysis_5_citation_velocity": velocity_analysis,
        "tables": {
            "per_retracted_scale": per_retracted_scale_df.to_dict(orient="records"),
            "temporal_per_retracted": temporal_df.to_dict(orient="records"),
            "severity_per_retracted": severity_df.to_dict(orient="records"),
            "velocity_per_retracted": velocity_df.to_dict(orient="records"),
        },
    }
    return _to_python_native(payload)


def main() -> None:
    data_frames = load_data()
    payload = build_analysis_payload(data_frames)
    OUTPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )

    _print_section("Output")
    print(f"Saved analysis JSON: {OUTPUT_JSON_PATH}")


if __name__ == "__main__":
    main()
