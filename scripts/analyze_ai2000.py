#!/usr/bin/env python3
"""Analyze AI 2000 researcher and domain data for Track 1 supplementary results."""
# pyright: basic

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

RESEARCHERS_PATH = Path("data/processed/ai2000_researchers.parquet")
DOMAINS_PATH = Path("data/processed/ai2000_domains.parquet")
OUTPUT_PATH = Path("data/processed/ai2000_analysis.json")

ANALYSIS_YEAR_START = 2019
ANALYSIS_YEAR_END = 2023

TRACK1_FIELDS = [
    "Computer Science",
    "Medicine",
    "Engineering",
    "Environmental Science",
    "Physics",
    "Biology",
    "Chemistry",
    "Political Science",
    "Mathematics",
    "Materials Science",
    "Psychology",
    "Economics",
    "Business",
    "Geology",
    "Geography",
]

TRACK1_SUBFIELD_MAP: dict[str, dict[str, float]] = {
    "AAAI/IJCAI": {"Computer Science": 1.0, "Mathematics": 0.4},
    "Machine Learning": {
        "Computer Science": 1.0,
        "Mathematics": 0.8,
        "Engineering": 0.6,
    },
    "Computer Vision": {
        "Computer Science": 1.0,
        "Engineering": 0.8,
        "Biology": 0.5,
        "Medicine": 0.7,
    },
    "NLP": {
        "Computer Science": 1.0,
        "Psychology": 0.6,
        "Political Science": 0.4,
        "Business": 0.3,
    },
    "Robotics": {
        "Engineering": 1.0,
        "Computer Science": 0.8,
        "Materials Science": 0.4,
    },
    "Knowledge Engineering": {
        "Computer Science": 1.0,
        "Business": 0.5,
        "Economics": 0.3,
    },
    "Speech Recognition": {
        "Computer Science": 1.0,
        "Psychology": 0.5,
        "Medicine": 0.4,
    },
    "Data Mining": {
        "Computer Science": 1.0,
        "Business": 0.7,
        "Economics": 0.6,
        "Medicine": 0.6,
        "Environmental Science": 0.5,
        "Geology": 0.4,
        "Geography": 0.5,
        "Political Science": 0.6,
        "Psychology": 0.4,
        "Engineering": 0.5,
    },
    "IR and Recommendation": {
        "Computer Science": 1.0,
        "Business": 0.7,
        "Economics": 0.6,
        "Psychology": 0.4,
        "Political Science": 0.3,
    },
    "HCI": {
        "Computer Science": 1.0,
        "Psychology": 0.8,
        "Business": 0.4,
        "Political Science": 0.3,
    },
    "Multimedia": {
        "Computer Science": 1.0,
        "Engineering": 0.6,
        "Psychology": 0.3,
    },
    "Database": {"Computer Science": 1.0, "Business": 0.5},
    "Computer Graphics": {
        "Computer Science": 1.0,
        "Engineering": 0.6,
        "Biology": 0.3,
    },
    "Visualization": {
        "Computer Science": 1.0,
        "Biology": 0.5,
        "Medicine": 0.5,
        "Environmental Science": 0.4,
        "Geography": 0.5,
    },
    "Security and Privacy": {
        "Computer Science": 1.0,
        "Political Science": 0.5,
        "Business": 0.6,
    },
    "Computer Networking": {
        "Computer Science": 1.0,
        "Engineering": 0.7,
        "Geography": 0.2,
    },
    "Computer Systems": {"Computer Science": 1.0, "Engineering": 0.7},
    "Theory": {"Computer Science": 0.9, "Mathematics": 1.0},
    "Chip Technology": {
        "Engineering": 1.0,
        "Computer Science": 0.7,
        "Materials Science": 0.6,
        "Physics": 0.4,
    },
    "Internet of Things": {
        "Engineering": 1.0,
        "Computer Science": 0.8,
        "Environmental Science": 0.3,
        "Geography": 0.3,
    },
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


def _herfindahl(counts: pd.Series) -> float | None:
    total = float(counts.sum())
    if total <= 0:
        return None
    shares = counts.astype(float) / total
    return float((shares**2).sum())


def _gini(values: np.ndarray) -> float | None:
    if values.size == 0:
        return None
    clean = values[np.isfinite(values)]
    clean = clean[clean >= 0]
    if clean.size == 0:
        return None
    if float(clean.sum()) == 0.0:
        return 0.0

    sorted_vals = np.sort(clean)
    n = sorted_vals.size
    index = np.arange(1, n + 1)
    numerator = np.sum((2 * index - n - 1) * sorted_vals)
    denominator = n * np.sum(sorted_vals)
    if denominator == 0:
        return None
    return float(numerator / denominator)


def _org_type(org_name: str) -> str:
    org_lower = org_name.lower()
    university_markers = [
        "university",
        "institute of technology",
        "college",
        "school of",
        "academy",
        "polytechnic",
    ]
    industry_markers = [
        "inc",
        "ltd",
        "llc",
        "corp",
        "company",
        "technologies",
        "technology",
        "google",
        "microsoft",
        "meta",
        "amazon",
        "ibm",
        "huawei",
        "tencent",
        "alibaba",
        "baidu",
        "megvii",
        "openai",
        "nvidia",
    ]
    if any(marker in org_lower for marker in university_markers):
        return "university"
    if any(marker in org_lower for marker in industry_markers):
        return "industry"
    return "other"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    researchers = pd.read_parquet(RESEARCHERS_PATH).copy()
    domains = pd.read_parquet(DOMAINS_PATH).copy()

    required_researcher_columns = {
        "domain_id",
        "domain_name",
        "entity_id",
        "name",
        "gender",
        "h_index",
        "n_pubs",
        "country",
        "org",
        "keywords",
        "ai2000_score",
        "ai2000_rank",
        "domain_citations",
        "domain_citation_rank",
        "normalized_citations",
    }
    missing = required_researcher_columns - set(researchers.columns)
    if missing:
        raise ValueError(f"Missing researcher columns: {sorted(missing)}")

    researchers["domain_name"] = researchers["domain_name"].fillna("Unknown")
    researchers["country"] = researchers["country"].fillna("Unknown")
    researchers["org"] = researchers["org"].fillna("Unknown")
    researchers["gender"] = researchers["gender"].fillna("unknown")
    researchers["keywords"] = researchers["keywords"].fillna("")

    for col in ["h_index", "n_pubs", "ai2000_rank", "domain_citation_rank"]:
        researchers[col] = pd.to_numeric(researchers[col], errors="coerce")
    for col in ["ai2000_score", "domain_citations", "normalized_citations"]:
        researchers[col] = pd.to_numeric(researchers[col], errors="coerce")

    if "year" in domains.columns:
        domains["year"] = pd.to_numeric(domains["year"], errors="coerce")
    if "pubs" in domains.columns:
        domains["pubs"] = pd.to_numeric(domains["pubs"], errors="coerce")
    if "scholars" in domains.columns:
        domains["scholars"] = pd.to_numeric(domains["scholars"], errors="coerce")

    return researchers, domains


def analyze_domain_size_distribution(
    researchers: pd.DataFrame,
    domains: pd.DataFrame,
) -> dict[str, Any]:
    scholars_per_domain = (
        researchers.groupby("domain_name", as_index=False)
        .size()
        .rename(columns={"size": "n_top_scholars"})
        .sort_values("n_top_scholars", ascending=False)
    )

    annual_domain_stats = domains.copy()
    annual_domain_stats = annual_domain_stats[
        annual_domain_stats["level"].eq(2)
        & annual_domain_stats["year"].between(ANALYSIS_YEAR_START, ANALYSIS_YEAR_END)
    ].copy()
    annual_domain_stats = annual_domain_stats.sort_values(["domain_name", "year"])

    growth_rows: list[dict[str, Any]] = []
    for domain_name, group in annual_domain_stats.groupby("domain_name", sort=True):
        group_sorted = group.sort_values("year")
        first = group_sorted.iloc[0]
        last = group_sorted.iloc[-1]
        year_diff = int(last["year"] - first["year"])

        pubs_start = float(first["pubs"]) if pd.notna(first["pubs"]) else np.nan
        pubs_end = float(last["pubs"]) if pd.notna(last["pubs"]) else np.nan
        scholars_start = (
            float(first["scholars"]) if pd.notna(first["scholars"]) else np.nan
        )
        scholars_end = float(last["scholars"]) if pd.notna(last["scholars"]) else np.nan

        pubs_growth = (
            ((pubs_end - pubs_start) / pubs_start)
            if year_diff > 0 and pubs_start > 0 and np.isfinite(pubs_end)
            else None
        )
        scholars_growth = (
            ((scholars_end - scholars_start) / scholars_start)
            if year_diff > 0 and scholars_start > 0 and np.isfinite(scholars_end)
            else None
        )

        pubs_cagr = (
            (pubs_end / pubs_start) ** (1 / year_diff) - 1
            if year_diff > 0 and pubs_start > 0 and pubs_end > 0
            else None
        )
        scholars_cagr = (
            (scholars_end / scholars_start) ** (1 / year_diff) - 1
            if year_diff > 0 and scholars_start > 0 and scholars_end > 0
            else None
        )

        growth_rows.append(
            {
                "domain_name": domain_name,
                "start_year": int(first["year"]),
                "end_year": int(last["year"]),
                "pubs_start": pubs_start,
                "pubs_end": pubs_end,
                "pubs_growth_rate": pubs_growth,
                "pubs_cagr": pubs_cagr,
                "scholars_start": scholars_start,
                "scholars_end": scholars_end,
                "scholars_growth_rate": scholars_growth,
                "scholars_cagr": scholars_cagr,
            },
        )

    growth_df = pd.DataFrame(growth_rows).sort_values(
        "scholars_growth_rate",
        ascending=False,
        na_position="last",
    )

    return {
        "n_domains": int(scholars_per_domain["domain_name"].nunique()),
        "top_scholar_counts_by_domain": scholars_per_domain.to_dict("records"),
        "annual_domain_statistics_2019_2023": annual_domain_stats[
            ["domain_id", "domain_name", "year", "pubs", "scholars"]
        ].to_dict("records"),
        "growth_trends_2019_2023": growth_df.to_dict("records"),
    }


def analyze_geographic_distribution(researchers: pd.DataFrame) -> dict[str, Any]:
    country_counts = (
        researchers.groupby("country", as_index=False)
        .size()
        .rename(columns={"size": "n_scholars"})
        .sort_values("n_scholars", ascending=False)
    )

    per_domain_rows: list[dict[str, Any]] = []
    domain_hhi_rows: list[dict[str, Any]] = []
    for domain_name, group in researchers.groupby("domain_name", sort=True):
        counts = group.groupby("country").size().sort_values(ascending=False)
        domain_hhi_rows.append(
            {
                "domain_name": domain_name,
                "country_herfindahl_index": _herfindahl(counts),
            },
        )
        for country, value in counts.head(10).items():
            per_domain_rows.append(
                {
                    "domain_name": domain_name,
                    "country": country,
                    "n_scholars": int(value),
                },
            )

    overall_hhi = _herfindahl(country_counts.set_index("country")["n_scholars"])

    return {
        "overall_country_distribution": country_counts.to_dict("records"),
        "per_domain_top_countries": per_domain_rows,
        "talent_concentration_herfindahl": {
            "overall": overall_hhi,
            "per_domain": sorted(
                domain_hhi_rows,
                key=lambda row: (
                    row["country_herfindahl_index"]
                    if row["country_herfindahl_index"] is not None
                    else -1
                ),
                reverse=True,
            ),
        },
    }


def analyze_institutional_distribution(researchers: pd.DataFrame) -> dict[str, Any]:
    org_counts = (
        researchers.groupby("org", as_index=False)
        .size()
        .rename(columns={"size": "n_scholars"})
        .sort_values("n_scholars", ascending=False)
    )

    researchers_with_type = researchers.copy()
    researchers_with_type["org_type"] = researchers_with_type["org"].map(_org_type)
    org_type_counts = (
        researchers_with_type.groupby("org_type", as_index=False)
        .size()
        .rename(columns={"size": "n_scholars"})
        .sort_values("n_scholars", ascending=False)
    )

    type_total = float(org_type_counts["n_scholars"].sum())
    if type_total > 0:
        org_type_counts["share"] = org_type_counts["n_scholars"] / type_total
    else:
        org_type_counts["share"] = 0.0

    per_domain_rows: list[dict[str, Any]] = []
    for domain_name, group in researchers.groupby("domain_name", sort=True):
        top_orgs = group.groupby("org").size().sort_values(ascending=False).head(10)
        for org, count in top_orgs.items():
            per_domain_rows.append(
                {
                    "domain_name": domain_name,
                    "org": org,
                    "n_scholars": int(count),
                },
            )

    ratio_lookup = {
        row["org_type"]: row["share"] for _, row in org_type_counts.iterrows()
    }
    university_share = float(ratio_lookup.get("university", 0.0))
    industry_share = float(ratio_lookup.get("industry", 0.0))

    return {
        "top_20_organizations": org_counts.head(20).to_dict("records"),
        "per_domain_top_organizations": per_domain_rows,
        "organization_type_distribution": org_type_counts.to_dict("records"),
        "university_vs_industry_ratio": {
            "university_share": university_share,
            "industry_share": industry_share,
            "university_to_industry_ratio": (
                university_share / industry_share if industry_share > 0 else None
            ),
        },
    }


def analyze_gender_distribution(researchers: pd.DataFrame) -> dict[str, Any]:
    normalized = researchers.copy()
    normalized["gender_normalized"] = (
        normalized["gender"]
        .str.lower()
        .map(
            lambda value: value if value in {"male", "female"} else "unknown",
        )
    )

    overall = (
        normalized.groupby("gender_normalized", as_index=False)
        .size()
        .rename(columns={"size": "n_scholars"})
        .sort_values("n_scholars", ascending=False)
    )
    total = float(overall["n_scholars"].sum())
    overall["share"] = overall["n_scholars"] / total if total > 0 else 0.0

    per_domain = (
        normalized.groupby(["domain_name", "gender_normalized"], as_index=False)
        .size()
        .rename(columns={"size": "n_scholars"})
    )
    domain_totals = (
        per_domain.groupby("domain_name", as_index=False)["n_scholars"]
        .sum()
        .assign(domain_total=lambda frame: frame["n_scholars"])[
            ["domain_name", "domain_total"]
        ]
    )
    per_domain = per_domain.merge(domain_totals, on="domain_name", how="left")
    per_domain["share"] = np.where(
        per_domain["domain_total"] > 0,
        per_domain["n_scholars"] / per_domain["domain_total"],
        0.0,
    )

    female_share = per_domain[per_domain["gender_normalized"].eq("female")].sort_values(
        "share", ascending=False
    )[["domain_name", "share", "n_scholars", "domain_total"]]

    male_count = int(
        overall.loc[overall["gender_normalized"].eq("male"), "n_scholars"].sum()
    )
    female_count = int(
        overall.loc[overall["gender_normalized"].eq("female"), "n_scholars"].sum()
    )
    male_female_ratio = (male_count / female_count) if female_count > 0 else None

    return {
        "overall_gender_distribution": overall.to_dict("records"),
        "per_domain_gender_distribution": per_domain.to_dict("records"),
        "gender_gap_analysis": {
            "male_count": male_count,
            "female_count": female_count,
            "male_to_female_ratio": male_female_ratio,
            "top_5_domains_by_female_share": female_share.head(5).to_dict("records"),
            "bottom_5_domains_by_female_share": female_share.tail(5).to_dict("records"),
        },
    }


def analyze_cross_domain(
    researchers: pd.DataFrame, domain_growth: pd.DataFrame
) -> dict[str, Any]:
    keyword_counts: dict[str, int] = {}
    for raw in researchers["keywords"].astype(str):
        tokens = [token.strip() for token in raw.split(";")]
        for token in tokens:
            if token:
                keyword_counts[token] = keyword_counts.get(token, 0) + 1

    keyword_df = pd.DataFrame(
        [
            {"keyword": keyword, "count": count}
            for keyword, count in keyword_counts.items()
        ],
    ).sort_values("count", ascending=False)

    h_index_stats = (
        researchers.groupby("domain_name")["h_index"]
        .agg(["count", "mean", "median", "min", "max"])
        .reset_index()
    )
    quantiles = researchers.groupby("domain_name")["h_index"].quantile(
        np.array([0.25, 0.75], dtype=float)
    )
    quantiles = quantiles.unstack(level=-1).reset_index()
    quantiles = quantiles.rename(columns={0.25: "h_index_q25", 0.75: "h_index_q75"})
    h_index_stats = h_index_stats.merge(quantiles, on="domain_name", how="left")

    gini_rows: list[dict[str, Any]] = []
    for domain_name, group in researchers.groupby("domain_name", sort=True):
        values = group["domain_citations"].to_numpy(dtype=float)
        gini_rows.append(
            {
                "domain_name": domain_name,
                "citation_gini": _gini(values),
                "n_scholars": len(group),
            },
        )

    fastest = domain_growth.sort_values(
        "scholars_growth_rate",
        ascending=False,
        na_position="last",
    )

    return {
        "fastest_growing_subfields_2019_2023": fastest.head(10).to_dict("records"),
        "keyword_frequency_top_50": keyword_df.head(50).to_dict("records"),
        "h_index_distribution_by_domain": h_index_stats.to_dict("records"),
        "citation_concentration_gini_by_domain": sorted(
            gini_rows,
            key=lambda row: (
                row["citation_gini"] if row["citation_gini"] is not None else -1
            ),
            reverse=True,
        ),
    }


def analyze_track1_integration(researchers: pd.DataFrame) -> dict[str, Any]:
    domain_sizes = researchers.groupby("domain_name").size().to_dict()

    matrix_rows: list[dict[str, Any]] = []
    for field in TRACK1_FIELDS:
        row: dict[str, Any] = {"field": field}
        weighted_sum = 0.0
        weight_mass = 0.0

        for subfield in sorted(TRACK1_SUBFIELD_MAP.keys()):
            affinity = TRACK1_SUBFIELD_MAP[subfield].get(field, 0.0)
            row[subfield] = affinity

            domain_weight = float(domain_sizes.get(subfield, 0))
            weighted_sum += affinity * domain_weight
            weight_mass += domain_weight

        row["weighted_affinity_index"] = (
            weighted_sum / weight_mass if weight_mass > 0 else 0.0
        )
        matrix_rows.append(row)

    matrix_df = pd.DataFrame(matrix_rows).sort_values(
        "weighted_affinity_index",
        ascending=False,
    )

    strongest_links: list[dict[str, Any]] = []
    for subfield, mapping in TRACK1_SUBFIELD_MAP.items():
        sorted_links = sorted(mapping.items(), key=lambda pair: pair[1], reverse=True)
        for field, score in sorted_links[:3]:
            strongest_links.append(
                {
                    "subfield": subfield,
                    "field": field,
                    "affinity": score,
                },
            )

    return {
        "mapping_notes": [
            "Computer Vision is linked to Biology/Medicine via medical imaging applications.",
            "NLP is linked to Psychology/Political Science via language and sentiment analysis.",
            "Data Mining is modeled as cross-cutting and connected to all Track 1 fields.",
        ],
        "field_ai_subfield_affinity_matrix": matrix_df.to_dict("records"),
        "strongest_field_subfield_links": strongest_links,
    }


def print_summary(results: dict[str, Any]) -> None:
    domain_df = pd.DataFrame(
        results["analysis_1_domain_size_distribution"]["top_scholar_counts_by_domain"]
    )
    country_df = pd.DataFrame(
        results["analysis_2_geographic_distribution"]["overall_country_distribution"]
    )
    org_df = pd.DataFrame(
        results["analysis_3_institutional_distribution"]["top_20_organizations"]
    )
    gender_df = pd.DataFrame(
        results["analysis_4_gender_distribution"]["overall_gender_distribution"]
    )
    growth_df = pd.DataFrame(
        results["analysis_5_cross_domain_analysis"][
            "fastest_growing_subfields_2019_2023"
        ]
    )

    print("=" * 88)
    print("AI2000 ANALYSIS SUMMARY")
    print("=" * 88)
    print("\n[1] Top domains by scholar count")
    if not domain_df.empty:
        print(domain_df.head(10).to_string(index=False))

    print("\n[2] Top countries")
    if not country_df.empty:
        print(country_df.head(10).to_string(index=False))

    print("\n[3] Top organizations")
    if not org_df.empty:
        print(org_df.head(10).to_string(index=False))

    print("\n[4] Overall gender distribution")
    if not gender_df.empty:
        print(gender_df.to_string(index=False))

    print("\n[5] Fastest growing subfields (scholars growth, 2019-2023)")
    if not growth_df.empty:
        display_cols = [
            "domain_name",
            "scholars_start",
            "scholars_end",
            "scholars_growth_rate",
            "scholars_cagr",
        ]
        display_cols = [col for col in display_cols if col in growth_df.columns]
        print(growth_df[display_cols].head(10).to_string(index=False))

    print("=" * 88)
    print(f"Results saved to: {OUTPUT_PATH}")


def main() -> None:
    researchers, domains = load_data()

    domain_size = analyze_domain_size_distribution(researchers, domains)
    domain_growth_df = pd.DataFrame(domain_size["growth_trends_2019_2023"])

    results: dict[str, Any] = {
        "metadata": {
            "researchers_path": str(RESEARCHERS_PATH),
            "domains_path": str(DOMAINS_PATH),
            "output_path": str(OUTPUT_PATH),
            "n_researcher_rows": len(researchers),
            "n_unique_domains_in_researchers": int(
                researchers["domain_name"].nunique()
            ),
            "analysis_year_window": [ANALYSIS_YEAR_START, ANALYSIS_YEAR_END],
        },
        "analysis_1_domain_size_distribution": domain_size,
        "analysis_2_geographic_distribution": analyze_geographic_distribution(
            researchers
        ),
        "analysis_3_institutional_distribution": analyze_institutional_distribution(
            researchers,
        ),
        "analysis_4_gender_distribution": analyze_gender_distribution(researchers),
        "analysis_5_cross_domain_analysis": analyze_cross_domain(
            researchers,
            domain_growth_df,
        ),
        "analysis_6_track1_integration": analyze_track1_integration(researchers),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(_to_native(results), f, ensure_ascii=False, indent=2)

    print_summary(results)


if __name__ == "__main__":
    main()
