<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# AGENTS.md — src/palimpsest/

**Scope**: Main research package — orchestrates data acquisition, network analysis, bibliometrics, and NLP.

## Overview

This package contains all production code for the science of science research toolkit. Code follows a layered architecture: **data → networks → bibliometrics**, with **utils** providing cross-cutting concerns.

## Structure

```
research/
├── __init__.py          # Package root, version
├── data/                # API clients (OpenAlex, Semantic Scholar)
├── networks/            # Graph construction (citation, collaboration)
├── bibliometrics/       # Publication metrics (h-index, disruption)
├── analysis/            # Research domain logic (AI adoption, retractions)
├── nlp/                 # Text mining & citation context
├── api/                 # FastAPI REST server
└── utils/               # Config, cache, logging, exceptions
```

## Module Interactions

```
data/ ──► networks/ ──► bibliometrics/
   │          │              │
   └──────────┴──────────────┘
              │
           utils/
         (config, cache)
```

- **data/**: Fetches raw scholarly data from external APIs
- **networks/**: Builds NetworkX graphs from data
- **bibliometrics/**: Computes metrics from graph/data
- **analysis/**: Research-specific domain logic
- **utils/**: Configuration (pydantic-settings), caching, structured logging

## Key Conventions (This Package)

### Imports
- Use `from palimpsest.X` (absolute), never relative imports
- Import order: stdlib → third-party → `from palimpsest.X`

### Type Hints
- All public functions must have typed signatures
- Use `X | None` (not `Optional[X]`)
- Complex types use `TypeAlias` in module scope

### Error Handling
- Never use bare `except:`
- Raise `APIError`, `DataValidationError`, or `RateLimitError` from `palimpsest.utils.exceptions`
- Always log errors with structured context before re-raising

### Graph Patterns
- Citation networks: `nx.DiGraph[str]` (directed, paper IDs as nodes)
- Collaboration networks: `nx.Graph[str]` (undirected, author IDs as nodes)
- Graphs carry node attributes (title, year, cited_by_count)

## Where to Look

| Task | Location | Notes |
|------|----------|-------|
| Fetch papers from OpenAlex | `data/openalex.py` | `OpenAlexClient.get_works()` |
| Build citation graph | `networks/citation.py` | `CitationNetwork.build_from_works()` |
| Compute h-index | `bibliometrics/indicators.py` | `compute_h_index()` |
| Analyze AI adoption trends | `analysis/ai_penetration.py` | `AIPenetrationAnalyzer` |
| Configure settings | `utils/config.py` | `Settings` class, reads `.env` |
| Cache API responses | `utils/cache.py` | `ResponseCache` with diskcache |

## Dependencies

- External APIs: `pyalex`, `httpx` (Semantic Scholar)
- Graphs: `networkx`
- Data: `pandas`, `pydantic`
- Cache: `diskcache`
