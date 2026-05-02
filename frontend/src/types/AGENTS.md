<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-17 | Updated: 2026-04-17 -->

# types

## Purpose
Shared TypeScript interfaces for graph data, search results, and Cytoscape integration.

## Key Files

| File | Description |
|------|-------------|
| `graph.ts` | Core interfaces — `GraphNode`, `GraphEdge`, `CytoscapeElement`, `SearchResult`, `PaperNode`, `AuthorNode`, API response envelopes |

## For AI Agents

### Working In This Directory
- Any shape crossing component boundaries belongs here
- Mirror backend response shapes (`src/research/api/routes/graph.py` — `CitationNode`, `AuthorNode`, `SearchResultItem`)
- Use `type` for unions/aliases, `interface` for object shapes
- Keep optional fields explicit with `?:` — don't rely on implicit undefined

### Common Patterns
```ts
export interface GraphNode {
  id: string;
  label: string;
  type: 'paper' | 'author';
  year?: number;
  citedByCount?: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight?: number;
}
```

## Dependencies

### Internal
- Backend response contracts in `src/research/api/routes/`

### External
- `cytoscape` — `ElementDefinition` type used as base for `CytoscapeElement`

<!-- MANUAL: -->
