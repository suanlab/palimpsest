<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# analysis

## Purpose
Research-domain analysis modules implementing the project's core scientific investigations: AI adoption tracking and retraction contamination propagation.

## Key Files

| File | Description |
|------|-------------|
| `ai_penetration.py` | AI adoption analyzer — detects AI-related papers via OpenAlex topics/keywords, tracks adoption rates across fields using `AI_SUBFIELD_ID` and `AI_TOPIC_IDS` |
| `retraction_propagation.py` | Retraction contamination analyzer — `ContaminationEdge` dataclass, BFS traversal of citation chains, time-weighted contamination scoring |
| `__init__.py` | Package exports |

## For AI Agents

### Working In This Directory
- Each file implements one research track (Track 1: AI adoption, Track 3: retraction contamination)
- `ai_penetration.py` uses hardcoded OpenAlex concept/topic IDs for AI classification
- `retraction_propagation.py` uses BFS over citation graphs with time-decay weighting
- Both modules depend on `palimpsest.networks.citation` for graph traversal

### Testing Requirements
- Tests in `tests/test_analysis/`
- Test with small synthetic citation graphs, not real API data
- Verify edge cases: isolated nodes, self-citations, retracted papers citing other retracted papers

### Common Patterns
- Dataclasses for structured results (`ContaminationEdge`)
- OpenAlex concept/topic ID constants for AI classification
- Graph algorithms (BFS) over NetworkX DiGraph

## Dependencies

### Internal
- `palimpsest.networks.citation` — Citation graph for traversal
- `palimpsest.data.openalex` — OpenAlex API client for work metadata

### External
- `networkx` — Graph traversal algorithms
- `pandas` — Tabular result aggregation

<!-- MANUAL: -->
