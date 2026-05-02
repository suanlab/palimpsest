<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# AGENTS.md — src/palimpsest/data/

**Scope**: External API clients for scholarly data acquisition.

## Overview

Unified interface to OpenAlex and Semantic Scholar APIs. All clients implement caching, rate limiting, and structured error handling.

## Files

| File | Purpose |
|------|---------|
| `openalex.py` | OpenAlex API wrapper (`pyalex`-based) |
| `semantic_scholar.py` | Semantic Scholar Graph API client |
| `retraction_watch.py` | Retraction Watch CSV loader |
| `__init__.py` | Module exports |

## Key Abstractions

### OpenAlexClient
- Wraps `pyalex` with project-specific error handling
- Methods: `get_works()`, `get_work()`, `get_authors()`, `get_cited_by()`, `get_references()`
- Automatic caching via `ResponseCache`
- Raises: `APIError`, `RateLimitError`

### SemanticScholarClient
- Direct `httpx` client with retry/backoff
- Methods: `get_paper()`, `batch_get_papers()`, `get_citations_with_context()`
- Batch endpoint supports 500 papers/request
- Raises: `APIError`, `DataValidationError`, `RateLimitError`

### RetractionWatchLoader
- Downloads CSV from GitLab source
- Methods: `load()`, `get_retracted_dois()`, `get_retracted_pmids()`
- Maps DOIs to OpenAlex IDs via client

## Conventions (This Module)

- All clients take optional `api_key` param, fall back to `settings`
- Cache keys: `{source}:{entity}:{id}` (e.g., `openalex:work:W123`)
- Pagination: OpenAlex uses cursor pagination, S2 uses batching
- Timeouts: 30s default, 60s for large downloads

## Error Handling Pattern

```python
try:
    works = client.get_works(filters={"author.id": aid})
except RateLimitError:
    # Back off and retry
except APIError as e:
    logger.error("Failed to fetch", extra={"error": e.details})
    raise
```
