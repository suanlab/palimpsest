import { useEffect, useState, useRef, useCallback, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  fetchCitationGraph,
  searchPapers,
  type CitationGraphResponse,
  type CitationGraphNode,
} from "../api/graphApi";
import { ExportMenu } from "../components/ExportMenu";
import type { CytoscapeElement } from "../types/graph";

const ACCENT_COLOR = "#ffa502";
const FOCAL_COLOR = "#2ed573";
const NORMAL_COLOR = "#00d4ff";
const RETRACTED_COLOR = "#ff4757";

interface NodePosition extends CitationGraphNode {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

interface LayoutNode extends NodePosition {
  isCiting: boolean;
  isCited: boolean;
}

function simpleForceLayout(
  nodes: LayoutNode[],
  edges: { source: string; target: string }[],
  width: number,
  height: number,
): LayoutNode[] {
  if (nodes.length === 0) return nodes;

  const focal = nodes.find((n) => n.is_focal);
  if (!focal) return nodes;

  // Place focal node at center
  focal.x = width / 2;
  focal.y = height / 2;
  focal.vx = 0;
  focal.vy = 0;

  // Categorize nodes
  const citingNodes = nodes.filter((n) => n.isCiting && !n.is_focal);
  const citedNodes = nodes.filter((n) => n.isCited && !n.is_focal && !n.isCiting);

  // Place citing nodes above focal
  const citingRadius = Math.min(200, height * 0.3);
  citingNodes.forEach((node, i) => {
    const angle = (Math.PI / (citingNodes.length + 1)) * (i + 1);
    node.x = focal.x + Math.cos(angle - Math.PI / 2) * citingRadius * 1.5;
    node.y = focal.y - citingRadius;
    node.vx = 0;
    node.vy = 0;
  });

  // Place cited nodes below focal
  const citedRadius = Math.min(200, height * 0.3);
  citedNodes.forEach((node, i) => {
    const angle = (Math.PI / (citedNodes.length + 1)) * (i + 1);
    node.x = focal.x + Math.cos(angle + Math.PI / 2) * citedRadius * 1.5;
    node.y = focal.y + citedRadius;
    node.vx = 0;
    node.vy = 0;
  });

  // Simple force simulation
  const iterations = 50;
  const repulsion = 5000;
  const attraction = 0.01;

  for (let iter = 0; iter < iterations; iter++) {
    // Repulsion between all nodes
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[j].x - nodes[i].x;
        const dy = nodes[j].y - nodes[i].y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const force = repulsion / (dist * dist);
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;

        if (!nodes[i].is_focal) {
          nodes[i].vx -= fx;
          nodes[i].vy -= fy;
        }
        if (!nodes[j].is_focal) {
          nodes[j].vx += fx;
          nodes[j].vy += fy;
        }
      }
    }

    // Attraction along edges
    for (const edge of edges) {
      const source = nodes.find((n) => n.id === edge.source);
      const target = nodes.find((n) => n.id === edge.target);
      if (!source || !target) continue;

      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const force = dist * attraction;
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;

      if (!source.is_focal) {
        source.vx += fx;
        source.vy += fy;
      }
      if (!target.is_focal) {
        target.vx -= fx;
        target.vy -= fy;
      }
    }

    // Apply velocities with damping
    const damping = 0.85;
    for (const node of nodes) {
      if (node.is_focal) continue;
      node.vx *= damping;
      node.vy *= damping;
      node.x += node.vx;
      node.y += node.vy;

      // Keep within bounds
      const margin = 50;
      node.x = Math.max(margin, Math.min(width - margin, node.x));
      node.y = Math.max(margin, Math.min(height - margin, node.y));
    }
  }

  return nodes;
}

function SearchPanel({
  onSearch,
  loading,
}: {
  onSearch: (id: string) => void;
  loading: boolean;
}) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<{ id: string; title: string }[]>([]);
  const [searching, setSearching] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    try {
      const res = await searchPapers(query, 10);
      setResults(res.results.map((r) => ({ id: r.id, title: r.title })));
    } catch {
      setResults([]);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="bg-[#16213e] border border-[#2a2a4a] rounded-xl p-4 mb-4">
      <div className="flex items-center gap-3 mb-3">
        <h3 className="font-[Outfit] text-sm font-semibold text-gray-200">
          Search Paper
        </h3>
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          placeholder="Search by title..."
          className="flex-1 bg-[#0d1b2a] border border-[#2a2a4a] rounded-lg px-3 py-2 font-[Outfit] text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-[#ffa502]/50"
        />
        <button
          type="button"
          onClick={handleSearch}
          disabled={searching || !query.trim()}
          className="px-4 py-2 bg-[#ffa502] hover:bg-[#ff7f00] text-white font-[Outfit] text-sm font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {searching ? "Searching..." : "Search"}
        </button>
      </div>
      {results.length > 0 && (
        <div className="mt-3 border border-[#2a2a4a] rounded-lg overflow-hidden max-h-48 overflow-y-auto">
          {results.map((r) => (
            <button
              key={r.id}
              type="button"
              onClick={() => {
                onSearch(r.id);
                setResults([]);
                setQuery("");
              }}
              disabled={loading}
              className="w-full text-left px-3 py-2 hover:bg-[#0d1b2a] transition-colors border-b border-[#2a2a4a]/50 last:border-0"
            >
              <p className="font-[Outfit] text-xs text-gray-300 truncate">
                {r.title}
              </p>
              <p className="font-[JetBrains_Mono] text-[10px] text-gray-500 mt-0.5">
                {r.id}
              </p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function CitationGraphSVG({
  data,
  onNodeClick,
  exportSvgRef,
}: {
  data: CitationGraphResponse;
  onNodeClick: (id: string) => void;
  exportSvgRef?: React.RefObject<SVGSVGElement | null>;
}) {
  const internalSvgRef = useRef<SVGSVGElement>(null);
  const svgRef = exportSvgRef ?? internalSvgRef;
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [hoveredNode, setHoveredNode] = useState<LayoutNode | null>(null);

  useEffect(() => {
    const updateDimensions = () => {
      if (svgRef.current?.parentElement) {
        const rect = svgRef.current.parentElement.getBoundingClientRect();
        setDimensions({ width: rect.width, height: rect.height });
      }
    };
    updateDimensions();
    window.addEventListener("resize", updateDimensions);
    return () => window.removeEventListener("resize", updateDimensions);
  }, []);

  const { nodes, edges } = useMemo(() => {
    // Determine which nodes are citing vs cited
    const citingIds = new Set(
      data.edges.filter((e) => e.target === data.focal_paper.id).map((e) => e.source),
    );
    const citedIds = new Set(
      data.edges.filter((e) => e.source === data.focal_paper.id).map((e) => e.target),
    );

    const layoutNodes: LayoutNode[] = data.nodes.map((n) => ({
      ...n,
      x: dimensions.width / 2,
      y: dimensions.height / 2,
      vx: 0,
      vy: 0,
      isCiting: citingIds.has(n.id),
      isCited: citedIds.has(n.id),
    }));

    const positioned = simpleForceLayout(
      layoutNodes,
      data.edges,
      dimensions.width,
      dimensions.height,
    );

    return { nodes: positioned, edges: data.edges };
  }, [data, dimensions]);

  const maxCitations = Math.max(...nodes.map((n) => n.cited_by_count), 1);

  const getNodeColor = (node: CitationGraphNode) => {
    if (node.is_focal) return FOCAL_COLOR;
    if (node.is_retracted) return RETRACTED_COLOR;
    return NORMAL_COLOR;
  };

  const getNodeRadius = (node: CitationGraphNode) => {
    const base = node.is_focal ? 25 : 12;
    const scale = node.is_focal ? 1 : Math.sqrt(node.cited_by_count / maxCitations) * 0.8 + 0.5;
    return base * scale;
  };

  return (
    <div className="relative w-full h-full min-h-[500px] bg-[#0d1b2a] rounded-xl border border-[#2a2a4a] overflow-hidden">
      <svg
        ref={svgRef}
        viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}
        className="w-full h-full"
      >
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 10 3.5, 0 7" fill="#4a4a6a" />
          </marker>
        </defs>

        {/* Edges */}
        {edges.map((edge, i) => {
          const source = nodes.find((n) => n.id === edge.source);
          const target = nodes.find((n) => n.id === edge.target);
          if (!source || !target) return null;

          const dx = target.x - source.x;
          const dy = target.y - source.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const sourceRadius = getNodeRadius(source);
          const targetRadius = getNodeRadius(target);

          const startX = source.x + (dx / dist) * sourceRadius;
          const startY = source.y + (dy / dist) * sourceRadius;
          const endX = target.x - (dx / dist) * (targetRadius + 5);
          const endY = target.y - (dy / dist) * (targetRadius + 5);

          return (
            <line
              key={`edge-${i}`}
              x1={startX}
              y1={startY}
              x2={endX}
              y2={endY}
              stroke="#4a4a6a"
              strokeWidth={1.5}
              markerEnd="url(#arrowhead)"
            />
          );
        })}

        {/* Nodes */}
        {nodes.map((node) => {
          const radius = getNodeRadius(node);
          const color = getNodeColor(node);
          const isHovered = hoveredNode?.id === node.id;

          return (
            <g
              key={node.id}
              transform={`translate(${node.x}, ${node.y})`}
              onMouseEnter={() => setHoveredNode(node)}
              onMouseLeave={() => setHoveredNode(null)}
              onClick={() => onNodeClick(node.id)}
              style={{ cursor: "pointer" }}
            >
              <circle
                r={radius}
                fill={color}
                stroke={isHovered ? "#ffffff" : "none"}
                strokeWidth={isHovered ? 2 : 0}
                opacity={0.9}
              />
              {node.is_focal && (
                <circle
                  r={radius + 4}
                  fill="none"
                  stroke={color}
                  strokeWidth={2}
                  strokeDasharray="4 2"
                  opacity={0.5}
                />
              )}
              {node.is_focal && (
                <text
                  y={radius + 16}
                  textAnchor="middle"
                  className="font-[Outfit] text-[10px] fill-gray-400"
                >
                  Focal Paper
                </text>
              )}
            </g>
          );
        })}
      </svg>

      {/* Tooltip */}
      {hoveredNode && (
        <div
          className="absolute bg-[#16213e] border border-[#2a2a4a] rounded-lg p-3 shadow-lg pointer-events-none z-10 max-w-xs"
          style={{
            left: Math.min(hoveredNode.x + 20, dimensions.width - 250),
            top: Math.max(hoveredNode.y - 80, 10),
          }}
        >
          <p className="font-[Outfit] text-sm text-gray-200 line-clamp-2">
            {hoveredNode.title}
          </p>
          <div className="flex items-center gap-3 mt-2 font-[JetBrains_Mono] text-[10px] text-gray-500">
            <span>Year: {hoveredNode.year ?? "N/A"}</span>
            <span>Citations: {hoveredNode.cited_by_count.toLocaleString()}</span>
          </div>
          {hoveredNode.is_retracted && (
            <span className="inline-block mt-2 px-2 py-0.5 rounded text-[10px] font-[Outfit] bg-[#ff4757]/20 text-[#ff4757]">
              Retracted
            </span>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-[#16213e]/90 border border-[#2a2a4a] rounded-lg p-3">
        <div className="flex flex-wrap gap-3 text-[10px] font-[Outfit]">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: FOCAL_COLOR }} />
            <span className="text-gray-400">Focal</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: NORMAL_COLOR }} />
            <span className="text-gray-400">Normal</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: RETRACTED_COLOR }} />
            <span className="text-gray-400">Retracted</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export function CitationExplorer() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [graph, setGraph] = useState<CitationGraphResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [limit, setLimit] = useState(50);
  const explorerSvgRef = useRef<SVGSVGElement>(null);

  const loadGraph = useCallback(
    (paperId: string) => {
      setLoading(true);
      setError(null);

      const controller = new AbortController();
      fetchCitationGraph(paperId, 1, limit, controller.signal)
        .then((data) => {
          setGraph(data);
          setLoading(false);
        })
        .catch((err) => {
          if (!controller.signal.aborted) {
            setError(err instanceof Error ? err.message : "Failed to load graph");
            setLoading(false);
          }
        });

      return () => controller.abort();
    },
    [limit],
  );

  useEffect(() => {
    if (id) {
      return loadGraph(id);
    }
    // "Attention Is All You Need" (Vaswani et al.)
    navigate("/explore/W2626778328", { replace: true });
  }, [id, loadGraph, navigate]);

  const handleNodeClick = (nodeId: string) => {
    if (graph && nodeId === graph.focal_paper.id) return;
    navigate(`/explore/${nodeId}`);
  };

  const handleSearch = (paperId: string) => {
    navigate(`/explore/${paperId}`);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center gap-4 px-5 py-3 border-b border-[#2a2a4a] bg-[#1a1a2e]/50">
        <h2 className="font-[Outfit] text-lg font-semibold text-white shrink-0">
          Citation Explorer
        </h2>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <label
              htmlFor="limit-slider"
              className="font-[Outfit] text-xs text-gray-500"
            >
              Limit:
            </label>
            <input
              id="limit-slider"
              type="range"
              min={10}
              max={200}
              step={10}
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="w-24 accent-[#ffa502]"
            />
            <span className="font-[JetBrains_Mono] text-xs text-gray-400 w-8">
              {limit}
            </span>
          </div>
        </div>
        {graph && (
          <ExportMenu
            svgRef={explorerSvgRef}
            elements={graph.nodes.map((n) => ({ data: { ...n, label: n.title, type: "paper" as const } } as CytoscapeElement)).concat(graph.edges.map((e) => ({ data: { ...e, id: `${e.source}-${e.target}` } } as CytoscapeElement)))}
            filenamePrefix="citation_explorer"
          />
        )}
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 border-r border-[#2a2a4a] bg-[#0d1b2a] p-4 overflow-y-auto shrink-0">
          <SearchPanel onSearch={handleSearch} loading={loading} />

          {graph && (
            <div className="bg-[#16213e] border border-[#2a2a4a] rounded-xl p-4 mb-4">
              <h3 className="font-[Outfit] text-sm font-semibold text-gray-200 mb-2">
                Focal Paper
              </h3>
              <p className="font-[Outfit] text-xs text-gray-300 line-clamp-3">
                {graph.focal_paper.title}
              </p>
              <div className="flex items-center gap-3 mt-2 font-[JetBrains_Mono] text-[10px] text-gray-500">
                <span>Year: {graph.focal_paper.year ?? "N/A"}</span>
                <span>
                  Citations: {graph.focal_paper.cited_by_count.toLocaleString()}
                </span>
              </div>
            </div>
          )}

          {graph && (
            <div className="bg-[#16213e] border border-[#2a2a4a] rounded-xl p-4">
              <h3 className="font-[Outfit] text-sm font-semibold text-gray-200 mb-2">
                Graph Stats
              </h3>
              <div className="space-y-2 font-[JetBrains_Mono] text-xs text-gray-400">
                <div className="flex justify-between">
                  <span>Total Nodes</span>
                  <span className="text-gray-200">{graph.nodes.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Total Edges</span>
                  <span className="text-gray-200">{graph.edges.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Citing Papers</span>
                  <span className="text-gray-200">
                    {graph.edges.filter((e) => e.target === graph.focal_paper.id).length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Cited Papers</span>
                  <span className="text-gray-200">
                    {graph.edges.filter((e) => e.source === graph.focal_paper.id).length}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {loading && (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div
                  className="w-10 h-10 border-2 rounded-full animate-spin mx-auto"
                  style={{ borderColor: `${ACCENT_COLOR}30`, borderTopColor: ACCENT_COLOR }}
                />
                <p className="font-[Outfit] text-sm text-gray-500 mt-4">
                  Loading citation graph...
                </p>
              </div>
            </div>
          )}

          {error && (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center max-w-md">
                <div className="w-12 h-12 rounded-full bg-[#ff4757]/10 flex items-center justify-center mx-auto">
                  <svg
                    className="w-6 h-6 text-[#ff4757]"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <title>Error indicator</title>
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
                    />
                  </svg>
                </div>
                <p className="font-[Outfit] text-sm text-gray-400 mt-3">{error}</p>
              </div>
            </div>
          )}

          {!loading && !error && !graph && (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center max-w-md">
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3"
                  style={{ backgroundColor: `${ACCENT_COLOR}15` }}
                >
                  <svg
                    className="w-6 h-6"
                    style={{ color: ACCENT_COLOR }}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={1.5}
                  >
                    <title>Explorer icon</title>
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
                    />
                  </svg>
                </div>
                <p className="font-[Outfit] text-gray-500">
                  Search for a paper to explore its citation network
                </p>
              </div>
            </div>
          )}

          {!loading && !error && graph && (
            <div className="flex-1 p-4">
              <CitationGraphSVG data={graph} onNodeClick={handleNodeClick} exportSvgRef={explorerSvgRef} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
