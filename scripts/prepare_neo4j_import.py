#!/usr/bin/env python3
"""Convert ETL parquet to neo4j-admin import format, directory by directory.

Processes each updated_date directory independently (low memory).
Outputs per-directory renamed-column parquets + deduplicated author/field nodes.
neo4j-admin import accepts glob patterns for multiple files.
"""

from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

PROCESSED_DIRS = Path("data/processed/graph/_processed_dirs")
OUTPUT_DIR = Path("data/processed/neo4j_import")

PAPER_SCHEMA = pa.schema(
    [
        pa.field("openalex_id:ID(Paper)", pa.string()),
        pa.field("doi", pa.string()),
        pa.field("title", pa.string()),
        pa.field("year:int", pa.int64()),
        pa.field("cited_by_count:int", pa.int64()),
        pa.field("is_retracted:boolean", pa.bool_()),
        pa.field("primary_field_id", pa.string()),
        pa.field("primary_field_name", pa.string()),
        pa.field("concepts_json", pa.string()),
    ]
)

PAPER_MAP = {
    "openalex_id": "openalex_id:ID(Paper)",
    "doi": "doi",
    "title": "title",
    "year": "year:int",
    "cited_by_count": "cited_by_count:int",
    "is_retracted": "is_retracted:boolean",
    "primary_field_id": "primary_field_id",
    "primary_field_name": "primary_field_name",
    "concepts_json": "concepts_json",
}

CITES_SCHEMA = pa.schema(
    [
        pa.field(":START_ID(Paper)", pa.string()),
        pa.field(":END_ID(Paper)", pa.string()),
    ]
)
CITES_MAP = {"citing_id": ":START_ID(Paper)", "cited_id": ":END_ID(Paper)"}

AUTHORED_SCHEMA = pa.schema(
    [
        pa.field(":START_ID(Author)", pa.string()),
        pa.field(":END_ID(Paper)", pa.string()),
        pa.field("position:int", pa.int64()),
        pa.field("is_corresponding:boolean", pa.bool_()),
    ]
)
AUTHORED_MAP = {
    "author_id": ":START_ID(Author)",
    "openalex_id": ":END_ID(Paper)",
    "position": "position:int",
    "is_corresponding": "is_corresponding:boolean",
}

BELONGS_SCHEMA = pa.schema(
    [
        pa.field(":START_ID(Paper)", pa.string()),
        pa.field(":END_ID(Field)", pa.string()),
    ]
)
BELONGS_MAP = {"openalex_id": ":START_ID(Paper)", "primary_field_id": ":END_ID(Field)"}


def rename_columns(
    src: Path,
    dst: Path,
    col_map: dict[str, str],
    schema: pa.Schema,
    batch_size: int = 500_000,
) -> int:
    """Read one parquet, rename columns, write to new file.

    Args:
        src: Input parquet.
        dst: Output parquet.
        col_map: old_name -> new_name.
        schema: Target schema.
        batch_size: Rows per batch.

    Returns:
        Rows written.
    """
    if not src.exists():
        return 0
    pf = pq.ParquetFile(src)
    total = 0
    tmp = dst.with_suffix(".parquet.tmp")
    with pq.ParquetWriter(str(tmp), schema=schema, compression="snappy") as w:
        for batch in pf.iter_batches(batch_size=batch_size):
            arrays = []
            for field in schema:
                src_col = next((k for k, v in col_map.items() if v == field.name), None)
                if src_col and src_col in batch.schema.names:
                    col = batch.column(src_col)
                    if col.type != field.type:
                        col = col.cast(field.type)
                    arrays.append(col)
                else:
                    arrays.append(pa.nulls(len(batch), type=field.type))
            w.write_batch(pa.RecordBatch.from_arrays(arrays, schema=schema))
            total += len(batch)
    tmp.replace(dst)
    return total


def build_author_nodes(dirs: list[Path], output: Path) -> int:
    """Build deduplicated author nodes from authorship files.

    Args:
        dirs: ETL output directories containing authorships.parquet.
        output: Output author_nodes.parquet.

    Returns:
        Unique author count.
    """
    logger = logging.getLogger(__name__)
    schema = pa.schema(
        [
            pa.field("author_id:ID(Author)", pa.string()),
            pa.field("author_name", pa.string()),
            pa.field("institution_name", pa.string()),
            pa.field("country", pa.string()),
        ]
    )
    seen: set[str] = set()
    buf: list[dict[str, str | None]] = []
    total = 0
    tmp = output.with_suffix(".parquet.tmp")

    with pq.ParquetWriter(str(tmp), schema=schema, compression="snappy") as w:
        for i, d in enumerate(dirs):
            f = d / "authorships.parquet"
            if not f.exists():
                continue
            pf = pq.ParquetFile(f)
            for batch in pf.iter_batches(
                batch_size=500_000,
                columns=["author_id", "author_name", "institution_name", "country"],
            ):
                ids = batch.column("author_id").to_pylist()
                names = batch.column("author_name").to_pylist()
                insts = batch.column("institution_name").to_pylist()
                ctry = batch.column("country").to_pylist()
                for j, aid in enumerate(ids):
                    if aid is None or aid in seen:
                        continue
                    seen.add(aid)
                    buf.append(
                        {
                            "author_id:ID(Author)": aid,
                            "author_name": names[j],
                            "institution_name": insts[j],
                            "country": ctry[j],
                        }
                    )
                    if len(buf) >= 500_000:
                        w.write_table(pa.Table.from_pylist(buf, schema=schema))
                        total += len(buf)
                        buf.clear()
            if (i + 1) % 50 == 0:
                logger.info(
                    "Authors: %d/%d dirs, %s unique so far",
                    i + 1,
                    len(dirs),
                    f"{total + len(buf):,}",
                )
        if buf:
            w.write_table(pa.Table.from_pylist(buf, schema=schema))
            total += len(buf)
    tmp.replace(output)
    logger.info("Authors done: %s unique", f"{total:,}")
    return total


def build_field_nodes(dirs: list[Path], output: Path) -> int:
    """Build deduplicated field nodes.

    Args:
        dirs: ETL output directories containing papers.parquet.
        output: Output field_nodes.parquet.

    Returns:
        Unique field count.
    """
    schema = pa.schema(
        [
            pa.field("field_id:ID(Field)", pa.string()),
            pa.field("field_name", pa.string()),
        ]
    )
    seen: dict[str, str | None] = {}
    for d in dirs:
        f = d / "papers.parquet"
        if not f.exists():
            continue
        pf = pq.ParquetFile(f)
        for batch in pf.iter_batches(
            batch_size=500_000, columns=["primary_field_id", "primary_field_name"]
        ):
            ids = batch.column("primary_field_id").to_pylist()
            names = batch.column("primary_field_name").to_pylist()
            for j, fid in enumerate(ids):
                if fid is not None and fid not in seen:
                    seen[fid] = names[j]
    rows = [{"field_id:ID(Field)": k, "field_name": v} for k, v in seen.items()]
    pq.write_table(
        pa.Table.from_pylist(rows, schema=schema), str(output), compression="snappy"
    )
    return len(rows)


def main() -> None:
    """Run per-directory neo4j-admin import preparation."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dirs", type=Path, default=PROCESSED_DIRS)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
    )
    logger = logging.getLogger(__name__)
    out = args.output_dir
    for sub in ["papers", "cites", "authored", "belongs_to"]:
        (out / sub).mkdir(parents=True, exist_ok=True)

    all_dirs = sorted(args.processed_dirs.glob("updated_date=*"))
    logger.info("Processing %d directories", len(all_dirs))
    t0 = time.monotonic()

    tp = tc = ta = tb = 0
    for i, d in enumerate(all_dirs):
        nm = d.name
        tp += rename_columns(
            d / "papers.parquet",
            out / "papers" / f"{nm}.parquet",
            PAPER_MAP,
            PAPER_SCHEMA,
        )
        tc += rename_columns(
            d / "citations.parquet",
            out / "cites" / f"{nm}.parquet",
            CITES_MAP,
            CITES_SCHEMA,
        )
        ta += rename_columns(
            d / "authorships.parquet",
            out / "authored" / f"{nm}.parquet",
            AUTHORED_MAP,
            AUTHORED_SCHEMA,
        )
        tb += rename_columns(
            d / "papers.parquet",
            out / "belongs_to" / f"{nm}.parquet",
            BELONGS_MAP,
            BELONGS_SCHEMA,
        )
        if (i + 1) % 10 == 0 or (i + 1) == len(all_dirs):
            logger.info(
                "Dir %d/%d — papers:%s cites:%s authored:%s",
                i + 1,
                len(all_dirs),
                f"{tp:,}",
                f"{tc:,}",
                f"{ta:,}",
            )

    logger.info("Building deduplicated author + field nodes...")
    build_author_nodes(all_dirs, out / "author_nodes.parquet")
    build_field_nodes(all_dirs, out / "field_nodes.parquet")

    logger.info(
        "Done in %.0fs. Papers:%s Cites:%s Authored:%s Belongs:%s",
        time.monotonic() - t0,
        f"{tp:,}",
        f"{tc:,}",
        f"{ta:,}",
        f"{tb:,}",
    )


if __name__ == "__main__":
    main()
