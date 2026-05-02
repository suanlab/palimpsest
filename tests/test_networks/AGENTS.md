<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-17 | Updated: 2026-04-17 -->

# test_networks

## Purpose
Tests for `palimpsest.networks` — citation graph, collaboration graph, and network metrics.

## Key Files

| File | Description |
|------|-------------|
| `test_citation.py` | Tests for `networks.citation.CitationNetwork` — graph construction from work records, `get_citing_papers`, `get_references`, `get_subgraph` BFS |
| `__init__.py` | Package marker |

## For AI Agents

### Working In This Directory
- Build graphs from small hand-crafted lists of `WorkRecord` dicts
- Assert node count, edge count, and attribute presence (title, year, cited_by_count)
- Cover: missing `referenced_works`, duplicate ids, cycles, isolated nodes
- Subgraph tests: vary seed set size and `depth` parameter, assert BFS reaches expected nodes
- Add tests for `collaboration.py` and `metrics.py` here when exercised

### Testing Requirements
```bash
uv run pytest tests/test_networks/ -v
```

### Common Patterns
```python
def test_citation_network_direction() -> None:
    works = [
        {"id": "W1", "referenced_works": ["W2"], "title": "A", "publication_year": 2020, "cited_by_count": 1},
        {"id": "W2", "referenced_works": [], "title": "B", "publication_year": 2019, "cited_by_count": 5},
    ]
    net = CitationNetwork()
    net.build_from_works(works)
    assert net.graph.has_edge("W1", "W2")  # citing → cited
```

## Dependencies

### Internal
- `palimpsest.networks.citation`, `palimpsest.networks.collaboration`, `palimpsest.networks.metrics`

### External
- `pytest`, `networkx`

<!-- MANUAL: -->
