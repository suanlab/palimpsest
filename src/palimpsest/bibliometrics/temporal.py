from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def citation_trajectory(
    work_id: str, citations_by_year: dict[int, int]
) -> pd.DataFrame:
    """Build annual and cumulative citation trajectory for a work.

    Args:
        work_id: Identifier of the focal work.
        citations_by_year: Mapping year -> annual citations.

    Returns:
        DataFrame with columns: year, cumulative_citations, annual_citations.
    """
    del work_id

    years = sorted(citations_by_year)
    annual_citations = [int(citations_by_year[year]) for year in years]

    cumulative_citations: list[int] = []
    running_total = 0
    for count in annual_citations:
        running_total += count
        cumulative_citations.append(running_total)

    return pd.DataFrame(
        {
            "year": years,
            "cumulative_citations": cumulative_citations,
            "annual_citations": annual_citations,
        },
    )


def field_growth_rate(
    works: list[dict[str, object]],
    year_field: str = "publication_year",
) -> pd.DataFrame:
    """Compute yearly publication counts and year-over-year growth.

    Args:
        works: List of work records.
        year_field: Key in each work containing publication year.

    Returns:
        DataFrame with columns: year, count, growth_rate.
    """
    counts_by_year: dict[int, int] = {}
    for work in works:
        year_raw = work.get(year_field)
        if not isinstance(year_raw, int):
            continue
        counts_by_year[year_raw] = counts_by_year.get(year_raw, 0) + 1

    years = sorted(counts_by_year)
    counts = [counts_by_year[year] for year in years]

    growth_rates: list[float] = []
    previous_count: int | None = None
    for current_count in counts:
        if previous_count is None or previous_count == 0:
            growth_rates.append(float("nan"))
        else:
            growth_rates.append((current_count - previous_count) / previous_count)
        previous_count = current_count

    return pd.DataFrame(
        {
            "year": years,
            "count": counts,
            "growth_rate": growth_rates,
        },
    )


def knowledge_half_life(citations_by_age: dict[int, int]) -> float:
    """Estimate citation half-life age by linear interpolation.

    Args:
        citations_by_age: Mapping age in years since publication -> citations.

    Returns:
        Age at which 50% of total citations have accumulated, or NaN when the
        input contains no citations.
    """
    if not citations_by_age:
        return float("nan")

    total_citations = sum(max(count, 0) for count in citations_by_age.values())
    if total_citations == 0:
        return float("nan")

    half_threshold = total_citations / 2
    cumulative = 0
    previous_age: int | None = None
    previous_cumulative = 0

    for age in sorted(citations_by_age):
        annual = max(citations_by_age[age], 0)
        previous_age = age if previous_age is None else previous_age
        cumulative += annual

        if cumulative >= half_threshold:
            if annual == 0:
                return float(age)
            if previous_cumulative == half_threshold:
                return float(previous_age)

            lower_age = previous_age
            upper_age = age
            interval_citations = cumulative - previous_cumulative
            if interval_citations <= 0:
                return float(age)

            fraction = (half_threshold - previous_cumulative) / interval_citations
            return float(lower_age + fraction * (upper_age - lower_age))

        previous_age = age
        previous_cumulative = cumulative

    return float("nan")
