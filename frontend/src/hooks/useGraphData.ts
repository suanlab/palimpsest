import { useState, useEffect, useCallback, useRef } from "react";
import type {
  GraphResponse,
  CytoscapeElement,
  GraphNode,
  GraphEdge,
  GraphFilters,
} from "../types/graph";
import { DEFAULT_FILTERS } from "../types/graph";

interface UseGraphDataReturn {
  elements: CytoscapeElement[];
  loading: boolean;
  error: string | null;
  rawData: GraphResponse | null;
  refetch: () => void;
}

/**
 * Normalize a backend node into a Cytoscape-compatible element.
 * Backend returns `title` (papers) or `name` (authors) — map to `label`.
 */
function nodeToCytoscape(node: GraphNode): CytoscapeElement {
  const raw = node as unknown as Record<string, unknown>;
  return {
    data: {
      ...node,
      label:
        node.label ||
        (raw.title as string | undefined) ||
        (raw.name as string | undefined) ||
        node.id,
    },
  };
}

/**
 * Normalize a backend edge into a Cytoscape-compatible element.
 * Auto-generate `id` if the backend doesn't provide one.
 */
function edgeToCytoscape(edge: GraphEdge, index: number): CytoscapeElement {
  return {
    data: {
      ...edge,
      id: edge.id || `e-${edge.source}-${edge.target}-${index}`,
    },
  };
}

function applyFilters(
  data: GraphResponse,
  filters: GraphFilters,
): CytoscapeElement[] {
  const filteredNodes = data.nodes.filter((node) => {
    if (
      filters.minCitations > 0 &&
      (node.cited_by_count ?? 0) < filters.minCitations
    ) {
      return false;
    }
    if (node.year !== undefined) {
      if (node.year < filters.yearFrom || node.year > filters.yearTo) {
        return false;
      }
    }
    if (!filters.showRetracted && node.is_retracted) {
      return false;
    }
    if (!filters.showAiRelated && node.is_ai_related) {
      return false;
    }
    return true;
  });

  const nodeIds = new Set(filteredNodes.map((n) => n.id));

  const filteredEdges = data.edges.filter(
    (edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target),
  );

  return [
    ...filteredNodes.map(nodeToCytoscape),
    ...filteredEdges.map(edgeToCytoscape),
  ];
}

export function useGraphData(
  fetcher: ((signal: AbortSignal) => Promise<GraphResponse>) | null,
  filters: GraphFilters = DEFAULT_FILTERS,
): UseGraphDataReturn {
  const [rawData, setRawData] = useState<GraphResponse | null>(null);
  const [elements, setElements] = useState<CytoscapeElement[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const filtersRef = useRef(filters);
  filtersRef.current = filters;

  /**
   * Core fetch function. Depends on `fetcher` so it recreates when
   * the caller provides a new fetcher (e.g. after seedId changes).
   */
  const doFetch = useCallback(() => {
    if (!fetcher) {
      setElements([]);
      setRawData(null);
      setLoading(false);
      setError(null);
      return;
    }

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    setError(null);

    fetcher(controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) {
          setRawData(data);
          setElements(applyFilters(data, filtersRef.current));
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (!controller.signal.aborted) {
          const message =
            err instanceof Error ? err.message : "An unknown error occurred";
          setError(message);
          setLoading(false);
        }
      });
  }, [fetcher]);

  // Re-fetch when fetcher changes (new seedId, depth, etc.)
  useEffect(() => {
    doFetch();
    return () => {
      abortRef.current?.abort();
    };
  }, [doFetch]);

  // Re-apply filters without re-fetching
  useEffect(() => {
    if (rawData) {
      setElements(applyFilters(rawData, filters));
    }
  }, [filters, rawData]);

  return { elements, loading, error, rawData, refetch: doFetch };
}
