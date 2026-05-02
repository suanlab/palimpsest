#!/usr/bin/env python3
"""Join Retraction Watch records with OpenAlex work metadata by DOI.

This script reads Retraction Watch CSV entries, normalizes original-paper DOIs,
queries OpenAlex in DOI batches, and writes an expanded joined dataset.
"""

from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path
from typing import cast

import httpx
import pandas as pd

from palimpsest.utils.config import settings
from palimpsest.utils.logging import setup_logging

LOGGER = logging.getLogger(__name__)

RW_CSV_PATH = Path(
    "data/raw/retraction_watch/retraction-watch-data/retraction_watch.csv",
)
OUTPUT_DIR = Path("data/processed")
JOINED_OUTPUT_PATH = OUTPUT_DIR / "retraction_watch_openalex_joined.parquet"
UNMATCHED_OUTPUT_PATH = OUTPUT_DIR / "retraction_watch_unmatched.csv"
CACHE_OUTPUT_PATH = OUTPUT_DIR / "retraction_watch_openalex_cache.parquet"

OPENALEX_WORKS_URL = "https://api.openalex.org/works"
BATCH_SIZE = 50
MAX_REQUESTS_PER_SECOND = 10.0
REQUEST_INTERVAL_SECONDS = 1.0 / MAX_REQUESTS_PER_SECOND
MAX_RETRIES = 3
PROGRESS_LOG_INTERVAL = 1000

RW_COLUMNS = {
    "OriginalPaperDOI": "doi",
    "RetractionDate": "retraction_date",
    "RetractionNature": "retraction_nature",
    "Reason": "reason",
    "Subject": "subject",
    "Journal": "journal",
    "Publisher": "publisher",
    "Country": "country",
}

OPENALEX_COLUMNS = [
    "doi",
    "openalex_id",
    "title",
    "year",
    "cited_by_count",
    "is_retracted",
    "found",
]


def normalize_doi(raw_value: object) -> str | None:
    """Normalize a DOI string for matching.

    Args:
        raw_value: Raw DOI-like value from source data.

    Returns:
        Lowercased DOI without URL prefix, or None for invalid values.
    """

    if not isinstance(raw_value, str):
        return None

    cleaned = raw_value.strip().lower()
    if not cleaned:
        return None

    prefixes = (
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
    )
    for prefix in prefixes:
        if cleaned.startswith(prefix):
            cleaned = cleaned.removeprefix(prefix)
            break

    cleaned = cleaned.strip()
    if not cleaned.startswith("10."):
        return None

    return cleaned


def chunked(values: list[str], chunk_size: int) -> list[list[str]]:
    """Split a list into fixed-size chunks.

    Args:
        values: Input values.
        chunk_size: Maximum chunk size.

    Returns:
        List of chunks.
    """

    return [values[i : i + chunk_size] for i in range(0, len(values), chunk_size)]


def load_retraction_watch() -> pd.DataFrame:
    """Load and prepare Retraction Watch rows with normalized DOI.

    Returns:
        DataFrame with selected Retraction Watch fields and normalized `doi`.
    """

    read_columns = list(RW_COLUMNS.keys())
    rw_df = pd.read_csv(
        RW_CSV_PATH,
        usecols=read_columns,
        dtype={column: "string" for column in read_columns},
    )
    rw_df = rw_df.rename(columns=RW_COLUMNS)
    rw_df["doi"] = rw_df["doi"].map(normalize_doi)
    rw_df = rw_df[rw_df["doi"].notna()].copy()

    for column in (
        "retraction_date",
        "retraction_nature",
        "reason",
        "subject",
        "journal",
        "publisher",
        "country",
    ):
        rw_df[column] = rw_df[column].fillna("")

    return rw_df


def load_existing_cache() -> pd.DataFrame:
    """Load existing DOI-to-OpenAlex cache for resume support.

    Returns:
        DataFrame with cached DOI resolution records.
    """

    if not CACHE_OUTPUT_PATH.exists():
        return pd.DataFrame(columns=OPENALEX_COLUMNS)

    cached = pd.read_parquet(CACHE_OUTPUT_PATH)
    for column in OPENALEX_COLUMNS:
        if column not in cached.columns:
            cached[column] = pd.NA

    cached = cached[OPENALEX_COLUMNS].copy()
    cached["doi"] = cached["doi"].map(normalize_doi)
    cached = cached[cached["doi"].notna()].copy()
    cached = cached.drop_duplicates(subset=["doi"], keep="last")
    return cached


def build_request_params(dois: list[str]) -> dict[str, str]:
    """Build OpenAlex request parameters for DOI batch lookup.

    Args:
        dois: Normalized DOI strings.

    Returns:
        Query parameter dictionary.
    """

    params: dict[str, str] = {
        "filter": "doi:" + "|".join(dois),
        "per-page": str(len(dois)),
    }

    if settings.openalex_email:
        params["mailto"] = settings.openalex_email
    if settings.openalex_api_key:
        params["api_key"] = settings.openalex_api_key

    return params


def _extract_openalex_doi(work: dict[str, object]) -> str | None:
    """Extract DOI from an OpenAlex work payload.

    Args:
        work: OpenAlex work JSON object.

    Returns:
        Normalized DOI or None.
    """

    doi_value = work.get("doi")
    if isinstance(doi_value, str):
        normalized = normalize_doi(doi_value)
        if normalized:
            return normalized

    ids = work.get("ids")
    if isinstance(ids, dict):
        ids = cast(dict[str, object], ids)
        ids_doi = ids.get("doi")
        if isinstance(ids_doi, str):
            return normalize_doi(ids_doi)

    return None


def fetch_openalex_batch(
    client: httpx.Client,
    dois: list[str],
    last_request_at: float,
) -> tuple[list[dict[str, object]], float]:
    """Fetch OpenAlex works for a DOI batch with retries and rate limiting.

    Args:
        client: Reusable HTTP client.
        dois: DOI batch to resolve.
        last_request_at: Monotonic timestamp of prior request.

    Returns:
        A tuple of (OpenAlex result rows, latest request timestamp).
    """

    elapsed = time.monotonic() - last_request_at
    wait_seconds = REQUEST_INTERVAL_SECONDS - elapsed
    if wait_seconds > 0:
        time.sleep(wait_seconds)

    request_params = build_request_params(dois)

    for attempt in range(1, MAX_RETRIES + 1):
        request_time = time.monotonic()
        try:
            response = client.get(OPENALEX_WORKS_URL, params=request_params)
            _ = response.raise_for_status()
            payload_obj = cast(object, response.json())
            if not isinstance(payload_obj, dict):
                LOGGER.warning(
                    "Unexpected OpenAlex payload type",
                    extra={"payload_type": type(payload_obj).__name__},
                )
                return [], request_time

            payload_dict = cast(dict[str, object], payload_obj)
            results = payload_dict.get("results")
            if isinstance(results, list):
                rows: list[dict[str, object]] = []
                result_items = cast(list[object], results)
                for row_obj in result_items:
                    if isinstance(row_obj, dict):
                        rows.append(cast(dict[str, object], row_obj))
                return rows, request_time
            LOGGER.warning(
                "Unexpected OpenAlex results payload",
                extra={"batch_size": len(dois), "attempt": attempt},
            )
            return [], request_time
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            should_retry = status_code == 429 or status_code >= 500
            if attempt < MAX_RETRIES and should_retry:
                retry_after_header = ""
                if "Retry-After" in exc.response.headers:
                    retry_after_header = exc.response.headers["Retry-After"]
                try:
                    retry_after = float(retry_after_header)
                except ValueError:
                    retry_after = float(attempt)
                LOGGER.warning(
                    "OpenAlex batch request retry after HTTP error",
                    extra={
                        "status_code": status_code,
                        "attempt": attempt,
                        "sleep_seconds": retry_after,
                    },
                )
                time.sleep(retry_after)
                continue

            LOGGER.error(
                "OpenAlex batch request failed",
                extra={
                    "status_code": status_code,
                    "attempt": attempt,
                    "batch_size": len(dois),
                    "error": str(exc),
                },
            )
            return [], request_time
        except httpx.RequestError as exc:
            if attempt < MAX_RETRIES:
                backoff_seconds = float(attempt)
                LOGGER.warning(
                    "OpenAlex network request retry",
                    extra={
                        "attempt": attempt,
                        "sleep_seconds": backoff_seconds,
                        "error": str(exc),
                    },
                )
                time.sleep(backoff_seconds)
                continue

            LOGGER.error(
                "OpenAlex network request failed",
                extra={
                    "attempt": attempt,
                    "batch_size": len(dois),
                    "error": str(exc),
                },
            )
            return [], request_time

    return [], time.monotonic()


def _to_int(value: object) -> int | None:
    """Convert unknown value to int when possible.

    Args:
        value: Value to convert.

    Returns:
        Integer value or None.
    """

    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def batch_to_cache_rows(
    requested_dois: list[str],
    openalex_rows: list[dict[str, object]],
) -> pd.DataFrame:
    """Convert one DOI batch response into cache rows.

    Args:
        requested_dois: DOI values included in the request.
        openalex_rows: OpenAlex `results` payload subset.

    Returns:
        DataFrame with one resolution row per requested DOI.
    """

    resolved_by_doi: dict[str, dict[str, object]] = {}
    for work in openalex_rows:
        normalized_doi = _extract_openalex_doi(work)
        if not normalized_doi or normalized_doi not in requested_dois:
            continue

        openalex_id_value = work.get("id")
        openalex_id = openalex_id_value if isinstance(openalex_id_value, str) else ""

        title_value = work.get("title")
        title = title_value if isinstance(title_value, str) else ""

        publication_year = _to_int(work.get("publication_year"))
        cited_by_count = _to_int(work.get("cited_by_count"))
        is_retracted_value = work.get("is_retracted")
        is_retracted = (
            is_retracted_value if isinstance(is_retracted_value, bool) else None
        )

        resolved_by_doi[normalized_doi] = {
            "doi": normalized_doi,
            "openalex_id": openalex_id,
            "title": title,
            "year": publication_year,
            "cited_by_count": cited_by_count,
            "is_retracted": is_retracted,
            "found": True,
        }

    rows: list[dict[str, object]] = []
    for doi in requested_dois:
        if doi in resolved_by_doi:
            rows.append(resolved_by_doi[doi])
            continue

        rows.append(
            {
                "doi": doi,
                "openalex_id": "",
                "title": "",
                "year": None,
                "cited_by_count": None,
                "is_retracted": None,
                "found": False,
            },
        )

    return pd.DataFrame(rows, columns=OPENALEX_COLUMNS)


def materialize_outputs(rw_df: pd.DataFrame, cache_df: pd.DataFrame) -> tuple[int, int]:
    """Write joined parquet and unmatched DOI CSV from current cache state.

    Args:
        rw_df: Retraction Watch rows with normalized DOI.
        cache_df: DOI resolution cache.

    Returns:
        Tuple of (matched_unique_dois, total_unique_dois).
    """

    found_mask = cache_df["found"].fillna(False).astype(bool)
    matched_cache = cache_df[found_mask].copy()
    matched_cache = matched_cache.drop(columns=["found"])

    joined_df = rw_df.merge(matched_cache, on="doi", how="inner")
    joined_df = joined_df[
        [
            "doi",
            "openalex_id",
            "title",
            "year",
            "cited_by_count",
            "is_retracted",
            "retraction_date",
            "retraction_nature",
            "reason",
            "subject",
            "journal",
            "publisher",
            "country",
        ]
    ]

    unmatched_df = cache_df[~found_mask][["doi"]].copy()
    unmatched_df = unmatched_df.drop_duplicates(subset=["doi"])
    unmatched_df = unmatched_df.merge(
        rw_df.groupby("doi", as_index=False).size().rename(columns={"size": "rw_rows"}),
        on="doi",
        how="left",
    )

    JOINED_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joined_df.to_parquet(JOINED_OUTPUT_PATH, index=False)
    unmatched_df.to_csv(UNMATCHED_OUTPUT_PATH, index=False)

    matched_unique = matched_cache["doi"].nunique()
    total_unique = rw_df["doi"].nunique()
    return int(matched_unique), int(total_unique)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the join workflow.

    Returns:
        Parsed argument namespace.
    """

    parser = argparse.ArgumentParser(
        description="Join Retraction Watch records with OpenAlex by DOI.",
    )
    _ = parser.add_argument(
        "--max-dois",
        type=int,
        default=None,
        help="Limit unique DOI count for smoke runs.",
    )
    return parser.parse_args()


def main(max_dois: int | None = None) -> None:
    """Run the Retraction Watch ↔ OpenAlex DOI join workflow.

    Args:
        max_dois: Optional limit on unique DOI count to process.
    """

    setup_logging(settings.log_level)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not settings.openalex_email:
        LOGGER.warning("RESEARCH_OPENALEX_EMAIL is not configured")
    if not settings.openalex_api_key:
        LOGGER.warning("RESEARCH_OPENALEX_API_KEY is not configured")

    LOGGER.info("Loading Retraction Watch CSV", extra={"path": str(RW_CSV_PATH)})
    rw_df = load_retraction_watch()

    unique_dois_raw = cast(
        list[object],
        rw_df["doi"].dropna().astype(str).unique().tolist(),
    )
    unique_dois: list[str] = sorted(
        value for value in unique_dois_raw if isinstance(value, str)
    )
    if isinstance(max_dois, int) and max_dois > 0:
        unique_dois = unique_dois[:max_dois]

    LOGGER.info(
        "Prepared normalized DOI set",
        extra={
            "rw_rows": len(rw_df),
            "unique_dois": len(unique_dois),
            "batch_size": BATCH_SIZE,
        },
    )

    cache_df = load_existing_cache()
    processed_dois = set(cache_df["doi"].dropna().astype(str).tolist())
    remaining_dois = [doi for doi in unique_dois if doi not in processed_dois]

    LOGGER.info(
        "Resume state",
        extra={
            "already_processed": len(processed_dois),
            "remaining": len(remaining_dois),
            "cache_path": str(CACHE_OUTPUT_PATH),
        },
    )

    last_request_at = 0.0
    matched_unique = 0
    total_unique = len(unique_dois)
    if remaining_dois:
        with httpx.Client(timeout=30.0) as client:
            for batch_index, doi_batch in enumerate(
                chunked(remaining_dois, BATCH_SIZE),
                start=1,
            ):
                openalex_rows, last_request_at = fetch_openalex_batch(
                    client=client,
                    dois=doi_batch,
                    last_request_at=last_request_at,
                )

                batch_cache_df = batch_to_cache_rows(
                    requested_dois=doi_batch,
                    openalex_rows=openalex_rows,
                )
                cache_df = pd.concat([cache_df, batch_cache_df], ignore_index=True)
                cache_df = cache_df.drop_duplicates(subset=["doi"], keep="last")

                cache_df.to_parquet(CACHE_OUTPUT_PATH, index=False)
                matched_unique, total_unique = materialize_outputs(
                    rw_df=rw_df,
                    cache_df=cache_df,
                )

                processed_count = len(processed_dois) + (batch_index * BATCH_SIZE)
                if (
                    batch_index == 1
                    or processed_count >= len(unique_dois)
                    or processed_count % PROGRESS_LOG_INTERVAL == 0
                ):
                    match_rate = (
                        (matched_unique / total_unique) * 100.0 if total_unique else 0.0
                    )
                    LOGGER.info(
                        (
                            "Join progress: processed=%s/%s unique DOIs, "
                            "matched=%s, match_rate=%.2f%%"
                        ),
                        min(processed_count, len(unique_dois)),
                        len(unique_dois),
                        matched_unique,
                        match_rate,
                        extra={
                            "processed_unique_dois": min(
                                processed_count, len(unique_dois)
                            ),
                            "total_unique_dois": len(unique_dois),
                            "matched_unique_dois": matched_unique,
                            "match_rate_pct": round(match_rate, 2),
                        },
                    )
    else:
        matched_unique, total_unique = materialize_outputs(
            rw_df=rw_df, cache_df=cache_df
        )

    final_match_rate = (matched_unique / total_unique) * 100.0 if total_unique else 0.0
    LOGGER.info(
        "Join complete: matched=%s/%s unique DOIs (%.2f%%)",
        matched_unique,
        total_unique,
        final_match_rate,
        extra={
            "rw_rows": len(rw_df),
            "total_unique_dois": total_unique,
            "matched_unique_dois": matched_unique,
            "match_rate_pct": round(final_match_rate, 2),
            "joined_output": str(JOINED_OUTPUT_PATH),
            "unmatched_output": str(UNMATCHED_OUTPUT_PATH),
        },
    )


if __name__ == "__main__":
    args = parse_args()
    max_dois_arg = cast(object, args.max_dois)
    main(max_dois=max_dois_arg if isinstance(max_dois_arg, int) else None)
