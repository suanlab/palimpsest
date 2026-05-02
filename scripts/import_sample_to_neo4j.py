#!/usr/bin/env python3
"""Import sample graph data directly into Neo4j using the driver."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "research2026"

GRAPH_DIR = Path("data/processed/graph")


def import_papers(driver: GraphDatabase.Driver, papers_df: pd.DataFrame) -> int:
    """Import papers into Neo4j."""
    query = """
    UNWIND $papers AS paper
    MERGE (p:Paper {id: paper.openalex_id})
    SET p.doi = paper.doi,
        p.title = paper.title,
        p.year = paper.year,
        p.cited_by_count = paper.cited_by_count,
        p.is_retracted = paper.is_retracted,
        p.primary_field = paper.primary_field_name
    RETURN count(p) as imported
    """

    with driver.session() as session:
        result = session.run(query, papers=papers_df.to_dict("records"))
        return result.single()["imported"]


def import_authors(
    driver: GraphDatabase.Driver, authorships_df: pd.DataFrame
) -> tuple[int, int]:
    """Import authors and authorship relationships."""
    # Get unique authors
    authors = authorships_df[["author_id", "author_name"]].drop_duplicates()

    author_query = """
    UNWIND $authors AS author
    MERGE (a:Author {id: author.author_id})
    SET a.name = author.author_name
    RETURN count(a) as imported
    """

    authored_query = """
    UNWIND $authorships AS auth
    MATCH (p:Paper {id: auth.paper_id})
    MATCH (a:Author {id: auth.author_id})
    MERGE (a)-[:AUTHORED]->(p)
    RETURN count(*) as imported
    """

    with driver.session() as session:
        authors_result = session.run(author_query, authors=authors.to_dict("records"))
        authored_result = session.run(
            authored_query, authorships=authorships_df.to_dict("records")
        )
        return authors_result.single()["imported"], authored_result.single()["imported"]


def import_citations(driver: GraphDatabase.Driver, citations_df: pd.DataFrame) -> int:
    """Import citation relationships."""
    query = """
    UNWIND $citations AS cite
    MATCH (from:Paper {id: cite.citing_paper_id})
    MATCH (to:Paper {id: cite.cited_paper_id})
    MERGE (from)-[:CITES]->(to)
    RETURN count(*) as imported
    """

    with driver.session() as session:
        result = session.run(query, citations=citations_df.to_dict("records"))
        return result.single()["imported"]


def main() -> None:
    """Main import function."""
    logger.info("Connecting to Neo4j at %s", NEO4J_URI)
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    # Verify connection
    driver.verify_connectivity()
    logger.info("Connected successfully")

    # Clear existing data
    logger.info("Clearing existing data...")
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

    # Load data
    logger.info("Loading papers...")
    papers_df = pd.read_parquet(GRAPH_DIR / "papers.parquet")
    papers_imported = import_papers(driver, papers_df)
    logger.info("Imported %d papers", papers_imported)

    logger.info("Loading authorships...")
    authorships_df = pd.read_parquet(GRAPH_DIR / "authorships.parquet")
    authors_imported, authored_imported = import_authors(driver, authorships_df)
    logger.info(
        "Imported %d authors and %d authorships", authors_imported, authored_imported
    )

    logger.info("Loading citations...")
    citations_df = pd.read_parquet(GRAPH_DIR / "citations.parquet")
    citations_imported = import_citations(driver, citations_df)
    logger.info("Imported %d citations", citations_imported)

    # Create indexes
    logger.info("Creating indexes...")
    with driver.session() as session:
        session.run("CREATE INDEX paper_id IF NOT EXISTS FOR (p:Paper) ON (p.id)")
        session.run("CREATE INDEX author_id IF NOT EXISTS FOR (a:Author) ON (a.id)")
        session.run("CREATE INDEX paper_year IF NOT EXISTS FOR (p:Paper) ON (p.year)")

    driver.close()
    logger.info("Import complete!")
    logger.info(
        "Summary: %d papers, %d authors, %d citations",
        papers_imported,
        authors_imported,
        citations_imported,
    )


if __name__ == "__main__":
    main()
