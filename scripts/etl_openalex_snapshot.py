#!/usr/bin/env python3
"""Stream ETL for OpenAlex snapshot works JSONL gzip files.

The script incrementally processes OpenAlex work snapshot files from
`updated_date=YYYY-MM-DD/part_*.gz` directories and writes graph-ready parquet
tables.

Features:
- Streaming JSON parsing (line by line, no full-file loads)
- Batch parquet writes (default: every 100,000 rows)
- Resumable directory-level processing
- Incremental merge into four output parquet files
"""

# pyright: basic

from __future__ import annotations

import argparse
import gzip
import itertools
import json
import logging
import shutil
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq

OPENALEX_PREFIX = "https://openalex.org/"
DOI_PREFIX = "https://doi.org/"

DEFAULT_INPUT_ROOT = Path("/home/suanlab/Projects/research/data/raw/openalex/works")
DEFAULT_OUTPUT_ROOT = Path("/home/suanlab/Projects/research/data/processed/graph")

STATE_FILE_NAME = "etl_openalex_snapshot_progress.json"
SUMMARY_FILE_NAME = "etl_openalex_snapshot_summary.json"


@dataclass(frozen=True)
class TableConfig:
    """Configuration for a parquet output table.

    Attributes:
        key: Stable internal key.
        file_name: Final parquet output file name.
        schema: PyArrow schema for deterministic writes.
    """

    key: str
    file_name: str
    schema: pa.Schema


TABLES: dict[str, TableConfig] = {
    "papers": TableConfig(
        key="papers",
        file_name="papers.parquet",
        schema=pa.schema(
            [
                pa.field("openalex_id", pa.string()),
                pa.field("doi", pa.string()),
                pa.field("title", pa.string()),
                pa.field("year", pa.int64()),
                pa.field("cited_by_count", pa.int64()),
                pa.field("is_retracted", pa.bool_()),
                pa.field("primary_field_id", pa.string()),
                pa.field("primary_field_name", pa.string()),
                pa.field("concepts_json", pa.string()),
            ],
        ),
    ),
    "citations": TableConfig(
        key="citations",
        file_name="citations.parquet",
        schema=pa.schema(
            [
                pa.field("citing_id", pa.string()),
                pa.field("cited_id", pa.string()),
            ],
        ),
    ),
    "authorships": TableConfig(
        key="authorships",
        file_name="authorships.parquet",
        schema=pa.schema(
            [
                pa.field("openalex_id", pa.string()),
                pa.field("author_id", pa.string()),
                pa.field("author_name", pa.string()),
                pa.field("position", pa.int64()),
                pa.field("is_corresponding", pa.bool_()),
                pa.field("institution_name", pa.string()),
                pa.field("country", pa.string()),
            ],
        ),
    ),
    "coauthorship_edges": TableConfig(
        key="coauthorship_edges",
        file_name="coauthorship_edges.parquet",
        schema=pa.schema(
            [
                pa.field("author_a", pa.string()),
                pa.field("author_b", pa.string()),
                pa.field("paper_id", pa.string()),
                pa.field("year", pa.int64()),
            ],
        ),
    ),
}


class DirectoryBatchWriter:
    """Write table rows to directory-local parquet files in batches."""

    def __init__(
        self,
        output_dir: Path,
        batch_size: int,
    ) -> None:
        self._output_dir = output_dir
        self._batch_size = batch_size
        self._output_dir.mkdir(parents=True, exist_ok=True)

        self._writers: dict[str, pq.ParquetWriter] = {}
        self._buffers: dict[str, list[dict[str, Any]]] = {}
        self.rows_written: dict[str, int] = {key: 0 for key in TABLES}

        for key, config in TABLES.items():
            table_path = self._output_dir / config.file_name
            self._writers[key] = pq.ParquetWriter(
                str(table_path),
                schema=config.schema,
                compression="snappy",
            )
            self._buffers[key] = []

    def add_row(self, table_key: str, row: dict[str, Any]) -> None:
        """Add one row to an in-memory table buffer.

        Args:
            table_key: Internal table key.
            row: Row dictionary matching the configured schema.
        """

        buffer = self._buffers[table_key]
        buffer.append(row)
        if len(buffer) >= self._batch_size:
            self.flush_table(table_key)

    def flush_table(self, table_key: str) -> None:
        """Flush one table buffer to parquet.

        Args:
            table_key: Internal table key.
        """

        rows = self._buffers[table_key]
        if not rows:
            return

        config = TABLES[table_key]
        table = pa.Table.from_pylist(rows, schema=config.schema)
        self._writers[table_key].write_table(table)
        self.rows_written[table_key] += len(rows)
        rows.clear()

    def flush_all(self) -> None:
        """Flush all table buffers."""

        for table_key in TABLES:
            self.flush_table(table_key)

    def close(self) -> None:
        """Flush and close all parquet writers."""

        self.flush_all()
        for writer in self._writers.values():
            writer.close()


def setup_logging(level: str = "INFO") -> None:
    """Configure process logging.

    Args:
        level: Logging level label.
    """

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
    )


def strip_prefix(value: Any, prefix: str) -> str | None:
    """Return a prefix-stripped string value when possible.

    Args:
        value: Raw source value.
        prefix: Prefix to strip if present.

    Returns:
        Stripped string, original string, or None for non-strings/empty strings.
    """

    if not isinstance(value, str) or not value:
        return None
    if value.startswith(prefix):
        return value[len(prefix) :]
    return value


def top_concepts_json(concepts_raw: Any) -> str:
    """Extract top-3 concepts by score and serialize as JSON.

    Args:
        concepts_raw: Raw `concepts` array from OpenAlex work record.

    Returns:
        JSON-encoded string for top 3 concepts.
    """

    if not isinstance(concepts_raw, list):
        return "[]"

    parsed: list[dict[str, Any]] = []
    for concept in concepts_raw:
        if not isinstance(concept, dict):
            continue
        score = concept.get("score")
        if not isinstance(score, int | float):
            continue
        parsed.append(
            {
                "id": strip_prefix(concept.get("id"), OPENALEX_PREFIX),
                "display_name": concept.get("display_name")
                if isinstance(concept.get("display_name"), str)
                else None,
                "score": float(score),
            },
        )

    parsed.sort(key=lambda item: item["score"], reverse=True)
    return json.dumps(parsed[:3], ensure_ascii=False)


def extract_rows_from_work(work: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Extract all graph-table rows from one OpenAlex work object.

    Args:
        work: OpenAlex work JSON object.

    Returns:
        Dictionary keyed by table names containing row lists.

    Raises:
        ValueError: If required top-level work fields are malformed.
    """

    openalex_id = strip_prefix(work.get("id"), OPENALEX_PREFIX)
    if not openalex_id:
        raise ValueError("missing work id")

    title_raw = work.get("title")
    display_name_raw = work.get("display_name")
    title = title_raw if isinstance(title_raw, str) else None
    if not title and isinstance(display_name_raw, str):
        title = display_name_raw

    publication_year = work.get("publication_year")
    year = publication_year if isinstance(publication_year, int) else None

    cited_by_count_raw = work.get("cited_by_count")
    cited_by_count = cited_by_count_raw if isinstance(cited_by_count_raw, int) else None

    is_retracted_raw = work.get("is_retracted")
    is_retracted = is_retracted_raw if isinstance(is_retracted_raw, bool) else None

    primary_field_id: str | None = None
    primary_field_name: str | None = None
    primary_topic = work.get("primary_topic")
    if isinstance(primary_topic, dict):
        field = primary_topic.get("field")
        if isinstance(field, dict):
            primary_field_id = strip_prefix(field.get("id"), OPENALEX_PREFIX)
            name_raw = field.get("display_name")
            if isinstance(name_raw, str):
                primary_field_name = name_raw

    papers_row = {
        "openalex_id": openalex_id,
        "doi": strip_prefix(work.get("doi"), DOI_PREFIX),
        "title": title,
        "year": year,
        "cited_by_count": cited_by_count,
        "is_retracted": is_retracted,
        "primary_field_id": primary_field_id,
        "primary_field_name": primary_field_name,
        "concepts_json": top_concepts_json(work.get("concepts")),
    }

    citations_rows: list[dict[str, Any]] = []
    references_raw = work.get("referenced_works")
    if isinstance(references_raw, list):
        for reference in references_raw:
            cited_id = strip_prefix(reference, OPENALEX_PREFIX)
            if not cited_id:
                continue
            citations_rows.append(
                {
                    "citing_id": openalex_id,
                    "cited_id": cited_id,
                },
            )

    authorships_rows: list[dict[str, Any]] = []
    author_ids_for_edges: list[str] = []
    authorships_raw = work.get("authorships")
    if isinstance(authorships_raw, list):
        for index, authorship in enumerate(authorships_raw):
            if not isinstance(authorship, dict):
                continue

            author_block = authorship.get("author")
            if not isinstance(author_block, dict):
                continue

            author_id = strip_prefix(author_block.get("id"), OPENALEX_PREFIX)
            if not author_id:
                continue

            author_name_raw = author_block.get("display_name")
            author_name = author_name_raw if isinstance(author_name_raw, str) else None

            is_corresponding_raw = authorship.get("is_corresponding")
            is_corresponding = (
                is_corresponding_raw if isinstance(is_corresponding_raw, bool) else None
            )

            institution_name: str | None = None
            country: str | None = None
            institutions_raw = authorship.get("institutions")
            if isinstance(institutions_raw, list) and institutions_raw:
                first_institution = institutions_raw[0]
                if isinstance(first_institution, dict):
                    inst_name_raw = first_institution.get("display_name")
                    if isinstance(inst_name_raw, str):
                        institution_name = inst_name_raw
                    country_raw = first_institution.get("country_code")
                    if isinstance(country_raw, str):
                        country = country_raw

            authorships_rows.append(
                {
                    "openalex_id": openalex_id,
                    "author_id": author_id,
                    "author_name": author_name,
                    "position": index,
                    "is_corresponding": is_corresponding,
                    "institution_name": institution_name,
                    "country": country,
                },
            )
            author_ids_for_edges.append(author_id)

    unique_authors = list(dict.fromkeys(author_ids_for_edges))
    coauthorship_rows: list[dict[str, Any]] = []
    for author_one, author_two in itertools.combinations(unique_authors, 2):
        author_a, author_b = sorted((author_one, author_two))
        coauthorship_rows.append(
            {
                "author_a": author_a,
                "author_b": author_b,
                "paper_id": openalex_id,
                "year": year,
            },
        )

    return {
        "papers": [papers_row],
        "citations": citations_rows,
        "authorships": authorships_rows,
        "coauthorship_edges": coauthorship_rows,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON payload with stable formatting.

    Args:
        path: Destination path.
        payload: Serializable object.
    """

    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
    temp_path.replace(path)


def load_state(progress_path: Path) -> dict[str, Any]:
    """Load resumability state from disk.

    Args:
        progress_path: Progress file path.

    Returns:
        State dictionary with processed directory set and counters.
    """

    if not progress_path.exists():
        return {
            "processed_directories": [],
            "totals": {
                "works": 0,
                "papers": 0,
                "citations": 0,
                "authorships": 0,
                "coauthorship_edges": 0,
                "files": 0,
                "warnings": 0,
            },
        }

    with progress_path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise ValueError(f"Invalid state format in {progress_path}")
    return loaded


def merge_parquet_files(
    source_files: list[Path],
    destination_file: Path,
    schema: pa.Schema,
    batch_size: int,
) -> int:
    """Merge multiple parquet files into one output parquet file.

    Args:
        source_files: Input parquet files.
        destination_file: Output file path.
        schema: Target schema.
        batch_size: Record batch size used while streaming.

    Returns:
        Number of rows written to the merged file.
    """

    destination_file.parent.mkdir(parents=True, exist_ok=True)
    temp_file = destination_file.with_suffix(destination_file.suffix + ".tmp")

    total_rows = 0
    with pq.ParquetWriter(
        str(temp_file), schema=schema, compression="snappy"
    ) as writer:
        dataset = ds.dataset([str(path) for path in source_files], format="parquet")
        scanner = dataset.scanner(batch_size=batch_size)
        for record_batch in scanner.to_batches():
            writer.write_batch(record_batch)
            total_rows += record_batch.num_rows

    temp_file.replace(destination_file)
    return total_rows


def run_etl(
    input_root: Path,
    output_root: Path,
    batch_size: int,
    log_interval: int,
    max_directories: int | None,
    rebuild_final: bool,
) -> None:
    """Execute OpenAlex snapshot ETL.

    Args:
        input_root: Path to OpenAlex works snapshot root.
        output_root: Path for graph parquet outputs.
        batch_size: Batch flush threshold for parquet writes.
        log_interval: Work-level progress log interval.
        max_directories: Optional cap on number of directories to process.
        rebuild_final: Rebuild final parquet from all processed directory files.
    """

    logger = logging.getLogger(__name__)

    if not input_root.exists():
        raise FileNotFoundError(f"Input root not found: {input_root}")

    output_root.mkdir(parents=True, exist_ok=True)
    processed_root = output_root / "_processed_dirs"
    staging_root = output_root / "_staging"
    processed_root.mkdir(parents=True, exist_ok=True)
    staging_root.mkdir(parents=True, exist_ok=True)

    progress_path = output_root / STATE_FILE_NAME
    summary_path = output_root / SUMMARY_FILE_NAME

    state = load_state(progress_path)
    processed_dirs = set(state.get("processed_directories", []))
    totals = state.get("totals", {})

    all_dirs = sorted(
        path for path in input_root.glob("updated_date=*") if path.is_dir()
    )
    pending_dirs = [path for path in all_dirs if path.name not in processed_dirs]
    if max_directories is not None:
        pending_dirs = pending_dirs[:max_directories]

    logger.info(
        "Starting ETL",
        extra={
            "directories_total": len(all_dirs),
            "directories_processed": len(processed_dirs),
            "directories_pending": len(pending_dirs),
            "batch_size": batch_size,
        },
    )

    started_at = time.monotonic()
    run_warnings = 0
    run_works = 0
    run_files = 0
    new_directory_files: dict[str, list[Path]] = {key: [] for key in TABLES}

    for directory_index, directory in enumerate(pending_dirs, start=1):
        directory_started = time.monotonic()
        gz_files = sorted(directory.glob("*.gz"))
        if not gz_files:
            logger.warning("No gzip files found in directory", extra={"dir": directory})
            processed_dirs.add(directory.name)
            state["processed_directories"] = sorted(processed_dirs)
            write_json(progress_path, state)
            continue

        staging_dir = staging_root / directory.name
        if staging_dir.exists():
            shutil.rmtree(staging_dir)

        writer = DirectoryBatchWriter(output_dir=staging_dir, batch_size=batch_size)
        directory_works = 0
        directory_warnings = 0
        directory_files = 0

        try:
            for gz_file in gz_files:
                directory_files += 1
                run_files += 1
                with gzip.open(gz_file, "rt", encoding="utf-8") as handle:
                    for line_number, line in enumerate(handle, start=1):
                        stripped = line.strip()
                        if not stripped:
                            continue

                        try:
                            payload = json.loads(stripped)
                        except json.JSONDecodeError:
                            directory_warnings += 1
                            run_warnings += 1
                            logger.warning(
                                "Malformed JSON line skipped",
                                extra={
                                    "file": str(gz_file),
                                    "line": line_number,
                                },
                            )
                            continue

                        if not isinstance(payload, dict):
                            directory_warnings += 1
                            run_warnings += 1
                            logger.warning(
                                "Non-object JSON line skipped",
                                extra={
                                    "file": str(gz_file),
                                    "line": line_number,
                                },
                            )
                            continue

                        try:
                            extracted = extract_rows_from_work(payload)
                        except ValueError as exc:
                            directory_warnings += 1
                            run_warnings += 1
                            logger.warning(
                                "Work record skipped",
                                extra={
                                    "file": str(gz_file),
                                    "line": line_number,
                                    "reason": str(exc),
                                },
                            )
                            continue

                        directory_works += 1
                        run_works += 1

                        for table_key, rows in extracted.items():
                            for row in rows:
                                writer.add_row(table_key, row)

                        if run_works % log_interval == 0:
                            elapsed = time.monotonic() - started_at
                            logger.info(
                                "Progress",
                                extra={
                                    "files_processed": run_files,
                                    "records_processed": run_works,
                                    "elapsed_seconds": round(elapsed, 2),
                                },
                            )
        finally:
            writer.close()

        final_dir = processed_root / directory.name
        if final_dir.exists():
            shutil.rmtree(final_dir)
        shutil.move(str(staging_dir), str(final_dir))

        for table_key, config in TABLES.items():
            new_directory_files[table_key].append(final_dir / config.file_name)

        processed_dirs.add(directory.name)
        state["processed_directories"] = sorted(processed_dirs)

        totals["works"] = int(totals.get("works", 0)) + directory_works
        totals["files"] = int(totals.get("files", 0)) + directory_files
        totals["warnings"] = int(totals.get("warnings", 0)) + directory_warnings
        for table_key in TABLES:
            totals[table_key] = (
                int(totals.get(table_key, 0)) + writer.rows_written[table_key]
            )

        state["totals"] = totals
        state["updated_at"] = datetime.now(UTC).isoformat()
        write_json(progress_path, state)

        directory_elapsed = time.monotonic() - directory_started
        logger.info(
            "Directory complete",
            extra={
                "dir": directory.name,
                "directory_index": directory_index,
                "directory_count": len(pending_dirs),
                "files": directory_files,
                "works": directory_works,
                "warnings": directory_warnings,
                "elapsed_seconds": round(directory_elapsed, 2),
            },
        )

    merged_counts: dict[str, int] = {}
    for table_key, config in TABLES.items():
        final_file = output_root / config.file_name
        sources: list[Path] = []

        if rebuild_final:
            sources = sorted(processed_root.glob(f"updated_date=*/{config.file_name}"))
        else:
            new_files = new_directory_files[table_key]
            if final_file.exists() and new_files:
                sources = [final_file, *new_files]
            elif (not final_file.exists()) and (new_files or processed_dirs):
                if new_files:
                    sources = new_files
                else:
                    sources = sorted(
                        processed_root.glob(f"updated_date=*/{config.file_name}"),
                    )

        if sources:
            merged_counts[table_key] = merge_parquet_files(
                source_files=sources,
                destination_file=final_file,
                schema=config.schema,
                batch_size=batch_size,
            )
        elif not final_file.exists():
            empty_table = pa.Table.from_pylist([], schema=config.schema)
            pq.write_table(empty_table, str(final_file), compression="snappy")
            merged_counts[table_key] = 0
        else:
            merged_counts[table_key] = int(totals.get(table_key, 0))

    elapsed_total = time.monotonic() - started_at
    summary = {
        "input_root": str(input_root),
        "output_root": str(output_root),
        "directories_total": len(all_dirs),
        "directories_processed": len(processed_dirs),
        "directories_processed_this_run": len(pending_dirs),
        "files_processed_this_run": run_files,
        "works_processed_this_run": run_works,
        "warnings_this_run": run_warnings,
        "elapsed_seconds": round(elapsed_total, 2),
        "totals": {
            "works": int(totals.get("works", 0)),
            "papers": int(totals.get("papers", 0)),
            "citations": int(totals.get("citations", 0)),
            "authorships": int(totals.get("authorships", 0)),
            "coauthorship_edges": int(totals.get("coauthorship_edges", 0)),
            "files": int(totals.get("files", 0)),
            "warnings": int(totals.get("warnings", 0)),
        },
        "final_parquet_row_counts": merged_counts,
        "updated_at": datetime.now(UTC).isoformat(),
    }
    write_json(summary_path, summary)

    logger.info(
        "ETL finished",
        extra={
            "elapsed_seconds": round(elapsed_total, 2),
            "summary_path": str(summary_path),
        },
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed CLI namespace.
    """

    parser = argparse.ArgumentParser(
        description="ETL OpenAlex works snapshot into graph parquet files.",
    )
    parser.add_argument(
        "--input-root",
        type=Path,
        default=DEFAULT_INPUT_ROOT,
        help="Root directory containing updated_date=* OpenAlex works folders.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory where graph parquet outputs are written.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100_000,
        help="Rows buffered per table before parquet flush.",
    )
    parser.add_argument(
        "--log-interval",
        type=int,
        default=10_000,
        help="Progress log interval in processed work records.",
    )
    parser.add_argument(
        "--max-directories",
        type=int,
        default=None,
        help="Optional limit on pending directories processed this run.",
    )
    parser.add_argument(
        "--rebuild-final",
        action="store_true",
        help="Rebuild final parquet files from all processed directories.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR).",
    )
    return parser.parse_args()


def main() -> None:
    """Run CLI entrypoint."""

    args = parse_args()
    setup_logging(args.log_level)
    run_etl(
        input_root=args.input_root,
        output_root=args.output_root,
        batch_size=args.batch_size,
        log_interval=args.log_interval,
        max_directories=args.max_directories,
        rebuild_final=args.rebuild_final,
    )


if __name__ == "__main__":
    main()
