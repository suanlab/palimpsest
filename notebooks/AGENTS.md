<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# notebooks

## Purpose
Exploratory Jupyter notebooks for data analysis and visualization. Notebooks are for exploration only — production logic lives in `src/research/`.

## Key Files

| File | Description |
|------|-------------|
| `01_ai_adoption_exploration.ipynb` | Exploratory analysis of AI field adoption trends (Track 1) |
| `02_retraction_propagation.ipynb` | Analysis of retraction contamination cascades (Track 3) |

## For AI Agents

### Working In This Directory
- Number-prefix naming: `01_`, `02_`, etc.
- Import reusable code from `research.*` modules, don't duplicate logic
- Clear cell outputs before committing
- Notebooks are exploration artifacts, not deliverables

### Running
```bash
uv run jupyter lab
```

## Dependencies

### Internal
- `src/research/` — Import all analysis functions from the main package

### External
- `jupyter`, `matplotlib`, `seaborn`, `pandas`

<!-- MANUAL: -->
