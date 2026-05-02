<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# utils

## Purpose
Cross-cutting utilities: configuration management, API response caching, custom exceptions, and structured logging.

## Key Files

| File | Description |
|------|-------------|
| `config.py` | `Settings` class (pydantic-settings) — reads `RESEARCH_*` env vars for OpenAlex keys, Neo4j credentials, data/cache paths, rate limits, CORS origins |
| `cache.py` | `ResponseCache` class — persistent function result caching via diskcache backend, keyed as `{source}:{entity}:{id}` |
| `exceptions.py` | Exception hierarchy — `ResearchError` (base), `APIError`, `RateLimitError`, `DataValidationError` |
| `logging.py` | `setup_logging()` — structured logging configuration with JSON-compatible extras |
| `__init__.py` | Package exports |

## For AI Agents

### Working In This Directory
- All settings use `RESEARCH_` env prefix (e.g., `RESEARCH_NEO4J_URI`)
- Cache keys follow `{source}:{entity}:{id}` convention
- New exceptions should inherit from `ResearchError`
- Always use `setup_logging()` in scripts, not manual `basicConfig`

### Testing Requirements
- Test config loading with mock environment variables
- Test cache hit/miss behavior
- Test exception hierarchy and attributes

### Common Patterns
```python
from palimpsest.utils.config import settings
from palimpsest.utils.cache import ResponseCache
from palimpsest.utils.exceptions import APIError, RateLimitError

cache = ResponseCache()
result = cache.get("openalex:work:W123")
```

## Dependencies

### External
- `pydantic-settings` — Environment-based configuration
- `diskcache` — Persistent key-value cache

<!-- MANUAL: -->
