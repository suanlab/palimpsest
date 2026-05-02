<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# routes

## Purpose
FastAPI route handlers for graph queries, search, and data export. Each file maps to an API prefix.

## Key Files

| File | Description |
|------|-------------|
| `graph.py` | Graph query endpoints (`/api/graph/citation-network`, `/api/graph/author-network`) — CitationNode/AuthorNode dataclasses, Neo4j Cypher queries, max 5000 nodes |
| `search.py` | Search endpoints (`/api/search/papers`, `/api/search/authors`) — SearchResultItem dataclass, Neo4j full-text search, max 500 results |
| `export.py` | Export endpoints (`/api/export/csv`, `/api/export/json`) — serves preprocessed parquet/JSON/CSV from `data/processed/` |
| `__init__.py` | Route exports |

## For AI Agents

### Working In This Directory
- Each route file is mounted with a prefix in `app.py` (graph → `/api/graph`, search → `/api/search`, export → `/api/export`)
- Neo4j driver injected via `dependencies.get_neo4j_driver`
- Rate limiting via `@limiter.limit()` decorator on each endpoint
- Enforce max limits: graph endpoints cap at 5000 nodes, search at 500 results
- Response models use Pydantic dataclasses

### Testing Requirements
- Test with mock Neo4j driver (don't require running database)
- Verify rate limit headers in responses
- Test limit enforcement and edge cases (empty results, invalid queries)

### Common Patterns
```python
@router.get("/citation-network")
@limiter.limit("60/minute")
async def get_citation_network(
    request: Request,
    seed_id: str,
    depth: int = 1,
    limit: int = 100,
    driver: AsyncDriver = Depends(get_neo4j_driver),
) -> GraphResponse:
    ...
```

## Dependencies

### Internal
- `../dependencies.py` — Neo4j driver, rate limiter injection
- `../app.py` — Mounts these routers

### External
- `fastapi` — Router, Request, Depends
- `neo4j` — AsyncDriver for Cypher queries
- `slowapi` — Rate limiting

<!-- MANUAL: -->
