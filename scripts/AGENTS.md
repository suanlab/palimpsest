<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# AGENTS.md — scripts/

**Scope**: CLI utilities, data pipelines, and analysis workflows.

## Overview

One-off scripts and data processing pipelines. Not part of the importable package. Scripts are organized by workflow: collection → ETL → analysis → visualization.

## File Organization

| Category | Scripts |
|----------|---------|
| **API Server** | `run_api.py` — Launch FastAPI dev server |
| **Data Collection** | `collect_ai2000.py`, `collect_ai_adoption.py`, `collect_retraction_data.py`, `harvest_arxiv.py`, `download_oag_v3.1.py` |
| **ETL Pipelines** | `etl_openalex_snapshot.py`, `merge_etl_output.py`, `build_id_mapping.py`, `prepare_neo4j_import.py` |
| **Analysis** | `analyze_ai2000.py`, `analyze_ai_adoption.py`, `analyze_retraction_propagation.py`, `deep_analyze_ai_adoption.py`, `deep_analyze_retraction.py` |
| **Neo4j** | `import_to_neo4j.py`, `analyze_neo4j_fields.py`, `run_neo4j_bulk_import.sh` |
| **Visualization** | `generate_publication_figures.py`, `generate_supplementary_figures.py`, `generate_neo4j_figures.py`, `generate_figures.py` |
| **Utilities** | `precompute_yearly_counts.py`, `precompute_concept_ai_counts.py`, `join_retraction_watch_openalex.py`, `check_status.sh`, `check_downloads.sh`, `download_all_datasets.sh` |

## Conventions (This Directory)

### Script Structure

All analysis scripts follow this pattern:

```python
#!/usr/bin/env python3
"""One-line description."""

from __future__ import annotations

import argparse
import logging

from palimpsest.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument("--input", required=True, help="Input path")
    parser.add_argument("--output", required=True, help="Output path")
    return parser.parse_args()


def main() -> None:
    """Entry point."""
    args = parse_args()
    setup_logging("INFO")
    # ... implementation


if __name__ == "__main__":
    main()
```

### Data Paths

Scripts use `settings.data_dir` for consistent paths:
- Raw data: `data/raw/{source}/`
- Processed: `data/processed/`
- Figures: `data/processed/figures/`
- Cache: `data/cache/`

### Logging

- Always call `setup_logging()` at startup
- Use `logger.info()` for progress, `logger.error()` for failures
- Include structured context: `extra={"n_records": len(df)}`

### Running Scripts

```bash
# With uv
uv run python scripts/analyze_ai_adoption.py --input data/raw/openalex/ --output data/processed/

# Direct (if venv activated)
python scripts/analyze_ai_adoption.py --input data/raw/openalex/ --output data/processed/
```

## Important Notes

- Scripts may be long-running (hours for large datasets)
- Prefer `scripts/run_api.py` for API development
- Large analysis scripts (e.g., `deep_analyze_*.py`) process GBs of data
- Check `check_status.sh` for pipeline health
