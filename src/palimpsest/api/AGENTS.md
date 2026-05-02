<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# AGENTS.md — src/palimpsest/api/

**Scope**: FastAPI REST server for bibliographic graph exploration.

## Overview

Provides HTTP endpoints for querying citation networks, author metrics, and graph exports. Integrates with Neo4j for persistent graph storage.

## Files

| File | Purpose |
|------|---------|
| `app.py` | FastAPI application factory |
| `dependencies.py` | Dependency injection (Neo4j driver, rate limiter) |
| `routes/graph.py` | Graph query endpoints |
| `routes/search.py` | Paper/author search endpoints |
| `routes/export.py` | Data export endpoints |
| `routes/__init__.py` | Route exports |

## Architecture

```
HTTP Request → FastAPI → Middleware → Router → Neo4j Driver → Neo4j
                    ↓
              Rate Limiter (slowapi)
              API Key Auth
              CORS
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check with Neo4j status |
| `/api/graph/citation-network` | GET | Fetch citation subgraph |
| `/api/graph/author-network` | GET | Fetch co-authorship subgraph |
| `/api/search/papers` | GET | Search papers by title/DOI |
| `/api/search/authors` | GET | Search authors by name |
| `/api/export/csv` | GET | Export results as CSV |

## Configuration

API behavior controlled via `settings`:
- `RESEARCH_API_KEY` — API key for auth (optional)
- `RESEARCH_RATE_LIMIT` — Rate limit string (default: "60/minute")
- `RESEARCH_CORS_ORIGINS` — Allowed origins
- `RESEARCH_NEO4J_URI` — Neo4j connection

## Running the Server

```bash
# Development
uv run python scripts/run_api.py --reload

# Production
uv run python scripts/run_api.py --host 0.0.0.0 --port 8300
```

## Conventions (This Module)

- Routes use dependency injection for Neo4j driver (`get_neo4j_driver`)
- Rate limiting via `@limiter.limit()` decorator
- Request timing logged with structured context
- Security headers added by middleware (CSP, X-Frame-Options, etc.)
- Static files served from `frontend/dist` for SPA fallback

## Error Handling

- Validation errors: 422 (Pydantic)
- Rate limit: 429
- Auth failure: 401
- Neo4j errors: 503 with retry suggestion
