import type { GraphNode } from "../types/graph";
import { FIELD_COLORS } from "../types/graph";

interface NodeDetailProps {
  node: GraphNode | null;
  onClose: () => void;
}

function Badge({ label, color }: { label: string; color: string }) {
  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium font-[JetBrains_Mono]"
      style={{ backgroundColor: `${color}20`, color }}
    >
      {label}
    </span>
  );
}

export function NodeDetail({ node, onClose }: NodeDetailProps) {
  if (!node) return null;

  const fieldColor = node.field
    ? (FIELD_COLORS[node.field] ?? "#64748b")
    : "#64748b";

  return (
    <div className="w-80 bg-[#1a1a2e] border-l border-[#2a2a4a] flex flex-col h-full shrink-0 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-[#2a2a4a]">
        <h3 className="font-[Outfit] text-sm font-semibold text-gray-300 truncate">
          Node Details
        </h3>
        <button
          type="button"
          onClick={onClose}
          className="text-gray-500 hover:text-gray-300 transition-colors p-1"
          aria-label="Close detail panel"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <title>Close</title>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div>
          <h4 className="font-[Outfit] text-base font-semibold text-white leading-snug">
            {node.label}
          </h4>
          <div className="flex flex-wrap gap-1.5 mt-2">
            {node.type && <Badge label={node.type} color="#64748b" />}
            {node.is_retracted && <Badge label="RETRACTED" color="#ff4757" />}
            {node.is_ai_related && <Badge label="AI" color="#00d4ff" />}
            {node.field && <Badge label={node.field} color={fieldColor} />}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2">
          {node.year !== undefined && (
            <MetricCard label="Year" value={String(node.year)} />
          )}
          {node.cited_by_count !== undefined && (
            <MetricCard
              label="Citations"
              value={node.cited_by_count.toLocaleString()}
            />
          )}
          {node.paper_count !== undefined && (
            <MetricCard
              label="Papers"
              value={node.paper_count.toLocaleString()}
            />
          )}
          {node.h_index !== undefined && (
            <MetricCard label="h-index" value={String(node.h_index)} />
          )}
          {node.depth !== undefined && (
            <MetricCard label="Depth" value={String(node.depth)} />
          )}
          {node.collaboration_count !== undefined && (
            <MetricCard
              label="Collaborators"
              value={node.collaboration_count.toLocaleString()}
            />
          )}
        </div>

        {node.authors && node.authors.length > 0 && (
          <div>
            <p className="font-[Outfit] text-xs text-gray-500 uppercase tracking-wider mb-1.5">
              Authors
            </p>
            <div className="space-y-1">
              {node.authors.map((author) => (
                <p
                  key={author}
                  className="font-[Outfit] text-sm text-gray-300"
                >
                  {author}
                </p>
              ))}
            </div>
          </div>
        )}

        {node.abstract && (
          <div>
            <p className="font-[Outfit] text-xs text-gray-500 uppercase tracking-wider mb-1.5">
              Abstract
            </p>
            <p className="font-[Outfit] text-sm text-gray-400 leading-relaxed line-clamp-6">
              {node.abstract}
            </p>
          </div>
        )}

        {node.doi && (
          <div>
            <p className="font-[Outfit] text-xs text-gray-500 uppercase tracking-wider mb-1">
              DOI
            </p>
            <a
              href={`https://doi.org/${node.doi}`}
              target="_blank"
              rel="noopener noreferrer"
              className="font-[JetBrains_Mono] text-xs text-[#00d4ff] hover:underline break-all"
            >
              {node.doi}
            </a>
          </div>
        )}

        <div className="pt-2 border-t border-[#2a2a4a]">
          <p className="font-[JetBrains_Mono] text-[10px] text-gray-600 break-all">
            ID: {node.id}
          </p>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-[#0d1b2a] rounded-lg px-3 py-2 border border-[#2a2a4a]/50">
      <p className="font-[Outfit] text-[11px] text-gray-500">{label}</p>
      <p className="font-[JetBrains_Mono] text-lg font-semibold text-white">
        {value}
      </p>
    </div>
  );
}
