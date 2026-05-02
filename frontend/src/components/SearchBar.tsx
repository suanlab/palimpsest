import { useState, useEffect, useRef, useCallback } from "react";
import type { SearchResult } from "../types/graph";
import { searchPapers, searchAuthors } from "../api/graphApi";
import { useAddRecentSearch } from "./RecentSearches";

interface SearchBarProps {
  searchType: "papers" | "authors";
  placeholder?: string;
  onSelect: (result: SearchResult) => void;
}

export function SearchBar({ searchType, placeholder, onSelect }: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const justSelectedRef = useRef(false);
  const addRecentSearch = useAddRecentSearch();
  const search = useCallback(
    async (term: string) => {
      if (term.length < 2) {
        setResults([]);
        setIsOpen(false);
        return;
      }

      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;
      setLoading(true);

      try {
        const searchFn = searchType === "papers" ? searchPapers : searchAuthors;
        const data = await searchFn(term, 10, controller.signal);
        if (!controller.signal.aborted) {
          setResults(data.results);
          setIsOpen(data.results.length > 0);
        }
      } catch {
        if (!controller.signal.aborted) {
          setResults([]);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    },
    [searchType],
  );

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (justSelectedRef.current) {
        justSelectedRef.current = false;
        return;
      }
      search(query);
    }, 300);
    return () => clearTimeout(timeout);
  }, [query, search]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handleSelect(result: SearchResult) {
    justSelectedRef.current = true;
    setQuery(result.title);
    setIsOpen(false);
    setResults([]);
    // Add to recent searches
    addRecentSearch(result.title, searchType === "papers" ? "paper" : "author");
    onSelect(result);
  }

  return (
    <div ref={containerRef} className="relative w-full max-w-lg">
      <div className="relative">
        <svg
          className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
          aria-hidden="true"
        >
          <title>Search</title>
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
        </svg>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder ?? `Search ${searchType}...`}
          className="w-full pl-10 pr-4 py-2.5 bg-[#0d1b2a] border border-[#2a2a4a] rounded-lg font-[Outfit] text-sm text-gray-200 placeholder:text-gray-600 focus:outline-none focus:border-[#00d4ff]/50 focus:ring-1 focus:ring-[#00d4ff]/25 transition-all"
        />
        {loading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 border-2 border-[#00d4ff]/30 border-t-[#00d4ff] rounded-full animate-spin" />
        )}
      </div>

      {isOpen && results.length > 0 && (
        <ul className="absolute z-50 mt-1.5 w-full bg-[#16213e] border border-[#2a2a4a] rounded-lg shadow-2xl max-h-64 overflow-y-auto">
          {results.map((result) => (
            <li key={result.id}>
              <button
                type="button"
                onClick={() => handleSelect(result)}
                className="w-full text-left px-4 py-2.5 hover:bg-white/5 transition-colors"
              >
                <p className="font-[Outfit] text-sm text-gray-200 truncate">
                  {result.title}
                </p>
                <p className="font-[JetBrains_Mono] text-[11px] text-gray-500 mt-0.5">
                  {result.year && <span>{result.year}</span>}
                  {result.cited_by_count !== undefined && (
                    <span className="ml-2">{result.cited_by_count} citations</span>
                  )}
                </p>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
