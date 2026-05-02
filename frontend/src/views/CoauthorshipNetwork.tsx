import { useState, useCallback, useRef, useMemo, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import type cytoscape from "cytoscape";
import type {
  GraphNode,
  GraphEdge,
  GraphFilters,
  LayoutName,
  SearchResult,
  CytoscapeElement,
} from "../types/graph";
import { DEFAULT_FILTERS } from "../types/graph";
import { useProgressiveCoauthorship } from "../hooks/useProgressiveCoauthorship";
import { SearchBar } from "../components/SearchBar";
import { GraphControls } from "../components/GraphControls";
import { GraphView } from "../components/GraphView";
import type { NodeContextMenuEvent } from "../components/GraphView";
import { NodeDetailSidebar } from "../components/NodeDetailSidebar";
import { NodeContextMenu, type ContextMenuAction } from "../components/NodeContextMenu";
import { ErrorState } from "../components/ErrorState";
import { EmptyGraphState } from "../components/EmptyGraphState";
import { ExportMenu } from "../components/ExportMenu";

function applyFilters(
  sourceElements: CytoscapeElement[],
  filters: GraphFilters,
): CytoscapeElement[] {
  const nodes = sourceElements.filter(
    (element): element is { data: GraphNode } => !("source" in element.data),
  );
  const edges = sourceElements.filter(
    (element): element is { data: GraphEdge } => "source" in element.data,
  );

  const filteredNodes = nodes.filter((element) => {
    const node = element.data;
    if (filters.minCitations > 0 && (node.cited_by_count ?? 0) < filters.minCitations) {
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

  const nodeIds = new Set(filteredNodes.map((element) => element.data.id));
  const filteredEdges = edges.filter((element) => {
    const edge = element.data as GraphEdge;
    return nodeIds.has(edge.source) && nodeIds.has(edge.target);
  });

  return [...filteredNodes, ...filteredEdges];
}

export function CoauthorshipNetwork() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [layout, setLayout] = useState<LayoutName>("fcose");
  const [filters, setFilters] = useState<GraphFilters>(DEFAULT_FILTERS);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [contextMenu, setContextMenu] = useState<NodeContextMenuEvent | null>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  const {
    elements,
    loading,
    error,
    seedId,
    initGraph,
    expandNode,
    expandingNodeId,
    isExpanded,
  } = useProgressiveCoauthorship();

  const filteredElements = useMemo(() => {
    return applyFilters(elements, filters);
  }, [elements, filters]);

  const nodeCount = filteredElements.filter((el) => !("source" in el.data)).length;
  const edgeCount = filteredElements.filter((el) => "source" in el.data).length;

  const handleSearch = useCallback((result: SearchResult) => {
    initGraph(result.id);
    setSelectedNode(null);
    setContextMenu(null);
    setSearchParams({ seed: result.id }, { replace: true });
  }, [initGraph, setSearchParams]);

  useEffect(() => {
    const urlSeed = searchParams.get("seed");
    if (urlSeed && !seedId) {
      initGraph(urlSeed);
    } else if (!urlSeed && !seedId) {
      // Geoffrey E. Hinton
      const defaultSeed = "A5108093963";
      initGraph(defaultSeed);
      setSearchParams({ seed: defaultSeed }, { replace: true });
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleNodeClick = useCallback((node: GraphNode) => {
    setSelectedNode(node);
    setContextMenu(null);
  }, []);

  const handleNodeContextMenu = useCallback((event: NodeContextMenuEvent) => {
    setContextMenu(event);
  }, []);

  const closeContextMenu = useCallback(() => {
    setContextMenu(null);
  }, []);

  const handleZoomIn = useCallback(() => {
    cyRef.current?.zoom({ level: (cyRef.current.zoom() ?? 1) * 1.3, renderedPosition: { x: (cyRef.current.width() ?? 0) / 2, y: (cyRef.current.height() ?? 0) / 2 } });
  }, []);
  const handleZoomOut = useCallback(() => {
    cyRef.current?.zoom({ level: (cyRef.current.zoom() ?? 1) / 1.3, renderedPosition: { x: (cyRef.current.width() ?? 0) / 2, y: (cyRef.current.height() ?? 0) / 2 } });
  }, []);
  const handleFit = useCallback(() => {
    cyRef.current?.fit(undefined, 50);
  }, []);

  const contextMenuActions = useMemo<ContextMenuAction[]>(() => {
    if (!contextMenu) return [];
    const node = contextMenu.node;
    const expanded = isExpanded(node.id);
    const isFocal = node.is_focal === true;

    return [
      {
        label: expanded ? "Already Expanded" : "Expand Collaborators",
        icon: (
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <title>Expand</title>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
          </svg>
        ),
        onClick: () => expandNode(node.id),
        disabled: expanded || expandingNodeId === node.id,
      },
      {
        label: "Set as Focal Author",
        icon: (
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <title>Set focal</title>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
          </svg>
        ),
        onClick: () => initGraph(node.id),
        disabled: isFocal,
      },
      {
        label: "View Author Detail",
        icon: (
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <title>Author detail</title>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
          </svg>
        ),
        onClick: () => navigate(`/author/${node.id}`),
        divider: true,
      },
      {
        label: "Show Details",
        icon: (
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <title>Details</title>
            <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
          </svg>
        ),
        onClick: () => setSelectedNode(node),
      },
      {
        label: "Copy Author ID",
        icon: (
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <title>Copy</title>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9.75a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184" />
          </svg>
        ),
        onClick: () => navigator.clipboard.writeText(node.id),
        divider: true,
      },
    ];
  }, [contextMenu, expandNode, expandingNodeId, initGraph, isExpanded, navigate]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-4 px-3 sm:px-5 py-2 sm:py-3 border-b border-[#2a2a4a] bg-[#1a1a2e]/50">
        <h2 className="font-[Outfit] text-lg font-semibold text-white shrink-0">
          Co-authorship Network
        </h2>
        <SearchBar
          searchType="authors"
          placeholder="Search for a seed author..."
          onSelect={handleSearch}
        />
      </div>

      <GraphControls
        layout={layout}
        onLayoutChange={setLayout}
        filters={filters}
        onFiltersChange={setFilters}
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
        onFit={handleFit}
        nodeCount={nodeCount}
        edgeCount={edgeCount}
      >
        <ExportMenu cyRef={cyRef} elements={filteredElements} filenamePrefix="coauthorship_network" />
      </GraphControls>

      <div className="flex flex-1 overflow-hidden">
        {!seedId && !loading && !error && (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-md">
              <div className="w-12 h-12 rounded-full bg-[#2ed573]/10 flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-[#2ed573]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <title>Co-authorship network icon</title>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
                </svg>
              </div>
              <p className="font-[Outfit] text-gray-500">
                Search for an author to explore their collaboration network
              </p>
            </div>
          </div>
        )}

        {loading && (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="w-8 h-8 border-2 border-[#2ed573]/30 border-t-[#2ed573] rounded-full animate-spin mx-auto" />
              <p className="font-[Outfit] text-sm text-gray-500 mt-3">
                Building co-authorship network...
              </p>
            </div>
          </div>
        )}

        {!loading && error && (
          <ErrorState message={error} onRetry={seedId ? () => initGraph(seedId) : undefined} />
        )}

        {!loading && !error && seedId && filteredElements.length === 0 && (
          <EmptyGraphState seedId={seedId} message="No collaborators found for this author." />
        )}

        {!loading && !error && filteredElements.length > 0 && (
          <div className="flex flex-1 overflow-hidden relative">
            <GraphView
              elements={filteredElements}
              layout={layout}
              onNodeClick={handleNodeClick}
              onExpandNode={expandNode}
              onNodeContextMenu={handleNodeContextMenu}
              cyRef={cyRef}
            />
            {selectedNode && (
              <NodeDetailSidebar
                node={selectedNode}
                isExpanded={isExpanded(selectedNode.id)}
                expanding={expandingNodeId === selectedNode.id}
                onExpand={expandNode}
                onClose={() => setSelectedNode(null)}
              />
            )}
            {contextMenu && (
              <NodeContextMenu
                node={contextMenu.node}
                x={contextMenu.x}
                y={contextMenu.y}
                actions={contextMenuActions}
                onClose={closeContextMenu}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
