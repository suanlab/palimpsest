import { useCallback, useMemo, useRef, useState } from "react";
import { fetchContaminationCascade } from "../api/graphApi";
import type {
  CytoscapeElement,
  GraphEdge,
  GraphNode,
  GraphResponse,
} from "../types/graph";

interface UseProgressiveCascadeReturn {
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

function normalizeNode(raw: GraphNode, isSeed: boolean): GraphNode {
  const record = raw as unknown as Record<string, unknown>;
  return {
    ...raw,
    label:
      raw.label ||
      (record.title as string | undefined) ||
      (record.name as string | undefined) ||
      raw.id,
    type: raw.type || "paper",
    is_focal: isSeed,
  };
}

function ensureEdgeId(
  edge: GraphEdge,
  index: number,
  existing: Map<string, GraphEdge>,
): string {
  if (edge.id && !existing.has(edge.id)) return edge.id;

  let idx = index;
  let edgeId = `e-${edge.source}-${edge.target}-${idx}`;
  while (existing.has(edgeId)) {
    const prev = existing.get(edgeId);
    if (prev && prev.source === edge.source && prev.target === edge.target) {
      return edgeId;
    }
    idx += 1;
    edgeId = `e-${edge.source}-${edge.target}-${idx}`;
  }
  return edgeId;
}

function mergeNodes(
  current: Map<string, GraphNode>,
  response: GraphResponse,
  seedId: string,
): Map<string, GraphNode> {
  const next = new Map(current);
  for (const node of response.nodes) {
    const isSeed = node.id === seedId;
    const normalized = normalizeNode(node, isSeed);
    const existing = next.get(node.id);
    next.set(node.id, existing ? { ...existing, ...normalized } : normalized);
  }
  return next;
}

function mergeEdges(
  current: Map<string, GraphEdge>,
  response: GraphResponse,
): Map<string, GraphEdge> {
  const next = new Map(current);
  response.edges.forEach((edge, index) => {
    const edgeId = ensureEdgeId(edge, index, next);
    if (!next.has(edgeId)) {
      next.set(edgeId, {
        ...edge,
        id: edgeId,
        type: edge.type || "contaminates",
      });
    }
  });
  return next;
}

export function useProgressiveCascade(): UseProgressiveCascadeReturn {
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

    fetchContaminationCascade(paperId, 1, 15, controller.signal)
      .then((response) => {
        if (controller.signal.aborted) return;
        setSeedId(paperId);
        setNodesMap(mergeNodes(new Map(), response, paperId));
        setEdgesMap(mergeEdges(new Map(), response));
        setExpandedNodes(new Set());
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (!controller.signal.aborted) {
          const message =
            err instanceof Error ? err.message : "Failed to load contamination cascade";
          setError(message);
          setLoading(false);
        }
      });
  }, []);

  const expandNode = useCallback(
    (nodeId: string) => {
      if (!seedId || expandedNodes.has(nodeId) || expandingNodeId) return;

      expandAbortRef.current?.abort();
      const controller = new AbortController();
      expandAbortRef.current = controller;

      setExpandingNodeId(nodeId);

      fetchContaminationCascade(nodeId, 1, 10, controller.signal)
        .then((response) => {
          if (controller.signal.aborted) return;
          setNodesMap((current) => mergeNodes(current, response, seedId));
          setEdgesMap((current) => mergeEdges(current, response));
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
    (nodeId: string) => expandedNodes.has(nodeId),
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
