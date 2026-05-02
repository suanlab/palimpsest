<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-17 | Updated: 2026-04-17 -->

# test_analysis

## Purpose
Tests for `palimpsest.analysis` — AI adoption detection and retraction contamination propagation.

## Key Files

| File | Description |
|------|-------------|
| `test_ai_penetration.py` | Tests for `analysis.ai_penetration` — AI paper classification via concept/topic IDs, adoption-rate computation |
| `test_retraction_propagation.py` | Tests for `analysis.retraction_propagation` — BFS citation traversal, `ContaminationEdge`, time-weighted scoring |
| `__init__.py` | Package marker |

## For AI Agents

### Working In This Directory
- Build small synthetic `nx.DiGraph` fixtures; do not call OpenAlex/Semantic Scholar APIs
- Cover edge cases: self-citations, retracted-cites-retracted, isolated nodes, empty graphs
- For AI penetration tests, use fake work records tagged with the `AI_SUBFIELD_ID` / `AI_TOPIC_IDS` constants
- For contamination tests, assert expected `ContaminationEdge` output with explicit time deltas

### Testing Requirements
```bash
uv run pytest tests/test_analysis/ -v
uv run pytest tests/test_analysis/test_retraction_propagation.py -k contamination
```

## Dependencies

### Internal
- `palimpsest.analysis.ai_penetration`, `palimpsest.analysis.retraction_propagation`
- `palimpsest.networks.citation` — graph fixtures built on `CitationNetwork`

### External
- `pytest`, `networkx`, `pandas`

<!-- MANUAL: -->
