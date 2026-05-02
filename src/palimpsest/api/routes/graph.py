from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Annotated, Literal, LiteralString, cast

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from neo4j import Driver
from neo4j.exceptions import Neo4jError
from pydantic import BaseModel

from palimpsest.api.dependencies import get_neo4j_driver, limiter, run_query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["graph"])

MAX_LIMIT = 5000
DEFAULT_LIMIT = 1000
DriverDep = Annotated[Driver, Depends(get_neo4j_driver)]


class CitationNode(BaseModel):
    id: str
    title: str
    year: int | None
    cited_by_count: int
    field: str | None
    is_retracted: bool


class CitationEdge(BaseModel):
    source: str
    target: str


class CitationNetworkResponse(BaseModel):
    nodes: list[CitationNode]
    edges: list[CitationEdge]


class CoauthorshipNode(BaseModel):
    id: str
    name: str
    institution: str
    country: str
    paper_count: int


class CoauthorshipEdge(BaseModel):
    source: str
    target: str
    paper_count: int


class CoauthorshipNetworkResponse(BaseModel):
    nodes: list[CoauthorshipNode]
    edges: list[CoauthorshipEdge]


class ContaminationNode(BaseModel):
    id: str
    title: str
    year: int | None
    depth: int
    is_retracted: bool
    contamination_score: float


class ContaminationEdge(BaseModel):
    source: str
    target: str
    depth: int
    post_retraction: bool


class ContaminationCascadeResponse(BaseModel):
    nodes: list[ContaminationNode]
    edges: list[ContaminationEdge]


class AIDiffusionNode(BaseModel):
    id: str
    name: str
    total_papers: int
    ai_papers: int
    ai_fraction: float


class AIDiffusionEdge(BaseModel):
    source: str
    target: str
    citation_count: int
    year: int


class AIDiffusionResponse(BaseModel):
    nodes: list[AIDiffusionNode]
    edges: list[AIDiffusionEdge]


class FieldStatResponse(BaseModel):
    name: str
    paper_count: int
    color: str


class YearlyCount(BaseModel):
    year: int
    count: int


class GraphStatsResponse(BaseModel):
    total_papers: int
    total_authors: int
    total_citations: int
    total_fields: int
    total_retracted: int
    ai_related_papers: int
    ai_concept_papers: int
    fields: list[FieldStatResponse]
    yearly_publications: list[YearlyCount]


class RetractionPrePostDistribution(BaseModel):
    pre_retraction: int
    same_year: int
    post_retraction: int
    total: int
    post_retraction_pct: float


class CitationPersistencePoint(BaseModel):
    years_after: int
    count: int


class RetractionFieldPattern(BaseModel):
    field: str
    post_retraction_citations: int
    total_papers: int
    rate_per_million: float


class ZombiePaper(BaseModel):
    title: str
    pub_year: int
    total_citations: int
    post_retraction_citations: int
    field: str


class RetractionRateFieldSummary(BaseModel):
    field_id: str
    field_name: str
    total_papers: int
    total_retractions: float
    mean_ai_fraction: float
    mean_retraction_rate: float
    retraction_rate: float
    retraction_per_million: float


class RetractionStatsResponse(BaseModel):
    pre_post_distribution: RetractionPrePostDistribution
    citation_persistence: list[CitationPersistencePoint]
    top_fields: list[RetractionFieldPattern]
    top_zombies: list[ZombiePaper]
    retraction_rate_by_field: list[RetractionRateFieldSummary]


BASE_PROCESSED_DIR = Path(__file__).resolve().parents[4] / "data" / "processed"
RETRACTION_CITATION_ANALYSIS_PATH = (
    BASE_PROCESSED_DIR / "retraction_analysis" / "retraction_citation_analysis.json"
)
FIELD_ANALYSIS_PATH = BASE_PROCESSED_DIR / "neo4j_field_analysis.json"


@limiter.limit("30/minute")
@router.get("/citation-network", response_model=CitationNetworkResponse)
def get_citation_network(
    request: Request,
    seed_paper_id: str,
    depth: Annotated[int, Query(ge=1, le=3)] = 2,
    min_citations: Annotated[int, Query(ge=0)] = 0,
    year_from: int | None = None,
    year_to: int | None = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    *,
    driver: DriverDep,
) -> CitationNetworkResponse:
    """Return a citation subgraph for the frontend citation-network view.

    Args:
        seed_paper_id: Seed paper OpenAlex ID.
        depth: Max traversal depth, between 1 and 3.
        min_citations: Minimum cited-by threshold for included papers.
        year_from: Optional lower publication-year bound.
        year_to: Optional upper publication-year bound.
        limit: Maximum number of nodes returned.
        driver: Shared Neo4j driver dependency.

    Returns:
        Citation network payload with nodes and edges.
    """

    # Variable-length CITES traversal capped at depth and limit; no APOC required.
    cypher: LiteralString = (
        "MATCH (seed:Paper {openalex_id: $seed_paper_id}) "
        "MATCH path = (seed)-[:CITES*0..3]->(paper:Paper) "
        "WHERE length(path) <= $depth "
        "AND coalesce(paper.cited_by_count, 0) >= $min_citations "
        "AND ($year_from IS NULL OR paper.year >= $year_from) "
        "AND ($year_to IS NULL OR paper.year <= $year_to) "
        "WITH DISTINCT paper "
        "ORDER BY paper.cited_by_count DESC "
        "LIMIT $limit "
        "WITH collect(paper) AS papers "
        "UNWIND papers AS p "
        "OPTIONAL MATCH (p)-[:BELONGS_TO]->(f:Field) "
        "WITH papers, collect({"
        "id: p.openalex_id, "
        "title: coalesce(p.title, ''), "
        "year: p.year, "
        "cited_by_count: coalesce(p.cited_by_count, 0), "
        "field: coalesce(f.field_name, p.primary_field_name), "
        "is_retracted: coalesce(p.is_retracted, false)"
        "}) AS nodes "
        "UNWIND papers AS src "
        "MATCH (src)-[:CITES]->(tgt) WHERE tgt IN papers "
        "WITH nodes, collect(DISTINCT {"
        "source: src.openalex_id, "
        "target: tgt.openalex_id"
        "}) AS edges "
        "RETURN nodes, edges"
    )
    params = {
        "seed_paper_id": seed_paper_id,
        "depth": depth,
        "min_citations": min_citations,
        "year_from": year_from,
        "year_to": year_to,
        "limit": limit,
    }

    try:
        rows = run_query(driver=driver, cypher=cypher, parameters=params)
    except Neo4jError as exc:
        logger.error("Citation network query failed", extra={"error": str(exc)})
        raise HTTPException(status_code=502, detail="Neo4j query failed") from exc

    if not rows:
        return CitationNetworkResponse(nodes=[], edges=[])

    payload = rows[0]
    nodes = cast(list[dict[str, object]], payload.get("nodes", []))
    edges = cast(list[dict[str, object]], payload.get("edges", []))
    return CitationNetworkResponse.model_validate({"nodes": nodes, "edges": edges})


@limiter.limit("30/minute")
@router.get("/coauthorship-network", response_model=CoauthorshipNetworkResponse)
def get_coauthorship_network(
    request: Request,
    seed_author_id: str,
    min_collaborations: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    *,
    driver: DriverDep,
) -> CoauthorshipNetworkResponse:
    """Return a co-authorship subgraph for the frontend collaboration view.

    Args:
        seed_author_id: Seed author ID.
        min_collaborations: Minimum edge collaboration count.
        limit: Maximum number of nodes returned.
        driver: Shared Neo4j driver dependency.

    Returns:
        Co-authorship network payload with nodes and edges.
    """

    cypher: LiteralString = (
        "MATCH (seed:Author {author_id: $seed_author_id}) "
        "-[:AUTHORED]->(shared:Paper)<-[:AUTHORED]-(coauthor:Author) "
        "WITH seed, coauthor, count(shared) AS collab_count "
        "WHERE collab_count >= $min_collaborations "
        "ORDER BY collab_count DESC "
        "WITH seed, collect({author: coauthor, collabs: collab_count})[..$limit] AS peers "
        "WITH [seed] + [p IN peers | p.author] AS authors, "
        "[p IN peers | {source: seed.author_id, target: p.author.author_id, "
        "paper_count: p.collabs}] AS raw_edges "
        "UNWIND authors AS a "
        "OPTIONAL MATCH (a)-[:AUTHORED]->(p:Paper) "
        "WITH authors, raw_edges, a, count(p) AS pc "
        "WITH raw_edges, collect({"
        "id: a.author_id, "
        "name: coalesce(a.author_name, ''), "
        "institution: coalesce(a.institution_name, ''), "
        "country: coalesce(a.country, ''), "
        "paper_count: pc"
        "}) AS nodes "
        "RETURN nodes, raw_edges AS edges"
    )
    params = {
        "seed_author_id": seed_author_id,
        "min_collaborations": min_collaborations,
        "limit": limit,
    }

    try:
        rows = run_query(driver=driver, cypher=cypher, parameters=params)
    except Neo4jError as exc:
        logger.error("Coauthorship query failed", extra={"error": str(exc)})
        raise HTTPException(status_code=502, detail="Neo4j query failed") from exc

    if not rows:
        return CoauthorshipNetworkResponse(nodes=[], edges=[])

    payload = rows[0]
    nodes = cast(list[dict[str, object]], payload.get("nodes", []))
    edges = cast(list[dict[str, object]], payload.get("edges", []))
    return CoauthorshipNetworkResponse.model_validate({"nodes": nodes, "edges": edges})


@limiter.limit("30/minute")
@router.get("/contamination-cascade", response_model=ContaminationCascadeResponse)
def get_contamination_cascade(
    request: Request,
    retracted_paper_id: str,
    max_depth: Annotated[int, Query(ge=1, le=3)] = 3,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    *,
    driver: DriverDep,
) -> ContaminationCascadeResponse:
    """Return contamination cascade from a retracted paper.

    Args:
        retracted_paper_id: Retracted paper OpenAlex ID.
        max_depth: Maximum cascade depth between 1 and 3.
        limit: Maximum number of nodes returned.
        driver: Shared Neo4j driver dependency.

    Returns:
        Contamination cascade payload.
    """

    # Variable-length traversal of inbound CITES (papers that cite the retracted
    # root). No APOC required. Depth captured via length(path).
    cypher: LiteralString = (
        "MATCH (root:Paper {openalex_id: $retracted_paper_id}) "
        "WHERE coalesce(root.is_retracted, false) = true "
        "MATCH path = (root)<-[:CITES*0..3]-(paper:Paper) "
        "WHERE length(path) <= $max_depth "
        "WITH root, paper, length(path) AS depth "
        "ORDER BY depth, paper.cited_by_count DESC "
        "LIMIT $limit "
        "WITH root, "
        "collect({"
        "id: paper.openalex_id, "
        "title: coalesce(paper.title, ''), "
        "year: paper.year, "
        "depth: depth, "
        "is_retracted: coalesce(paper.is_retracted, false), "
        "contamination_score: "
        "CASE WHEN depth = 0 THEN 1.0 ELSE 1.0 / toFloat(depth) END"
        "}) AS nodes, "
        "collect(paper) AS papers "
        "UNWIND papers AS child "
        "MATCH (child)-[:CITES]->(parent) WHERE parent IN papers "
        "WITH root, nodes, collect(DISTINCT {"
        "source: parent.openalex_id, "
        "target: child.openalex_id, "
        "depth: 1, "
        "post_retraction: CASE "
        "WHEN root.retraction_date IS NULL OR child.year IS NULL THEN false "
        "ELSE child.year >= date(root.retraction_date).year "
        "END"
        "}) AS edges "
        "RETURN nodes, edges"
    )
    params = {
        "retracted_paper_id": retracted_paper_id,
        "max_depth": max_depth,
        "limit": limit,
    }

    try:
        rows = run_query(driver=driver, cypher=cypher, parameters=params)
    except Neo4jError as exc:
        logger.error("Contamination query failed", extra={"error": str(exc)})
        raise HTTPException(status_code=502, detail="Neo4j query failed") from exc

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Retracted paper not found or not marked as retracted",
        )

    payload = rows[0]
    nodes = cast(list[dict[str, object]], payload.get("nodes", []))
    edges = cast(list[dict[str, object]], payload.get("edges", []))
    return ContaminationCascadeResponse.model_validate(
        {"nodes": nodes, "edges": edges},
    )


@limiter.limit("30/minute")
@router.get("/ai-diffusion", response_model=AIDiffusionResponse)
def get_ai_diffusion(
    request: Request,
    year_from: int,
    year_to: int,
    method: Annotated[Literal["title", "concept"], Query()] = "title",
    *,
    driver: DriverDep,
) -> AIDiffusionResponse:
    """Return field-level AI diffusion graph for Track 1 view.

    Args:
        year_from: Start year for aggregation.
        year_to: End year for aggregation.
        method: AI identification method — 'title' (keyword-based) or
            'concept' (OpenAlex concept-based, broader).
        driver: Shared Neo4j driver dependency.

    Returns:
        AI diffusion graph payload.
    """

    if year_from > year_to:
        raise HTTPException(status_code=400, detail="year_from must be <= year_to")

    cypher: LiteralString = (
        "MATCH (f:Field) "
        "RETURN f.field_id AS id, "
        "coalesce(f.field_name, '') AS name, "
        "coalesce(f.yearly_paper_counts, '{}') AS yearly_papers, "
        "coalesce(f.yearly_ai_paper_counts, '{}') AS yearly_ai_title, "
        "coalesce(f.yearly_ai_concept_counts, '{}') AS yearly_ai_concept, "
        "coalesce(f.paper_count, 0) AS total_papers, "
        "coalesce(f.ai_paper_count, 0) AS total_ai_title, "
        "coalesce(f.ai_concept_count, 0) AS total_ai_concept"
    )

    try:
        rows = run_query(driver=driver, cypher=cypher, parameters={})
    except Neo4jError as exc:
        logger.error("AI diffusion query failed", extra={"error": str(exc)})
        raise HTTPException(status_code=502, detail="Neo4j query failed") from exc

    yearly_ai_key = "yearly_ai_title" if method == "title" else "yearly_ai_concept"
    total_ai_key = "total_ai_title" if method == "title" else "total_ai_concept"

    nodes: list[AIDiffusionNode] = []
    for row in rows:
        yearly_papers: dict[str, int] = json.loads(cast(str, row["yearly_papers"]))
        yearly_ai: dict[str, int] = json.loads(cast(str, row[yearly_ai_key]))

        if yearly_papers:
            total = sum(
                v for k, v in yearly_papers.items() if year_from <= int(k) <= year_to
            )
            ai = sum(v for k, v in yearly_ai.items() if year_from <= int(k) <= year_to)
        else:
            total = cast(int, row["total_papers"])
            ai = cast(int, row[total_ai_key])

        fraction = float(ai) / float(total) if total > 0 else 0.0
        nodes.append(
            AIDiffusionNode(
                id=cast(str, row["id"]),
                name=cast(str, row["name"]),
                total_papers=total,
                ai_papers=ai,
                ai_fraction=round(fraction, 6),
            )
        )

    return AIDiffusionResponse(nodes=nodes, edges=[])


FIELD_COLORS: dict[str, str] = {
    "Computer Science": "#00d4ff",
    "Medicine": "#ff6b6b",
    "Biochemistry, Genetics and Molecular Biology": "#51cf66",
    "Physics and Astronomy": "#ffd43b",
    "Chemistry": "#ff922b",
    "Mathematics": "#cc5de8",
    "Engineering": "#20c997",
    "Psychology": "#f06595",
    "Economics, Econometrics and Finance": "#868e96",
    "Materials Science": "#a9e34b",
    "Social Sciences": "#74b9ff",
    "Agricultural and Biological Sciences": "#6ab04c",
    "Arts and Humanities": "#e17055",
    "Business, Management and Accounting": "#00cec9",
    "Chemical Engineering": "#fd79a8",
    "Decision Sciences": "#636e72",
    "Dentistry": "#dfe6e9",
    "Earth and Planetary Sciences": "#b2bec3",
    "Energy": "#fdcb6e",
    "Environmental Science": "#00b894",
    "Health Professions": "#e84393",
    "Immunology and Microbiology": "#0984e3",
    "Neuroscience": "#6c5ce7",
    "Nursing": "#fab1a0",
    "Pharmacology, Toxicology and Pharmaceutics": "#55efc4",
    "Veterinary": "#81ecec",
}


@limiter.limit("60/minute")
@router.get("/stats", response_model=GraphStatsResponse)
def get_graph_stats(
    request: Request,
    *,
    driver: DriverDep,
) -> GraphStatsResponse:
    """Return graph summary statistics for dashboard metadata.

    Args:
        driver: Shared Neo4j driver dependency.

    Returns:
        Graph-level summary counts including field breakdown.
    """

    counts_cypher: LiteralString = (
        "CALL () { MATCH (p:Paper) RETURN count(p) AS total_papers } "
        "CALL () { MATCH (a:Author) RETURN count(a) AS total_authors } "
        "CALL () { MATCH (f:Field) RETURN count(f) AS total_fields } "
        "CALL () { MATCH ()-[r:CITES]->() RETURN count(r) AS total_citations } "
        "CALL () { MATCH (p:Paper) WHERE p.is_retracted = true "
        "RETURN count(p) AS total_retracted } "
        "RETURN total_papers, total_authors, total_fields, "
        "total_citations, total_retracted"
    )

    fields_cypher: LiteralString = (
        "MATCH (f:Field) "
        "RETURN f.field_name AS name, "
        "coalesce(f.paper_count, 0) AS paper_count "
        "ORDER BY paper_count DESC"
    )

    yearly_cypher: LiteralString = (
        "OPTIONAL MATCH (g:GlobalStats {id: 'singleton'}) "
        "RETURN coalesce(g.yearly_publications, '{}') AS yearly_json, "
        "coalesce(g.ai_concept_papers, 0) AS ai_concept_papers"
    )

    try:
        counts_rows = run_query(
            driver=driver,
            cypher=counts_cypher,
            parameters={},
        )
        fields_rows = run_query(
            driver=driver,
            cypher=fields_cypher,
            parameters={},
        )
        yearly_rows = run_query(
            driver=driver,
            cypher=yearly_cypher,
            parameters={},
        )
    except Neo4jError as exc:
        logger.error("Graph stats query failed", extra={"error": str(exc)})
        raise HTTPException(status_code=502, detail="Neo4j query failed") from exc

    if not counts_rows:
        raise HTTPException(status_code=500, detail="Stats query returned no rows")

    payload = counts_rows[0]
    fields = [
        FieldStatResponse(
            name=cast(str, row["name"]),
            paper_count=cast(int, row["paper_count"]),
            color=FIELD_COLORS.get(cast(str, row["name"]), "#636e72"),
        )
        for row in fields_rows
    ]

    yearly_pubs: list[YearlyCount] = []
    ai_concept_total = 0
    if yearly_rows:
        yearly_data: dict[str, int] = json.loads(
            cast(str, yearly_rows[0]["yearly_json"])
        )
        ai_concept_total = cast(int, yearly_rows[0]["ai_concept_papers"])
        yearly_pubs = sorted(
            [YearlyCount(year=int(y), count=c) for y, c in yearly_data.items()],
            key=lambda x: x.year,
        )

    return GraphStatsResponse(
        total_papers=cast(int, payload["total_papers"]),
        total_authors=cast(int, payload["total_authors"]),
        total_citations=cast(int, payload["total_citations"]),
        total_fields=cast(int, payload["total_fields"]),
        total_retracted=cast(int, payload["total_retracted"]),
        ai_related_papers=845284,
        ai_concept_papers=ai_concept_total,
        fields=fields,
        yearly_publications=yearly_pubs,
    )


@router.get("/retraction-stats", response_model=RetractionStatsResponse)
def get_retraction_stats() -> RetractionStatsResponse:
    """Return aggregated retraction statistics for the frontend analysis view."""

    if not RETRACTION_CITATION_ANALYSIS_PATH.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Data file not found: {RETRACTION_CITATION_ANALYSIS_PATH.name}",
        )
    if not FIELD_ANALYSIS_PATH.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Data file not found: {FIELD_ANALYSIS_PATH.name}",
        )

    try:
        retraction_analysis = json.loads(RETRACTION_CITATION_ANALYSIS_PATH.read_text())
        field_analysis = json.loads(FIELD_ANALYSIS_PATH.read_text())
    except Exception as exc:
        logger.error("Failed to load retraction stats JSON", extra={"error": str(exc)})
        raise HTTPException(
            status_code=500, detail="Failed to load retraction stats"
        ) from exc

    pre_post = cast(
        dict[str, object], retraction_analysis.get("pre_post_distribution", {})
    )
    citation_persistence = cast(
        list[dict[str, object]],
        retraction_analysis.get("citation_persistence", []),
    )
    field_patterns = cast(
        list[dict[str, object]],
        retraction_analysis.get("field_patterns", []),
    )
    zombie_papers = cast(
        list[dict[str, object]],
        retraction_analysis.get("zombie_papers", []),
    )

    retraction_rate_field_summary = cast(
        list[dict[str, object]],
        field_analysis.get("methods", {})
        .get("title", {})
        .get("analysis_5_retraction_rate", {})
        .get("field_summary", []),
    )

    top_fields = sorted(
        field_patterns,
        key=lambda item: float(cast(float, item.get("rate_per_million", 0.0))),
        reverse=True,
    )[:10]
    top_zombies = sorted(
        zombie_papers,
        key=lambda item: int(cast(int, item.get("post_retraction_citations", 0))),
        reverse=True,
    )[:10]

    return RetractionStatsResponse(
        pre_post_distribution=RetractionPrePostDistribution.model_validate(pre_post),
        citation_persistence=[
            CitationPersistencePoint.model_validate(point)
            for point in citation_persistence
        ],
        top_fields=[
            RetractionFieldPattern.model_validate(field) for field in top_fields
        ],
        top_zombies=[ZombiePaper.model_validate(zombie) for zombie in top_zombies],
        retraction_rate_by_field=[
            RetractionRateFieldSummary.model_validate(item)
            for item in retraction_rate_field_summary
        ],
    )


class AuthorPublication(BaseModel):
    """A publication in author detail response."""

    id: str
    title: str
    year: int | None
    cited_by_count: int
    is_retracted: bool
    field: str | None


class CoauthorSummary(BaseModel):
    """A co-author summary in author detail response."""

    id: str
    name: str
    shared_papers: int


class AuthorDetailResponse(BaseModel):
    """Author profile with publications and co-authors."""

    id: str
    name: str
    openalex_id: str | None
    institution: str | None
    country: str | None
    works_count: int
    cited_by_count: int
    h_index: int | None
    publications: list[AuthorPublication]
    coauthors: list[CoauthorSummary]


class PaperDetailAuthor(BaseModel):
    """An author entry in the paper detail response."""

    id: str
    name: str
    institution: str | None
    country: str | None


class PaperDetailReference(BaseModel):
    """A referenced or citing paper in the paper detail response."""

    id: str
    title: str
    year: int | None
    cited_by_count: int
    field: str | None
    is_retracted: bool


class PaperDetailResponse(BaseModel):
    """Full paper metadata for the paper detail page."""

    id: str
    title: str
    year: int | None
    doi: str | None
    cited_by_count: int
    field: str | None
    is_retracted: bool
    abstract: str | None
    authors: list[PaperDetailAuthor]
    references: list[PaperDetailReference]
    citers: list[PaperDetailReference]
    references_count: int
    citers_count: int


class CitationGraphNodeItem(BaseModel):
    """A node in the citation graph."""

    id: str
    title: str
    year: int | None
    cited_by_count: int
    field: str | None
    is_retracted: bool
    is_focal: bool


class CitationGraphEdgeItem(BaseModel):
    """An edge in the citation graph."""

    source: str
    target: str


class CitationGraphResponse(BaseModel):
    """Citation graph for a focal paper with its citing and cited papers."""

    focal_paper: CitationGraphNodeItem
    nodes: list[CitationGraphNodeItem]
    edges: list[CitationGraphEdgeItem]


@limiter.limit("30/minute")
@router.get("/author/{author_id}", response_model=AuthorDetailResponse)
def get_author_detail(
    request: Request,
    author_id: str,
    *,
    driver: DriverDep,
) -> AuthorDetailResponse:
    """Return author profile with recent publications and top co-authors.

    Args:
        author_id: Author identifier (author_id field in Neo4j).
        driver: Shared Neo4j driver dependency.

    Returns:
        Author profile with publications list and co-authors.
    """

    author_cypher: LiteralString = (
        "MATCH (a:Author {author_id: $author_id}) "
        "OPTIONAL MATCH (a)-[:AUTHORED]->(p:Paper) "
        "WITH a, count(DISTINCT p) AS works_count, "
        "sum(coalesce(p.cited_by_count, 0)) AS total_citations "
        "RETURN a.author_id AS id, "
        "coalesce(a.author_name, '') AS name, "
        "a.openalex_id AS openalex_id, "
        "a.institution_name AS institution, "
        "a.country AS country, "
        "works_count, "
        "total_citations AS cited_by_count, "
        "a.h_index AS h_index"
    )

    pubs_cypher: LiteralString = (
        "MATCH (a:Author {author_id: $author_id})-[:AUTHORED]->(p:Paper) "
        "OPTIONAL MATCH (p)-[:BELONGS_TO]->(f:Field) "
        "RETURN p.openalex_id AS id, "
        "coalesce(p.title, '') AS title, "
        "p.year AS year, "
        "coalesce(p.cited_by_count, 0) AS cited_by_count, "
        "coalesce(p.is_retracted, false) AS is_retracted, "
        "coalesce(f.field_name, p.primary_field_name) AS field "
        "ORDER BY p.year DESC, p.cited_by_count DESC "
        "LIMIT 20"
    )

    coauthors_cypher: LiteralString = (
        "MATCH (a:Author {author_id: $author_id})-[:AUTHORED]->(p:Paper) "
        "<-[:AUTHORED]-(co:Author) "
        "WHERE co <> a "
        "WITH co, count(DISTINCT p) AS shared_papers "
        "ORDER BY shared_papers DESC "
        "LIMIT 10 "
        "RETURN co.author_id AS id, "
        "coalesce(co.author_name, '') AS name, "
        "shared_papers"
    )

    params = {"author_id": author_id}

    try:
        author_rows = run_query(driver=driver, cypher=author_cypher, parameters=params)
        pubs_rows = run_query(driver=driver, cypher=pubs_cypher, parameters=params)
        coauthors_rows = run_query(
            driver=driver, cypher=coauthors_cypher, parameters=params
        )
    except Neo4jError as exc:
        logger.error("Author detail query failed", extra={"error": str(exc)})
        raise HTTPException(status_code=502, detail="Neo4j query failed") from exc

    if not author_rows:
        raise HTTPException(status_code=404, detail="Author not found")

    author_data = cast(dict[str, object], author_rows[0])
    publications = [
        AuthorPublication.model_validate(cast(dict[str, object], row))
        for row in pubs_rows
    ]
    coauthors = [
        CoauthorSummary.model_validate(cast(dict[str, object], row))
        for row in coauthors_rows
    ]

    return AuthorDetailResponse(
        id=cast(str, author_data["id"]),
        name=cast(str, author_data["name"]),
        openalex_id=cast(str | None, author_data.get("openalex_id")),
        institution=cast(str | None, author_data.get("institution")),
        country=cast(str | None, author_data.get("country")),
        works_count=cast(int, author_data["works_count"]),
        cited_by_count=cast(int, author_data["cited_by_count"]),
        h_index=cast(int | None, author_data.get("h_index")),
        publications=publications,
        coauthors=coauthors,
    )


@limiter.limit("30/minute")
@router.get("/citation-graph/{paper_id}", response_model=CitationGraphResponse)
def get_citation_graph(
    request: Request,
    paper_id: str,
    depth: Annotated[int, Query(ge=1, le=2)] = 1,
    limit: Annotated[int, Query(ge=10, le=200)] = 50,
    *,
    driver: DriverDep,
) -> CitationGraphResponse:
    """Return citation graph for a focal paper.

    Args:
        paper_id: Paper OpenAlex ID.
        depth: Traversal depth (1 or 2 hops).
        limit: Maximum number of citing/cited papers to return.
        driver: Shared Neo4j driver dependency.

    Returns:
        Citation graph with focal paper, citing papers, cited papers, and edges.
    """

    focal_cypher: LiteralString = (
        "MATCH (p:Paper {openalex_id: $paper_id}) "
        "OPTIONAL MATCH (p)-[:BELONGS_TO]->(f:Field) "
        "RETURN p.openalex_id AS id, "
        "coalesce(p.title, '') AS title, "
        "p.year AS year, "
        "coalesce(p.cited_by_count, 0) AS cited_by_count, "
        "coalesce(f.field_name, p.primary_field_name) AS field, "
        "coalesce(p.is_retracted, false) AS is_retracted"
    )

    # NOTE: For pop papers (e.g. "Attention Is All You Need", 100K+ citers),
    # a naive `ORDER BY citing.cited_by_count DESC LIMIT N` requires materialising
    # every citing paper and then sorting them — prohibitively slow under Neo4j
    # without a cited_by_count range index. We bound the scan to scan_limit (5000)
    # rows; for very large citer sets this returns an approximation of top-N
    # rather than the global top-N. In exchange, response time stays under 1 s.
    citing_cypher: LiteralString = (
        "MATCH (p:Paper {openalex_id: $paper_id})<-[:CITES]-(citing:Paper) "
        "WITH citing LIMIT $scan_limit "
        "OPTIONAL MATCH (citing)-[:BELONGS_TO]->(f:Field) "
        "WITH citing, f "
        "ORDER BY citing.cited_by_count DESC "
        "LIMIT $limit "
        "RETURN citing.openalex_id AS id, "
        "coalesce(citing.title, '') AS title, "
        "citing.year AS year, "
        "coalesce(citing.cited_by_count, 0) AS cited_by_count, "
        "coalesce(f.field_name, citing.primary_field_name) AS field, "
        "coalesce(citing.is_retracted, false) AS is_retracted"
    )

    cited_cypher: LiteralString = (
        "MATCH (p:Paper {openalex_id: $paper_id})-[:CITES]->(cited:Paper) "
        "WITH cited LIMIT $scan_limit "
        "OPTIONAL MATCH (cited)-[:BELONGS_TO]->(f:Field) "
        "WITH cited, f "
        "ORDER BY cited.cited_by_count DESC "
        "LIMIT $limit "
        "RETURN cited.openalex_id AS id, "
        "coalesce(cited.title, '') AS title, "
        "cited.year AS year, "
        "coalesce(cited.cited_by_count, 0) AS cited_by_count, "
        "coalesce(f.field_name, cited.primary_field_name) AS field, "
        "coalesce(cited.is_retracted, false) AS is_retracted"
    )

    # CRITICAL: keep `focal` in every WITH clause; otherwise it becomes
    # unbound after the first WITH and the second MATCH expands to ALL Papers,
    # returning ~400k spurious edges for hot focal papers.
    edges_cypher: LiteralString = (
        "MATCH (focal:Paper {openalex_id: $paper_id}) "
        "OPTIONAL MATCH (focal)<-[:CITES]-(citing:Paper) "
        "WHERE citing.openalex_id IN $node_ids "
        "WITH focal, collect(DISTINCT {source: citing.openalex_id, target: focal.openalex_id}) AS incoming "
        "OPTIONAL MATCH (focal)-[:CITES]->(cited:Paper) "
        "WHERE cited.openalex_id IN $node_ids "
        "WITH incoming, collect(DISTINCT {source: focal.openalex_id, target: cited.openalex_id}) AS outgoing "
        "RETURN incoming + outgoing AS edges"
    )

    params = {"paper_id": paper_id, "limit": limit, "scan_limit": 5000}

    try:
        focal_rows = run_query(driver=driver, cypher=focal_cypher, parameters=params)
        citing_rows = run_query(driver=driver, cypher=citing_cypher, parameters=params)
        cited_rows = run_query(driver=driver, cypher=cited_cypher, parameters=params)
    except Neo4jError as exc:
        logger.error(
            "Citation graph query failed",
            extra={"error": str(exc), "paper_id": paper_id, "depth": depth, "limit": limit},
        )
        raise HTTPException(status_code=502, detail=f"Neo4j query failed: {str(exc)[:120]}") from exc
    except Exception as exc:
        logger.error(
            "Citation graph unexpected failure",
            extra={"error": str(exc), "paper_id": paper_id, "type": type(exc).__name__},
        )
        raise HTTPException(status_code=500, detail=f"Server error: {type(exc).__name__}: {str(exc)[:120]}") from exc

    if not focal_rows:
        raise HTTPException(status_code=404, detail="Paper not found")

    focal_data = cast(dict[str, object], focal_rows[0])
    focal_node = CitationGraphNodeItem(
        id=cast(str, focal_data["id"]),
        title=cast(str, focal_data["title"]),
        year=cast(int | None, focal_data.get("year")),
        cited_by_count=cast(int, focal_data["cited_by_count"]),
        field=cast(str | None, focal_data.get("field")),
        is_retracted=cast(bool, focal_data["is_retracted"]),
        is_focal=True,
    )

    citing_nodes = [
        CitationGraphNodeItem(
            id=cast(str, row["id"]),
            title=cast(str, row["title"]),
            year=cast(int | None, row.get("year")),
            cited_by_count=cast(int, row["cited_by_count"]),
            field=cast(str | None, row.get("field")),
            is_retracted=cast(bool, row["is_retracted"]),
            is_focal=False,
        )
        for row in citing_rows
    ]

    cited_nodes = [
        CitationGraphNodeItem(
            id=cast(str, row["id"]),
            title=cast(str, row["title"]),
            year=cast(int | None, row.get("year")),
            cited_by_count=cast(int, row["cited_by_count"]),
            field=cast(str | None, row.get("field")),
            is_retracted=cast(bool, row["is_retracted"]),
            is_focal=False,
        )
        for row in cited_rows
    ]
    all_nodes = [focal_node, *citing_nodes, *cited_nodes]
    node_ids = [n.id for n in all_nodes]

    # Fetch edges
    try:
        edges_rows = run_query(
            driver=driver,
            cypher=edges_cypher,
            parameters={"paper_id": paper_id, "node_ids": node_ids},
        )
    except Neo4jError as exc:
        logger.error("Citation graph edges query failed", extra={"error": str(exc)})
        raise HTTPException(status_code=502, detail="Neo4j query failed") from exc

    edges: list[CitationGraphEdgeItem] = []
    if edges_rows:
        raw_edges = cast(list[dict[str, object]], edges_rows[0].get("edges", []))
        edges = [CitationGraphEdgeItem.model_validate(e) for e in raw_edges]

    return CitationGraphResponse(
        focal_paper=focal_node,
        nodes=all_nodes,
        edges=edges,
    )


@limiter.limit("30/minute")
@router.get("/paper/{paper_id}", response_model=PaperDetailResponse)
def get_paper_detail(
    request: Request,
    paper_id: str,
    *,
    driver: DriverDep,
) -> PaperDetailResponse:
    """Return full paper metadata with authors, references, and citers.

    Args:
        paper_id: Paper OpenAlex ID.
        driver: Shared Neo4j driver dependency.

    Returns:
        Paper profile with authors, references, and citing papers.
    """

    paper_cypher: LiteralString = (
        "MATCH (p:Paper {openalex_id: $paper_id}) "
        "OPTIONAL MATCH (p)-[:BELONGS_TO]->(f:Field) "
        "RETURN p.openalex_id AS id, "
        "coalesce(p.title, '') AS title, "
        "p.year AS year, "
        "p.doi AS doi, "
        "coalesce(p.cited_by_count, 0) AS cited_by_count, "
        "coalesce(f.field_name, p.primary_field_name) AS field, "
        "coalesce(p.is_retracted, false) AS is_retracted, "
        "p.abstract AS abstract"
    )

    authors_cypher: LiteralString = (
        "MATCH (p:Paper {openalex_id: $paper_id})<-[:AUTHORED]-(a:Author) "
        "RETURN a.author_id AS id, "
        "coalesce(a.author_name, '') AS name, "
        "a.institution_name AS institution, "
        "a.country AS country "
        "ORDER BY name"
    )

    # See note on citation_graph: bound scan size to 5000 to keep response < 1 s
    # for hot papers with 100K+ citers.
    refs_cypher: LiteralString = (
        "MATCH (p:Paper {openalex_id: $paper_id})-[:CITES]->(ref:Paper) "
        "WITH ref LIMIT 5000 "
        "OPTIONAL MATCH (ref)-[:BELONGS_TO]->(f:Field) "
        "WITH ref, f "
        "ORDER BY ref.cited_by_count DESC "
        "LIMIT 50 "
        "RETURN ref.openalex_id AS id, "
        "coalesce(ref.title, '') AS title, "
        "ref.year AS year, "
        "coalesce(ref.cited_by_count, 0) AS cited_by_count, "
        "coalesce(f.field_name, ref.primary_field_name) AS field, "
        "coalesce(ref.is_retracted, false) AS is_retracted"
    )

    citers_cypher: LiteralString = (
        "MATCH (p:Paper {openalex_id: $paper_id})<-[:CITES]-(citer:Paper) "
        "WITH citer LIMIT 5000 "
        "OPTIONAL MATCH (citer)-[:BELONGS_TO]->(f:Field) "
        "WITH citer, f "
        "ORDER BY citer.cited_by_count DESC "
        "LIMIT 50 "
        "RETURN citer.openalex_id AS id, "
        "coalesce(citer.title, '') AS title, "
        "citer.year AS year, "
        "coalesce(citer.cited_by_count, 0) AS cited_by_count, "
        "coalesce(f.field_name, citer.primary_field_name) AS field, "
        "coalesce(citer.is_retracted, false) AS is_retracted"
    )

    # Counts capped at 100k to avoid full traversal on hot papers.
    refs_count_cypher: LiteralString = (
        "MATCH (p:Paper {openalex_id: $paper_id})-[:CITES]->(ref:Paper) "
        "WITH ref LIMIT 100000 "
        "RETURN count(*) AS cnt"
    )

    citers_count_cypher: LiteralString = (
        "MATCH (p:Paper {openalex_id: $paper_id})<-[:CITES]-(citer:Paper) "
        "WITH citer LIMIT 100000 "
        "RETURN count(*) AS cnt"
    )

    params = {"paper_id": paper_id}

    try:
        paper_rows = run_query(driver=driver, cypher=paper_cypher, parameters=params)
        author_rows = run_query(driver=driver, cypher=authors_cypher, parameters=params)
        refs_rows = run_query(driver=driver, cypher=refs_cypher, parameters=params)
        citers_rows = run_query(driver=driver, cypher=citers_cypher, parameters=params)
        refs_count_rows = run_query(
            driver=driver, cypher=refs_count_cypher, parameters=params
        )
        citers_count_rows = run_query(
            driver=driver, cypher=citers_count_cypher, parameters=params
        )
    except Neo4jError as exc:
        logger.error("Paper detail query failed", extra={"error": str(exc)})
        raise HTTPException(status_code=502, detail="Neo4j query failed") from exc

    if not paper_rows:
        raise HTTPException(status_code=404, detail="Paper not found")

    paper_data = cast(dict[str, object], paper_rows[0])
    authors = [
        PaperDetailAuthor.model_validate(cast(dict[str, object], row))
        for row in author_rows
    ]
    references = [
        PaperDetailReference.model_validate(cast(dict[str, object], row))
        for row in refs_rows
    ]
    citers = [
        PaperDetailReference.model_validate(cast(dict[str, object], row))
        for row in citers_rows
    ]

    refs_count = cast(int, refs_count_rows[0]["cnt"]) if refs_count_rows else 0
    citers_count = cast(int, citers_count_rows[0]["cnt"]) if citers_count_rows else 0

    return PaperDetailResponse(
        id=cast(str, paper_data["id"]),
        title=cast(str, paper_data["title"]),
        year=cast(int | None, paper_data.get("year")),
        doi=cast(str | None, paper_data.get("doi")),
        cited_by_count=cast(int, paper_data["cited_by_count"]),
        field=cast(str | None, paper_data.get("field")),
        is_retracted=cast(bool, paper_data["is_retracted"]),
        abstract=cast(str | None, paper_data.get("abstract")),
        authors=authors,
        references=references,
        citers=citers,
        references_count=refs_count,
        citers_count=citers_count,
    )
