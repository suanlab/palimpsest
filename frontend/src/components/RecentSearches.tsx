import { useState, useEffect, useCallback } from "react";

const STORAGE_KEY = "scigraph_recent_searches";
const MAX_ENTRIES = 10;

export interface RecentSearchEntry {
  query: string;
  type: "paper" | "author";
  timestamp: number;
}

function loadRecentSearches(): RecentSearchEntry[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored) as RecentSearchEntry[];
      return Array.isArray(parsed) ? parsed.slice(0, MAX_ENTRIES) : [];
    }
  } catch {
    // Ignore parse errors
  }
  return [];
}

function saveRecentSearches(searches: RecentSearchEntry[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(searches));
  } catch {
    // Ignore storage errors
  }
}

interface RecentSearchesProps {
  onSelect: (entry: RecentSearchEntry) => void;
  onAdd?: (query: string, type: "paper" | "author") => void;
  className?: string;
}

export function RecentSearches({
  onSelect,
  className = "",
}: RecentSearchesProps) {
  const [searches, setSearches] = useState<RecentSearchEntry[]>([]);

  useEffect(() => {
    setSearches(loadRecentSearches());
  }, []);

  const handleRemove = useCallback(
    (index: number, e: React.MouseEvent) => {
      e.stopPropagation();
      const newSearches = searches.filter((_, i) => i !== index);
      setSearches(newSearches);
      saveRecentSearches(newSearches);
    },
    [searches]
  );

  const handleClearAll = useCallback(() => {
    setSearches([]);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const formatTimeAgo = (timestamp: number): string => {
    const seconds = Math.floor((Date.now() - timestamp) / 1000);
    if (seconds < 60) return "Just now";
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d ago`;
    return new Date(timestamp).toLocaleDateString();
  };

  if (searches.length === 0) {
    return null;
  }

  return (
    <div className={`bg-[#16213e] border border-[#2a2a4a] rounded-lg p-3 ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-[Outfit] text-xs font-medium text-gray-400 uppercase tracking-wider">
          Recent Searches
        </h3>
        <button
          type="button"
          onClick={handleClearAll}
          className="font-[Outfit] text-[10px] text-gray-500 hover:text-gray-300 transition-colors"
        >
          Clear all
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {searches.map((entry, index) => (
          <button
            key={`${entry.query}-${entry.timestamp}`}
            type="button"
            onClick={() => onSelect(entry)}
            className="group flex items-center gap-1.5 px-2.5 py-1.5 bg-[#0d1b2a] border border-[#2a2a4a] rounded-full hover:border-[#3a3a5a] transition-all"
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                entry.type === "paper" ? "bg-[#4fc3f7]" : "bg-[#2ed573]"
              }`}
            />
            <span className="font-[Outfit] text-xs text-gray-300 max-w-[120px] truncate">
              {entry.query}
            </span>
            <span className="font-[JetBrains_Mono] text-[9px] text-gray-600">
              {formatTimeAgo(entry.timestamp)}
            </span>
            <button
              type="button"
              onClick={(e) => handleRemove(index, e)}
              className="ml-0.5 w-3.5 h-3.5 flex items-center justify-center rounded-full hover:bg-[#ff4757]/20 text-gray-600 hover:text-[#ff4757] transition-colors"
              aria-label={`Remove ${entry.query}`}
            >
              <svg className="w-2.5 h-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </button>
        ))}
      </div>
    </div>
  );
}

// Hook to add searches to recent history
export function useAddRecentSearch() {
  return useCallback((query: string, type: "paper" | "author") => {
    if (!query.trim()) return;

    const searches = loadRecentSearches();
    const newEntry: RecentSearchEntry = {
      query: query.trim(),
      type,
      timestamp: Date.now(),
    };

    // Remove duplicate entries
    const filtered = searches.filter(
      (s) => s.query.toLowerCase() !== query.trim().toLowerCase()
    );

    // Add new entry at the beginning
    const updated = [newEntry, ...filtered].slice(0, MAX_ENTRIES);
    saveRecentSearches(updated);
  }, []);
}
