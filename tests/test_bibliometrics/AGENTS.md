<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-17 | Updated: 2026-04-17 -->

# test_bibliometrics

## Purpose
Tests for `palimpsest.bibliometrics` — citation indicators (`h_index`, `i10_index`) and temporal trajectories.

## Key Files

| File | Description |
|------|-------------|
| `test_indicators.py` | Tests for `bibliometrics.indicators` — h-index, i10-index on synthetic citation-count lists |
| `__init__.py` | Package marker |

## For AI Agents

### Working In This Directory
- Indicators are pure functions — pass `list[int]` citation counts directly
- Parametrize over multiple input shapes: empty, single paper, all-zero, uniform, skewed
- Assert known closed-form values (e.g., `h_index([5,4,3,2,1]) == 3`)
- Add new indicator tests here when `bibliometrics/indicators.py` grows

### Testing Requirements
```bash
uv run pytest tests/test_bibliometrics/ -v
```

### Common Patterns
```python
@pytest.mark.parametrize("counts,expected", [
    ([], 0),
    ([5, 4, 3, 2, 1], 3),
    ([10, 10, 10], 3),
])
def test_h_index(counts: list[int], expected: int) -> None:
    assert h_index(counts) == expected
```

## Dependencies

### Internal
- `palimpsest.bibliometrics.indicators`, `palimpsest.bibliometrics.temporal`

### External
- `pytest`, `pandas` (for temporal tests)

<!-- MANUAL: -->
