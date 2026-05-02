<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# frontend/src

## Purpose
React application source code for the bibliographic graph explorer. Organized by feature: API client, reusable components, custom hooks, route views, type definitions, and styles.

## Key Files

| File | Description |
|------|-------------|
| `App.tsx` | Main router — lazy-loads all views (CitationNetwork, CoauthorshipNetwork, ContaminationCascade, AIDiffusion, FieldComparison, AuthorDetail, PaperDetail) |
| `main.tsx` | Entry point — React root, Cytoscape plugin registration (cose-bilkent, fcose, node-html-label) |
| `cytoscape-cose-bilkent.d.ts` | Type declarations for Cytoscape cose-bilkent layout plugin |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `api/` | API client — `graphApi.ts` with fetchJson, searchPapers, searchAuthors |
| `components/` | Reusable UI components (GraphView, SearchBar, NodeDetailSidebar, GraphControls, etc.) |
| `hooks/` | Custom React hooks (useGraphData, useProgressiveGraph, useProgressiveCascade, useProgressiveCoauthorship) |
| `views/` | Route-level page components (Dashboard, CitationNetwork, CoauthorshipNetwork, ContaminationCascade, AIDiffusion, FieldComparison, Help) |
| `types/` | TypeScript interfaces — `graph.ts` (GraphNode, GraphEdge, CytoscapeElement, SearchResult) |
| `styles/` | Global CSS (Tailwind setup) |
| `assets/` | Static assets (SVG icons) |

## For AI Agents

### Working In This Directory
- All views are lazy-loaded in `App.tsx` — add new views there with `React.lazy()`
- Graph rendering uses Cytoscape with D3-Force physics — see `components/GraphView.tsx`
- API calls go through `api/graphApi.ts` — centralizes fetch logic and error handling
- Types are shared via `types/graph.ts` — update interfaces there, not inline
- Progressive loading hooks manage incremental graph expansion from the API

### Key Architectural Patterns
- **Lazy routing**: Views loaded on-demand via React Router + React.lazy
- **Progressive graph loading**: Hooks fetch graph data incrementally (BFS expansion)
- **Cytoscape + D3-Force**: Cytoscape renders, D3 handles force-directed layout simulation
- **Component composition**: GraphView + NodeDetailSidebar + GraphControls form the exploration UI

### Common Patterns
- Props interfaces defined above components
- Hooks return `{ data, loading, error }` pattern
- API responses typed via `types/graph.ts` interfaces

## Dependencies

### Internal
- `../` — Vite config, Tailwind config, TypeScript config

### External
- `react` 19, `react-router-dom` 7 — UI framework + routing
- `cytoscape` 3.33, `cytoscape-cose-bilkent`, `cytoscape-fcose` — Graph rendering + layouts
- `d3-force` 3 — Physics simulation
- `tailwindcss` 4 — Utility-first CSS

<!-- MANUAL: -->
