import { NavLink, useNavigate } from "react-router-dom";
import { useState, useCallback } from "react";
import { SearchInput } from "./SearchInput";
import { useAddRecentSearch, type RecentSearchEntry } from "./RecentSearches";
import type { AutocompleteSuggestion } from "../api/graphApi";


const NAV_ITEMS = [
  {
    to: "/",
    label: "Dashboard",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5} aria-hidden="true">
        <title>Dashboard</title>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
      </svg>
    ),
  },
  {
    to: "/citation",
    label: "Citation Network",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5} aria-hidden="true">
        <title>Citation Network</title>
        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
      </svg>
    ),
  },
  {
    to: "/coauthorship",
    label: "Co-authorship",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5} aria-hidden="true">
        <title>Co-authorship</title>
        <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
      </svg>
    ),
  },
  {
    to: "/contamination",
    label: "Retraction Cascade",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5} aria-hidden="true">
        <title>Retraction Cascade</title>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
      </svg>
    ),
  },
  {
    to: "/ai-diffusion",
    label: "AI Diffusion",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5} aria-hidden="true">
        <title>AI Diffusion</title>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
      </svg>
    ),
  },
  {
    to: "/field-comparison",
    label: "Field Comparison",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5} aria-hidden="true">
        <title>Field Comparison</title>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 5.25h16.5M3.75 12h16.5M3.75 18.75h16.5M7.5 3.75v16.5M16.5 3.75v16.5" />
      </svg>
    ),
  },
  {
    to: "/explore",
    label: "Citation Explorer",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5} aria-hidden="true">
        <title>Citation Explorer</title>
        <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
      </svg>
    ),
  },
  {
    to: "/help",
    label: "Help & Guide",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5} aria-hidden="true">
        <title>Help</title>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
      </svg>
    ),
  },
];

function SearchInputWrapper({ onNavigate }: { onNavigate?: () => void }) {
  const navigate = useNavigate();
  const addRecentSearch = useAddRecentSearch();

  const handleSelect = useCallback(
    (suggestion: AutocompleteSuggestion) => {
      addRecentSearch(suggestion.text, suggestion.type);
      if (suggestion.type === "paper") {
        navigate(`/citation?paper=${encodeURIComponent(suggestion.id)}`);
      } else {
        navigate(`/coauthorship?author=${encodeURIComponent(suggestion.id)}`);
      }
      onNavigate?.();
    },
    [navigate, addRecentSearch, onNavigate]
  );

  return (
    <SearchInput
      placeholder="Search papers or authors..."
      onSelect={handleSelect}
      className="w-full"
    />
  );
}

function RecentSearchesMini() {
  const navigate = useNavigate();
  const [searches, setSearches] = useState<RecentSearchEntry[]>([]);

  // Load searches on mount
  useState(() => {
    const stored = localStorage.getItem("scigraph_recent_searches");
    if (stored) {
      try {
        setSearches(JSON.parse(stored).slice(0, 5));
      } catch {
        // Ignore
      }
    }
  });

  const handleSelect = useCallback(
    (entry: RecentSearchEntry) => {
      if (entry.type === "paper") {
        navigate(`/citation?q=${encodeURIComponent(entry.query)}`);
      } else {
        navigate(`/coauthorship?q=${encodeURIComponent(entry.query)}`);
      }
    },
    [navigate]
  );

  if (searches.length === 0) return null;

  return (
    <div className="space-y-1">
      <p className="font-[Outfit] text-[10px] text-gray-600 uppercase tracking-wider px-1">
        Recent
      </p>
      {searches.slice(0, 3).map((entry, idx) => (
        <button
          key={`${entry.query}-${idx}`}
          type="button"
          onClick={() => handleSelect(entry)}
          className="w-full flex items-center gap-2 px-2 py-1.5 rounded text-left hover:bg-white/5 transition-colors"
        >
          <span
            className={`w-1.5 h-1.5 rounded-full shrink-0 ${
              entry.type === "paper" ? "bg-[#4fc3f7]" : "bg-[#2ed573]"
            }`}
          />
          <span className="font-[Outfit] text-xs text-gray-400 truncate">
            {entry.query}
          </span>
        </button>
      ))}
    </div>
  );
}

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <aside className="w-64 bg-[#1a1a2e] border-r border-[#2a2a4a] flex flex-col h-full shrink-0">
      <div className="p-5 border-b border-[#2a2a4a]">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#00d4ff] to-[#a855f7] flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
              <title>SciGraph logo</title>
              <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
            </svg>
          </div>
          <div>
            <h1 className="font-[Outfit] text-base font-semibold text-white tracking-tight">
              SuanAI
            </h1>
            <p className="font-[Outfit] text-[11px] text-gray-500 tracking-widest uppercase">
              SciGraph
            </p>
          </div>
        </div>
      </div>

      {/* Global Search */}
      <div className="px-3 py-3 border-b border-[#2a2a4a]">
        <SearchInputWrapper onNavigate={onNavigate} />
      </div>

      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            onClick={onNavigate}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg font-[Outfit] text-sm transition-all duration-200 ${
                isActive
                  ? "nav-link-active bg-[#00d4ff]/8 text-[#00d4ff]"
                  : "text-gray-400 hover:text-gray-200 hover:bg-white/4"
              }`
            }
          >
            {item.icon}
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Recent Searches */}
      <div className="px-3 py-2 border-t border-[#2a2a4a]">
        <RecentSearchesMini />
      </div>

      <div className="p-4 border-t border-[#2a2a4a]">
        <p className="font-[JetBrains_Mono] text-[10px] text-gray-600 text-center">
          v0.2.0 - SuanAI SciGraph
        </p>
      </div>
    </aside>
  );
}
