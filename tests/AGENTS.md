<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# tests

## Purpose
pytest test suite mirroring the `src/palimpsest/` package structure.

## Key Files

| File | Description |
|------|-------------|
| `conftest.py` | Shared fixtures — sample OpenAlex-compatible work records, test graphs |
| `__init__.py` | Package marker |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `test_analysis/` | Tests for `palimpsest.analysis` (AI penetration, retraction propagation) |
| `test_bibliometrics/` | Tests for `palimpsest.bibliometrics` (h-index, temporal metrics) |
| `test_data/` | Tests for `palimpsest.data` (API client mocks) |
| `test_networks/` | Tests for `palimpsest.networks` (citation/collaboration graph builders) |

## For AI Agents

### Working In This Directory
- Mirror source structure: `src/palimpsest/X/y.py` → `tests/test_X/test_y.py`
- Prefix files with `test_`, functions with `test_`
- Use fixtures from `conftest.py` for shared test data
- Mock all external API calls — never hit real APIs
- Use `pytest.mark.slow` for large-dataset integration tests
- Parametrize tests when checking multiple inputs

### Testing Requirements
```bash
uv run pytest                           # Run all tests
uv run pytest tests/test_X/test_y.py    # Run single file
uv run pytest -x --tb=short -q          # Quick failure mode
```

### Common Patterns
```python
@pytest.mark.parametrize("metric", ["h_index", "i10_index"])
def test_indicator(metric: str, sample_works: list[dict]) -> None:
    result = compute_indicator(metric, sample_works)
    assert result >= 0
```

## Dependencies

### Internal
- `src/palimpsest/` — All modules under test

### External
- `pytest`, `pytest-asyncio`

<!-- MANUAL: -->
