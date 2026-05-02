import { useCallback, useMemo, useRef, useState } from "react";
import { fetchCitationGraph } from "../api/graphApi";
import type { CitationGraphNode, CitationGraphResponse } from "../api/graphApi";
import type { CytoscapeElement, GraphEdge, GraphNode } from "../types/graph";

interface UseProgressiveGraphReturn {
  elements: CytoscapeElement[];
  loading: boolean;
  error: string | null;
  expandingNodeId: string | null;
  expandNode: (nodeId: string) => void;
  isExpanded: (nodeId: string) => boolean;
  initGraph: (paperId: string) => void;
  seedId: string | null;
  reset: () => void;
}

function toGraphNode(node: CitationGraphNode): GraphNode {
  return {
    id: node.id,
    label: node.title,
    type: "paper",
    cited_by_count: node.cited_by_count,
    year: node.year ?? undefined,
    field: node.field ?? undefined,
    is_retracted: node.is_retracted,
    is_focal: node.is_focal,
  };
}

function buildEdgeId(
  source: string,
  target: string,
  baseIndex: number,
  existingEdges: Map<string, GraphEdge>,
): string {
  let index = baseIndex;
  let edgeId = `e-${source}-${target}-${index}`;

  while (existingEdges.has(edgeId)) {
    const existing = existingEdges.get(edgeId);
    if (existing && existing.source === source && existing.target === target) {
      return edgeId;
    }
    index += 1;
    edgeId = `e-${source}-${target}-${index}`;
  }

  return edgeId;
}

function mergeGraphEdges(
  currentEdges: Map<string, GraphEdge>,
  response: CitationGraphResponse,
): Map<string, GraphEdge> {
  const next = new Map(currentEdges);

  response.edges.forEach((edge, index) => {
    const edgeId = buildEdgeId(edge.source, edge.target, index, next);
    if (!next.has(edgeId)) {
      next.set(edgeId, {
        id: edgeId,
        source: edge.source,
        target: edge.target,
        type: "cites",
      });
    }
  });

  return next;
}

function mergeGraphNodes(
  currentNodes: Map<string, GraphNode>,
  response: CitationGraphResponse,
): Map<string, GraphNode> {
  const next = new Map(currentNodes);
  const incomingNodes = [response.focal_paper, ...response.nodes];

  incomingNodes.forEach((node) => {
    const normalized = toGraphNode(node);
    const existing = next.get(node.id);
    next.set(node.id, existing ? { ...existing, ...normalized } : normalized);
  });

  return next;
}

export function useProgressiveGraph(): UseProgressiveGraphReturn {
  const [seedId, setSeedId] = useState<string | null>(null);
  const [nodesMap, setNodesMap] = useState<Map<string, GraphNode>>(new Map());
  const [edgesMap, setEdgesMap] = useState<Map<string, GraphEdge>>(new Map());
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandingNodeId, setExpandingNodeId] = useState<string | null>(null);
  const initAbortRef = useRef<AbortController | null>(null);
  const expandAbortRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    initAbortRef.current?.abort();
    expandAbortRef.current?.abort();
    setSeedId(null);
    setNodesMap(new Map());
    setEdgesMap(new Map());
    setExpandedNodes(new Set());
    setLoading(false);
    setError(null);
    setExpandingNodeId(null);
  }, []);

  const initGraph = useCallback((paperId: string) => {
    initAbortRef.current?.abort();
    expandAbortRef.current?.abort();
    const controller = new AbortController();
    initAbortRef.current = controller;

    setLoading(true);
    setError(null);
    setExpandingNodeId(null);

    fetchCitationGraph(paperId, 1, 15, controller.signal)
      .then((response) => {
        if (controller.signal.aborted) {
          return;
        }

        setSeedId(paperId);
        setNodesMap(mergeGraphNodes(new Map(), response));
        setEdgesMap(mergeGraphEdges(new Map(), response));
        setExpandedNodes(new Set());
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (!controller.signal.aborted) {
          const message =
            err instanceof Error ? err.message : "Failed to load citation graph";
          setError(message);
          setLoading(false);
        }
      });
  }, []);

  const expandNode = useCallback(
    (nodeId: string) => {
      if (!seedId || expandedNodes.has(nodeId) || expandingNodeId) {
        return;
      }

      expandAbortRef.current?.abort();
      const controller = new AbortController();
      expandAbortRef.current = controller;

      setExpandingNodeId(nodeId);

      fetchCitationGraph(nodeId, 1, 10, controller.signal)
        .then((response) => {
          if (controller.signal.aborted) {
            return;
          }

          setNodesMap((current) => mergeGraphNodes(current, response));
          setEdgesMap((current) => mergeGraphEdges(current, response));
          setExpandedNodes((current) => {
            const next = new Set(current);
            next.add(nodeId);
            return next;
          });
          setExpandingNodeId(null);
        })
        .catch(() => {
          if (!controller.signal.aborted) {
            setExpandingNodeId(null);
          }
        });
    },
    [expandedNodes, expandingNodeId, seedId],
  );

  const isExpanded = useCallback(
    (nodeId: string) => {
      return expandedNodes.has(nodeId);
    },
    [expandedNodes],
  );

  const elements = useMemo<CytoscapeElement[]>(() => {
    const nodes = Array.from(nodesMap.values()).map((node) => ({
      data: {
        ...node,
        is_expanded: expandedNodes.has(node.id),
      },
    }));

    const edges = Array.from(edgesMap.values()).map((edge) => ({
      data: edge,
    }));

    return [...nodes, ...edges];
  }, [edgesMap, expandedNodes, nodesMap]);

  return {
    elements,
    loading,
    error,
    expandingNodeId,
    expandNode,
    isExpanded,
    initGraph,
    seedId,
    reset,
  };
}
