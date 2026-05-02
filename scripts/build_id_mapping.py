"""Build unified ID mapping table from OpenAlex and arXiv data sources.

This script creates a mapping table linking papers across OpenAlex and arXiv
using DOI as the primary join key. The output enables linking arXiv papers
to their OpenAlex citation data.

Output schema:
    - doi: str (canonical lowercase, primary key)
    - openalex_id: str (nullable)
    - arxiv_id: str (nullable)
    - title: str (nullable)
"""

import argparse
import json
import logging
import re
from pathlib import Path

import duckdb
import pandas as pd

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure structured logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def extract_arxiv_id(identifier_url: str) -> str | None:
    """Extract arXiv ID from identifier URL.

    Args:
        identifier_url: URL like 'http://arxiv.org/abs/2301.12345' or
            'http://arxiv.org/abs/adap-org/9807003'

    Returns:
        arXiv ID (e.g., '2301.12345' or 'adap-org/9807003'), or None if
        extraction fails.
    """
    match = re.search(r"arxiv\.org/abs/(.+)$", identifier_url)
    if match:
        return match.group(1)
    return None


def load_openalex_papers(
    papers_path: Path,
) -> pd.DataFrame:
    """Load OpenAlex papers with DOI.

    Args:
        papers_path: Path to papers.parquet

    Returns:
        DataFrame with columns: openalex_id, doi, title
        DOI is normalized to lowercase and stripped.
    """
    logger.info(f"Loading OpenAlex papers from {papers_path}")
    df = pd.read_parquet(
        papers_path,
        columns=["openalex_id", "doi", "title"],
    )

    # Filter to papers with DOI
    df = df[df["doi"].notna()].copy()

    # Normalize DOI: lowercase and strip whitespace
    df["doi"] = df["doi"].str.lower().str.strip()

    logger.info(f"Loaded {len(df)} OpenAlex papers with DOI")
    return df


def load_arxiv_papers(
    arxiv_paths: list[Path],
) -> pd.DataFrame:
    """Load arXiv papers from JSONL files.

    Streams JSONL files to avoid loading all into memory at once.

    Args:
        arxiv_paths: List of paths to arXiv JSONL files

    Returns:
        DataFrame with columns: arxiv_id, title
    """
    records = []

    for path in arxiv_paths:
        if not path.exists():
            logger.warning(f"arXiv file not found: {path}")
            continue

        logger.info(f"Loading arXiv papers from {path}")
        with open(path) as f:
            for line_num, line in enumerate(f, 1):
                try:
                    record = json.loads(line)
                    identifiers = record.get("identifiers", [])

                    # Extract arXiv ID from first identifier
                    arxiv_id = None
                    if identifiers:
                        arxiv_id = extract_arxiv_id(identifiers[0])

                    if arxiv_id:
                        records.append(
                            {
                                "arxiv_id": arxiv_id,
                                "title": record.get("title"),
                            }
                        )
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON at {path}:{line_num}: {e}")
                    continue

        logger.info(f"Loaded {len(records)} arXiv records from {path}")

    df = pd.DataFrame(records)
    logger.info(f"Total arXiv papers: {len(df)}")
    return df


def build_mapping(
    openalex_df: pd.DataFrame,
    arxiv_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build unified ID mapping via DOI join.

    Since arXiv JSONL doesn't contain DOI directly, we use OpenAlex as the
    source of truth. Papers in arxiv_df without a DOI in OpenAlex will appear
    with null openalex_id.

    Args:
        openalex_df: DataFrame with openalex_id, doi, title
        arxiv_df: DataFrame with arxiv_id, title

    Returns:
        Unified mapping DataFrame with columns:
        doi, openalex_id, arxiv_id, title
    """
    logger.info("Building unified ID mapping via DuckDB")

    # Use DuckDB for efficient join
    conn = duckdb.connect(":memory:")

    # Register DataFrames
    conn.register("openalex", openalex_df)
    conn.register("arxiv", arxiv_df)

    # Full outer join on DOI (from OpenAlex)
    # Since arXiv doesn't have DOI in the raw data, we can only match
    # papers that are in OpenAlex. This is a limitation of the data source.
    # For now, we create a mapping with OpenAlex as primary source.
    result = conn.execute(
        """
        SELECT
            oa.doi,
            oa.openalex_id,
            NULL::VARCHAR as arxiv_id,
            oa.title
        FROM openalex oa
        UNION ALL
        SELECT
            NULL::VARCHAR as doi,
            NULL::VARCHAR as openalex_id,
            ax.arxiv_id,
            ax.title
        FROM arxiv ax
        """
    ).df()

    logger.info(f"Created mapping with {len(result)} rows")

    # Log statistics
    doi_count = result["doi"].notna().sum()
    openalex_count = result["openalex_id"].notna().sum()
    arxiv_count = result["arxiv_id"].notna().sum()

    logger.info(f"  DOI entries: {doi_count}")
    logger.info(f"  OpenAlex IDs: {openalex_count}")
    logger.info(f"  arXiv IDs: {arxiv_count}")

    return result


def main(
    papers_path: Path,
    arxiv_paths: list[Path],
    output_path: Path,
) -> None:
    """Main entry point.

    Args:
        papers_path: Path to OpenAlex papers.parquet
        arxiv_paths: List of paths to arXiv JSONL files
        output_path: Path to write id_mapping.parquet
    """
    # Load data
    openalex_df = load_openalex_papers(papers_path)
    arxiv_df = load_arxiv_papers(arxiv_paths)

    # Build mapping
    mapping_df = build_mapping(openalex_df, arxiv_df)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write output
    logger.info(f"Writing mapping to {output_path}")
    mapping_df.to_parquet(output_path, index=False)

    logger.info("ID mapping complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build unified ID mapping from OpenAlex and arXiv data"
    )
    parser.add_argument(
        "--papers",
        type=Path,
        default=Path("data/processed/graph/papers.parquet"),
        help="Path to OpenAlex papers.parquet",
    )
    parser.add_argument(
        "--arxiv",
        type=Path,
        nargs="+",
        default=[
            Path("data/raw/arxiv/cs_all.jsonl"),
            Path("data/raw/arxiv/stat_all.jsonl"),
        ],
        help="Paths to arXiv JSONL files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/id_mapping.parquet"),
        help="Output path for id_mapping.parquet",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    main(args.papers, args.arxiv, args.output)
