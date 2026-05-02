#!/usr/bin/env python3
"""Collect retraction data and citation networks for contamination analysis."""

from __future__ import annotations

import json
import logging
import time
from itertools import chain
from pathlib import Path
from typing import Any

import pandas as pd
import pyalex
from pyalex import Works

from palimpsest.data.retraction_watch import RetractionWatchLoader
from palimpsest.utils.config import settings
from palimpsest.utils.logging import setup_logging

pyalex.config.email = settings.openalex_email or ""
pyalex.config.api_key = settings.openalex_api_key or ""

setup_logging("INFO")
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RETRACTED_PARQUET_PATH = OUTPUT_DIR / "retracted_papers.parquet"
RETRACTED_CSV_PATH = OUTPUT_DIR / "retracted_papers.csv"
CITERS_PARQUET_PATH = OUTPUT_DIR / "retraction_citers.parquet"
CITERS_CSV_PATH = OUTPUT_DIR / "retraction_citers.csv"
REFERENCES_PARQUET_PATH = OUTPUT_DIR / "retraction_references.parquet"
REFERENCES_CSV_PATH = OUTPUT_DIR / "retraction_references.csv"
STATS_PARQUET_PATH = OUTPUT_DIR / "retraction_propagation_stats.parquet"
STATS_CSV_PATH = OUTPUT_DIR / "retraction_propagation_stats.csv"

MAX_INITIAL_DOIS = 500
TOP_RETRACTED_COUNT = 50
MAX_CITERS_PER_PAPER = 500

PROGRESS_INTERVAL = 50
DOI_REQUEST_DELAY_SECONDS = 0.1
CITER_REQUEST_DELAY_SECONDS = 0.3


def _normalize_doi(doi: str) -> str:
    cleaned = doi.strip().lower()
    if cleaned.startswith("https://doi.org/"):
        return cleaned
    return f"https://doi.org/{cleaned}"


def fetch_work_by_doi(doi: str) -> dict[str, Any] | None:
    normalized = _normalize_doi(doi)
    try:
        result = Works()[normalized]
    except Exception as exc:
        logger.warning(
            "Failed to fetch retracted work by DOI",
            extra={"doi": doi, "normalized": normalized, "error": str(exc)},
        )
        return None

    if isinstance(result, tuple):
        if not result:
            return None
        first = result[0]
        return first if isinstance(first, dict) else None

    return result if isinstance(result, dict) else None


def fetch_citers(
    openalex_id: str, max_results: int = MAX_CITERS_PER_PAPER
) -> list[dict[str, Any]]:
    try:
        pages = (
            Works().filter(cites=openalex_id).paginate(per_page=200, n_max=max_results)
        )
        records = list(chain.from_iterable(pages))
    except Exception as exc:
        logger.warning(
            "Failed to fetch citing works",
            extra={
                "openalex_id": openalex_id,
                "max_results": max_results,
                "error": str(exc),
            },
        )
        return []

    return [record for record in records if isinstance(record, dict)]


def extract_reference_ids(work: dict[str, Any]) -> list[str]:
    raw_references = work.get("referenced_works")
    if not isinstance(raw_references, list):
        return []
    return [ref for ref in raw_references if isinstance(ref, str) and ref]


def build_stats(
    top_retracted_df: pd.DataFrame,
    citers_df: pd.DataFrame,
    references_df: pd.DataFrame,
) -> pd.DataFrame:
    if top_retracted_df.empty:
        return pd.DataFrame()

    citer_counts = (
        citers_df.groupby("retracted_openalex_id", as_index=False)
        .size()
        .rename(columns={"size": "direct_citers_count"})
        if not citers_df.empty
        else pd.DataFrame(columns=["retracted_openalex_id", "direct_citers_count"])
    )
    reference_counts = (
        references_df.groupby("retracted_openalex_id", as_index=False)
        .size()
        .rename(columns={"size": "references_count"})
        if not references_df.empty
        else pd.DataFrame(columns=["retracted_openalex_id", "references_count"])
    )

    stats_df = top_retracted_df[
        ["doi", "openalex_id", "title", "publication_year", "cited_by_count"]
    ].copy()
    stats_df = stats_df.merge(
        citer_counts,
        left_on="openalex_id",
        right_on="retracted_openalex_id",
        how="left",
    )
    stats_df = stats_df.merge(
        reference_counts,
        left_on="openalex_id",
        right_on="retracted_openalex_id",
        how="left",
        suffixes=("", "_ref"),
    )

    stats_df = stats_df.drop(
        columns=["retracted_openalex_id", "retracted_openalex_id_ref"], errors="ignore"
    )
    stats_df["direct_citers_count"] = (
        stats_df["direct_citers_count"].fillna(0).astype(int)
    )
    stats_df["references_count"] = stats_df["references_count"].fillna(0).astype(int)
    stats_df["captured_vs_openalex_cited_by_ratio"] = stats_df.apply(
        lambda row: (
            float(row["direct_citers_count"]) / float(row["cited_by_count"])
            if row["cited_by_count"]
            else 0.0
        ),
        axis=1,
    )

    global_row = {
        "doi": "__ALL__",
        "openalex_id": "__ALL__",
        "title": "All sampled retracted papers",
        "publication_year": None,
        "cited_by_count": int(stats_df["cited_by_count"].sum()),
        "direct_citers_count": int(stats_df["direct_citers_count"].sum()),
        "references_count": int(stats_df["references_count"].sum()),
        "captured_vs_openalex_cited_by_ratio": (
            float(stats_df["direct_citers_count"].sum())
            / float(stats_df["cited_by_count"].sum())
            if int(stats_df["cited_by_count"].sum()) > 0
            else 0.0
        ),
    }
    return pd.concat([stats_df, pd.DataFrame([global_row])], ignore_index=True)


def main() -> None:
    logger.info("Loading Retraction Watch data")
    loader = RetractionWatchLoader()

    try:
        rw_df = loader.load()
    except Exception as exc:
        logger.error("Failed to load Retraction Watch data", extra={"error": str(exc)})
        raise

    logger.info("Loaded Retraction Watch records", extra={"count": len(rw_df)})

    retracted_dois = sorted(loader.get_retracted_dois())
    logger.info("Collected unique retracted DOIs", extra={"count": len(retracted_dois)})
    if not retracted_dois:
        logger.error("No retracted DOIs found in Retraction Watch data")
        return

    sample_dois = retracted_dois[:MAX_INITIAL_DOIS]
    logger.info(
        "Fetching OpenAlex metadata for sampled DOIs",
        extra={"sample_size": len(sample_dois), "progress_interval": PROGRESS_INTERVAL},
    )

    retracted_rows: list[dict[str, Any]] = []
    references_rows: list[dict[str, Any]] = []

    for index, doi in enumerate(sample_dois, start=1):
        if index == 1 or index % PROGRESS_INTERVAL == 0:
            logger.info(
                "OpenAlex DOI progress",
                extra={"processed": index, "total": len(sample_dois)},
            )

        work = fetch_work_by_doi(doi)
        if work is None:
            time.sleep(DOI_REQUEST_DELAY_SECONDS)
            continue

        openalex_id = work.get("id")
        if not isinstance(openalex_id, str) or not openalex_id:
            logger.warning("Work has no valid OpenAlex ID", extra={"doi": doi})
            time.sleep(DOI_REQUEST_DELAY_SECONDS)
            continue

        references = extract_reference_ids(work)
        retracted_rows.append(
            {
                "doi": doi,
                "openalex_id": openalex_id,
                "title": work.get("title", ""),
                "publication_year": work.get("publication_year"),
                "cited_by_count": int(work.get("cited_by_count", 0) or 0),
                "references_count": len(references),
                "referenced_works_json": json.dumps(references, ensure_ascii=True),
                "is_retracted_sample": True,
            },
        )

        for referenced_openalex_id in references:
            references_rows.append(
                {
                    "retracted_doi": doi,
                    "retracted_openalex_id": openalex_id,
                    "referenced_openalex_id": referenced_openalex_id,
                    "depth": -1,
                },
            )

        time.sleep(DOI_REQUEST_DELAY_SECONDS)

    retracted_df = pd.DataFrame(retracted_rows)
    references_df = pd.DataFrame(references_rows)

    if retracted_df.empty:
        logger.error("No sampled retracted papers were resolved in OpenAlex")
        return

    logger.info(
        "Resolved retracted papers in OpenAlex",
        extra={"resolved_count": len(retracted_df), "sampled_count": len(sample_dois)},
    )

    top_retracted_df = retracted_df.nlargest(
        TOP_RETRACTED_COUNT, "cited_by_count"
    ).copy()
    logger.info(
        "Selected top retracted papers for 1-hop propagation",
        extra={
            "selected": len(top_retracted_df),
            "min_cited_by": int(top_retracted_df["cited_by_count"].min()),
            "max_cited_by": int(top_retracted_df["cited_by_count"].max()),
        },
    )

    citer_rows: list[dict[str, Any]] = []
    for index, (_, row) in enumerate(top_retracted_df.iterrows(), start=1):
        if index == 1 or index % 10 == 0:
            logger.info(
                "Citer fetch progress",
                extra={"processed": index, "total": len(top_retracted_df)},
            )

        openalex_id = str(row["openalex_id"])
        citers = fetch_citers(openalex_id=openalex_id, max_results=MAX_CITERS_PER_PAPER)

        for citer in citers:
            citer_rows.append(
                {
                    "retracted_doi": row["doi"],
                    "retracted_openalex_id": openalex_id,
                    "retracted_title": row["title"],
                    "retracted_year": row["publication_year"],
                    "citing_openalex_id": citer.get("id", ""),
                    "citing_title": citer.get("title", ""),
                    "citing_year": citer.get("publication_year"),
                    "citing_cited_by_count": int(citer.get("cited_by_count", 0) or 0),
                    "depth": 1,
                },
            )

        time.sleep(CITER_REQUEST_DELAY_SECONDS)

    citers_df = pd.DataFrame(citer_rows)
    stats_df = build_stats(
        top_retracted_df=top_retracted_df,
        citers_df=citers_df,
        references_df=references_df,
    )

    retracted_df.to_parquet(RETRACTED_PARQUET_PATH, index=False)
    retracted_df.to_csv(RETRACTED_CSV_PATH, index=False)

    citers_df.to_parquet(CITERS_PARQUET_PATH, index=False)
    citers_df.to_csv(CITERS_CSV_PATH, index=False)

    references_df.to_parquet(REFERENCES_PARQUET_PATH, index=False)
    references_df.to_csv(REFERENCES_CSV_PATH, index=False)

    stats_df.to_parquet(STATS_PARQUET_PATH, index=False)
    stats_df.to_csv(STATS_CSV_PATH, index=False)

    logger.info("=== Collection Summary ===")
    logger.info("Retraction Watch rows", extra={"count": len(rw_df)})
    logger.info("Unique retracted DOIs", extra={"count": len(retracted_dois)})
    logger.info("Sampled DOIs (initial pass)", extra={"count": len(sample_dois)})
    logger.info(
        "Resolved retracted papers in OpenAlex", extra={"count": len(retracted_df)}
    )
    logger.info("Top retracted papers analyzed", extra={"count": len(top_retracted_df)})
    logger.info("Direct citer rows (depth=1)", extra={"count": len(citers_df)})
    logger.info("Reference rows (depth=-1)", extra={"count": len(references_df)})
    logger.info("Stats rows", extra={"count": len(stats_df)})
    logger.info(
        "Outputs",
        extra={
            "retracted_parquet": str(RETRACTED_PARQUET_PATH),
            "retracted_csv": str(RETRACTED_CSV_PATH),
            "citers_parquet": str(CITERS_PARQUET_PATH),
            "citers_csv": str(CITERS_CSV_PATH),
            "references_parquet": str(REFERENCES_PARQUET_PATH),
            "references_csv": str(REFERENCES_CSV_PATH),
            "stats_parquet": str(STATS_PARQUET_PATH),
            "stats_csv": str(STATS_CSV_PATH),
        },
    )


if __name__ == "__main__":
    main()
