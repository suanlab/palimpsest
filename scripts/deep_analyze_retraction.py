#!/usr/bin/env python3
# pyright: basic, reportMissingImports=false
"""Run deep Track 3 analysis for retraction contamination."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

try:
    import statsmodels.api as sm

    HAS_STATSMODELS = True
except ModuleNotFoundError:
    sm = None
    HAS_STATSMODELS = False

DATA_DIR = Path("data/processed")

RETRACTED_PATH = DATA_DIR / "retracted_papers.parquet"
CITERS_PATH = DATA_DIR / "retraction_citers.parquet"
STATS_PATH = DATA_DIR / "retraction_propagation_stats.parquet"
REFERENCES_PATH = DATA_DIR / "retraction_references.parquet"

OUTPUT_JSON_PATH = DATA_DIR / "retraction_deep_analysis.json"

PERCENTILES: tuple[float, ...] = (0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95)
DEFAULT_MEDIAN_RETRACTION_LAG_YEARS = 5

DOI_FIELD_PREFIX_MAP: dict[str, str] = {
    "10.1001": "Medicine",
    "10.1056": "Medicine",
    "10.1097": "Medicine",
    "10.1093": "Biology & Medicine",
    "10.1021": "Chemistry",
    "10.1103": "Physics",
    "10.1109": "Engineering & Computer Science",
    "10.1145": "Computer Science",
    "10.1126": "Multidisciplinary Science",
    "10.1038": "Multidisciplinary Science",
    "10.1016": "Medicine & Life Sciences",
    "10.1002": "Life Sciences",
}

FIELD_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Medicine": (
        "clinical",
        "patient",
        "cancer",
        "tumor",
        "disease",
        "therapy",
        "treatment",
        "surgery",
        "hospital",
        "drug",
        "stroke",
        "fracture",
        "nausea",
        "vomiting",
        "cardio",
        "diabetes",
        "infection",
        "trial",
    ),
    "Biology": (
        "protein",
        "gene",
        "cell",
        "dna",
        "rna",
        "genome",
        "enzyme",
        "molecular",
        "pathway",
        "neuro",
        "dopamine",
        "huntington",
    ),
    "Chemistry": (
        "chemical",
        "synthesis",
        "catalyst",
        "compound",
        "polymer",
        "electrochemical",
        "spectroscopy",
        "nanoparticle",
        "adsorption",
    ),
    "Physics": (
        "quantum",
        "photon",
        "superconduct",
        "magnetic",
        "particle",
        "lattice",
        "spin",
        "relativity",
        "thermodynamic",
    ),
    "Computer Science": (
        "algorithm",
        "machine learning",
        "deep learning",
        "neural network",
        "computer",
        "classification",
        "prediction",
        "optimization",
        "data mining",
    ),
    "Engineering": (
        "engineering",
        "mechanical",
        "electrical",
        "sensor",
        "material",
        "robot",
        "manufacturing",
    ),
    "Psychology & Social Science": (
        "behavior",
        "social",
        "psychology",
        "education",
        "economics",
        "policy",
        "survey",
        "school",
        "lunch",
    ),
    "Environmental Science": (
        "climate",
        "ecology",
        "environment",
        "soil",
        "water",
        "pollution",
        "atmospheric",
    ),
}


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


def _to_int(value: Any, default: int = 0) -> int:
    converted = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(converted):
        return default
    return int(converted)


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


def _extract_year_from_date_like(value: Any) -> int | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return int(value.year)

    text = str(value).strip()
    if not text:
        return None

    parsed = pd.to_datetime(text, errors="coerce")
    if pd.isna(parsed):
        return None
    return int(parsed.year)


def _linear_slope(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 2 or y.size < 2:
        return 0.0
    try:
        return float(np.polyfit(x, y, 1)[0])
    except (TypeError, ValueError, np.linalg.LinAlgError):
        return 0.0


def _years_to_reach_fraction(
    year_counts: pd.Series,
    fraction: float,
    origin_year: int,
) -> int | None:
    if year_counts.empty:
        return None

    cumulative = year_counts.sort_index().cumsum()
    threshold = cumulative.iloc[-1] * fraction
    reached = cumulative[cumulative >= threshold]
    if reached.empty:
        return None
    reached_year = int(reached.index[0])
    return reached_year - origin_year


def _normalize_doi(doi: str) -> str:
    lowered = doi.strip().lower()
    return lowered.replace("https://doi.org/", "")


def _classify_field_from_keyword_text(text: str) -> str | None:
    lowered = text.lower()
    for field, keywords in FIELD_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return field
    return None


def _extract_field_from_concepts(value: Any) -> str | None:
    candidates: list[str] = []

    if isinstance(value, list):
        raw_items = value
    elif isinstance(value, dict):
        raw_items = [value]
    elif isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        if stripped.startswith("[") or stripped.startswith("{"):
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                parsed = None
            if isinstance(parsed, list):
                raw_items = parsed
            elif isinstance(parsed, dict):
                raw_items = [parsed]
            else:
                raw_items = [part.strip() for part in stripped.split(",") if part]
        else:
            raw_items = [part.strip() for part in stripped.split(",") if part]
    else:
        return None

    for item in raw_items:
        if isinstance(item, dict):
            name = item.get("display_name") or item.get("name")
            if isinstance(name, str) and name.strip():
                candidates.append(name.strip())
        elif isinstance(item, str) and item.strip():
            candidates.append(item.strip())

    if not candidates:
        return None

    direct_matches = {
        "medicine": "Medicine",
        "biology": "Biology",
        "chemistry": "Chemistry",
        "physics": "Physics",
        "computer science": "Computer Science",
        "engineering": "Engineering",
        "psychology": "Psychology & Social Science",
        "sociology": "Psychology & Social Science",
        "environmental science": "Environmental Science",
    }
    for candidate in candidates:
        lowered = candidate.lower()
        if lowered in direct_matches:
            return direct_matches[lowered]

    return _classify_field_from_keyword_text(" ".join(candidates))


def load_data() -> dict[str, pd.DataFrame]:
    return {
        "retracted": pd.read_parquet(RETRACTED_PATH),
        "citers": pd.read_parquet(CITERS_PATH),
        "stats": pd.read_parquet(STATS_PATH),
        "references": pd.read_parquet(REFERENCES_PATH),
    }


def estimate_retraction_years(
    retracted_df: pd.DataFrame,
    default_median_lag_years: int = DEFAULT_MEDIAN_RETRACTION_LAG_YEARS,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    working = retracted_df.copy()
    working["openalex_id"] = working["openalex_id"].astype(str)
    working["publication_year"] = _safe_int_series(working["publication_year"])

    explicit_year_columns = [
        col
        for col in ["retraction_year", "withdrawal_year", "date_retracted_year"]
        if col in working.columns
    ]
    explicit_date_columns = [
        col
        for col in [
            "retraction_date",
            "withdrawn_date",
            "date_retracted",
            "retracted_at",
        ]
        if col in working.columns
    ]

    explicit_year = pd.Series(np.nan, index=working.index, dtype="float64")
    for column in explicit_year_columns:
        explicit_year = explicit_year.fillna(
            pd.to_numeric(working[column], errors="coerce"),
        )

    for column in explicit_date_columns:
        parsed_year = working[column].map(_extract_year_from_date_like)
        explicit_year = explicit_year.fillna(
            pd.to_numeric(parsed_year, errors="coerce"),
        )

    lag_years = (explicit_year - working["publication_year"]).where(
        explicit_year.notna(), np.nan
    )
    lag_years = lag_years[(lag_years >= 0) & (lag_years <= 100)]
    median_lag = (
        round(float(lag_years.median()))
        if not lag_years.dropna().empty
        else default_median_lag_years
    )

    estimated = explicit_year.fillna(working["publication_year"] + median_lag)
    current_year = int(pd.Timestamp.now().year)
    estimated = np.maximum(estimated, working["publication_year"])
    estimated = np.minimum(estimated, current_year)

    sources = np.where(
        explicit_year.notna(),
        "observed_metadata",
        f"heuristic_publication_plus_{median_lag}y",
    )

    output = working[
        [
            "openalex_id",
            "doi",
            "title",
            "publication_year",
            "cited_by_count",
            "references_count",
            "is_retracted_sample",
        ]
    ].copy()
    output["estimated_retraction_year"] = pd.Series(estimated, index=working.index)
    output["estimated_retraction_year"] = _safe_int_series(
        output["estimated_retraction_year"]
    )
    output["retraction_year_source"] = sources

    info = {
        "explicit_year_columns": explicit_year_columns,
        "explicit_date_columns": explicit_date_columns,
        "estimated_median_time_to_retraction_years": int(median_lag),
        "default_fallback_years": int(default_median_lag_years),
        "papers_with_observed_retraction_year": int(explicit_year.notna().sum()),
        "papers_with_heuristic_retraction_year": int(explicit_year.isna().sum()),
    }
    return output, info


def build_per_paper_metrics(
    citers_df: pd.DataFrame,
    retraction_meta_df: pd.DataFrame,
) -> pd.DataFrame:
    working = citers_df.copy()
    working["retracted_openalex_id"] = working["retracted_openalex_id"].astype(str)
    working["citing_year"] = pd.to_numeric(working["citing_year"], errors="coerce")
    working = working.dropna(subset=["citing_year"])
    working["citing_year"] = working["citing_year"].astype(int)
    working["citing_cited_by_count"] = _safe_int_series(
        working["citing_cited_by_count"]
    )

    meta_lookup = retraction_meta_df.copy()
    meta_lookup["openalex_id"] = meta_lookup["openalex_id"].astype(str)
    meta_by_id = meta_lookup.set_index("openalex_id")

    rows: list[dict[str, Any]] = []
    grouped = working.groupby("retracted_openalex_id", sort=False)
    for openalex_id, paper_citers in grouped:
        if openalex_id not in meta_by_id.index:
            continue

        meta_lookup = meta_by_id.loc[openalex_id]
        if isinstance(meta_lookup, pd.DataFrame):
            meta = meta_lookup.iloc[0]
        else:
            meta = meta_lookup

        publication_year = _to_int(meta.get("publication_year"), default=0)
        estimated_retraction_year = _to_int(
            meta.get("estimated_retraction_year"),
            default=publication_year,
        )

        citing_years = paper_citers["citing_year"]
        total_citations = len(paper_citers)

        pre_mask = citing_years < estimated_retraction_year
        post_mask = citing_years >= estimated_retraction_year

        pre_citations = int(pre_mask.sum())
        post_citations = int(post_mask.sum())
        post_fraction = (
            float(post_citations / total_citations) if total_citations else 0.0
        )

        post_year_counts = citing_years[post_mask].value_counts().sort_index()
        post_offset_series = citing_years[post_mask] - estimated_retraction_year
        post_offset_counts = post_offset_series.value_counts().sort_index()

        post_year_index = post_year_counts.index.to_numpy(dtype=int)
        post_year_values = post_year_counts.to_numpy(dtype=int)
        post_offset_index = post_offset_counts.index.to_numpy(dtype=int)
        post_offset_values = post_offset_counts.to_numpy(dtype=int)

        post_curve_year = {
            str(int(year)): int(count)
            for year, count in zip(post_year_index, post_year_values, strict=False)
        }
        post_curve_offset = {
            str(int(offset)): int(count)
            for offset, count in zip(
                post_offset_index,
                post_offset_values,
                strict=False,
            )
        }
        normalized_post_curve = {
            str(int(offset)): float(count / post_citations)
            for offset, count in zip(
                post_offset_index,
                post_offset_values,
                strict=False,
            )
        }

        time_to_50_post = _years_to_reach_fraction(
            post_year_counts,
            fraction=0.5,
            origin_year=estimated_retraction_year,
        )

        valid_for_half_life = citing_years[citing_years >= publication_year]
        all_year_counts = valid_for_half_life.value_counts().sort_index()
        citation_half_life = _years_to_reach_fraction(
            all_year_counts,
            fraction=0.5,
            origin_year=publication_year,
        )

        if post_offset_counts.shape[0] >= 2:
            x = post_offset_counts.index.to_numpy(dtype=float)
            y = post_offset_counts.to_numpy(dtype=float)
            decay_rate = _linear_slope(x, y)
        else:
            decay_rate = 0.0

        direct_citers_count = int(
            paper_citers["citing_openalex_id"].nunique(dropna=True)
        )
        two_hop_reach = int(paper_citers["citing_cited_by_count"].sum())
        avg_citer_citations = float(paper_citers["citing_cited_by_count"].mean())
        severity = float(direct_citers_count * avg_citer_citations)
        amplification = (
            float(two_hop_reach / direct_citers_count)
            if direct_citers_count > 0
            else 0.0
        )

        current_year = int(pd.Timestamp.now().year)
        years_since_retraction = int(max(0, current_year - estimated_retraction_year))

        rows.append(
            {
                "retracted_openalex_id": openalex_id,
                "doi": str(meta["doi"]),
                "title": str(meta["title"]),
                "publication_year": publication_year,
                "estimated_retraction_year": estimated_retraction_year,
                "retraction_year_source": str(meta["retraction_year_source"]),
                "cited_by_count": _to_int(meta.get("cited_by_count"), default=0),
                "references_count": _to_int(meta.get("references_count"), default=0),
                "is_retracted_sample": bool(meta["is_retracted_sample"]),
                "total_citations": total_citations,
                "pre_retraction_citations": pre_citations,
                "post_retraction_citations": post_citations,
                "post_retraction_fraction": post_fraction,
                "post_retraction_rate_pct": post_fraction * 100.0,
                "post_retraction_annual_counts": post_curve_year,
                "post_retraction_persistence_curve": normalized_post_curve,
                "post_retraction_offset_counts": post_curve_offset,
                "time_to_50pct_post_retraction_years": time_to_50_post,
                "citation_half_life_years": citation_half_life,
                "post_retraction_decay_rate": decay_rate,
                "direct_citers_count": direct_citers_count,
                "avg_citer_citations": avg_citer_citations,
                "two_hop_reach_estimate": two_hop_reach,
                "contamination_severity": severity,
                "amplification_factor": amplification,
                "years_since_retraction": years_since_retraction,
                "self_correction_index": 1.0 - post_fraction,
            },
        )

    return pd.DataFrame(rows)


def infer_field_labels(retracted_df: pd.DataFrame) -> pd.DataFrame:
    working = retracted_df.copy()
    working["openalex_id"] = working["openalex_id"].astype(str)

    has_concepts = "concepts" in working.columns
    has_primary_topic = "primary_topic" in working.columns

    fields: list[dict[str, str]] = []
    for row in working.itertuples(index=False):
        openalex_id = str(row.openalex_id)
        doi = str(row.doi)
        title = str(row.title)

        inferred_field: str | None = None
        source = ""

        if has_concepts:
            inferred_field = _extract_field_from_concepts(row.concepts)
            if inferred_field is not None:
                source = "concepts"

        if inferred_field is None and has_primary_topic:
            inferred_field = _extract_field_from_concepts(row.primary_topic)
            if inferred_field is not None:
                source = "primary_topic"

        if inferred_field is None and doi:
            normalized_doi = _normalize_doi(doi)
            matched_field = None
            for prefix, field in DOI_FIELD_PREFIX_MAP.items():
                if normalized_doi.startswith(prefix):
                    matched_field = field
                    break
            if matched_field is not None:
                inferred_field = matched_field
                source = "doi_prefix_proxy"

        if inferred_field is None and title:
            inferred_field = _classify_field_from_keyword_text(title)
            if inferred_field is not None:
                source = "title_keyword_fallback"

        if inferred_field is None:
            inferred_field = "Unclassified"
            source = "unclassified"

        fields.append(
            {
                "openalex_id": openalex_id,
                "field_label": inferred_field,
                "field_source": source,
            },
        )

    return pd.DataFrame(fields)


def analyze_post_vs_pre_split(
    per_paper_df: pd.DataFrame,
    retraction_info: dict[str, Any],
) -> dict[str, Any]:
    curve_points: dict[int, list[float]] = {}
    for curve in per_paper_df["post_retraction_persistence_curve"]:
        if not isinstance(curve, dict):
            continue
        for year_after_str, normalized_count in curve.items():
            try:
                year_after = int(year_after_str)
                value = float(normalized_count)
            except (TypeError, ValueError):
                continue
            curve_points.setdefault(year_after, []).append(value)

    aggregated_curve = [
        {
            "years_after_retraction": year_after,
            "mean_normalized_citations": float(np.mean(values)),
            "median_normalized_citations": float(np.median(values)),
            "papers_contributing": len(values),
        }
        for year_after, values in sorted(curve_points.items())
    ]

    return {
        "retraction_year_estimation": retraction_info,
        "papers_with_citers": int(per_paper_df.shape[0]),
        "papers_with_post_retraction_citations": int(
            (per_paper_df["post_retraction_citations"] > 0).sum()
        ),
        "post_retraction_citation_rate_pct_distribution": _distribution_stats(
            per_paper_df["post_retraction_rate_pct"],
        ),
        "time_to_50pct_post_retraction_years_distribution": _distribution_stats(
            per_paper_df["time_to_50pct_post_retraction_years"],
        ),
        "normalized_post_retraction_persistence_curve": aggregated_curve,
        "highest_post_retraction_rate_papers": per_paper_df.sort_values(
            "post_retraction_rate_pct",
            ascending=False,
        )
        .head(10)
        .to_dict(orient="records"),
    }


def analyze_field_contamination_distribution(
    per_paper_df: pd.DataFrame,
    field_df: pd.DataFrame,
) -> tuple[dict[str, Any], pd.DataFrame]:
    merged = per_paper_df.merge(
        field_df,
        left_on="retracted_openalex_id",
        right_on="openalex_id",
        how="left",
    ).drop(columns=["openalex_id"], errors="ignore")
    merged["field_label"] = merged["field_label"].fillna("Unclassified")
    merged["field_source"] = merged["field_source"].fillna("unclassified")

    grouped = (
        merged.groupby("field_label", as_index=False)
        .agg(
            paper_count=("retracted_openalex_id", "nunique"),
            mean_citers=("direct_citers_count", "mean"),
            mean_severity=("contamination_severity", "mean"),
            self_correction_rate=("self_correction_index", "mean"),
            mean_post_retraction_fraction=("post_retraction_fraction", "mean"),
        )
        .sort_values(["paper_count", "mean_severity"], ascending=[False, False])
    )

    analysis = {
        "field_inference_source_counts": merged["field_source"]
        .value_counts()
        .to_dict(),
        "field_distribution": grouped.to_dict(orient="records"),
        "top_field_by_mean_severity": grouped.head(1).to_dict(orient="records"),
    }
    return analysis, grouped


def _run_ols_numpy(
    y: np.ndarray,
    x_design: np.ndarray,
    terms: list[str],
) -> dict[str, Any]:
    """Fallback OLS using pure numpy (no statsmodels)."""
    n_obs = x_design.shape[0]
    beta, _, rank, _ = np.linalg.lstsq(x_design, y, rcond=None)
    y_hat = x_design @ beta
    residuals = y - y_hat

    sse = float(np.sum(residuals**2))
    sst = float(np.sum((y - y.mean()) ** 2))
    r_squared = float(1.0 - (sse / sst)) if sst > 0 else 0.0

    rank_int = int(rank)
    dof = n_obs - rank_int
    adjusted_r_squared: float | None
    if dof > 0:
        adjusted_r_squared = float(1.0 - (1.0 - r_squared) * ((n_obs - 1) / dof))
    else:
        adjusted_r_squared = None

    xtx = x_design.T @ x_design
    xtx_inv = np.linalg.pinv(xtx)
    if dof > 0:
        sigma2 = sse / dof
        se = np.sqrt(np.clip(np.diag(sigma2 * xtx_inv), a_min=0.0, a_max=None))
        with np.errstate(divide="ignore", invalid="ignore"):
            t_stats = np.divide(
                beta,
                se,
                out=np.zeros_like(beta),
                where=se > 0,
            )
        p_values = 2.0 * stats.t.sf(np.abs(t_stats), dof)
    else:
        se = np.full(beta.shape, np.nan)
        t_stats = np.full(beta.shape, np.nan)
        p_values = np.full(beta.shape, np.nan)

    coefficients: list[dict[str, Any]] = []
    for idx, term in enumerate(terms):
        coefficients.append(
            {
                "term": term,
                "coefficient": float(beta[idx]),
                "std_error": float(se[idx]) if np.isfinite(se[idx]) else None,
                "t_stat": float(t_stats[idx]) if np.isfinite(t_stats[idx]) else None,
                "p_value": float(p_values[idx]) if np.isfinite(p_values[idx]) else None,
            },
        )

    try:
        condition_number = float(np.linalg.cond(x_design))
    except np.linalg.LinAlgError:
        condition_number = float("inf")

    k = x_design.shape[1] - 1
    f_statistic: float | None = None
    f_pvalue: float | None = None
    if k > 0 and dof > 0 and sst > 0:
        msr = (sst - sse) / k
        mse = sse / dof
        if mse > 0:
            f_statistic = float(msr / mse)
            f_pvalue = float(stats.f.sf(f_statistic, k, dof))

    log_likelihood: float | None = None
    aic: float | None = None
    bic: float | None = None
    if n_obs > 0 and sse > 0:
        log_likelihood = float(
            -0.5 * n_obs * (np.log(2.0 * np.pi) + 1.0 + np.log(sse / n_obs))
        )
        n_params = x_design.shape[1]
        aic = float(2.0 * n_params - 2.0 * log_likelihood)
        bic = float(np.log(n_obs) * n_params - 2.0 * log_likelihood)

    return {
        "n_obs": n_obs,
        "rank": rank_int,
        "degrees_of_freedom": int(dof),
        "r_squared": r_squared,
        "adjusted_r_squared": adjusted_r_squared,
        "f_statistic": f_statistic,
        "f_pvalue": f_pvalue,
        "log_likelihood": log_likelihood,
        "aic": aic,
        "bic": bic,
        "condition_number": condition_number,
        "multicollinearity_flag": bool(
            rank_int < x_design.shape[1] or condition_number > 1e8
        ),
        "coefficients": coefficients,
        "engine": "numpy",
    }


def _run_ols_statsmodels(
    y: np.ndarray,
    x_design: np.ndarray,
    terms: list[str],
) -> dict[str, Any]:
    """OLS using statsmodels with HC3 robust standard errors."""
    assert sm is not None
    model = sm.OLS(y, x_design).fit(cov_type="HC3")

    coefficients: list[dict[str, Any]] = []
    for idx, term in enumerate(terms):
        coefficients.append(
            {
                "term": term,
                "coefficient": float(model.params[idx]),
                "std_error": float(model.bse[idx]),
                "t_stat": float(model.tvalues[idx]),
                "p_value": float(model.pvalues[idx]),
                "ci_lower_95": float(model.conf_int()[idx, 0]),
                "ci_upper_95": float(model.conf_int()[idx, 1]),
            },
        )

    try:
        condition_number = float(model.condition_number)
    except Exception:
        condition_number = float(np.linalg.cond(x_design))

    return {
        "n_obs": int(model.nobs),
        "rank": int(model.df_model + 1),
        "degrees_of_freedom": int(model.df_resid),
        "r_squared": float(model.rsquared),
        "adjusted_r_squared": float(model.rsquared_adj),
        "f_statistic": float(model.fvalue) if model.fvalue is not None else None,
        "f_pvalue": float(model.f_pvalue) if model.f_pvalue is not None else None,
        "log_likelihood": float(model.llf),
        "aic": float(model.aic),
        "bic": float(model.bic),
        "condition_number": condition_number,
        "multicollinearity_flag": bool(condition_number > 1e8),
        "coefficients": coefficients,
        "cov_type": "HC3",
        "durbin_watson": float(sm.stats.stattools.durbin_watson(model.resid)),
        "engine": "statsmodels",
    }


def _run_ols(
    frame: pd.DataFrame,
    dependent_col: str,
    independent_cols: list[str],
) -> dict[str, Any]:
    working = frame[[dependent_col, *independent_cols]].copy()
    for column in [dependent_col, *independent_cols]:
        working[column] = pd.to_numeric(working[column], errors="coerce")
    working = working.dropna()

    n_obs = int(working.shape[0])
    if n_obs == 0:
        return {
            "n_obs": 0,
            "error": "No complete rows after filtering numeric values.",
            "coefficients": [],
        }

    y = working[dependent_col].to_numpy(dtype=float)
    x = working[independent_cols].to_numpy(dtype=float)
    x_design = np.column_stack([np.ones(n_obs), x])
    terms = ["intercept", *independent_cols]

    if HAS_STATSMODELS and sm is not None:
        return _run_ols_statsmodels(y, x_design, terms)
    return _run_ols_numpy(y, x_design, terms)


def analyze_self_correction_by_cohort(
    per_paper_df: pd.DataFrame,
) -> tuple[dict[str, Any], pd.DataFrame]:
    working = per_paper_df.copy()
    working["retraction_decade"] = (
        (working["estimated_retraction_year"] // 10) * 10
    ).astype(int)
    working["retraction_cohort"] = working["retraction_decade"].map(
        lambda value: f"{value}s",
    )

    cohort_table = (
        working.groupby(["retraction_decade", "retraction_cohort"], as_index=False)
        .agg(
            paper_count=("retracted_openalex_id", "nunique"),
            mean_citation_half_life_years=("citation_half_life_years", "mean"),
            mean_post_retraction_fraction=("post_retraction_fraction", "mean"),
            mean_decay_rate=("post_retraction_decay_rate", "mean"),
        )
        .sort_values("retraction_decade")
    )

    trend_model = _run_ols(
        working,
        dependent_col="post_retraction_decay_rate",
        independent_cols=["estimated_retraction_year"],
    )

    slope = None
    p_value = None
    if trend_model["coefficients"] and len(trend_model["coefficients"]) > 1:
        slope = trend_model["coefficients"][1]["coefficient"]
        p_value = trend_model["coefficients"][1]["p_value"]

    improving = bool(
        slope is not None
        and p_value is not None
        and slope < 0
        and float(p_value) < 0.05
    )

    analysis = {
        "cohorts": cohort_table.to_dict(orient="records"),
        "decay_trend_regression": trend_model,
        "self_correction_improving": improving,
        "interpretation": (
            "More recent retractions show faster citation decay"
            if improving
            else "No statistically robust improvement signal in citation decay"
        ),
    }
    return analysis, cohort_table


def analyze_two_hop_contamination(
    per_paper_df: pd.DataFrame,
    field_df: pd.DataFrame,
    citers_df: pd.DataFrame,
) -> tuple[dict[str, Any], pd.DataFrame]:
    merged = per_paper_df.merge(
        field_df,
        left_on="retracted_openalex_id",
        right_on="openalex_id",
        how="left",
    ).drop(columns=["openalex_id"], errors="ignore")
    merged["field_label"] = merged["field_label"].fillna("Unclassified")

    citers_working = citers_df.copy()
    citers_working["retracted_openalex_id"] = citers_working[
        "retracted_openalex_id"
    ].astype(str)
    citers_working["citing_cited_by_count"] = _safe_int_series(
        citers_working["citing_cited_by_count"],
    )
    citers_with_field = citers_working.merge(
        field_df,
        left_on="retracted_openalex_id",
        right_on="openalex_id",
        how="left",
    )
    citers_with_field["field_label"] = citers_with_field["field_label"].fillna(
        "Unclassified"
    )

    field_medians = (
        citers_with_field.groupby("field_label")["citing_cited_by_count"].median()
    ).to_dict()
    global_median_citation = float(citers_working["citing_cited_by_count"].median())

    merged["field_median_citation_per_paper"] = merged["field_label"].map(
        lambda field: float(field_medians.get(field, global_median_citation)),
    )
    merged["expected_3_hop_reach"] = (
        merged["two_hop_reach_estimate"] * merged["field_median_citation_per_paper"]
    )

    denominator = (
        merged["direct_citers_count"] * merged["field_median_citation_per_paper"]
    )
    merged["p_estimate_raw"] = np.where(
        denominator > 0,
        merged["two_hop_reach_estimate"] / denominator,
        np.nan,
    )
    merged["p_estimate_clipped"] = merged["p_estimate_raw"].clip(lower=0.0, upper=1.0)

    p_candidates = merged["p_estimate_clipped"].dropna()
    p_hat = float(p_candidates.median()) if not p_candidates.empty else 0.0

    baseline_n = (
        float(merged["direct_citers_count"].mean()) if not merged.empty else 0.0
    )
    generation_projection = [
        {
            "generation": g,
            "expected_contamination": float(baseline_n * (p_hat**g)),
        }
        for g in range(0, 6)
    ]

    direct_q25 = float(merged["direct_citers_count"].quantile(0.25))
    high_amp_low_direct = merged[
        merged["direct_citers_count"] <= direct_q25
    ].sort_values("amplification_factor", ascending=False)

    analysis = {
        "total_direct_citers": int(merged["direct_citers_count"].sum()),
        "total_two_hop_reach_estimate": int(merged["two_hop_reach_estimate"].sum()),
        "amplification_factor_distribution": _distribution_stats(
            merged["amplification_factor"],
        ),
        "expected_3_hop_reach_distribution": _distribution_stats(
            merged["expected_3_hop_reach"],
        ),
        "field_median_citation_per_paper": {
            key: float(value) for key, value in field_medians.items()
        },
        "estimated_p_distribution": _distribution_stats(merged["p_estimate_clipped"]),
        "estimated_p_global": p_hat,
        "contamination_decay_model": {
            "formula": "E[g] = N * p^g",
            "baseline_N_mean_direct_citers": baseline_n,
            "p_estimate": p_hat,
            "projection": generation_projection,
        },
        "highest_amplification_papers": merged.sort_values(
            "amplification_factor",
            ascending=False,
        )
        .head(10)
        .to_dict(orient="records"),
        "highest_amplification_low_direct_papers": high_amp_low_direct.head(10).to_dict(
            orient="records"
        ),
    }
    return analysis, merged


def analyze_severity_factors_regression(per_paper_df: pd.DataFrame) -> dict[str, Any]:
    predictors = [
        "publication_year",
        "years_since_retraction",
        "cited_by_count",
        "references_count",
        "post_retraction_fraction",
    ]
    model = _run_ols(
        per_paper_df,
        dependent_col="contamination_severity",
        independent_cols=predictors,
    )

    sorted_terms = sorted(
        [row for row in model.get("coefficients", []) if row["term"] != "intercept"],
        key=lambda row: abs(float(row["coefficient"])),
        reverse=True,
    )
    return {
        "dependent_variable": "contamination_severity",
        "severity_formula": "direct_citers_count * avg_citer_citations",
        "independent_variables": predictors,
        "model": model,
        "largest_effect_terms": sorted_terms[:5],
    }


def _print_section(title: str) -> None:
    print(f"\n{'=' * 20} {title} {'=' * 20}")


def print_summary_tables(
    analysis_1: dict[str, Any],
    field_table: pd.DataFrame,
    cohort_table: pd.DataFrame,
    two_hop_df: pd.DataFrame,
    analysis_5: dict[str, Any],
) -> None:
    _print_section("Analysis 1: Post vs Pre")
    rows = [
        {
            "metric": "papers_with_citers",
            "value": analysis_1["papers_with_citers"],
        },
        {
            "metric": "papers_with_post_retraction_citations",
            "value": analysis_1["papers_with_post_retraction_citations"],
        },
        {
            "metric": "mean_post_retraction_rate_pct",
            "value": analysis_1["post_retraction_citation_rate_pct_distribution"][
                "mean"
            ],
        },
    ]
    print(pd.DataFrame(rows).to_string(index=False))

    _print_section("Analysis 2: Field Distribution")
    print(field_table.head(12).to_string(index=False))

    _print_section("Analysis 3: Temporal Cohorts")
    print(cohort_table.to_string(index=False))

    _print_section("Analysis 4: Top Amplification")
    amp_cols = [
        "doi",
        "field_label",
        "direct_citers_count",
        "two_hop_reach_estimate",
        "amplification_factor",
        "expected_3_hop_reach",
    ]
    print(
        two_hop_df.sort_values("amplification_factor", ascending=False)[amp_cols]
        .head(12)
        .to_string(index=False),
    )

    _print_section("Analysis 5: Severity Regression")
    coefficients = analysis_5["model"].get("coefficients", [])
    if coefficients:
        print(pd.DataFrame(coefficients).to_string(index=False))
    else:
        print("No coefficients available.")


def build_analysis_payload(
    data_frames: dict[str, pd.DataFrame],
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    retracted_df = data_frames["retracted"]
    citers_df = data_frames["citers"]
    stats_df = data_frames["stats"]
    references_df = data_frames["references"]

    retraction_meta_df, retraction_info = estimate_retraction_years(retracted_df)
    per_paper_df = build_per_paper_metrics(citers_df, retraction_meta_df)
    field_df = infer_field_labels(retracted_df)

    analysis_1 = analyze_post_vs_pre_split(per_paper_df, retraction_info)
    analysis_2, field_table = analyze_field_contamination_distribution(
        per_paper_df,
        field_df,
    )
    analysis_3, cohort_table = analyze_self_correction_by_cohort(per_paper_df)
    analysis_4, two_hop_df = analyze_two_hop_contamination(
        per_paper_df,
        field_df,
        citers_df,
    )
    analysis_5 = analyze_severity_factors_regression(per_paper_df)

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
                "per_paper_analyzed": len(per_paper_df),
            },
            "input_columns": {
                "retracted_papers": retracted_df.columns.tolist(),
                "retraction_citers": citers_df.columns.tolist(),
                "retraction_propagation_stats": stats_df.columns.tolist(),
                "retraction_references": references_df.columns.tolist(),
            },
        },
        "analysis_1_post_vs_pre_retraction_split": analysis_1,
        "analysis_2_field_level_contamination_distribution": analysis_2,
        "analysis_3_self_correction_by_temporal_cohort": analysis_3,
        "analysis_4_two_hop_contamination_estimation": analysis_4,
        "analysis_5_severity_factors_regression": analysis_5,
        "tables": {
            "per_paper_metrics": per_paper_df.to_dict(orient="records"),
            "field_table": field_table.to_dict(orient="records"),
            "cohort_table": cohort_table.to_dict(orient="records"),
            "two_hop_table": two_hop_df.to_dict(orient="records"),
        },
    }
    return _to_python_native(payload), field_table, cohort_table, two_hop_df


def main() -> None:
    data_frames = load_data()
    payload, field_table, cohort_table, two_hop_df = build_analysis_payload(data_frames)

    print_summary_tables(
        analysis_1=payload["analysis_1_post_vs_pre_retraction_split"],
        field_table=field_table,
        cohort_table=cohort_table,
        two_hop_df=two_hop_df,
        analysis_5=payload["analysis_5_severity_factors_regression"],
    )

    OUTPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )

    _print_section("Output")
    print(f"Saved deep analysis JSON: {OUTPUT_JSON_PATH}")


if __name__ == "__main__":
    main()
