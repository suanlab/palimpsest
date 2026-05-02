#!/usr/bin/env python3
"""Import graph parquet outputs into Neo4j using batched UNWIND queries.

This script streams ETL-produced parquet files and upserts graph entities into
Neo4j with idempotent MERGE patterns.
"""

# pyright: basic, reportMissingImports=false

from __future__ import annotations

import argparse
import logging
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq
from neo4j import Driver, GraphDatabase
from neo4j.exceptions import Neo4jError

from palimpsest.utils.config import settings
from palimpsest.utils.logging import setup_logging

LOGGER = logging.getLogger(__name__)

DEFAULT_GRAPH_DIR = Path("data/processed/graph")
DEFAULT_NEO4J_URI = "bolt://localhost:7687"
DEFAULT_NEO4J_USER = "neo4j"
DEFAULT_NEO4J_PASSWORD = "research2026"

PAPERS_FILE = "papers.parquet"
CITATIONS_FILE = "citations.parquet"
AUTHORSHIPS_FILE = "authorships.parquet"
COAUTHORSHIPS_FILE = "coauthorship_edges.parquet"


@dataclass
class ImportStats:
    """Track import progress and final summary metrics.

    Attributes:
        rows_read: Number of parquet rows read for each stage.
        rows_sent: Number of rows submitted to Neo4j for each stage.
        nodes_created: Number of nodes created in each stage.
        relationships_created: Number of relationships created in each stage.
        properties_set: Number of properties set in each stage.
        elapsed_seconds: Runtime per stage in seconds.
    """

    rows_read: dict[str, int] = field(default_factory=dict)
    rows_sent: dict[str, int] = field(default_factory=dict)
    nodes_created: dict[str, int] = field(default_factory=dict)
    relationships_created: dict[str, int] = field(default_factory=dict)
    properties_set: dict[str, int] = field(default_factory=dict)
    elapsed_seconds: dict[str, float] = field(default_factory=dict)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed CLI namespace.
    """

    parser = argparse.ArgumentParser(
        description="Import ETL parquet graph tables into Neo4j.",
    )
    parser.add_argument(
        "--graph-dir",
        type=Path,
        default=DEFAULT_GRAPH_DIR,
        help="Directory containing graph parquet files.",
    )
    parser.add_argument(
        "--uri",
        default=DEFAULT_NEO4J_URI,
        help="Neo4j Bolt URI.",
    )
    parser.add_argument(
        "--user",
        default=DEFAULT_NEO4J_USER,
        help="Neo4j username.",
    )
    parser.add_argument(
        "--password",
        default=DEFAULT_NEO4J_PASSWORD,
        help="Neo4j password.",
    )
    parser.add_argument(
        "--database",
        default="neo4j",
        help="Neo4j database name.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5_000,
        help="Base batch size (nodes=base, relationships=base*2).",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Use create-only property setting to skip updates on existing data.",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete all existing graph data before import.",
    )
    parser.add_argument(
        "--log-interval",
        type=int,
        default=100_000,
        help="Progress log interval in submitted rows.",
    )
    parser.add_argument(
        "--log-level",
        default=settings.log_level,
        help="Logging level (DEBUG, INFO, WARNING, ERROR).",
    )
    return parser.parse_args()


def _require_input_files(graph_dir: Path) -> dict[str, Path]:
    """Validate required parquet files are present.

    Args:
        graph_dir: Directory containing ETL parquet outputs.

    Returns:
        Mapping of logical table name to file path.

    Raises:
        FileNotFoundError: If one or more required files are missing.
    """

    files = {
        "papers": graph_dir / PAPERS_FILE,
        "citations": graph_dir / CITATIONS_FILE,
        "authorships": graph_dir / AUTHORSHIPS_FILE,
        "coauthorship_edges": graph_dir / COAUTHORSHIPS_FILE,
    }
    missing = [name for name, path in files.items() if not path.exists()]
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise FileNotFoundError(
            f"Missing required parquet files in {graph_dir}: {missing_text}",
        )
    return files


def _rows_from_parquet(
    path: Path,
    batch_size: int,
) -> Iterator[tuple[int, list[dict[str, Any]]]]:
    """Yield parquet rows in bounded-size Python lists.

    Args:
        path: Input parquet file.
        batch_size: Number of rows per yielded chunk.

    Yields:
        Tuples of (rows_read, row dictionaries).
    """

    parquet = pq.ParquetFile(path)
    for record_batch in parquet.iter_batches(batch_size=batch_size):
        rows = record_batch.to_pylist()
        yield len(rows), rows


def _to_clean_str(value: Any) -> str | None:
    """Normalize a nullable string value for Cypher parameters.

    Args:
        value: Raw value from parquet row.

    Returns:
        Clean string or None.
    """

    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else None
    return str(value)


def _to_clean_int(value: Any) -> int | None:
    """Normalize an integer-like value.

    Args:
        value: Raw value from parquet row.

    Returns:
        Integer or None.
    """

    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return int(text)
        except ValueError:
            return None
    return None


def _to_clean_bool(value: Any) -> bool | None:
    """Normalize a boolean-like value.

    Args:
        value: Raw value from parquet row.

    Returns:
        Boolean or None.
    """

    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"true", "1", "yes", "y"}:
            return True
        if text in {"false", "0", "no", "n"}:
            return False
    return None


def _create_constraints_and_indexes(driver: Driver, database: str) -> None:
    """Create required uniqueness constraints and indexes.

    Args:
        driver: Neo4j driver.
        database: Target database.
    """

    statements = [
        (
            "paper_openalex_id_unique",
            "CREATE CONSTRAINT paper_openalex_id_unique IF NOT EXISTS "
            "FOR (p:Paper) REQUIRE p.openalex_id IS UNIQUE",
        ),
        (
            "author_author_id_unique",
            "CREATE CONSTRAINT author_author_id_unique IF NOT EXISTS "
            "FOR (a:Author) REQUIRE a.author_id IS UNIQUE",
        ),
        (
            "field_field_id_unique",
            "CREATE CONSTRAINT field_field_id_unique IF NOT EXISTS "
            "FOR (f:Field) REQUIRE f.field_id IS UNIQUE",
        ),
        (
            "paper_doi_idx",
            "CREATE INDEX paper_doi_idx IF NOT EXISTS FOR (p:Paper) ON (p.doi)",
        ),
        (
            "paper_year_idx",
            "CREATE INDEX paper_year_idx IF NOT EXISTS FOR (p:Paper) ON (p.year)",
        ),
        (
            "paper_is_retracted_idx",
            "CREATE INDEX paper_is_retracted_idx IF NOT EXISTS "
            "FOR (p:Paper) ON (p.is_retracted)",
        ),
        (
            "author_author_name_idx",
            "CREATE INDEX author_author_name_idx IF NOT EXISTS "
            "FOR (a:Author) ON (a.author_name)",
        ),
    ]

    with driver.session(database=database) as session:
        for name, statement in statements:
            session.run(statement).consume()
            LOGGER.info("Schema ensured", extra={"schema_name": name})


def _clear_database(driver: Driver, database: str, batch_size: int) -> int:
    """Delete all nodes and relationships in batches.

    Args:
        driver: Neo4j driver.
        database: Target database.
        batch_size: Deletion batch size.

    Returns:
        Total nodes deleted.
    """

    total_deleted = 0
    query = (
        "CALL { "
        "MATCH (n) "
        "WITH n LIMIT $batch_size "
        "DETACH DELETE n "
        "RETURN count(*) AS deleted "
        "} "
        "RETURN deleted"
    )

    with driver.session(database=database) as session:
        while True:
            result = session.run(query, batch_size=batch_size)
            record = result.single()
            deleted = int(record["deleted"]) if record else 0
            total_deleted += deleted
            if deleted == 0:
                break

    return total_deleted


def _run_batch(
    driver: Driver,
    database: str,
    query: str,
    rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Execute one batched UNWIND query and return counter metrics.

    Args:
        driver: Neo4j driver.
        database: Target database.
        query: Cypher statement.
        rows: Parameter rows.

    Returns:
        Counter dictionary.
    """

    with driver.session(database=database) as session:
        summary = session.run(query, rows=rows).consume()

    counters = summary.counters
    return {
        "nodes_created": counters.nodes_created,
        "relationships_created": counters.relationships_created,
        "properties_set": counters.properties_set,
    }


def _import_papers(
    driver: Driver,
    database: str,
    papers_path: Path,
    batch_size: int,
    log_interval: int,
    skip_existing: bool,
    stats: ImportStats,
) -> None:
    """Import Paper nodes from papers parquet.

    Args:
        driver: Neo4j driver.
        database: Target database.
        papers_path: Source parquet path.
        batch_size: Batch size for parquet and Cypher.
        log_interval: Progress log interval.
        skip_existing: If True, only set properties on new nodes.
        stats: Mutable stats object.
    """

    stage = "papers"
    started = time.monotonic()

    if skip_existing:
        query = (
            "UNWIND $rows AS row "
            "MERGE (p:Paper {openalex_id: row.openalex_id}) "
            "ON CREATE SET "
            "p.doi = row.doi, "
            "p.title = row.title, "
            "p.year = row.year, "
            "p.cited_by_count = row.cited_by_count, "
            "p.is_retracted = row.is_retracted, "
            "p.primary_field_id = row.primary_field_id, "
            "p.primary_field_name = row.primary_field_name, "
            "p.concepts_json = row.concepts_json"
        )
    else:
        query = (
            "UNWIND $rows AS row "
            "MERGE (p:Paper {openalex_id: row.openalex_id}) "
            "SET "
            "p.doi = CASE WHEN row.doi IS NULL THEN p.doi ELSE row.doi END, "
            "p.title = CASE WHEN row.title IS NULL THEN p.title ELSE row.title END, "
            "p.year = CASE WHEN row.year IS NULL THEN p.year ELSE row.year END, "
            "p.cited_by_count = CASE "
            "WHEN row.cited_by_count IS NULL THEN p.cited_by_count "
            "ELSE row.cited_by_count END, "
            "p.is_retracted = CASE "
            "WHEN row.is_retracted IS NULL THEN p.is_retracted "
            "ELSE row.is_retracted END, "
            "p.primary_field_id = CASE "
            "WHEN row.primary_field_id IS NULL THEN p.primary_field_id "
            "ELSE row.primary_field_id END, "
            "p.primary_field_name = CASE "
            "WHEN row.primary_field_name IS NULL THEN p.primary_field_name "
            "ELSE row.primary_field_name END, "
            "p.concepts_json = CASE "
            "WHEN row.concepts_json IS NULL THEN p.concepts_json "
            "ELSE row.concepts_json END"
        )

    rows_read = 0
    rows_sent = 0
    nodes_created = 0
    relationships_created = 0
    properties_set = 0

    for batch_count, rows in _rows_from_parquet(papers_path, batch_size=batch_size):
        prepared_rows: list[dict[str, Any]] = []
        for row in rows:
            openalex_id = _to_clean_str(row.get("openalex_id"))
            if not openalex_id:
                continue
            prepared_rows.append(
                {
                    "openalex_id": openalex_id,
                    "doi": _to_clean_str(row.get("doi")),
                    "title": _to_clean_str(row.get("title")),
                    "year": _to_clean_int(row.get("year")),
                    "cited_by_count": _to_clean_int(row.get("cited_by_count")),
                    "is_retracted": _to_clean_bool(row.get("is_retracted")),
                    "primary_field_id": _to_clean_str(row.get("primary_field_id")),
                    "primary_field_name": _to_clean_str(row.get("primary_field_name")),
                    "concepts_json": _to_clean_str(row.get("concepts_json")),
                },
            )

        rows_read += batch_count
        if not prepared_rows:
            continue

        counters = _run_batch(driver, database, query, prepared_rows)
        rows_sent += len(prepared_rows)
        nodes_created += counters["nodes_created"]
        relationships_created += counters["relationships_created"]
        properties_set += counters["properties_set"]

        if rows_sent % log_interval == 0:
            LOGGER.info(
                "Import progress",
                extra={
                    "stage": stage,
                    "rows_sent": rows_sent,
                    "rows_read": rows_read,
                    "nodes_created": nodes_created,
                },
            )

    stats.rows_read[stage] = rows_read
    stats.rows_sent[stage] = rows_sent
    stats.nodes_created[stage] = nodes_created
    stats.relationships_created[stage] = relationships_created
    stats.properties_set[stage] = properties_set
    stats.elapsed_seconds[stage] = round(time.monotonic() - started, 2)


def _import_authors_and_authored(
    driver: Driver,
    database: str,
    authorships_path: Path,
    batch_size: int,
    log_interval: int,
    skip_existing: bool,
    stats: ImportStats,
) -> None:
    """Import Author nodes and AUTHORED relationships.

    Args:
        driver: Neo4j driver.
        database: Target database.
        authorships_path: Source parquet path.
        batch_size: Batch size for parquet and Cypher.
        log_interval: Progress log interval.
        skip_existing: If True, only set properties on new nodes/relationships.
        stats: Mutable stats object.
    """

    stage = "authorships"
    started = time.monotonic()

    if skip_existing:
        query = (
            "UNWIND $rows AS row "
            "MATCH (p:Paper {openalex_id: row.openalex_id}) "
            "MERGE (a:Author {author_id: row.author_id}) "
            "ON CREATE SET "
            "a.author_name = row.author_name, "
            "a.institution = row.institution_name, "
            "a.country = row.country "
            "MERGE (a)-[r:AUTHORED]->(p) "
            "ON CREATE SET "
            "r.position = row.position, "
            "r.is_corresponding = row.is_corresponding"
        )
    else:
        query = (
            "UNWIND $rows AS row "
            "MATCH (p:Paper {openalex_id: row.openalex_id}) "
            "MERGE (a:Author {author_id: row.author_id}) "
            "SET "
            "a.author_name = CASE "
            "WHEN row.author_name IS NULL THEN a.author_name "
            "ELSE row.author_name END, "
            "a.institution = CASE "
            "WHEN row.institution_name IS NULL THEN a.institution "
            "ELSE row.institution_name END, "
            "a.country = CASE WHEN row.country IS NULL THEN a.country ELSE row.country END "
            "MERGE (a)-[r:AUTHORED]->(p) "
            "SET "
            "r.position = CASE WHEN row.position IS NULL THEN r.position ELSE row.position END, "
            "r.is_corresponding = CASE "
            "WHEN row.is_corresponding IS NULL THEN r.is_corresponding "
            "ELSE row.is_corresponding END"
        )

    rows_read = 0
    rows_sent = 0
    nodes_created = 0
    relationships_created = 0
    properties_set = 0

    for batch_count, rows in _rows_from_parquet(
        authorships_path, batch_size=batch_size
    ):
        prepared_rows: list[dict[str, Any]] = []
        for row in rows:
            openalex_id = _to_clean_str(row.get("openalex_id"))
            author_id = _to_clean_str(row.get("author_id"))
            if not openalex_id or not author_id:
                continue

            prepared_rows.append(
                {
                    "openalex_id": openalex_id,
                    "author_id": author_id,
                    "author_name": _to_clean_str(row.get("author_name")),
                    "position": _to_clean_int(row.get("position")),
                    "is_corresponding": _to_clean_bool(row.get("is_corresponding")),
                    "institution_name": _to_clean_str(row.get("institution_name")),
                    "country": _to_clean_str(row.get("country")),
                },
            )

        rows_read += batch_count
        if not prepared_rows:
            continue

        counters = _run_batch(driver, database, query, prepared_rows)
        rows_sent += len(prepared_rows)
        nodes_created += counters["nodes_created"]
        relationships_created += counters["relationships_created"]
        properties_set += counters["properties_set"]

        if rows_sent % log_interval == 0:
            LOGGER.info(
                "Import progress",
                extra={
                    "stage": stage,
                    "rows_sent": rows_sent,
                    "rows_read": rows_read,
                    "nodes_created": nodes_created,
                    "relationships_created": relationships_created,
                },
            )

    stats.rows_read[stage] = rows_read
    stats.rows_sent[stage] = rows_sent
    stats.nodes_created[stage] = nodes_created
    stats.relationships_created[stage] = relationships_created
    stats.properties_set[stage] = properties_set
    stats.elapsed_seconds[stage] = round(time.monotonic() - started, 2)


def _import_fields_and_belongs_to(
    driver: Driver,
    database: str,
    papers_path: Path,
    batch_size: int,
    log_interval: int,
    skip_existing: bool,
    stats: ImportStats,
) -> None:
    """Import Field nodes and BELONGS_TO relationships.

    Args:
        driver: Neo4j driver.
        database: Target database.
        papers_path: Source papers parquet path.
        batch_size: Batch size for parquet and Cypher.
        log_interval: Progress log interval.
        skip_existing: If True, only set properties on newly created fields.
        stats: Mutable stats object.
    """

    stage = "fields"
    started = time.monotonic()

    if skip_existing:
        query = (
            "UNWIND $rows AS row "
            "MATCH (p:Paper {openalex_id: row.openalex_id}) "
            "MERGE (f:Field {field_id: row.primary_field_id}) "
            "ON CREATE SET f.field_name = row.primary_field_name "
            "MERGE (p)-[:BELONGS_TO]->(f)"
        )
    else:
        query = (
            "UNWIND $rows AS row "
            "MATCH (p:Paper {openalex_id: row.openalex_id}) "
            "MERGE (f:Field {field_id: row.primary_field_id}) "
            "SET f.field_name = CASE "
            "WHEN row.primary_field_name IS NULL THEN f.field_name "
            "ELSE row.primary_field_name END "
            "MERGE (p)-[:BELONGS_TO]->(f)"
        )

    rows_read = 0
    rows_sent = 0
    nodes_created = 0
    relationships_created = 0
    properties_set = 0

    for batch_count, rows in _rows_from_parquet(papers_path, batch_size=batch_size):
        prepared_rows: list[dict[str, Any]] = []
        for row in rows:
            openalex_id = _to_clean_str(row.get("openalex_id"))
            field_id = _to_clean_str(row.get("primary_field_id"))
            if not openalex_id or not field_id:
                continue

            prepared_rows.append(
                {
                    "openalex_id": openalex_id,
                    "primary_field_id": field_id,
                    "primary_field_name": _to_clean_str(row.get("primary_field_name")),
                },
            )

        rows_read += batch_count
        if not prepared_rows:
            continue

        counters = _run_batch(driver, database, query, prepared_rows)
        rows_sent += len(prepared_rows)
        nodes_created += counters["nodes_created"]
        relationships_created += counters["relationships_created"]
        properties_set += counters["properties_set"]

        if rows_sent % log_interval == 0:
            LOGGER.info(
                "Import progress",
                extra={
                    "stage": stage,
                    "rows_sent": rows_sent,
                    "rows_read": rows_read,
                    "nodes_created": nodes_created,
                    "relationships_created": relationships_created,
                },
            )

    stats.rows_read[stage] = rows_read
    stats.rows_sent[stage] = rows_sent
    stats.nodes_created[stage] = nodes_created
    stats.relationships_created[stage] = relationships_created
    stats.properties_set[stage] = properties_set
    stats.elapsed_seconds[stage] = round(time.monotonic() - started, 2)


def _import_citations(
    driver: Driver,
    database: str,
    citations_path: Path,
    batch_size: int,
    log_interval: int,
    stats: ImportStats,
) -> None:
    """Import CITES relationships.

    Args:
        driver: Neo4j driver.
        database: Target database.
        citations_path: Source parquet path.
        batch_size: Batch size for parquet and Cypher.
        log_interval: Progress log interval.
        stats: Mutable stats object.
    """

    stage = "citations"
    started = time.monotonic()

    query = (
        "UNWIND $rows AS row "
        "MATCH (citing:Paper {openalex_id: row.citing_id}) "
        "MATCH (cited:Paper {openalex_id: row.cited_id}) "
        "MERGE (citing)-[:CITES]->(cited)"
    )

    rows_read = 0
    rows_sent = 0
    nodes_created = 0
    relationships_created = 0
    properties_set = 0

    for batch_count, rows in _rows_from_parquet(citations_path, batch_size=batch_size):
        prepared_rows: list[dict[str, Any]] = []
        for row in rows:
            citing_id = _to_clean_str(row.get("citing_id"))
            cited_id = _to_clean_str(row.get("cited_id"))
            if not citing_id or not cited_id:
                continue
            prepared_rows.append({"citing_id": citing_id, "cited_id": cited_id})

        rows_read += batch_count
        if not prepared_rows:
            continue

        counters = _run_batch(driver, database, query, prepared_rows)
        rows_sent += len(prepared_rows)
        nodes_created += counters["nodes_created"]
        relationships_created += counters["relationships_created"]
        properties_set += counters["properties_set"]

        if rows_sent % log_interval == 0:
            LOGGER.info(
                "Import progress",
                extra={
                    "stage": stage,
                    "rows_sent": rows_sent,
                    "rows_read": rows_read,
                    "relationships_created": relationships_created,
                },
            )

    stats.rows_read[stage] = rows_read
    stats.rows_sent[stage] = rows_sent
    stats.nodes_created[stage] = nodes_created
    stats.relationships_created[stage] = relationships_created
    stats.properties_set[stage] = properties_set
    stats.elapsed_seconds[stage] = round(time.monotonic() - started, 2)


def _import_coauthored(
    driver: Driver,
    database: str,
    coauthorship_path: Path,
    batch_size: int,
    log_interval: int,
    skip_existing: bool,
    stats: ImportStats,
) -> None:
    """Import CO_AUTHORED relationships.

    CO_AUTHORED edges are created with `paper_id` as part of relationship identity
    for idempotent resume behavior.

    Args:
        driver: Neo4j driver.
        database: Target database.
        coauthorship_path: Source parquet path.
        batch_size: Batch size for parquet and Cypher.
        log_interval: Progress log interval.
        skip_existing: If True, only set properties on newly created relations.
        stats: Mutable stats object.
    """

    stage = "coauthorship_edges"
    started = time.monotonic()

    if skip_existing:
        query = (
            "UNWIND $rows AS row "
            "MATCH (a:Author {author_id: row.author_a}) "
            "MATCH (b:Author {author_id: row.author_b}) "
            "MERGE (a)-[r:CO_AUTHORED {paper_id: row.paper_id}]->(b) "
            "ON CREATE SET "
            "r.year = row.year, "
            "r.paper_count = 1, "
            "r.first_year = row.year, "
            "r.last_year = row.year"
        )
    else:
        query = (
            "UNWIND $rows AS row "
            "MATCH (a:Author {author_id: row.author_a}) "
            "MATCH (b:Author {author_id: row.author_b}) "
            "MERGE (a)-[r:CO_AUTHORED {paper_id: row.paper_id}]->(b) "
            "SET "
            "r.year = CASE WHEN row.year IS NULL THEN r.year ELSE row.year END, "
            "r.paper_count = coalesce(r.paper_count, 1), "
            "r.first_year = CASE "
            "WHEN row.year IS NULL THEN r.first_year "
            "ELSE coalesce(r.first_year, row.year) END, "
            "r.last_year = CASE "
            "WHEN row.year IS NULL THEN r.last_year "
            "ELSE coalesce(r.last_year, row.year) END"
        )

    rows_read = 0
    rows_sent = 0
    nodes_created = 0
    relationships_created = 0
    properties_set = 0

    for batch_count, rows in _rows_from_parquet(
        coauthorship_path, batch_size=batch_size
    ):
        prepared_rows: list[dict[str, Any]] = []
        for row in rows:
            author_a = _to_clean_str(row.get("author_a"))
            author_b = _to_clean_str(row.get("author_b"))
            paper_id = _to_clean_str(row.get("paper_id"))
            if not author_a or not author_b or not paper_id:
                continue
            prepared_rows.append(
                {
                    "author_a": author_a,
                    "author_b": author_b,
                    "paper_id": paper_id,
                    "year": _to_clean_int(row.get("year")),
                },
            )

        rows_read += batch_count
        if not prepared_rows:
            continue

        counters = _run_batch(driver, database, query, prepared_rows)
        rows_sent += len(prepared_rows)
        nodes_created += counters["nodes_created"]
        relationships_created += counters["relationships_created"]
        properties_set += counters["properties_set"]

        if rows_sent % log_interval == 0:
            LOGGER.info(
                "Import progress",
                extra={
                    "stage": stage,
                    "rows_sent": rows_sent,
                    "rows_read": rows_read,
                    "relationships_created": relationships_created,
                },
            )

    stats.rows_read[stage] = rows_read
    stats.rows_sent[stage] = rows_sent
    stats.nodes_created[stage] = nodes_created
    stats.relationships_created[stage] = relationships_created
    stats.properties_set[stage] = properties_set
    stats.elapsed_seconds[stage] = round(time.monotonic() - started, 2)


def _log_stage_summary(stats: ImportStats, stage: str) -> None:
    """Log summary metrics for one stage.

    Args:
        stats: Import stats holder.
        stage: Stage key.
    """

    LOGGER.info(
        "Stage complete",
        extra={
            "stage": stage,
            "rows_read": stats.rows_read.get(stage, 0),
            "rows_sent": stats.rows_sent.get(stage, 0),
            "nodes_created": stats.nodes_created.get(stage, 0),
            "relationships_created": stats.relationships_created.get(stage, 0),
            "properties_set": stats.properties_set.get(stage, 0),
            "elapsed_seconds": stats.elapsed_seconds.get(stage, 0.0),
        },
    )


def _log_final_summary(stats: ImportStats, total_elapsed_seconds: float) -> None:
    """Log final import totals across all stages.

    Args:
        stats: Import stats holder.
        total_elapsed_seconds: Full runtime.
    """

    LOGGER.info(
        "Import finished",
        extra={
            "total_rows_read": sum(stats.rows_read.values()),
            "total_rows_sent": sum(stats.rows_sent.values()),
            "total_nodes_created": sum(stats.nodes_created.values()),
            "total_relationships_created": sum(stats.relationships_created.values()),
            "total_properties_set": sum(stats.properties_set.values()),
            "elapsed_seconds": round(total_elapsed_seconds, 2),
        },
    )


def run_import(args: argparse.Namespace) -> None:
    """Execute Neo4j import workflow.

    Args:
        args: Parsed CLI arguments.

    Raises:
        FileNotFoundError: If required parquet files are missing.
        Neo4jError: If Neo4j returns an error.
    """

    input_files = _require_input_files(args.graph_dir)
    node_batch_size = args.batch_size
    relationship_batch_size = args.batch_size * 2

    LOGGER.info(
        "Import configuration",
        extra={
            "graph_dir": str(args.graph_dir),
            "database": args.database,
            "node_batch_size": node_batch_size,
            "relationship_batch_size": relationship_batch_size,
            "skip_existing": args.skip_existing,
            "clear": args.clear,
        },
    )

    stats = ImportStats()
    started_total = time.monotonic()

    with GraphDatabase.driver(args.uri, auth=(args.user, args.password)) as driver:
        driver.verify_connectivity()

        if args.clear:
            deleted = _clear_database(driver, args.database, batch_size=50_000)
            LOGGER.info("Database cleared", extra={"nodes_deleted": deleted})

        _create_constraints_and_indexes(driver, args.database)

        _import_papers(
            driver=driver,
            database=args.database,
            papers_path=input_files["papers"],
            batch_size=node_batch_size,
            log_interval=args.log_interval,
            skip_existing=args.skip_existing,
            stats=stats,
        )
        _log_stage_summary(stats, "papers")

        _import_authors_and_authored(
            driver=driver,
            database=args.database,
            authorships_path=input_files["authorships"],
            batch_size=relationship_batch_size,
            log_interval=args.log_interval,
            skip_existing=args.skip_existing,
            stats=stats,
        )
        _log_stage_summary(stats, "authorships")

        _import_fields_and_belongs_to(
            driver=driver,
            database=args.database,
            papers_path=input_files["papers"],
            batch_size=node_batch_size,
            log_interval=args.log_interval,
            skip_existing=args.skip_existing,
            stats=stats,
        )
        _log_stage_summary(stats, "fields")

        _import_citations(
            driver=driver,
            database=args.database,
            citations_path=input_files["citations"],
            batch_size=relationship_batch_size,
            log_interval=args.log_interval,
            stats=stats,
        )
        _log_stage_summary(stats, "citations")

        _import_coauthored(
            driver=driver,
            database=args.database,
            coauthorship_path=input_files["coauthorship_edges"],
            batch_size=relationship_batch_size,
            log_interval=args.log_interval,
            skip_existing=args.skip_existing,
            stats=stats,
        )
        _log_stage_summary(stats, "coauthorship_edges")

    _log_final_summary(stats, total_elapsed_seconds=time.monotonic() - started_total)


def main() -> None:
    """Run CLI entrypoint."""

    args = parse_args()
    setup_logging(args.log_level)
    try:
        run_import(args)
    except (FileNotFoundError, Neo4jError, OSError, ValueError) as exc:
        LOGGER.error("Import failed", extra={"error": str(exc)})
        raise


if __name__ == "__main__":
    main()
