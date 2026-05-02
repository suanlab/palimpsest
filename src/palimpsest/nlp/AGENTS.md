<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# nlp

## Purpose
Citation context classification — determines the intent behind citations (supporting, contrasting, methodological, etc.) using Semantic Scholar data.

## Key Files

| File | Description |
|------|-------------|
| `citation_context.py` | Citation intent classifier — `CitationIntent` enum (SUPPORTING, CONTRASTING, METHODOLOGICAL, BACKGROUND, PERFUNCTORY, UNKNOWN), uses Semantic Scholar API for citation context |
| `__init__.py` | Package exports |

## For AI Agents

### Working In This Directory
- `CitationIntent` enum classifies why a paper cites another
- Intent data comes from Semantic Scholar's citation context API
- This module bridges citation network structure with semantic meaning

### Testing Requirements
- Tests in `tests/` (mock Semantic Scholar API responses)
- Test all enum values with representative citation contexts
- Test fallback to UNKNOWN when context is unavailable

### Common Patterns
```python
class CitationIntent(Enum):
    SUPPORTING = "supporting"
    CONTRASTING = "contrasting"
    METHODOLOGICAL = "methodological"
    BACKGROUND = "background"
    PERFUNCTORY = "perfunctory"
    UNKNOWN = "unknown"
```

## Dependencies

### Internal
- `palimpsest.data.semantic_scholar` — Semantic Scholar API client for citation contexts

### External
- (No additional external dependencies beyond the data client)

<!-- MANUAL: -->
