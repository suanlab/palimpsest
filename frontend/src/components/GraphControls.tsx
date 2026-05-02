import type { ReactNode } from "react";
import type { LayoutName, GraphFilters } from "../types/graph";

interface GraphControlsProps {
  layout: LayoutName;
  onLayoutChange: (layout: LayoutName) => void;
  filters: GraphFilters;
  onFiltersChange: (filters: GraphFilters) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFit: () => void;
  nodeCount: number;
  edgeCount: number;
  children?: ReactNode;
}

const LAYOUT_OPTIONS: { value: LayoutName; label: string }[] = [
  { value: "fcose", label: "Physics" },
  { value: "cose-bilkent", label: "Force-directed" },
  { value: "breadthfirst", label: "Hierarchical" },
  { value: "concentric", label: "Concentric" },
  { value: "circle", label: "Circle" },
  { value: "grid", label: "Grid" },
];

export function GraphControls({
  layout,
  onLayoutChange,
  filters,
  onFiltersChange,
  onZoomIn,
  onZoomOut,
  onFit,
  nodeCount,
  edgeCount,
  children,
}: GraphControlsProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-2 sm:gap-4 px-3 sm:px-5 py-2 sm:py-3 bg-[#1a1a2e]/80 border-b border-[#2a2a4a] backdrop-blur-sm">
      <div className="flex items-center gap-2 sm:gap-3">
        <div className="flex items-center bg-[#0d1b2a] rounded-lg border border-[#2a2a4a] overflow-hidden">
          <button
            type="button"
            onClick={onZoomOut}
            className="px-2.5 py-1.5 text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
            aria-label="Zoom out"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
              <title>Zoom out</title>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 12h-15" />
            </svg>
          </button>
          <button
            type="button"
            onClick={onFit}
            className="px-2.5 py-1.5 text-gray-400 hover:text-white hover:bg-white/5 transition-colors border-x border-[#2a2a4a]"
            aria-label="Fit to view"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
              <title>Fit to view</title>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15" />
            </svg>
          </button>
          <button
            type="button"
            onClick={onZoomIn}
            className="px-2.5 py-1.5 text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
            aria-label="Zoom in"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
              <title>Zoom in</title>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
          </button>
        </div>

        <select
          value={layout}
          onChange={(e) => onLayoutChange(e.target.value as LayoutName)}
          className="bg-[#0d1b2a] border border-[#2a2a4a] rounded-lg px-2 sm:px-3 py-1.5 font-[Outfit] text-xs sm:text-sm text-gray-300 focus:outline-none focus:border-[#00d4ff]/50"
        >
          {LAYOUT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-2 sm:gap-4">
        <label className="flex items-center gap-1.5 sm:gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={filters.showRetracted}
            onChange={(e) =>
              onFiltersChange({ ...filters, showRetracted: e.target.checked })
            }
            className="w-3.5 h-3.5 rounded border-[#2a2a4a] bg-[#0d1b2a] text-[#ff4757] focus:ring-[#ff4757]/25"
          />
          <span className="font-[Outfit] text-[10px] sm:text-xs text-gray-400">Retracted</span>
        </label>
        <label className="hidden sm:flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={filters.showAiRelated}
            onChange={(e) =>
              onFiltersChange({ ...filters, showAiRelated: e.target.checked })
            }
            className="w-3.5 h-3.5 rounded border-[#2a2a4a] bg-[#0d1b2a] text-[#00d4ff] focus:ring-[#00d4ff]/25"
          />
          <span className="font-[Outfit] text-xs text-gray-400">AI-related</span>
        </label>

        <div className="hidden sm:flex items-center gap-2 ml-2 pl-4 border-l border-[#2a2a4a]">
          <span className="font-[JetBrains_Mono] text-[11px] text-gray-500">
            {nodeCount} nodes
          </span>
          <span className="text-gray-700">|</span>
          <span className="font-[JetBrains_Mono] text-[11px] text-gray-500">
            {edgeCount} edges
          </span>
        </div>
        {children}
      </div>
    </div>
  );
}
