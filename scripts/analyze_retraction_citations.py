"""Analyze citation patterns around retracted papers for Track 3.

Produces key statistics using verified retraction dates from Retraction Watch:
1. Pre vs post-retraction citation counts (using ACTUAL retraction dates, not publication year)
2. Citation half-life after retraction
3. Field-level citation persistence
4. Top "zombie" papers (most post-retraction citations)

BUG FIX: Previous version used r.year (publication year) instead of actual
retraction year from Retraction Watch, producing an incorrect 90.88% post-retraction
figure. This version uses the verified retraction dates.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import pandas as pd
from neo4j import Driver, GraphDatabase

from palimpsest.utils.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("data/processed/retraction_analysis")
RW_JOINED_PATH = Path("data/processed/retraction_watch_openalex_joined.parquet")


def _load_retraction_dates() -> dict[str, int]:
    """Load retraction dates from Retraction Watch, return {oa_id: retraction_year}."""
    rw = pd.read_parquet(RW_JOINED_PATH)
    rw["retraction_year"] = pd.to_datetime(
        rw["retraction_date"], format="mixed", errors="coerce"
    ).dt.year
    rw["oa_id"] = rw["openalex_id"].str.replace("https://openalex.org/", "", regex=False)
    valid = rw.dropna(subset=["retraction_year"])
    mapping = dict(zip(valid["oa_id"], valid["retraction_year"].astype(int)))
    logger.info("Loaded %d retraction dates from Retraction Watch", len(mapping))
    return mapping


def _fetch_citation_edges(driver: Driver) -> pd.DataFrame:
    """Fetch all citation edges to retracted papers from Neo4j."""
    cypher = (
        "MATCH (r:Paper {is_retracted: true})<-[:CITES]-(c:Paper) "
        "WHERE r.year IS NOT NULL AND c.year IS NOT NULL "
        "RETURN r.openalex_id AS retracted_id, r.year AS retracted_pub_year, "
        "c.year AS citing_year, r.title AS title, "
        "r.cited_by_count AS total_cites, r.primary_field_name AS field"
    )
    logger.info("Fetching citation edges from Neo4j...")
    with driver.session(database="neo4j") as session:
        records = list(session.run(cypher))

    df = pd.DataFrame([dict(r) for r in records])
    logger.info("Fetched %d citation edges", len(df))
    return df


def main() -> None:
    """Run retraction citation analysis."""
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )
    driver.verify_connectivity()
    logger.info("Connected to Neo4j")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()

    # Load verified retraction dates
    retraction_dates = _load_retraction_dates()

    # Fetch citation edges
    edges = _fetch_citation_edges(driver)

    # Classify using ACTUAL retraction dates (not publication year)
    edges["retraction_year"] = edges["retracted_id"].map(retraction_dates)
    classified = edges.dropna(subset=["retraction_year"])
    classified["retraction_year"] = classified["retraction_year"].astype(int)

    classified["timing"] = "unknown"
    classified.loc[classified["citing_year"] < classified["retraction_year"], "timing"] = "pre"
    classified.loc[classified["citing_year"] == classified["retraction_year"], "timing"] = "same_year"
    classified.loc[classified["citing_year"] > classified["retraction_year"], "timing"] = "post"

    results: dict[str, object] = {}

    logger.info("1/4: Pre vs post-retraction citation distribution...")
    results["pre_post_distribution"] = _pre_post_distribution(classified, edges)

    logger.info("2/4: Citation persistence by years since retraction...")
    results["citation_persistence"] = _citation_persistence(classified)

    logger.info("3/4: Field-level citation patterns...")
    results["field_patterns"] = _field_citation_patterns(classified)

    logger.info("4/4: Top zombie papers (most post-retraction citations)...")
    results["zombie_papers"] = _zombie_papers(classified)

    output_path = OUTPUT_DIR / "retraction_citation_analysis.json"
    output_path.write_text(json.dumps(results, indent=2, default=str))
    logger.info("Results saved to %s", output_path)

    elapsed = time.perf_counter() - t0
    logger.info("Analysis complete in %.1f seconds", elapsed)
    driver.close()

    _print_summary(results)


def _pre_post_distribution(
    classified: pd.DataFrame, all_edges: pd.DataFrame
) -> dict[str, object]:
    """Count citations before and after actual retraction date."""
    dist = classified["timing"].value_counts().to_dict()
    total_classified = len(classified)
    total_all = len(all_edges)
    matched_pct = round(total_classified / max(total_all, 1) * 100, 1)

    return {
        "pre_retraction": dist.get("pre", 0),
        "same_year": dist.get("same_year", 0),
        "post_retraction": dist.get("post", 0),
        "total_classified": total_classified,
        "total_all_edges": total_all,
        "coverage_pct": matched_pct,
        "pre_retraction_pct": round(dist.get("pre", 0) / max(total_classified, 1) * 100, 2),
        "post_retraction_pct": round(dist.get("post", 0) / max(total_classified, 1) * 100, 2),
        "note": "Uses verified retraction dates from Retraction Watch, NOT publication year",
    }


def _citation_persistence(classified: pd.DataFrame) -> list[dict[str, object]]:
    """Count citations by years-since-retraction using actual retraction dates."""
    post = classified[classified["timing"] == "post"].copy()
    post["years_after"] = post["citing_year"] - post["retraction_year"]
    persistence = (
        post[post["years_after"] <= 15]
        .groupby("years_after")
        .size()
        .reset_index(name="count")
        .sort_values("years_after")
    )
    return [
        {"years_after": int(row["years_after"]), "count": int(row["count"])}
        for _, row in persistence.iterrows()
    ]


def _field_citation_patterns(classified: pd.DataFrame) -> list[dict[str, object]]:
    """Analyze which fields continue citing retracted papers post-retraction."""
    post = classified[classified["timing"] == "post"]
    field_counts = post.groupby("field").size().reset_index(name="post_cites")
    field_counts = field_counts.sort_values("post_cites", ascending=False)
    return [
        {"field": row["field"], "post_retraction_citations": int(row["post_cites"])}
        for _, row in field_counts.iterrows()
    ]


def _zombie_papers(classified: pd.DataFrame) -> list[dict[str, object]]:
    """Find papers with most citations received AFTER retraction (using actual retraction date)."""
    post = classified[classified["timing"] == "post"]
    zombie = (
        post.groupby(["retracted_id", "title", "retracted_pub_year", "total_cites", "field"])
        .size()
        .reset_index(name="post_cites")
        .sort_values("post_cites", ascending=False)
        .head(20)
    )
    return [
        {
            "title": row["title"],
            "pub_year": int(row["retracted_pub_year"]),
            "total_citations": int(row["total_cites"]),
            "post_retraction_citations": int(row["post_cites"]),
            "field": row["field"],
        }
        for _, row in zombie.iterrows()
    ]


def _print_summary(results: dict[str, object]) -> None:
    """Print key findings to stdout."""
    dist = results["pre_post_distribution"]
    print("\n" + "=" * 60)
    print("RETRACTION CITATION ANALYSIS SUMMARY")
    print("(Using verified retraction dates from Retraction Watch)")
    print("=" * 60)
    print(f"\nCoverage: {dist['total_classified']:,} / {dist['total_all_edges']:,} edges ({dist['coverage_pct']}%)")
    print("\nPre/Post Distribution (classified edges only):")
    print(f"  Pre-retraction:  {dist['pre_retraction']:>10,}  ({dist['pre_retraction_pct']}%)")
    print(f"  Same year:       {dist['same_year']:>10,}")
    print(f"  Post-retraction: {dist['post_retraction']:>10,}  ({dist['post_retraction_pct']}%)")

    persistence = results["citation_persistence"]
    print("\nCitation Persistence (years after ACTUAL retraction):")
    for p in persistence[:6]:
        print(f"  +{p['years_after']} years: {p['count']:>8,}")

    fields = results["field_patterns"]
    print("\nTop Fields Citing Retracted Papers (post-retraction):")
    for f in fields[:5]:
        print(f"  {f['field']}: {f['post_retraction_citations']:>8,}")

    zombies = results["zombie_papers"]
    print("\nTop 'Zombie' Papers (most post-retraction citations):")
    for z in zombies[:5]:
        print(f"  {z['title'][:60]}...")
        print(f"    Post-retraction: {z['post_retraction_citations']:,}")


if __name__ == "__main__":
    main()
