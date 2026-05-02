#!/usr/bin/env python3
"""Extract pre-computed yearly field data from Neo4j into analysis-ready parquet files."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BOLT_URI = "bolt://localhost:7687"
AUTH = ("neo4j", "research2026")
OUTPUT_DIR = Path("data/processed")


def main() -> None:
    driver = GraphDatabase.driver(BOLT_URI, auth=AUTH)
    logger.info("Connected to Neo4j")

    with driver.session() as session:
        result = session.run(
            "MATCH (f:Field) "
            "RETURN f.field_id AS field_id, "
            "f.field_name AS field_name, "
            "f.paper_count AS paper_count, "
            "f.ai_paper_count AS ai_title_count, "
            "f.ai_concept_count AS ai_concept_count, "
            "coalesce(f.yearly_paper_counts, '{}') AS yearly_papers, "
            "coalesce(f.yearly_ai_paper_counts, '{}') AS yearly_ai_title, "
            "coalesce(f.yearly_ai_concept_counts, '{}') AS yearly_ai_concept"
        )
        fields = [dict(r) for r in result]

    driver.close()
    logger.info("Fetched %d fields", len(fields))

    # Build long-format panel: field x year
    rows: list[dict[str, object]] = []
    for f in fields:
        yearly_papers: dict[str, int] = json.loads(f["yearly_papers"])
        yearly_ai_title: dict[str, int] = json.loads(f["yearly_ai_title"])
        yearly_ai_concept: dict[str, int] = json.loads(f["yearly_ai_concept"])

        for year_str, total in yearly_papers.items():
            year = int(year_str)
            ai_title = yearly_ai_title.get(year_str, 0)
            ai_concept = yearly_ai_concept.get(year_str, 0)
            rows.append(
                {
                    "field_id": f["field_id"],
                    "field_name": f["field_name"],
                    "year": year,
                    "total_count": total,
                    "ai_title_count": ai_title,
                    "ai_concept_count": ai_concept,
                    "ai_title_fraction": ai_title / total if total > 0 else 0.0,
                    "ai_concept_fraction": ai_concept / total if total > 0 else 0.0,
                }
            )

    df = pd.DataFrame(rows).sort_values(["field_name", "year"]).reset_index(drop=True)
    logger.info(
        "Panel shape: %s (%d fields x %d years)",
        df.shape,
        df["field_name"].nunique(),
        df["year"].nunique(),
    )

    # Save
    out_path = OUTPUT_DIR / "neo4j_field_panel.parquet"
    df.to_parquet(out_path, index=False)
    logger.info("Saved to %s", out_path)

    # Also save field-level summary
    summary_rows: list[dict[str, object]] = []
    for f in fields:
        summary_rows.append(
            {
                "field_id": f["field_id"],
                "field_name": f["field_name"],
                "paper_count": f["paper_count"],
                "ai_title_count": f["ai_title_count"],
                "ai_concept_count": f["ai_concept_count"],
                "ai_title_fraction": f["ai_title_count"] / f["paper_count"]
                if f["paper_count"]
                else 0.0,
                "ai_concept_fraction": f["ai_concept_count"] / f["paper_count"]
                if f["paper_count"]
                else 0.0,
            }
        )
    summary_df = (
        pd.DataFrame(summary_rows)
        .sort_values("paper_count", ascending=False)
        .reset_index(drop=True)
    )
    summary_path = OUTPUT_DIR / "neo4j_field_summary.parquet"
    summary_df.to_parquet(summary_path, index=False)
    logger.info("Summary saved to %s", summary_path)

    # Also export retraction data per field
    with GraphDatabase.driver(BOLT_URI, auth=AUTH).session() as session:
        retraction_result = session.run(
            "MATCH (p:Paper) WHERE p.is_retracted = true "
            "RETURN p.primary_field_id AS field_id, p.year AS year, count(*) AS retracted_count "
            "ORDER BY field_id, year"
        )
        retraction_rows = [dict(r) for r in retraction_result]

    if retraction_rows:
        ret_df = pd.DataFrame(retraction_rows)
        # Join field names
        field_map = {f["field_id"]: f["field_name"] for f in fields}
        ret_df["field_name"] = ret_df["field_id"].map(field_map)
        ret_path = OUTPUT_DIR / "neo4j_retraction_by_field_year.parquet"
        ret_df.to_parquet(ret_path, index=False)
        logger.info("Retraction data saved to %s (%d rows)", ret_path, len(ret_df))

    # Print summary table
    print("\n" + "=" * 80)
    print("FIELD SUMMARY (26 fields)")
    print("=" * 80)
    for _, row in summary_df.iterrows():
        print(
            f"  {row['field_name']:55s} "
            f"{row['paper_count']:>12,} papers  "
            f"AI(title): {row['ai_title_fraction'] * 100:5.2f}%  "
            f"AI(concept): {row['ai_concept_fraction'] * 100:5.2f}%"
        )

    print(f"\nTotal papers: {summary_df['paper_count'].sum():,}")
    print(f"Total AI (title): {summary_df['ai_title_count'].sum():,}")
    print(f"Total AI (concept): {summary_df['ai_concept_count'].sum():,}")


if __name__ == "__main__":
    main()
