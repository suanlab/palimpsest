import { useRef, useEffect, useCallback, useMemo } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import type cytoscape from "cytoscape";
import {
  forceSimulation,
  forceLink,
  forceManyBody,
  forceCenter,
  forceCollide,
  type SimulationNodeDatum,
  type SimulationLinkDatum,
} from "d3-force";
import type { CytoscapeElement, LayoutName, GraphNode } from "../types/graph";
import { FIELD_COLORS, DEPTH_COLORS } from "../types/graph";

export interface NodeContextMenuEvent {
  node: GraphNode;
  x: number;
  y: number;
}

interface GraphViewProps {
  elements: CytoscapeElement[];
  layout: LayoutName;
  onNodeClick: (node: GraphNode) => void;
  onExpandNode?: (nodeId: string) => void;
  onNodeContextMenu?: (event: NodeContextMenuEvent) => void;
  cyRef?: { current: cytoscape.Core | null };
}

const SVG_PAPER = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>`;
const SVG_AUTHOR = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`;
const SVG_FIELD = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>`;
const SVG_RETRACTED = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;
const SVG_AI = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><circle cx="9" cy="9" r="1.5" fill="white"/><circle cx="15" cy="9" r="1.5" fill="white"/><path d="M9 15c.83.67 1.83 1 3 1s2.17-.33 3-1"/></svg>`;
const SVG_FOCAL = `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`;

function getIconSvg(data: Record<string, unknown>): string {
  if (data.is_focal) return SVG_FOCAL;
  if (data.is_retracted) return SVG_RETRACTED;
  if (data.type === "author") return SVG_AUTHOR;
  if (data.type === "field") return SVG_FIELD;
  if (data.is_ai_related) return SVG_AI;
  return SVG_PAPER;
}

function computeNodeColor(data: GraphNode): string {
  if (data.is_focal) return "#34d399";
  if (data.is_retracted) return "#fb7185";
  if (data.type === "author") return "#a78bfa";
  if (data.type === "field") return "#fbbf24";
  if (data.is_ai_related) return "#22d3ee";
  if (typeof data.depth === "number" && data.depth in DEPTH_COLORS) {
    return DEPTH_COLORS[data.depth];
  }
  if (typeof data.field === "string" && data.field in FIELD_COLORS) {
    return FIELD_COLORS[data.field];
  }
  return "#818cf8";
}

function computeNodeSize(data: GraphNode, degree: number): number {
  const base = data.is_focal ? 54 : 28;
  const citationBoost = Math.log2((data.cited_by_count ?? data.paper_count ?? 0) + 1) * 2;
  const centralityBoost = Math.sqrt(degree) * 4;
  return Math.max(30, Math.min(60, base + citationBoost + centralityBoost));
}

function enrichElements(elements: CytoscapeElement[]): CytoscapeElement[] {
  const degreeMap = new Map<string, number>();
  for (const el of elements) {
    if ("source" in el.data) {
      const s = el.data.source as string;
      const t = el.data.target as string;
      degreeMap.set(s, (degreeMap.get(s) ?? 0) + 1);
      degreeMap.set(t, (degreeMap.get(t) ?? 0) + 1);
    }
  }

  const maxDegree = Math.max(1, ...degreeMap.values());

  return elements.map((el) => {
    if ("source" in el.data) return el;
    const data = el.data as GraphNode;
    const degree = degreeMap.get(data.id) ?? 0;
    const norm = degree / maxDegree;
    return {
      data: {
        ...data,
        _color: computeNodeColor(data),
        _size: computeNodeSize(data, degree),
        _borderW: data.is_focal ? 3 : Math.max(0, norm * 3),
        _borderOpacity: data.is_focal ? 0.6 : Math.max(0, norm * 0.5),
      },
    };
  });
}

function setupHtmlLabels(cy: cytoscape.Core): void {
  const cyAny = cy as unknown as {
    nodeHtmlLabel: (configs: unknown[]) => void;
  };
  if (typeof cyAny.nodeHtmlLabel !== "function") return;

  cyAny.nodeHtmlLabel([
    {
      query: "node",
      valign: "center",
      halign: "center",
      cssClass: "cy-html-icon",
      tpl: (data: Record<string, unknown>) => {
        return `<div class="cy-icon-wrap">${getIconSvg(data)}</div>`;
      },
    },
  ]);
}

const STYLESHEET: cytoscape.StylesheetStyle[] = [
  {
    selector: "node",
    style: {
      label: "data(label)",
      "font-family": "Outfit, sans-serif",
      "font-size": "9px",
      color: "#cbd5e1",
      "text-valign": "bottom",
      "text-halign": "center",
      "text-margin-y": 5,
      "text-max-width": "90px",
      "text-wrap": "ellipsis",
      shape: "ellipse",
      "background-color": "data(_color)",
      "background-opacity": 0.88,
      width: "data(_size)",
      height: "data(_size)",
      "border-width": "data(_borderW)",
      "border-color": "#ffffff",
      "border-opacity": "data(_borderOpacity)",
      "overlay-padding": 4,
      "overlay-opacity": 0,
      "transition-property": "background-opacity, width, height, border-width",
      "transition-duration": 200,
    },
  },
  {
    selector: "node:active",
    style: {
      "overlay-opacity": 0.08,
      "overlay-color": "#ffffff",
    },
  },
  {
    selector: "node.highlighted",
    style: {
      "background-opacity": 1,
      "border-width": 3,
      "border-color": "#ffffff",
      "border-opacity": 0.7,
      "z-index": 10,
    },
  },
  {
    selector: "node[?is_focal]",
    style: {
      "background-opacity": 1,
      "font-size": "11px",
      "font-weight": "bold" as unknown as number,
      color: "#34d399",
      "z-index": 12,
    },
  },
  {
    selector: "edge",
    style: {
      width: 1,
      "line-color": "#475569",
      "target-arrow-color": "#475569",
      "target-arrow-shape": "triangle",
      "arrow-scale": 0.5,
      "curve-style": "bezier",
      opacity: 0.3,
      "line-style": "solid",
      "transition-property": "line-color, opacity, width",
      "transition-duration": 200,
    },
  },
  {
    selector: "edge.highlighted",
    style: {
      "line-color": "#38bdf8",
      "target-arrow-color": "#38bdf8",
      opacity: 0.85,
      width: 2,
    },
  },
  {
    selector: "node.faded",
    style: {
      opacity: 0.1,
    },
  },
  {
    selector: "edge.faded",
    style: {
      opacity: 0.03,
    },
  },
];

function buildLayoutConfig(
  layout: LayoutName,
  nodeCount: number,
): cytoscape.LayoutOptions {
  const isLarge = nodeCount > 40;

  switch (layout) {
    case "fcose":
      return {
        name: "fcose",
        animate: true,
        animationDuration: 1000,
        animationEasing: "ease-out-cubic" as unknown as string,
        quality: isLarge ? "default" : "proof",
        randomize: true,
        nodeDimensionsIncludeLabels: false,
        idealEdgeLength: isLarge ? 110 : 150,
        nodeRepulsion: isLarge ? 10000 : 15000,
        edgeElasticity: 0.4,
        nestingFactor: 0.1,
        gravity: 0.15,
        gravityRange: 4.0,
        numIter: isLarge ? 2500 : 3000,
        tile: false,
        packComponents: true,
      } as cytoscape.LayoutOptions;
    case "cose-bilkent":
      return {
        name: "cose-bilkent",
        animate: !isLarge,
        animationDuration: isLarge ? 0 : 600,
        nodeDimensionsIncludeLabels: true,
        idealEdgeLength: isLarge ? 80 : 120,
        nodeRepulsion: isLarge ? 6000 : 8500,
        edgeElasticity: 0.45,
        nestingFactor: 0.1,
        gravity: isLarge ? 0.4 : 0.25,
        numIter: isLarge ? 1500 : 2500,
        tile: true,
        tilingPaddingVertical: 10,
        tilingPaddingHorizontal: 10,
      } as cytoscape.LayoutOptions;
    case "breadthfirst":
      return {
        name: "breadthfirst",
        animate: !isLarge,
        animationDuration: isLarge ? 0 : 500,
        directed: true,
        spacingFactor: isLarge ? 1.0 : 1.5,
        padding: 30,
      } as cytoscape.LayoutOptions;
    case "concentric":
      return {
        name: "concentric",
        animate: !isLarge,
        animationDuration: isLarge ? 0 : 500,
        minNodeSpacing: isLarge ? 30 : 50,
        concentric: (node: cytoscape.NodeSingular) => {
          return node.data("cited_by_count") ?? node.data("paper_count") ?? 0;
        },
        levelWidth: () => (isLarge ? 3 : 2),
      } as cytoscape.LayoutOptions;
    case "circle":
      return {
        name: "circle",
        animate: !isLarge,
        animationDuration: isLarge ? 0 : 500,
        padding: 40,
      } as cytoscape.LayoutOptions;
    case "grid":
      return {
        name: "grid",
        animate: !isLarge,
        animationDuration: isLarge ? 0 : 500,
        padding: 30,
        condense: true,
      } as cytoscape.LayoutOptions;
  }
}

export function GraphView({
  elements,
  layout,
  onNodeClick,
  onExpandNode,
  onNodeContextMenu,
  cyRef,
}: GraphViewProps) {
  const internalCyRef = useRef<cytoscape.Core | null>(null);
  const tooltipRef = useRef<HTMLDivElement | null>(null);

  const getCy = useCallback((): cytoscape.Core | null => {
    return cyRef?.current ?? internalCyRef.current;
  }, [cyRef]);

  const prevElementCountRef = useRef(0);
  const prevLayoutRef = useRef<LayoutName>(layout);
  const simRef = useRef<ReturnType<typeof forceSimulation> | null>(null);

  const enrichedElements = useMemo(() => enrichElements(elements), [elements]);

  useEffect(() => {
    const cy = getCy();
    if (!cy || enrichedElements.length === 0) return;

    const nodeCount = enrichedElements.filter((el) => !("source" in el.data)).length;
    const layoutChanged = prevLayoutRef.current !== layout;
    const elementsChanged = prevElementCountRef.current !== enrichedElements.length;

    prevElementCountRef.current = enrichedElements.length;
    prevLayoutRef.current = layout;

    if (!layoutChanged && !elementsChanged) return;

    if (simRef.current) {
      simRef.current.stop();
      simRef.current = null;
    }

    if (layout === "fcose") {
      const containerEl = cy.container();
      const w = containerEl?.clientWidth ?? 800;
      const h = containerEl?.clientHeight ?? 600;

      interface D3Node extends SimulationNodeDatum {
        id: string;
      }
      interface D3Link extends SimulationLinkDatum<D3Node> {
        source: string;
        target: string;
      }

      const d3Nodes: D3Node[] = cy.nodes().map((n) => ({
        id: n.id(),
        x: Math.random() * w - w / 2,
        y: Math.random() * h - h / 2,
      }));

      const nodeMap = new Map(d3Nodes.map((n) => [n.id, n]));

      const d3Links: D3Link[] = cy.edges().map((e) => ({
        source: e.source().id(),
        target: e.target().id(),
      }));

      const sim = forceSimulation(d3Nodes)
        .force(
          "link",
          forceLink<D3Node, D3Link>(d3Links)
            .id((d) => d.id)
            .distance(nodeCount > 40 ? 100 : 140),
        )
        .force("charge", forceManyBody().strength(nodeCount > 40 ? -300 : -500))
        .force("center", forceCenter(0, 0))
        .force("collide", forceCollide().radius(25))
        .alphaDecay(0.01)
        .velocityDecay(0.3)
        .on("tick", () => {
          cy.batch(() => {
            cy.nodes().forEach((n) => {
              const d = nodeMap.get(n.id());
              if (d && d.x != null && d.y != null) {
                n.position({ x: d.x, y: d.y });
              }
            });
          });
        });

      simRef.current = sim;

      const handleGrab = (evt: cytoscape.EventObject) => {
        const node = evt.target;
        const d = nodeMap.get(node.id());
        if (d) {
          d.fx = d.x;
          d.fy = d.y;
          sim.alphaTarget(0.3).restart();
        }
      };

      const handleDrag = (evt: cytoscape.EventObject) => {
        const node = evt.target;
        const d = nodeMap.get(node.id());
        if (d) {
          const pos = node.position();
          d.fx = pos.x;
          d.fy = pos.y;
        }
      };

      const handleFree = (evt: cytoscape.EventObject) => {
        const node = evt.target;
        const d = nodeMap.get(node.id());
        if (d) {
          d.fx = null;
          d.fy = null;
          sim.alphaTarget(0);
        }
      };

      cy.on("grab", "node", handleGrab);
      cy.on("drag", "node", handleDrag);
      cy.on("dragfree", "node", handleFree);

      return () => {
        sim.stop();
        simRef.current = null;
        cy.off("grab", "node", handleGrab);
        cy.off("drag", "node", handleDrag);
        cy.off("dragfree", "node", handleFree);
      };
    }

    const layoutConfig = buildLayoutConfig(layout, nodeCount);
    const runLayout = cy.layout(layoutConfig);
    runLayout.run();
    return undefined;
  }, [layout, getCy, enrichedElements]);

  useEffect(() => {
    const cy = getCy();
    if (!cy) return;

    function showTooltip(evt: cytoscape.EventObject) {
      const node = evt.target;
      const data = node.data() as GraphNode;
      const pos = evt.renderedPosition ?? evt.position;

      if (!tooltipRef.current) {
        const el = document.createElement("div");
        el.className = "cy-tooltip";
        document.body.appendChild(el);
        tooltipRef.current = el;
      }

      const tip = tooltipRef.current;
      const typeLabel =
        data.type === "author"
          ? "Author"
          : data.type === "field"
            ? "Field"
            : "Paper";
      const typeColor =
        data.type === "author"
          ? "#a78bfa"
          : data.type === "field"
            ? "#fbbf24"
            : "#22d3ee";

      const lines: string[] = [];
      lines.push(
        `<div class="tooltip-type" style="color:${typeColor}">${typeLabel}</div>`,
      );
      lines.push(`<div class="tooltip-title">${data.label}</div>`);

      const meta: string[] = [];
      if (data.year) meta.push(`${data.year}`);
      if (data.cited_by_count !== undefined)
        meta.push(`${data.cited_by_count.toLocaleString()} citations`);
      if (data.paper_count !== undefined)
        meta.push(`${data.paper_count.toLocaleString()} papers`);
      if (data.is_retracted) meta.push("RETRACTED");
      if (data.is_ai_related) meta.push("AI");
      if (data.field) meta.push(data.field);
      if (meta.length > 0) {
        lines.push(`<div class="tooltip-meta">${meta.join(" · ")}</div>`);
      }

      tip.innerHTML = lines.join("");
      tip.style.display = "block";
      tip.style.left = `${pos.x + 15}px`;
      tip.style.top = `${pos.y - 10}px`;
    }

    function hideTooltip() {
      if (tooltipRef.current) {
        tooltipRef.current.style.display = "none";
      }
    }

    function handleNodeClick(evt: cytoscape.EventObject) {
      const currentCy = getCy();
      if (!currentCy) return;
      const node = evt.target;
      const data = node.data() as GraphNode;

      currentCy.elements().removeClass("highlighted faded");
      node.addClass("highlighted");
      node.connectedEdges().addClass("highlighted");
      node.neighborhood("node").addClass("highlighted");

      currentCy
        .elements()
        .not(node)
        .not(node.connectedEdges())
        .not(node.neighborhood("node"))
        .addClass("faded");

      onNodeClick(data);
    }

    function handleBgClick(evt: cytoscape.EventObject) {
      const currentCy = getCy();
      if (!currentCy) return;
      if (evt.target === currentCy) {
        currentCy.elements().removeClass("highlighted faded");
      }
    }

    function handleNodeDoubleClick(evt: cytoscape.EventObject) {
      const node = evt.target;
      const data = node.data() as GraphNode;
      onExpandNode?.(data.id);
    }

    function handleNodeRightClick(evt: cytoscape.EventObject) {
      evt.originalEvent?.preventDefault();
      const node = evt.target;
      const data = node.data() as GraphNode;
      const renderedPos = node.renderedPosition();
      const container = getCy()?.container();
      if (!container) return;
      const containerRect = container.getBoundingClientRect();
      onNodeContextMenu?.({
        node: data,
        x: containerRect.left + renderedPos.x,
        y: containerRect.top + renderedPos.y,
      });
    }

    cy.on("mouseover", "node", showTooltip);
    cy.on("mouseout", "node", hideTooltip);
    cy.on("tap", "node", handleNodeClick);
    cy.on("dblclick", "node", handleNodeDoubleClick);
    cy.on("cxttap", "node", handleNodeRightClick);
    cy.on("tap", handleBgClick);

    return () => {
      cy.off("mouseover", "node", showTooltip);
      cy.off("mouseout", "node", hideTooltip);
      cy.off("tap", "node", handleNodeClick);
      cy.off("dblclick", "node", handleNodeDoubleClick);
      cy.off("cxttap", "node", handleNodeRightClick);
      cy.off("tap", handleBgClick);
      hideTooltip();
    };
  }, [getCy, onExpandNode, onNodeClick, onNodeContextMenu]);

  const htmlLabelInitRef = useRef(false);

  return (
    <div className="graph-container flex-1" onContextMenu={(e) => e.preventDefault()}>
      <CytoscapeComponent
        elements={enrichedElements}
        stylesheet={STYLESHEET}
        layout={{ name: "preset" }}
        style={{ width: "100%", height: "100%" }}
        cy={(cy) => {
          internalCyRef.current = cy;
          if (cyRef) {
            cyRef.current = cy;
          }
          if (!htmlLabelInitRef.current) {
            htmlLabelInitRef.current = true;
            setupHtmlLabels(cy);
          }
        }}
        minZoom={0.1}
        maxZoom={5}
        wheelSensitivity={0.3}
      />
    </div>
  );
}
