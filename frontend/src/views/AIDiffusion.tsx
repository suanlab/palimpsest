import { useState, useCallback, useRef, useMemo } from "react";
import type cytoscape from "cytoscape";
import type { GraphNode, GraphFilters, LayoutName } from "../types/graph";
import { DEFAULT_FILTERS } from "../types/graph";
import { fetchAiDiffusion } from "../api/graphApi";
import { useGraphData } from "../hooks/useGraphData";
import { GraphControls } from "../components/GraphControls";
import { GraphView } from "../components/GraphView";
import type { NodeContextMenuEvent } from "../components/GraphView";
import { NodeDetail } from "../components/NodeDetail";
import { NodeContextMenu, type ContextMenuAction } from "../components/NodeContextMenu";
import { ExportMenu } from "../components/ExportMenu";

export function AIDiffusion() {
  const [yearFrom, setYearFrom] = useState(2000);
  const [yearTo, setYearTo] = useState(2024);
  const [method, setMethod] = useState<"title" | "concept">("title");
  const [layout, setLayout] = useState<LayoutName>("concentric");
  const [filters, setFilters] = useState<GraphFilters>(DEFAULT_FILTERS);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [contextMenu, setContextMenu] = useState<NodeContextMenuEvent | null>(null);
  const [autoLoad, setAutoLoad] = useState(true);
  const cyRef = useRef<cytoscape.Core | null>(null);

  const fetcher = useMemo(() => {
    if (!autoLoad) return null;
    return (signal: AbortSignal) =>
      fetchAiDiffusion(yearFrom, yearTo, method, signal);
  }, [yearFrom, yearTo, method, autoLoad]);

  const { elements, loading, error } = useGraphData(fetcher, filters);

  const nodeCount = elements.filter((el) => !("source" in el.data)).length;
  const edgeCount = elements.filter((el) => "source" in el.data).length;

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

    return [
      {
        label: "View Field Details",
        icon: (
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <title>Details</title>
            <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
          </svg>
        ),
        onClick: () => setSelectedNode(node),
      },
      {
        label: "Copy Field ID",
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
  }, [contextMenu]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-4 px-3 sm:px-5 py-2 sm:py-3 border-b border-[#2a2a4a] bg-[#1a1a2e]/50">
        <h2 className="font-[Outfit] text-lg font-semibold text-white shrink-0">
          AI Diffusion
        </h2>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <label htmlFor="ai-year-from" className="font-[Outfit] text-xs text-gray-500">From:</label>
            <input
              id="ai-year-from"
              type="number"
              value={yearFrom}
              onChange={(e) => setYearFrom(Number(e.target.value))}
              min={1950}
              max={yearTo}
              className="w-20 bg-[#0d1b2a] border border-[#2a2a4a] rounded px-2 py-1 font-[JetBrains_Mono] text-xs text-gray-300 focus:outline-none focus:border-[#00d4ff]/50"
            />
          </div>
          <div className="flex items-center gap-2">
            <label htmlFor="ai-year-to" className="font-[Outfit] text-xs text-gray-500">To:</label>
            <input
              id="ai-year-to"
              type="number"
              value={yearTo}
              onChange={(e) => setYearTo(Number(e.target.value))}
              min={yearFrom}
              max={2030}
              className="w-20 bg-[#0d1b2a] border border-[#2a2a4a] rounded px-2 py-1 font-[JetBrains_Mono] text-xs text-gray-300 focus:outline-none focus:border-[#00d4ff]/50"
            />
          </div>
          <div className="flex items-center rounded-lg overflow-hidden border border-[#2a2a4a]">
            <button
              type="button"
              onClick={() => setMethod("title")}
              className={`px-3 py-1.5 font-[Outfit] text-xs font-medium transition-colors ${
                method === "title"
                  ? "bg-[#a855f7] text-white"
                  : "bg-transparent text-gray-400 hover:text-gray-200"
              }`}
            >
              Title-based
            </button>
            <button
              type="button"
              onClick={() => setMethod("concept")}
              className={`px-3 py-1.5 font-[Outfit] text-xs font-medium transition-colors ${
                method === "concept"
                  ? "bg-[#a855f7] text-white"
                  : "bg-transparent text-gray-400 hover:text-gray-200"
              }`}
            >
              Concept-based
            </button>
          </div>
          <button
            type="button"
            onClick={() => setAutoLoad(true)}
            className="px-4 py-1.5 bg-[#a855f7] hover:bg-[#9333ea] text-white font-[Outfit] text-xs font-medium rounded-lg transition-colors"
          >
            Load Network
          </button>
        </div>
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
        <ExportMenu cyRef={cyRef} elements={elements} filenamePrefix="ai_diffusion" />
      </GraphControls>

      <div className="flex flex-1 overflow-hidden">
        {!autoLoad && !loading && !error && (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-md">
              <div className="w-12 h-12 rounded-full bg-[#a855f7]/10 flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-[#a855f7]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <title>AI diffusion icon</title>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
                </svg>
              </div>
              <p className="font-[Outfit] text-gray-500">
                Select a year range and click &ldquo;Load Network&rdquo; to
                visualize how AI methods diffused across scientific fields
              </p>
            </div>
          </div>
        )}

        {loading && (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="w-8 h-8 border-2 border-[#a855f7]/30 border-t-[#a855f7] rounded-full animate-spin mx-auto" />
              <p className="font-[Outfit] text-sm text-gray-500 mt-3">
                Loading AI diffusion network...
              </p>
            </div>
          </div>
        )}

        {error && (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-sm">
              <p className="font-[Outfit] text-sm text-[#ff4757]">{error}</p>
            </div>
          </div>
        )}

        {!loading && !error && elements.length > 0 && (
          <div className="flex flex-1 overflow-hidden relative">
            <GraphView
              elements={elements}
              layout={layout}
              onNodeClick={handleNodeClick}
              onNodeContextMenu={handleNodeContextMenu}
              cyRef={cyRef}
            />
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

        <NodeDetail
          node={selectedNode}
          onClose={() => setSelectedNode(null)}
        />
      </div>
    </div>
  );
}
