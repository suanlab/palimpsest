<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-17 | Updated: 2026-04-17 -->

# test_data

## Purpose
Tests for `palimpsest.data` — OpenAlex, Semantic Scholar, and Retraction Watch clients. All external API calls are mocked.

## Key Files

| File | Description |
|------|-------------|
| `test_openalex.py` | Tests for `data.openalex.OpenAlexClient` — pagination, cache lookup, error mapping (APIError/RateLimitError) |
| `__init__.py` | Package marker |

## For AI Agents

### Working In This Directory
- **Never hit real APIs** — mock `pyalex` and `httpx` transports
- Use fixtures from `tests/conftest.py` for sample work records
- Cover: normal response, 429 rate limit, 500 server error, malformed JSON, empty results
- Verify cache keys follow `{source}:{entity}:{id}` convention
- New clients (`semantic_scholar`, `retraction_watch`) should get their own `test_*.py` here

### Testing Requirements
```bash
uv run pytest tests/test_data/ -v
uv run pytest tests/test_data/test_openalex.py::test_rate_limit -v
```

### Common Patterns
```python
def test_get_work_uses_cache(mocker, sample_work: dict) -> None:
    mock_cache = mocker.patch("palimpsest.data.openalex.ResponseCache")
    mock_cache.return_value.get.return_value = sample_work
    client = OpenAlexClient()
    result = client.get_work("W123")
    assert result == sample_work
```

## Dependencies

### Internal
- `palimpsest.data.openalex`, `palimpsest.data.semantic_scholar`, `palimpsest.data.retraction_watch`
- `palimpsest.utils.exceptions` — assert raised exception types

### External
- `pytest`, `pytest-mock` (or `unittest.mock`), `httpx` (MockTransport)

<!-- MANUAL: -->
