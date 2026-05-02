<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# AGENTS.md — Science of Science Research Project

## Project Overview

Python research project for **science of science** (과학의 과학) — analyzing scholarly metadata, citation networks, collaboration patterns, and research dynamics. Data sources: OpenAlex, Semantic Scholar, PubMed, Web of Science, Scopus, arXiv, DBLP.

**Stack**: Python 3.12+ · uv (package manager) · ruff (lint+format) · mypy (types) · pytest (tests)

---

## Build / Lint / Test Commands

```bash
# --- Environment ---
uv sync                          # Install all deps from lockfile
uv sync --all-extras --dev       # Install with all extras + dev deps
uv add <pkg>                     # Add dependency (updates pyproject.toml + uv.lock)
uv add <pkg> --dev               # Add dev dependency
uv lock                          # Regenerate lockfile without installing

# --- Run ---
uv run python <script.py>        # Run script in project venv
uv run jupyter lab               # Launch Jupyter

# --- Lint & Format ---
uv run ruff check .              # Lint all files
uv run ruff check . --fix        # Lint + auto-fix
uv run ruff format .             # Format all files
uv run ruff format --check .     # Check formatting without changing

# --- Type Check ---
uv run mypy src/                 # Type check source code

# --- Tests ---
uv run pytest                    # Run all tests
uv run pytest tests/test_foo.py  # Run single test file
uv run pytest tests/test_foo.py::test_bar       # Run single test function
uv run pytest tests/test_foo.py::TestClass      # Run single test class
uv run pytest -k "keyword"       # Run tests matching keyword
uv run pytest -x                 # Stop on first failure
uv run pytest --tb=short -q      # Quiet output, short tracebacks

# --- Full Check (run before commit) ---
uv run ruff check . --fix && uv run ruff format . && uv run mypy src/ && uv run pytest
```

---

## Project Structure

```
research/
├── pyproject.toml
├── uv.lock
├── AGENTS.md
├── src/
│   └── research/              # Main package (importable)
│       ├── __init__.py
│       ├── data/              # Data acquisition & cleaning
│       │   ├── openalex.py    # OpenAlex API client
│       │   ├── semantic_scholar.py
│       │   ├── pubmed.py
│       │   └── loader.py      # Unified data loading interface
│       ├── networks/          # Graph construction & analysis
│       │   ├── citation.py    # Citation network builder
│       │   ├── collaboration.py
│       │   └── metrics.py     # Network metrics (centrality, communities)
│       ├── bibliometrics/     # Publication-level metrics
│       │   ├── indicators.py  # h-index, disruption index, etc.
│       │   └── temporal.py    # Time-series analysis of fields
│       ├── nlp/               # Text mining & embeddings
│       │   ├── topics.py      # Topic modeling (LDA, BERTopic)
│       │   └── embeddings.py  # Paper similarity, SPECTER
│       └── utils/             # Shared utilities
│           ├── config.py      # Settings via pydantic-settings
│           ├── cache.py       # API response caching
│           └── logging.py     # Structured logging setup
├── tests/
│   ├── conftest.py            # Shared fixtures
│   ├── test_data/
│   ├── test_networks/
│   └── test_bibliometrics/
├── notebooks/                 # Exploratory Jupyter notebooks
├── scripts/                   # One-off or CLI scripts
└── data/                      # Local data cache (gitignored)
    ├── raw/
    └── processed/
```

---

## Code Style Guidelines

### Formatting & Linting (ruff)

- **Line length**: 88 characters (Black-compatible)
- **Indent**: 4 spaces, no tabs
- **Quotes**: Double quotes (`"string"`)
- **Trailing commas**: Always use in multi-line collections
- Ruff rules: `E4, E7, E9, F, B, I, UP, SIM, N` (pycodestyle, pyflakes, bugbear, isort, pyupgrade, simplify, pep8-naming)

### Imports

Order enforced by ruff's isort (`I`):

```python
# 1. Standard library
import json
from collections import defaultdict
from pathlib import Path

# 2. Third-party
import networkx as nx
import pandas as pd
from pydantic import BaseModel

# 3. Local
from research.data.openalex import fetch_works
from research.utils.config import settings
```

- One import per line for `from` imports with 3+ names
- Use absolute imports, never relative (`from research.x` not `from .x`)
- No wildcard imports (`from x import *`)

### Type Hints

- **All function signatures** must have type hints (params + return)
- Use modern syntax: `list[str]`, `dict[str, int]`, `X | None` (not `Optional[X]`)
- Complex types → use `TypeAlias` or `TypedDict`
- DataFrames: annotate as `pd.DataFrame` with docstring describing columns

```python
def build_citation_network(
    works: list[dict[str, Any]],
    min_citations: int = 5,
) -> nx.DiGraph:
    """Build directed citation graph from OpenAlex works.

    Args:
        works: List of work dicts with keys: id, referenced_works, cited_by_count.
        min_citations: Minimum citations to include a node.

    Returns:
        Directed graph where edges represent citations (citing -> cited).
    """
```

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Modules | `snake_case` | `citation_network.py` |
| Classes | `PascalCase` | `CitationGraph` |
| Functions | `snake_case` | `compute_h_index()` |
| Constants | `UPPER_SNAKE` | `MAX_API_PAGE_SIZE` |
| Private | `_leading_underscore` | `_parse_response()` |
| Type aliases | `PascalCase` | `WorkId = str` |

### Docstrings

- **Google style** (standard in scientific Python)
- Required for: all public functions, classes, and modules
- Include `Args`, `Returns`, `Raises` sections for non-trivial functions
- Add `Example` section for key public API functions

```python
def disruption_index(
    paper_id: str,
    citation_graph: nx.DiGraph,
) -> float:
    """Calculate the CD index (Funk & Owen-Smith, 2017).

    Measures how a paper disrupts vs. consolidates its field.
    Range: [-1, 1] where 1 = maximally disruptive.

    Args:
        paper_id: Unique paper identifier.
        citation_graph: Directed graph of citation relationships.

    Returns:
        CD index value between -1 and 1.

    Raises:
        KeyError: If paper_id not found in the graph.
    """
```

### Error Handling

- Use specific exceptions, never bare `except:`
- API clients: raise custom exceptions inheriting from a base `ResearchError`
- Data validation: use Pydantic models for API responses
- Always log errors with context before re-raising

```python
class ResearchError(Exception):
    """Base exception for this project."""

class APIError(ResearchError):
    """External API call failed."""

class DataValidationError(ResearchError):
    """Data failed validation checks."""
```

### Data Handling Patterns

- Raw API responses → Pydantic models → pandas DataFrames → analysis
- Cache API responses locally (`data/raw/`) to avoid re-fetching
- Use `pathlib.Path` for all file paths, never `os.path`
- Configuration via `pydantic-settings` with `.env` file support
- Large datasets: use Parquet format (`df.to_parquet()`)

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use structured messages
logger.info("Fetching works", extra={"source": "openalex", "count": 1000})
logger.error("API request failed", extra={"url": url, "status": status_code})
```

### Testing Conventions

- Mirror source structure: `src/research/data/openalex.py` → `tests/test_data/test_openalex.py`
- Prefix test files with `test_`, test functions with `test_`
- Use fixtures in `conftest.py` for shared test data (sample API responses, small graphs)
- Mock external API calls — never hit real APIs in tests
- Use `pytest.mark.slow` for integration tests that process large datasets
- Parametrize when testing multiple inputs:

```python
@pytest.mark.parametrize("metric", ["h_index", "i10_index", "g_index"])
def test_bibliometric_indicator(metric: str, sample_papers: list[dict]) -> None:
    result = compute_indicator(metric, sample_papers)
    assert result >= 0
```

### Jupyter Notebooks

- Notebooks are for **exploration only** — production logic lives in `src/`
- Name with number prefix: `01_data_exploration.ipynb`, `02_network_analysis.ipynb`
- Clear outputs before committing
- Extract reusable code into `src/` modules, import from notebooks

---

## Key Libraries Reference

| Domain | Libraries |
|--------|-----------|
| Data APIs | `pyalex`, `semanticscholar`, `biopython`, `pybliometrics` |
| DataFrames | `pandas`, `polars` (for large-scale) |
| Networks | `networkx`, `igraph`, `graph-tool` |
| NLP | `scikit-learn`, `sentence-transformers`, `bertopic` |
| Visualization | `matplotlib`, `seaborn`, `plotly` |
| Statistics | `scipy`, `statsmodels` |
| Config | `pydantic-settings` |
| HTTP | `httpx` (async-capable) |
| Caching | `diskcache`, `joblib` |

---

## Git Conventions

- Never commit `.env`, API keys, or `data/raw/` contents
- Commit `uv.lock` — ensures reproducible environments
- Branch names: `feat/<topic>`, `fix/<issue>`, `data/<source>`
