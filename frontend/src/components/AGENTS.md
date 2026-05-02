<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-17 | Updated: 2026-04-17 -->

# components

## Purpose
Reusable React UI components for graph exploration, search, node inspection, and layout. Used across all route views.

## Key Files

| File | Description |
|------|-------------|
| `GraphView.tsx` | Cytoscape graph renderer — registers cose-bilkent/fcose layouts, applies D3-Force physics, handles node selection |
| `GraphControls.tsx` | Graph manipulation controls — zoom, layout reset, physics toggle, expand depth |
| `NodeDetailSidebar.tsx` | Right sidebar — displays selected node metadata (title, authors, year, citations) |
| `NodeDetail.tsx` | Inline node detail card |
| `NodeContextMenu.tsx` | Right-click menu — expand node, open paper, copy ID |
| `SearchBar.tsx` | Top search bar composite — combines SearchInput, SearchFilters |
| `SearchInput.tsx` | Debounced search input with autocomplete dropdown |
| `SearchFilters.tsx` | Filter UI — entity type (paper/author), year range, field |
| `RecentSearches.tsx` | Dropdown of recently submitted searches (localStorage-backed) |
| `ExportMenu.tsx` | Export menu — download graph as CSV/JSON/PNG |
| `Sidebar.tsx` | Left navigation sidebar — route links |
| `Layout.tsx` | App shell — sidebar + header + main content slot |
| `EmptyGraphState.tsx` | Empty state when no nodes are loaded |
| `ErrorState.tsx` | Error state with retry action |
| `WelcomeModal.tsx` | First-visit onboarding modal |

## For AI Agents

### Working In This Directory
- Components are presentational + local state only — no global stores
- Graph rendering logic lives in `GraphView.tsx`; don't duplicate Cytoscape setup elsewhere
- Keep props interfaces defined above each component (inline, not in `types/`)
- Use Tailwind utility classes; avoid ad-hoc CSS
- For new graph interactions, extend `GraphView` via callback props (`onNodeClick`, `onNodeExpand`)

### Common Patterns
- Props typed as `interface XProps { ... }` directly above the component
- Controlled components — parent owns state, component emits callbacks
- `forwardRef` used where DOM refs are exposed

## Dependencies

### Internal
- `../types/graph.ts` — GraphNode, GraphEdge, CytoscapeElement types
- `../hooks/` — Data-fetching hooks called from view components, not these

### External
- `cytoscape`, `cytoscape-cose-bilkent`, `cytoscape-fcose` — Graph rendering
- `d3-force` — Physics simulation
- `react-router-dom` — Link, useNavigate in Sidebar/Layout
- `tailwindcss` — Styling

<!-- MANUAL: -->
