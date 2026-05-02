#!/usr/bin/env python3
"""Collect AI adoption rates across scientific fields from OpenAlex."""
# pyright: reportAny=false, reportImplicitStringConcatenation=false, reportMissingImports=false, reportMissingTypeStubs=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false

from __future__ import annotations

import importlib
import logging
import time
from pathlib import Path
from typing import cast

import pandas as pd

from palimpsest.utils.config import settings

pyalex = importlib.import_module("pyalex")
Works = pyalex.Works

pyalex.config.email = settings.openalex_email or ""
pyalex.config.api_key = settings.openalex_api_key or ""

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

FIELDS: dict[str, str] = {
    "C41008148": "Computer Science",
    "C71924100": "Medicine",
    "C127413603": "Engineering",
    "C39432304": "Environmental Science",
    "C121332964": "Physics",
    "C86803240": "Biology",
    "C185592680": "Chemistry",
    "C17744445": "Political Science",
    "C33923547": "Mathematics",
    "C192562407": "Materials Science",
    "C15744967": "Psychology",
    "C162324750": "Economics",
    "C144133560": "Business",
    "C127313418": "Geology",
    "C205649164": "Geography",
}
AI_CONCEPT_ID = "C154945302"
ML_CONCEPT_ID = "C119857082"
START_YEAR = 2000
END_YEAR = 2025
MAX_RETRIES = 3
RETRY_BASE_SECONDS = 1.0
API_CALL_DELAY_SECONDS = 0.2

OUTPUT_DIR = Path("data/processed")
PARQUET_PATH = OUTPUT_DIR / "ai_adoption_by_field.parquet"
CSV_PATH = OUTPUT_DIR / "ai_adoption_by_field.csv"


def _extract_group_by_rows(result: object) -> list[dict[str, object]]:
    if isinstance(result, tuple):
        rows: object = result[0]
    else:
        rows = result

    if not isinstance(rows, list):
        raise TypeError(f"Unexpected group_by response type: {type(rows).__name__}")

    parsed_rows: list[dict[str, object]] = []
    for row in rows:
        if isinstance(row, dict):
            parsed_rows.append(cast(dict[str, object], row))
    return parsed_rows


def _group_rows_to_year_counts(rows: list[dict[str, object]]) -> dict[int, int]:
    counts_by_year: dict[int, int] = {}
    for row in rows:
        key = row.get("key")
        count = row.get("count")
        if not isinstance(key, int | str):
            continue
        try:
            year = int(key)
        except ValueError:
            continue

        if START_YEAR <= year <= END_YEAR and isinstance(count, int):
            counts_by_year[year] = count

    return counts_by_year


def _fetch_grouped_publication_counts(concept_id: str, ai_only: bool) -> dict[int, int]:
    full_id = f"https://openalex.org/{concept_id}"
    ai_full_id = f"https://openalex.org/{AI_CONCEPT_ID}"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if ai_only:
                query = Works().filter(concepts={"id": [full_id, ai_full_id]})
            else:
                query = Works().filter(concepts={"id": full_id})
            result = query.group_by("publication_year").get()
            time.sleep(API_CALL_DELAY_SECONDS)
            rows = _extract_group_by_rows(result)
            return _group_rows_to_year_counts(rows)
        except Exception as exc:
            if attempt == MAX_RETRIES:
                logger.exception(
                    "OpenAlex grouped count request failed after retries",
                    extra={
                        "concept_id": concept_id,
                        "ai_only": ai_only,
                        "attempts": MAX_RETRIES,
                    },
                )
                raise RuntimeError(
                    f"Failed request for concept_id={concept_id}, ai_only={ai_only}"
                ) from exc

            backoff_seconds = float(RETRY_BASE_SECONDS * (2 ** (attempt - 1)))
            logger.warning(
                "Retrying OpenAlex grouped count request",
                extra={
                    "concept_id": concept_id,
                    "ai_only": ai_only,
                    "attempt": attempt,
                    "sleep_seconds": backoff_seconds,
                    "error": str(exc),
                },
            )
            time.sleep(backoff_seconds)

    raise RuntimeError("Unreachable retry state")


def get_yearly_counts(concept_id: str) -> dict[int, int]:
    return _fetch_grouped_publication_counts(concept_id=concept_id, ai_only=False)


def get_yearly_ai_counts(concept_id: str) -> dict[int, int]:
    return _fetch_grouped_publication_counts(concept_id=concept_id, ai_only=True)


def _build_field_rows(
    concept_id: str, field_name: str
) -> list[dict[str, str | int | float]]:
    logger.info("Processing: %s (%s)", field_name, concept_id)
    total_by_year = get_yearly_counts(concept_id)
    ai_by_year = get_yearly_ai_counts(concept_id)

    rows: list[dict[str, str | int | float]] = []
    for year in range(START_YEAR, END_YEAR + 1):
        total_count = total_by_year.get(year, 0)
        ai_count = ai_by_year.get(year, 0)
        ai_fraction = (ai_count / total_count) if total_count > 0 else 0.0
        rows.append(
            {
                "field_id": concept_id,
                "field_name": field_name,
                "year": year,
                "total_count": total_count,
                "ai_count": ai_count,
                "ai_fraction": ai_fraction,
            },
        )

    return rows


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict[str, str | int | float]] = []
    for concept_id, field_name in FIELDS.items():
        all_rows.extend(_build_field_rows(concept_id=concept_id, field_name=field_name))

    df = pd.DataFrame(all_rows)
    df.to_parquet(PARQUET_PATH, index=False)
    df.to_csv(CSV_PATH, index=False)

    fields_processed = df["field_id"].nunique() if not df.empty else 0
    logger.info(
        "Saved AI adoption data",
        extra={
            "rows": len(df),
            "fields_processed": fields_processed,
            "parquet_path": str(PARQUET_PATH),
            "csv_path": str(CSV_PATH),
        },
    )
    print(
        f"Collection complete: rows={len(df)}, fields_processed={fields_processed}, year_range={START_YEAR}-{END_YEAR}"
    )


if __name__ == "__main__":
    main()
