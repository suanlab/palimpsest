"""Pre-compute concept-based AI paper counts per field per year.

Uses the paper_concepts_ft fulltext index on concepts_json to identify
AI papers by OpenAlex concept IDs (broader than title-keyword matching).

Key AI concept IDs:
  C154945302 = Artificial intelligence
  C119857082 = Machine learning
  C108583219 = Deep learning
  C50644808  = Computer vision
  C204321447 = Natural language processing
  C31258907  = Pattern recognition

Stores on Field nodes:
  - yearly_ai_concept_counts: {"2020": 5000, "2021": 5500, ...}
  - ai_concept_count: total count (all years)
Also updates GlobalStats with total ai_concept_papers count.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from collections import defaultdict

from neo4j import Driver, GraphDatabase

from palimpsest.utils.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

YEAR_MIN = 1950
YEAR_MAX = 2025
BATCH_SIZE = 500_000

AI_CONCEPT_IDS = [
    "C154945302",
    "C119857082",
    "C108583219",
    "C50644808",
    "C204321447",
    "C31258907",
]


def main() -> None:
    """Run concept-based AI paper pre-computation."""
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )

    try:
        driver.verify_connectivity()
        logger.info("Connected to Neo4j at %s", settings.neo4j_uri)
    except Exception:
        logger.exception("Cannot connect to Neo4j")
        sys.exit(1)

    t0 = time.perf_counter()

    logger.info("Streaming concept-based AI papers via fulltext index...")
    field_yearly, total_count = _stream_concept_ai_counts(driver)
    logger.info(
        "Found %d AI concept papers across %d fields",
        total_count,
        len(field_yearly),
    )

    logger.info("Storing on Neo4j nodes...")
    _store_counts(driver, field_yearly, total_count)

    elapsed = time.perf_counter() - t0
    logger.info("Done in %.1f seconds (%.1f minutes)", elapsed, elapsed / 60)
    driver.close()


def _stream_concept_ai_counts(
    driver: Driver,
) -> tuple[dict[str, dict[str, int]], int]:
    """Stream AI concept papers and aggregate by field+year in Python.

    Returns:
        (field_yearly: {field_id -> {year: count}}, total_count).
    """
    lucene_query = " OR ".join(AI_CONCEPT_IDS)
    field_yearly: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    total_count = 0
    offset = 0

    while True:
        with driver.session(database="neo4j") as session:
            records = list(
                session.run(
                    "CALL db.index.fulltext.queryNodes("
                    "'paper_concepts_ft', $query"
                    ") YIELD node AS p "
                    "WHERE p.year >= $year_min AND p.year <= $year_max "
                    "RETURN p.year AS year, p.primary_field_id AS fid "
                    "SKIP $offset LIMIT $batch_size",
                    {
                        "query": lucene_query,
                        "year_min": YEAR_MIN,
                        "year_max": YEAR_MAX,
                        "offset": offset,
                        "batch_size": BATCH_SIZE,
                    },
                )
            )

        batch_count = len(records)
        if batch_count == 0:
            break

        for record in records:
            fid = record["fid"]
            year = record["year"]
            total_count += 1
            if fid is not None and year is not None:
                field_yearly[fid][str(year)] += 1

        logger.info(
            "Batch: offset=%d, got=%d, running_total=%d",
            offset,
            batch_count,
            total_count,
        )
        offset += BATCH_SIZE
        if batch_count < BATCH_SIZE:
            break

    return dict(field_yearly), total_count


def _store_counts(
    driver: Driver,
    field_yearly: dict[str, dict[str, int]],
    total_count: int,
) -> None:
    """Store concept-based AI counts on Field and GlobalStats nodes."""
    with driver.session(database="neo4j") as session:
        for fid in sorted(field_yearly.keys()):
            yearly = field_yearly[fid]
            field_total = sum(yearly.values())
            session.run(
                "MATCH (f:Field {field_id: $field_id}) "
                "SET f.yearly_ai_concept_counts = $yearly_json, "
                "f.ai_concept_count = $total",
                {
                    "field_id": fid,
                    "yearly_json": json.dumps(dict(yearly)),
                    "total": field_total,
                },
            )
            logger.info("Stored %s: %d concept-AI papers", fid, field_total)

        session.run(
            "MERGE (g:GlobalStats {id: 'singleton'}) SET g.ai_concept_papers = $total",
            {"total": total_count},
        )
        logger.info("Stored global AI concept count: %d", total_count)


if __name__ == "__main__":
    main()
