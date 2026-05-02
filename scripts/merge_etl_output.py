#!/usr/bin/env python3
"""Merge per-directory ETL parquet files into single output files.

Uses PyArrow dataset scanner for streaming merge — avoids loading
all data into memory at once.
"""

from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

import pyarrow.dataset as ds
import pyarrow.parquet as pq

TABLES = ["papers", "citations", "authorships", "coauthorship_edges"]

DEFAULT_PROCESSED_DIRS = Path(
    "data/processed/graph/_processed_dirs",
)
DEFAULT_OUTPUT_DIR = Path("data/processed/graph")


def merge_table(
    table_name: str,
    processed_dirs: Path,
    output_dir: Path,
    row_group_size: int,
) -> int:
    """Merge all per-directory parquet files for one table.

    Args:
        table_name: Name of the table (e.g. "papers").
        processed_dirs: Root of per-directory ETL outputs.
        output_dir: Where to write the merged file.
        row_group_size: Rows per parquet row group.

    Returns:
        Total rows written.
    """
    logger = logging.getLogger(__name__)
    pattern = f"updated_date=*/{table_name}.parquet"
    source_files = sorted(processed_dirs.glob(pattern))

    if not source_files:
        logger.warning("No files found for %s", table_name)
        return 0

    logger.info(
        "Merging %s: %d source files",
        table_name,
        len(source_files),
    )

    dataset = ds.dataset(
        [str(f) for f in source_files],
        format="parquet",
    )

    output_path = output_dir / f"{table_name}.parquet"
    temp_path = output_path.with_suffix(".parquet.tmp")

    total_rows = 0
    scanner = dataset.scanner(batch_size=row_group_size)

    with pq.ParquetWriter(
        str(temp_path),
        schema=dataset.schema,
        compression="snappy",
    ) as writer:
        for batch in scanner.to_batches():
            writer.write_batch(batch)
            total_rows += batch.num_rows
            if total_rows % (row_group_size * 10) == 0:
                logger.info(
                    "%s progress: %s rows",
                    table_name,
                    f"{total_rows:,}",
                )

    temp_path.replace(output_path)
    logger.info(
        "%s complete: %s rows, %.1f MB",
        table_name,
        f"{total_rows:,}",
        output_path.stat().st_size / 1e6,
    )
    return total_rows


def main() -> None:
    """Run the merge CLI."""
    parser = argparse.ArgumentParser(
        description="Merge per-directory ETL parquet files.",
    )
    parser.add_argument(
        "--processed-dirs",
        type=Path,
        default=DEFAULT_PROCESSED_DIRS,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
    )
    parser.add_argument(
        "--tables",
        nargs="+",
        default=TABLES,
        choices=TABLES,
    )
    parser.add_argument(
        "--row-group-size",
        type=int,
        default=500_000,
    )
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
    )

    logger = logging.getLogger(__name__)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for table_name in args.tables:
        started = time.monotonic()
        rows = merge_table(
            table_name,
            args.processed_dirs,
            args.output_dir,
            args.row_group_size,
        )
        elapsed = time.monotonic() - started
        logger.info(
            "Table %s: %s rows in %.1f seconds",
            table_name,
            f"{rows:,}",
            elapsed,
        )


if __name__ == "__main__":
    main()
