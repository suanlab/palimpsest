import { useEffect, useRef } from "react";
import type { GraphNode } from "../types/graph";

export interface ContextMenuAction {
  label: string;
  icon: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
  danger?: boolean;
  divider?: boolean;
}

interface NodeContextMenuProps {
  node: GraphNode;
  x: number;
  y: number;
  actions: ContextMenuAction[];
  onClose: () => void;
}

export function NodeContextMenu({
  node,
  x,
  y,
  actions,
  onClose,
}: NodeContextMenuProps) {
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    }

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onClose();
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [onClose]);

  // Clamp position so menu stays within viewport
  useEffect(() => {
    if (!menuRef.current) return;
    const rect = menuRef.current.getBoundingClientRect();
    const vw = window.innerWidth;
    const vh = window.innerHeight;

    let adjustedX = x;
    let adjustedY = y;

    if (rect.right > vw - 8) {
      adjustedX = vw - rect.width - 8;
    }
    if (rect.bottom > vh - 8) {
      adjustedY = vh - rect.height - 8;
    }

    if (adjustedX !== x || adjustedY !== y) {
      menuRef.current.style.left = `${adjustedX}px`;
      menuRef.current.style.top = `${adjustedY}px`;
    }
  }, [x, y]);

  const title =
    node.label.length > 36 ? `${node.label.slice(0, 36)}…` : node.label;

  return (
    <div
      ref={menuRef}
      className="fixed z-[9999] min-w-[200px] max-w-[260px] rounded-xl border border-[#2a2a4a] bg-[#16213e]/95 backdrop-blur-md shadow-2xl shadow-black/40 py-1.5 animate-in fade-in zoom-in-95 duration-100"
      style={{ left: x, top: y }}
      role="menu"
      aria-label={`Actions for ${node.label}`}
    >
      {/* Header: node title */}
      <div className="px-3 py-2 border-b border-[#2a2a4a]/70">
        <p
          className="font-[Outfit] text-xs font-semibold text-gray-200 truncate"
          title={node.label}
        >
          {title}
        </p>
        {node.year !== undefined && (
          <p className="font-[JetBrains_Mono] text-[10px] text-gray-500 mt-0.5">
            {node.year}
            {node.cited_by_count !== undefined &&
              ` · ${node.cited_by_count.toLocaleString()} citations`}
          </p>
        )}
      </div>

      {/* Menu items */}
      <div className="py-1">
        {actions.map((action, idx) => (
          <div key={action.label}>
            {action.divider && idx > 0 && (
              <div className="my-1 border-t border-[#2a2a4a]/50" />
            )}
            <button
              type="button"
              role="menuitem"
              disabled={action.disabled}
              onClick={() => {
                action.onClick();
                onClose();
              }}
              className={`w-full flex items-center gap-2.5 px-3 py-2 text-left font-[Outfit] text-[13px] transition-colors ${
                action.disabled
                  ? "text-gray-600 cursor-not-allowed"
                  : action.danger
                    ? "text-[#ff4757] hover:bg-[#ff4757]/10"
                    : "text-gray-300 hover:bg-white/7 hover:text-white"
              }`}
            >
              <span className="w-4 h-4 shrink-0 flex items-center justify-center opacity-70">
                {action.icon}
              </span>
              {action.label}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
