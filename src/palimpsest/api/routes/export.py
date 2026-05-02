from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Literal

import pandas as pd
from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse

from palimpsest.api.dependencies import limiter

router = APIRouter(prefix="/export", tags=["export"])

BASE_PROCESSED_DIR = Path(__file__).resolve().parents[4] / "data" / "processed"
FIELD_SUMMARY_PATH = BASE_PROCESSED_DIR / "neo4j_field_summary.parquet"
FIELD_PANEL_PATH = BASE_PROCESSED_DIR / "neo4j_field_panel.parquet"
RETRACTION_ANALYSIS_PATH = (
    BASE_PROCESSED_DIR / "retraction_analysis" / "retraction_citation_analysis.json"
)


def _load_parquet(path: Path) -> pd.DataFrame:
    """Load a parquet file and normalize file-related failures.

    Args:
        path: Absolute path to a parquet file.

    Returns:
        Loaded DataFrame.

    Raises:
        HTTPException: If file is missing or unreadable.
    """

    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"Data file not found: {path.name}")

    try:
        return pd.read_parquet(path)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load data file: {path.name}",
        ) from exc


def _csv_response(dataframe: pd.DataFrame, filename: str) -> StreamingResponse:
    """Build a CSV download response from a DataFrame.

    Args:
        dataframe: Data to serialize as CSV.
        filename: Download filename for Content-Disposition.

    Returns:
        StreamingResponse configured for CSV attachment download.
    """

    buffer = io.StringIO()
    dataframe.to_csv(buffer, index=False)
    buffer.seek(0)
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        iter([buffer.getvalue()]), media_type="text/csv", headers=headers
    )


@limiter.limit("20/minute")
@router.get("/field-summary")
def export_field_summary(
    request: Request,
    format: Literal["csv", "json"] = Query(default="json"),
) -> Response:
    """Export field-level summary table in CSV or JSON format.

    Args:
        format: Export format, either csv or json.

    Returns:
        CSV attachment download or JSON payload of all field summary rows.
    """

    summary_df = _load_parquet(FIELD_SUMMARY_PATH)
    if format == "csv":
        return _csv_response(summary_df, "field_summary.csv")

    return JSONResponse(content=summary_df.to_dict(orient="records"))


@limiter.limit("20/minute")
@router.get("/field-yearly")
def export_field_yearly(
    request: Request,
    field: str,
    format: Literal["csv", "json"] = Query(default="json"),
) -> Response:
    """Export yearly time series rows for a selected field.

    Args:
        field: Exact field_name to filter rows.
        format: Export format, either csv or json.

    Returns:
        CSV attachment download or JSON payload for the selected field.

    Raises:
        HTTPException: If no data is found for the requested field.
    """

    panel_df = _load_parquet(FIELD_PANEL_PATH)
    field_df = panel_df.loc[panel_df["field_name"] == field].sort_values("year")

    if field_df.empty:
        raise HTTPException(status_code=404, detail=f"Unknown field: {field}")

    safe_field_name = field.lower().replace(" ", "_").replace(",", "")
    if format == "csv":
        return _csv_response(field_df, f"field_yearly_{safe_field_name}.csv")

    return JSONResponse(content=field_df.to_dict(orient="records"))


@limiter.limit("20/minute")
@router.get("/retraction-summary")
def export_retraction_summary(
    request: Request,
    format: Literal["csv", "json"] = Query(default="json"),
) -> Response:
    """Export retraction analysis summary in CSV or JSON format.

    Args:
        format: Export format, either csv or json.

    Returns:
        CSV attachment download or JSON payload from retraction analysis.
    """

    if not RETRACTION_ANALYSIS_PATH.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Data file not found: {RETRACTION_ANALYSIS_PATH.name}",
        )

    try:
        retraction_data = json.loads(RETRACTION_ANALYSIS_PATH.read_text())
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load data file: {RETRACTION_ANALYSIS_PATH.name}",
        ) from exc

    if format == "csv":
        flattened_rows = []
        for key, value in retraction_data.items():
            if isinstance(value, list):
                for item in value:
                    row = {"section": key}
                    if isinstance(item, dict):
                        row.update(item)
                    else:
                        row["value"] = item
                    flattened_rows.append(row)
            elif isinstance(value, dict):
                row = {"section": key}
                row.update(value)
                flattened_rows.append(row)
            else:
                flattened_rows.append({"section": key, "value": value})

        retraction_df = pd.DataFrame(flattened_rows)
        return _csv_response(retraction_df, "retraction_summary.csv")

    return JSONResponse(content=retraction_data)
