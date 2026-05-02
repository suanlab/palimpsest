"""Pre-compute per-field per-year paper counts and store on Neo4j Field nodes.

Stores two JSON properties on each Field node:
  - yearly_paper_counts: {"2020": 12345, "2021": 13000, ...}
  - yearly_ai_paper_counts: {"2020": 500, "2021": 600, ...}

Also creates/updates a singleton :GlobalStats node with:
  - yearly_publications: {"2020": 5000000, "2021": 5200000, ...}

Strategy: stream papers year-by-year using the year index,
reading primary_field_id as a property (avoiding BELONGS_TO traversal),
and aggregate in Python. ~3-5s per year, 76 years total.
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

AI_TERMS = [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "neural network",
    "natural language processing",
    "computer vision",
    "reinforcement learning",
    "generative adversarial",
    "transformer model",
    "large language model",
    "convolutional neural",
    "recurrent neural",
]


def main() -> None:
    """Run all pre-computations."""
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

    logger.info("Phase 1: Streaming per-year per-field paper counts...")
    field_yearly, global_yearly = _stream_yearly_counts(driver)
    logger.info(
        "Got counts for %d fields across %d years",
        len(field_yearly),
        len(global_yearly),
    )

    logger.info("Phase 2: Computing per-field per-year AI paper counts...")
    field_yearly_ai = _stream_ai_yearly_counts(driver)
    logger.info("Got AI counts for %d fields", len(field_yearly_ai))

    logger.info("Phase 3: Storing on Neo4j nodes...")
    _store_field_yearly(driver, field_yearly, field_yearly_ai)
    _store_global_yearly(driver, global_yearly)

    elapsed = time.perf_counter() - t0
    logger.info("All done in %.1f seconds (%.1f minutes)", elapsed, elapsed / 60)
    driver.close()


def _stream_yearly_counts(
    driver: Driver,
) -> tuple[dict[str, dict[str, int]], dict[str, int]]:
    """Aggregate papers per field per year by querying one year at a time.

    Uses Neo4j's year index for efficient per-year scans, then GROUP BY
    primary_field_id in Cypher (26 groups per year is small enough).
    ~30s for small years, ~3min for large years (2020+).

    Returns:
        (field_yearly: {field_id -> {year: count}}, global_yearly: {year: count}).
    """
    field_yearly: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    global_yearly: dict[str, int] = {}

    for year in range(YEAR_MIN, YEAR_MAX + 1):
        t = time.perf_counter()
        year_total = 0

        with driver.session(database="neo4j") as session:
            records = list(
                session.run(
                    "MATCH (p:Paper) WHERE p.year = $year "
                    "RETURN p.primary_field_id AS fid, count(p) AS cnt",
                    {"year": year},
                )
            )

        for record in records:
            fid = record["fid"]
            cnt = record["cnt"]
            year_total += cnt
            if fid is not None:
                field_yearly[fid][str(year)] = cnt

        global_yearly[str(year)] = year_total
        elapsed_y = time.perf_counter() - t
        logger.info(
            "Year %d: %d papers, %d fields (%.1fs)",
            year,
            year_total,
            len([r for r in records if r["fid"] is not None]),
            elapsed_y,
        )

    return dict(field_yearly), global_yearly


def _stream_ai_yearly_counts(
    driver: Driver,
) -> dict[str, dict[str, int]]:
    """Stream AI papers via fulltext index, aggregating field+year in Python.

    Returns:
        Dict mapping field_id -> {year_str: count}.
    """
    lucene_query = " OR ".join(f'"{term}"' for term in AI_TERMS)
    result: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    offset = 0
    total_processed = 0

    while True:
        with driver.session(database="neo4j") as session:
            records = list(
                session.run(
                    "CALL db.index.fulltext.queryNodes('paper_title_ft', $query) "
                    "YIELD node AS p "
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
            if fid is not None and year is not None:
                result[fid][str(year)] += 1

        total_processed += batch_count
        logger.info(
            "AI papers: offset=%d, batch=%d, total=%d",
            offset,
            batch_count,
            total_processed,
        )
        offset += BATCH_SIZE
        if batch_count < BATCH_SIZE:
            break

    return dict(result)


def _store_field_yearly(
    driver: Driver,
    field_yearly: dict[str, dict[str, int]],
    field_yearly_ai: dict[str, dict[str, int]],
) -> None:
    """Store yearly counts as JSON properties on Field nodes."""
    all_field_ids = set(field_yearly.keys()) | set(field_yearly_ai.keys())

    with driver.session(database="neo4j") as session:
        for fid in sorted(all_field_ids):
            papers_json = json.dumps(dict(field_yearly.get(fid, {})))
            ai_json = json.dumps(dict(field_yearly_ai.get(fid, {})))
            session.run(
                "MATCH (f:Field {field_id: $field_id}) "
                "SET f.yearly_paper_counts = $yearly_paper_counts, "
                "f.yearly_ai_paper_counts = $yearly_ai_paper_counts",
                {
                    "field_id": fid,
                    "yearly_paper_counts": papers_json,
                    "yearly_ai_paper_counts": ai_json,
                },
            )
            total_p = sum(field_yearly.get(fid, {}).values())
            total_ai = sum(field_yearly_ai.get(fid, {}).values())
            logger.info("Stored %s: %d papers, %d AI", fid, total_p, total_ai)


def _store_global_yearly(
    driver: Driver,
    global_yearly: dict[str, int],
) -> None:
    """Store global yearly publications on a singleton GlobalStats node."""
    with driver.session(database="neo4j") as session:
        session.run(
            "MERGE (g:GlobalStats {id: 'singleton'}) "
            "SET g.yearly_publications = $yearly_publications",
            {"yearly_publications": json.dumps(global_yearly)},
        )
    total = sum(global_yearly.values())
    logger.info(
        "Stored global yearly (%d years, %d total papers)",
        len(global_yearly),
        total,
    )


if __name__ == "__main__":
    main()
