import { Link } from "react-router-dom";
import type { GraphNode } from "../types/graph";
import { FIELD_COLORS } from "../types/graph";

interface NodeDetailSidebarProps {
  node: GraphNode | null;
  isExpanded: boolean;
  expanding: boolean;
  onExpand: (nodeId: string) => void;
  onClose: () => void;
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3 py-2 border-b border-[#2a2a4a]/60 last:border-b-0">
      <span className="font-[Outfit] text-xs uppercase tracking-wider text-gray-500">
        {label}
      </span>
      <span className="font-[JetBrains_Mono] text-xs text-gray-200 text-right">
        {value}
      </span>
    </div>
  );
}

function PaperDetails({ node }: { node: GraphNode }) {
  const fieldLabel = node.field ?? "Unclassified";
  const fieldColor = node.field ? (FIELD_COLORS[node.field] ?? "#64748b") : "#64748b";
  const citations = node.cited_by_count ?? 0;

  return (
    <>
      <div>
        <h4 className="font-[Outfit] text-base font-semibold text-white leading-snug">
          {node.label}
        </h4>
        <div className="mt-2 flex items-center gap-2 flex-wrap">
          <span
            className="inline-flex items-center rounded-full px-2 py-0.5 font-[JetBrains_Mono] text-[11px]"
            style={{ backgroundColor: `${fieldColor}20`, color: fieldColor }}
          >
            {fieldLabel}
          </span>
          {node.is_retracted && (
            <span className="inline-flex items-center rounded-full px-2 py-0.5 font-[JetBrains_Mono] text-[11px] bg-[#ff4757]/20 text-[#ff4757]">
              RETRACTED
            </span>
          )}
        </div>
      </div>

      <div className="rounded-lg border border-[#2a2a4a] bg-[#0b1624] px-3">
        <DetailRow label="Year" value={node.year !== undefined ? String(node.year) : "N/A"} />
        <DetailRow label="Citations" value={citations.toLocaleString()} />
        <DetailRow
          label="Retraction"
          value={node.is_retracted ? "Retracted" : "Not retracted"}
        />
        {node.depth !== undefined && (
          <DetailRow label="Depth" value={String(node.depth)} />
        )}
      </div>
    </>
  );
}

function AuthorDetails({ node }: { node: GraphNode }) {
  const raw = node as unknown as Record<string, unknown>;
  const institution = (raw.institution as string | undefined) || node.institution || "N/A";
  const country = (raw.country as string | undefined) || "N/A";
  const paperCount = node.paper_count ?? 0;
  const hIndex = node.h_index;

  return (
    <>
      <div>
        <h4 className="font-[Outfit] text-base font-semibold text-white leading-snug">
          {node.label}
        </h4>
        <div className="mt-2 flex items-center gap-2 flex-wrap">
          <span className="inline-flex items-center rounded-full px-2 py-0.5 font-[JetBrains_Mono] text-[11px] bg-[#2ed573]/20 text-[#2ed573]">
            Author
          </span>
        </div>
      </div>

      <div className="rounded-lg border border-[#2a2a4a] bg-[#0b1624] px-3">
        <DetailRow label="Institution" value={institution} />
        <DetailRow label="Country" value={country} />
        <DetailRow label="Papers" value={paperCount.toLocaleString()} />
        {hIndex !== undefined && (
          <DetailRow label="h-index" value={String(hIndex)} />
        )}
      </div>
    </>
  );
}

export function NodeDetailSidebar({
  node,
  isExpanded,
  expanding,
  onExpand,
  onClose,
}: NodeDetailSidebarProps) {
  if (!node) return null;

  const isAuthor = node.type === "author";
  const headerLabel = isAuthor ? "Author Details" : "Paper Details";
  const expandLabel = isAuthor ? "Collaborators" : "Connections";
  const explorerPath = isAuthor ? `/author/${node.id}` : `/explore/${node.id}`;
  const explorerLabel = isAuthor ? "View Author Detail" : "View in Explorer";
  const idLabel = isAuthor ? "Author ID" : "Paper ID";

  return (
    <aside className="fixed inset-y-0 right-0 z-40 w-[85vw] max-w-80 h-full shrink-0 bg-[#0d1b2a] border-l border-[#2a2a4a] overflow-y-auto transition-all duration-300 shadow-2xl lg:relative lg:inset-auto lg:z-auto lg:w-80 lg:shadow-none">
      <div className="flex items-center justify-between px-4 py-3 border-b border-[#2a2a4a]">
        <h3 className="font-[Outfit] text-sm font-semibold text-gray-200">{headerLabel}</h3>
        <button
          type="button"
          onClick={onClose}
          className="text-gray-500 hover:text-gray-300 transition-colors p-1"
          aria-label="Close detail panel"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <title>Close</title>
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      <div className="p-4 space-y-4">
        {isAuthor ? <AuthorDetails node={node} /> : <PaperDetails node={node} />}

        <button
          type="button"
          onClick={() => onExpand(node.id)}
          disabled={isExpanded || expanding}
          className="w-full rounded-lg px-3 py-2 font-[Outfit] text-sm font-medium transition-colors bg-[#ffa502] text-[#0d1b2a] hover:bg-[#ffb733] disabled:bg-[#2a2a4a] disabled:text-gray-500 disabled:cursor-not-allowed"
        >
          {expanding
            ? "Expanding..."
            : isExpanded
              ? `${expandLabel} Expanded`
              : `Expand ${expandLabel}`}
        </button>

        <Link
          to={explorerPath}
          className="inline-flex items-center gap-2 font-[Outfit] text-sm text-[#7dd3fc] hover:text-[#a5f3fc] transition-colors"
        >
          {explorerLabel}
          <span aria-hidden="true">-&gt;</span>
        </Link>

        {!isAuthor && (
          <Link
            to={`/paper/${node.id}`}
            className="inline-flex items-center gap-2 font-[Outfit] text-sm text-[#ffa502] hover:text-[#ffb733] transition-colors"
          >
            View Paper Page
            <span aria-hidden="true">-&gt;</span>
          </Link>
        )}

        <div className="pt-1 border-t border-[#2a2a4a]">
          <p className="font-[Outfit] text-[11px] uppercase tracking-wider text-gray-500 mb-1">
            {idLabel}
          </p>
          <p className="font-[JetBrains_Mono] text-[11px] text-gray-400 break-all">{node.id}</p>
        </div>
      </div>
    </aside>
  );
}
