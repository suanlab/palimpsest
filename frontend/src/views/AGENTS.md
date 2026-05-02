<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-17 | Updated: 2026-04-17 -->

# views

## Purpose
Route-level page components for the bibliographic graph explorer. Each view is a top-level React page lazy-loaded by `App.tsx` via React Router.

## Key Files

| File | Description |
|------|-------------|
| `Dashboard.tsx` | Landing page — project overview, search entry, recent activity |
| `CitationNetwork.tsx` | Citation graph explorer — directed citation subgraphs with BFS expansion |
| `CoauthorshipNetwork.tsx` | Co-authorship graph explorer — undirected collaboration network with weighted edges |
| `ContaminationCascade.tsx` | Retraction contamination cascade visualization (Track 3) — propagation of retracted paper influence |
| `AIDiffusion.tsx` | AI adoption diffusion view (Track 1) — time-animated AI adoption across fields |
| `FieldComparison.tsx` | Side-by-side comparison of two fields — adoption curves, metric diffs |
| `AuthorDetail.tsx` | Author profile — metrics, collaborators, citation timeline |
| `PaperDetail.tsx` | Paper detail — references, citations, citation context |
| `CitationExplorer.tsx` | General citation exploration UI |
| `Help.tsx` | In-app help and documentation |

## For AI Agents

### Working In This Directory
- Each view is lazy-loaded in `App.tsx` via `React.lazy(() => import('./views/X'))`
- Views compose `GraphView`, `NodeDetailSidebar`, `GraphControls`, `SearchBar` from `components/`
- Data fetching goes through progressive hooks in `hooks/` — never fetch directly
- Keep view components focused on layout/state; delegate rendering to `components/GraphView`

### Common Patterns
- Views own URL query-string state (seed ids, depth, filters)
- Pass query params to progressive hooks to drive fetches
- Show `EmptyGraphState` / `ErrorState` when data is empty or failed

## Dependencies

### Internal
- `../components/` — GraphView, SearchBar, NodeDetailSidebar, etc.
- `../hooks/` — useProgressiveGraph, useProgressiveCascade, useProgressiveCoauthorship, useGraphData
- `../api/graphApi.ts` — Backend search + graph endpoints
- `../types/graph.ts` — Graph data interfaces

### External
- `react-router-dom` — Route params, navigation
- `cytoscape` + layouts — Graph rendering (via GraphView)

<!-- MANUAL: -->
