<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# bibliometrics

## Purpose
Publication-level citation metrics and temporal analysis for researcher impact assessment.

## Key Files

| File | Description |
|------|-------------|
| `indicators.py` | Citation metrics — `h_index()`, `i10_index()` for researcher-level impact |
| `temporal.py` | Time-series citation analysis — `citation_trajectory()` computes annual/cumulative citations over time |
| `__init__.py` | Package exports |

## For AI Agents

### Working In This Directory
- Functions take lists of citation counts or work records, return scalar metrics or time-series
- Keep functions pure — no API calls or side effects
- New indicators should follow the same signature pattern: `(works: list[dict]) -> numeric`

### Testing Requirements
- Tests in `tests/test_bibliometrics/`
- Use parametrized tests for multiple indicators
- Edge cases: empty publication list, single paper, all-zero citations

### Common Patterns
```python
def h_index(citation_counts: list[int]) -> int:
    """Compute h-index from list of citation counts."""
```

## Dependencies

### Internal
- None — standalone computation module

### External
- `pandas` — Time-series aggregation in `temporal.py`

<!-- MANUAL: -->
