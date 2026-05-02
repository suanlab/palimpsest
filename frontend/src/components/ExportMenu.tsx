import { useState, useRef, useEffect, useCallback } from "react";
import type cytoscape from "cytoscape";
import type { CytoscapeElement, GraphNode, GraphEdge } from "../types/graph";

interface ExportMenuProps {
  /** Cytoscape instance ref (for PNG/SVG graph export). */
  cyRef?: { current: cytoscape.Core | null };
  /** SVG element ref (for CitationExplorer SVG export). */
  svgRef?: React.RefObject<SVGSVGElement | null>;
  /** Current visible elements (for CSV export). */
  elements: CytoscapeElement[];
  /** Optional filename prefix. */
  filenamePrefix?: string;
}

function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function timestamp(): string {
  const d = new Date();
  return `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, "0")}${String(d.getDate()).padStart(2, "0")}_${String(d.getHours()).padStart(2, "0")}${String(d.getMinutes()).padStart(2, "0")}`;
}

function escapeCsvField(value: string): string {
  if (value.includes(",") || value.includes('"') || value.includes("\n")) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

export function ExportMenu({
  cyRef,
  svgRef,
  elements,
  filenamePrefix = "scigraph",
}: ExportMenuProps) {
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) return;

    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open]);

  const exportPng = useCallback(() => {
    const cy = cyRef?.current;
    if (!cy) return;

    const dataUri = cy.png({
      full: true,
      bg: "#0d1b2a",
      scale: 2,
      maxWidth: 4096,
      maxHeight: 4096,
    });

    // Convert data URI to Blob
    const byteString = atob(dataUri.split(",")[1]);
    const mimeType = "image/png";
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    const blob = new Blob([ab], { type: mimeType });
    triggerDownload(blob, `${filenamePrefix}_${timestamp()}.png`);
    setOpen(false);
  }, [cyRef, filenamePrefix]);

  const exportSvg = useCallback(() => {
    // Cytoscape SVG export
    const cy = cyRef?.current;
    if (cy) {
      const svgContent = cy.svg({ full: true, bg: "#0d1b2a" });
      const blob = new Blob([svgContent], { type: "image/svg+xml" });
      triggerDownload(blob, `${filenamePrefix}_${timestamp()}.svg`);
      setOpen(false);
      return;
    }

    // SVG element export (CitationExplorer)
    const svgEl = svgRef?.current;
    if (svgEl) {
      const serializer = new XMLSerializer();
      const svgString = serializer.serializeToString(svgEl);
      const blob = new Blob([svgString], { type: "image/svg+xml" });
      triggerDownload(blob, `${filenamePrefix}_${timestamp()}.svg`);
      setOpen(false);
    }
  }, [cyRef, svgRef, filenamePrefix]);

  const exportCsv = useCallback(() => {
    const nodes = elements.filter(
      (el): el is { data: GraphNode } => !("source" in el.data),
    );
    const edges = elements.filter(
      (el): el is { data: GraphEdge } => "source" in el.data,
    );

    // Build nodes CSV
    const nodeHeaders = [
      "id",
      "label",
      "type",
      "year",
      "cited_by_count",
      "field",
      "is_retracted",
    ];
    const nodeRows = nodes.map((n) => {
      const d = n.data;
      return [
        d.id,
        escapeCsvField(d.label ?? ""),
        d.type ?? "",
        d.year !== undefined ? String(d.year) : "",
        d.cited_by_count !== undefined ? String(d.cited_by_count) : "",
        escapeCsvField(d.field ?? ""),
        d.is_retracted ? "true" : "false",
      ].join(",");
    });
    const nodesCsv = [nodeHeaders.join(","), ...nodeRows].join("\n");

    // Build edges CSV
    const edgeHeaders = ["source", "target", "type", "weight", "year"];
    const edgeRows = edges.map((e) => {
      const d = e.data;
      return [
        d.source,
        d.target,
        d.type ?? "",
        d.weight !== undefined ? String(d.weight) : "",
        d.year !== undefined ? String(d.year) : "",
      ].join(",");
    });
    const edgesCsv = [edgeHeaders.join(","), ...edgeRows].join("\n");

    const combined = `=== NODES ===\n${nodesCsv}\n\n=== EDGES ===\n${edgesCsv}`;
    const blob = new Blob([combined], { type: "text/csv;charset=utf-8" });
    triggerDownload(blob, `${filenamePrefix}_${timestamp()}.csv`);
    setOpen(false);
  }, [elements, filenamePrefix]);

  const hasCy = !!cyRef;
  const hasSvg = !!svgRef;
  const canExportImage = hasCy || hasSvg;

  return (
    <div ref={menuRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-[#2a2a4a] bg-[#0d1b2a]/80 backdrop-blur-sm text-gray-400 hover:text-white hover:border-[#3a3a5a] transition-colors"
        aria-label="Export graph"
        title="Export"
      >
        <svg
          className="w-4 h-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <title>Export</title>
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"
          />
        </svg>
        <span className="font-[Outfit] text-xs hidden sm:inline">Export</span>
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-1 z-50 min-w-[160px] rounded-xl border border-[#2a2a4a] bg-[#16213e]/95 backdrop-blur-md shadow-2xl shadow-black/40 py-1.5 animate-in fade-in zoom-in-95 duration-100">
          {canExportImage && (
            <>
              <button
                type="button"
                onClick={exportPng}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-left font-[Outfit] text-[13px] text-gray-300 hover:bg-white/7 hover:text-white transition-colors"
              >
                <svg
                  className="w-4 h-4 opacity-70"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <title>PNG</title>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.41a2.25 2.25 0 013.182 0l2.909 2.91m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z"
                  />
                </svg>
                Export PNG
              </button>
              <button
                type="button"
                onClick={exportSvg}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-left font-[Outfit] text-[13px] text-gray-300 hover:bg-white/7 hover:text-white transition-colors"
              >
                <svg
                  className="w-4 h-4 opacity-70"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <title>SVG</title>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5"
                  />
                </svg>
                Export SVG
              </button>
              <div className="my-1 border-t border-[#2a2a4a]/50" />
            </>
          )}
          <button
            type="button"
            onClick={exportCsv}
            className="w-full flex items-center gap-2.5 px-3 py-2 text-left font-[Outfit] text-[13px] text-gray-300 hover:bg-white/7 hover:text-white transition-colors"
          >
            <svg
              className="w-4 h-4 opacity-70"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <title>CSV</title>
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-7.5A1.125 1.125 0 0112 18.375m9.75-12.75c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125m19.5 0v1.5c0 .621-.504 1.125-1.125 1.125M2.25 5.625v1.5c0 .621.504 1.125 1.125 1.125m0 0h17.25m-17.25 0h7.5c.621 0 1.125.504 1.125 1.125M3.375 8.25c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m17.25-3.75h-7.5c-.621 0-1.125.504-1.125 1.125m8.625-1.125c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M12 10.875v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125M12 12h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125M21 12c0 .621-.504 1.125-1.125 1.125m-5.25 0c.621 0 1.125.504 1.125 1.125m-12.75-1.125c-.621 0-1.125.504-1.125 1.125m19.5-1.125c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125M2.25 14.625v1.5c0 .621.504 1.125 1.125 1.125m17.25 0h-7.5c-.621 0-1.125-.504-1.125-1.125m8.625 1.125c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m-17.25 0h7.5m-7.5 0c-.621 0-1.125-.504-1.125-1.125"
              />
            </svg>
            Export CSV
          </button>
        </div>
      )}
    </div>
  );
}
