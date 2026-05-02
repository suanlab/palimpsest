from __future__ import annotations

import logging
from typing import Annotated, LiteralString, cast

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from neo4j import Driver
from neo4j.exceptions import Neo4jError
from pydantic import BaseModel

from palimpsest.api.dependencies import get_neo4j_driver, limiter, run_query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])

MAX_LIMIT = 500
MAX_QUERY_LENGTH = 500
DEFAULT_LIMIT = 100
DriverDep = Annotated[Driver, Depends(get_neo4j_driver)]


class SearchResultItem(BaseModel):
    """Unified search result item for papers and authors."""

    id: str
    title: str
    type: str
    year: int | None = None
    cited_by_count: int | None = None
    is_retracted: bool | None = None
    field: str | None = None


class SearchResultResponse(BaseModel):
    """Wrapper for search results matching frontend SearchResponse type."""

    results: list[SearchResultItem]
    total: int


class AutocompleteSuggestion(BaseModel):
    """Single autocomplete suggestion."""

    type: str
    id: str
    text: str


@limiter.limit("60/minute")
@router.get("/papers", response_model=SearchResultResponse)
def search_papers(
    request: Request,
    q: Annotated[str, Query(max_length=MAX_QUERY_LENGTH)],
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
    year_from: int | None = None,
    year_to: int | None = None,
    field: str | None = None,
    retracted_only: bool = False,
    *,
    driver: DriverDep,
) -> SearchResultResponse:
    """Search papers by title using fulltext index.

    Args:
        q: Search query string.
        limit: Maximum number of returned rows.
        offset: Pagination offset.
        year_from: Filter papers from this year (inclusive).
        year_to: Filter papers up to this year (inclusive).
        field: Filter by field name.
        retracted_only: If True, only return retracted papers.
        driver: Shared Neo4j driver dependency.

    Returns:
        Wrapped search results with total count.
    """
    normalized_query = q.strip()
    if not normalized_query:
        return SearchResultResponse(results=[], total=0)

    lucene_query = normalized_query.replace('"', '\\"')
    candidate_limit = offset + limit + 100

    # Build dynamic WHERE clauses for filters
    where_parts: list[str] = []
    if year_from is not None:
        where_parts.append("p.year >= $year_from")
    if year_to is not None:
        where_parts.append("p.year <= $year_to")
    if retracted_only:
        where_parts.append("p.is_retracted = true")

    where_clause = ""
    if where_parts:
        where_clause = "WHERE " + " AND ".join(where_parts)

    # Field filter requires additional join
    field_match = ""
    if field:
        field_match = (
            "MATCH (p)-[:BELONGS_TO]->(ff:Field) "
            "WHERE ff.field_name = $field "
            "WITH p, score "
        )

    cypher: LiteralString = cast(
        LiteralString,
        "CALL db.index.fulltext.queryNodes('paper_title_ft', $q) "
        "YIELD node AS p, score "
        + field_match
        + "WITH p, score "
        + where_clause
        + " ORDER BY score DESC "
        "SKIP $offset LIMIT $limit "
        "OPTIONAL MATCH (p)-[:BELONGS_TO]->(f:Field) "
        "RETURN {"
        "id: p.openalex_id, "
        "title: coalesce(p.title, ''), "
        "year: p.year, "
        "cited_by_count: coalesce(p.cited_by_count, 0), "
        "is_retracted: coalesce(p.is_retracted, false), "
        "field: coalesce(f.field_name, p.primary_field_name)"
        "} AS paper",
    )

    params: dict[str, object] = {
        "q": lucene_query,
        "limit": limit,
        "offset": offset,
        "candidate_limit": candidate_limit,
    }
    if year_from is not None:
        params["year_from"] = year_from
    if year_to is not None:
        params["year_to"] = year_to
    if field:
        params["field"] = field

    try:
        rows = run_query(driver=driver, cypher=cypher, parameters=params)
    except Neo4jError as exc:
        logger.error("Paper search failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=502, detail="Neo4j query failed") from exc
    except Exception as exc:
        logger.error("Paper search unexpected error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed") from exc

    items: list[SearchResultItem] = []
    for row in rows:
        if "paper" not in row:
            continue
        data = cast(dict[str, object], row["paper"])
        items.append(
            SearchResultItem(
                id=str(data.get("id", "")),
                title=str(data.get("title", "")),
                type="paper",
                year=data.get("year"),
                cited_by_count=data.get("cited_by_count"),
                is_retracted=data.get("is_retracted"),
                field=data.get("field"),
            )
        )
    return SearchResultResponse(results=items, total=len(items))


@limiter.limit("60/minute")
@router.get("/authors", response_model=SearchResultResponse)
def search_authors(
    request: Request,
    q: Annotated[str, Query(max_length=MAX_QUERY_LENGTH)],
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    *,
    driver: DriverDep,
) -> SearchResultResponse:
    """Search authors by name using fulltext index.

    Args:
        q: Search query string.
        limit: Maximum number of returned rows.
        driver: Shared Neo4j driver dependency.

    Returns:
        Wrapped search results with total count.
    """
    normalized_query = q.strip()
    if not normalized_query:
        return SearchResultResponse(results=[], total=0)

    cypher: LiteralString = (
        "CALL db.index.fulltext.queryNodes('author_name_ft', $q) "
        "YIELD node AS a, score "
        "WITH a, score "
        "ORDER BY score DESC "
        "LIMIT $limit "
        "OPTIONAL MATCH (a)-[:AUTHORED]->(p:Paper) "
        "WITH a, count(DISTINCT p) AS paper_count "
        "RETURN {"
        "id: a.author_id, "
        "name: coalesce(a.author_name, ''), "
        "institution: coalesce(a.institution_name, ''), "
        "country: coalesce(a.country, ''), "
        "paper_count: paper_count"
        "} AS author"
    )
    params = {
        "q": normalized_query,
        "limit": limit,
    }

    try:
        rows = run_query(driver=driver, cypher=cypher, parameters=params)
    except Neo4jError as exc:
        logger.error("Author search failed", extra={"error": str(exc)})
        raise HTTPException(status_code=502, detail="Neo4j query failed") from exc

    items: list[SearchResultItem] = []
    for row in rows:
        if "author" not in row:
            continue
        data = cast(dict[str, object], row["author"])
        items.append(
            SearchResultItem(
                id=str(data.get("id", "")),
                title=str(data.get("name", "")),
                type="author",
                cited_by_count=data.get("paper_count"),
            )
        )
    return SearchResultResponse(results=items, total=len(items))


@limiter.limit("120/minute")
@router.get("/autocomplete", response_model=list[AutocompleteSuggestion])
def autocomplete(
    request: Request,
    q: Annotated[str, Query(min_length=2, max_length=MAX_QUERY_LENGTH)],
    limit: Annotated[int, Query(ge=1, le=20)] = 8,
    *,
    driver: DriverDep,
) -> list[AutocompleteSuggestion]:
    """Autocomplete suggestions combining papers and authors.

    Args:
        q: Search query string (minimum 2 characters).
        limit: Maximum number of suggestions to return.
        driver: Shared Neo4j driver dependency.

    Returns:
        List of autocomplete suggestions with type, id, and text.
    """
    normalized_query = q.strip()
    if not normalized_query:
        return []

    # Use wildcard prefix for prefix matching
    lucene_query = f"{normalized_query.replace('"', '\\"')}*"
    per_type_limit = limit

    suggestions: list[AutocompleteSuggestion] = []

    # Query paper titles
    paper_cypher: LiteralString = (
        "CALL db.index.fulltext.queryNodes('paper_title_ft', $q, "
        "{limit: $limit}) "
        "YIELD node AS p, score "
        "WITH p, score "
        "ORDER BY score DESC "
        "LIMIT $limit "
        "RETURN {type: 'paper', id: p.openalex_id, "
        "text: coalesce(p.title, '')} AS suggestion"
    )

    try:
        paper_rows = run_query(
            driver=driver,
            cypher=paper_cypher,
            parameters={"q": lucene_query, "limit": per_type_limit},
        )
        for row in paper_rows:
            if "suggestion" in row:
                data = cast(dict[str, object], row["suggestion"])
                suggestions.append(AutocompleteSuggestion.model_validate(data))
    except Neo4jError as exc:
        logger.error("Paper autocomplete failed", extra={"error": str(exc)})

    # Query author names
    author_cypher: LiteralString = (
        "CALL db.index.fulltext.queryNodes('author_name_ft', $q, "
        "{limit: $limit}) "
        "YIELD node AS a, score "
        "WITH a, score "
        "ORDER BY score DESC "
        "LIMIT $limit "
        "RETURN {type: 'author', id: a.author_id, "
        "text: coalesce(a.author_name, '')} AS suggestion"
    )

    try:
        author_rows = run_query(
            driver=driver,
            cypher=author_cypher,
            parameters={"q": lucene_query, "limit": per_type_limit},
        )
        for row in author_rows:
            if "suggestion" in row:
                data = cast(dict[str, object], row["suggestion"])
                suggestions.append(AutocompleteSuggestion.model_validate(data))
    except Neo4jError as exc:
        logger.error("Author autocomplete failed", extra={"error": str(exc)})

    # Return top suggestions by type priority (papers first, then authors)
    return suggestions[:limit]
