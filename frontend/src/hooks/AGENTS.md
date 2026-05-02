<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-17 | Updated: 2026-04-17 -->

# hooks

## Purpose
Custom React hooks for progressive graph data loading. Each hook manages incremental BFS expansion against the backend graph API, exposing `{ nodes, edges, loading, error, expand }`.

## Key Files

| File | Description |
|------|-------------|
| `useGraphData.ts` | Base graph-data hook — one-shot fetch of a citation/author subgraph |
| `useProgressiveGraph.ts` | Progressive citation graph — BFS expansion from a seed, depth-controlled |
| `useProgressiveCoauthorship.ts` | Progressive co-authorship graph — expand from seed author to collaborators |
| `useProgressiveCascade.ts` | Progressive retraction contamination cascade — traverses citation chain from retracted seed |

## For AI Agents

### Working In This Directory
- Hooks own all graph-fetching logic — views must not call `graphApi` directly
- Progressive hooks maintain an internal `nodeSet`/`edgeSet` to dedupe across expansions
- Each `expand(nodeId)` call triggers a follow-up API request merging new elements into state
- Return shape is stable: `{ nodes, edges, loading, error, expand, reset }`
- Cancel in-flight requests on unmount via `AbortController`

### Common Patterns
```ts
export function useProgressiveGraph(seedId: string, depth: number) {
  const [state, setState] = useState<GraphState>({ nodes: [], edges: [], loading: false, error: null });
  const expand = useCallback(async (nodeId: string) => { ... }, []);
  return { ...state, expand, reset };
}
```

### Testing Requirements
- No test framework currently configured — verify via manual exercise in dev server

## Dependencies

### Internal
- `../api/graphApi.ts` — Backend fetches
- `../types/graph.ts` — GraphNode, GraphEdge types

### External
- `react` 19 — `useState`, `useEffect`, `useCallback`, `useMemo`

<!-- MANUAL: -->
