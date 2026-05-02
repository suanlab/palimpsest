import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { fetchAutocomplete } from "../api/graphApi";
import type { AutocompleteSuggestion } from "../api/graphApi";

interface SearchInputProps {
  placeholder?: string;
  className?: string;
  onSelect?: (suggestion: AutocompleteSuggestion) => void;
}

export function SearchInput({
  placeholder = "Search papers or authors...",
  className = "",
  onSelect,
}: SearchInputProps) {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<AutocompleteSuggestion[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const navigate = useNavigate();

  const fetchSuggestions = useCallback(async (term: string) => {
    if (term.length < 2) {
      setSuggestions([]);
      setIsOpen(false);
      return;
    }

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setLoading(true);

    try {
      const results = await fetchAutocomplete(term, 8, controller.signal);
      if (!controller.signal.aborted) {
        setSuggestions(results);
        setIsOpen(results.length > 0);
        setHighlightedIndex(-1);
      }
    } catch {
      if (!controller.signal.aborted) {
        setSuggestions([]);
      }
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    const timeout = setTimeout(() => {
      fetchSuggestions(query);
    }, 300);
    return () => clearTimeout(timeout);
  }, [query, fetchSuggestions]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = useCallback(
    (suggestion: AutocompleteSuggestion) => {
      setQuery(suggestion.text);
      setIsOpen(false);

      if (onSelect) {
        onSelect(suggestion);
      } else {
        // Default navigation behavior
        if (suggestion.type === "paper") {
          navigate(`/citation?paper=${encodeURIComponent(suggestion.id)}`);
        } else {
          navigate(`/coauthorship?author=${encodeURIComponent(suggestion.id)}`);
        }
      }
    },
    [navigate, onSelect]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (!isOpen || suggestions.length === 0) return;

      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          setHighlightedIndex((prev) =>
            prev < suggestions.length - 1 ? prev + 1 : prev
          );
          break;
        case "ArrowUp":
          e.preventDefault();
          setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : -1));
          break;
        case "Enter":
          e.preventDefault();
          if (highlightedIndex >= 0 && highlightedIndex < suggestions.length) {
            handleSelect(suggestions[highlightedIndex]);
          }
          break;
        case "Escape":
          setIsOpen(false);
          setHighlightedIndex(-1);
          break;
      }
    },
    [isOpen, suggestions, highlightedIndex, handleSelect]
  );

  const papers = suggestions.filter((s) => s.type === "paper");
  const authors = suggestions.filter((s) => s.type === "author");

  return (
    <div ref={containerRef} className={`relative ${className}`}>
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
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
          />
        </svg>
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            if (suggestions.length > 0) setIsOpen(true);
          }}
          placeholder={placeholder}
          className="w-full pl-10 pr-10 py-2.5 bg-[#0d1b2a] border border-[#2a2a4a] rounded-lg font-[Outfit] text-sm text-gray-200 placeholder:text-gray-600 focus:outline-none focus:border-[#4fc3f7]/50 focus:ring-1 focus:ring-[#4fc3f7]/25 transition-all"
        />
        {loading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 border-2 border-[#4fc3f7]/30 border-t-[#4fc3f7] rounded-full animate-spin" />
        )}
      </div>

      {isOpen && (
        <div className="absolute z-50 mt-1.5 w-full bg-[#16213e] border border-[#2a2a4a] rounded-lg shadow-2xl max-h-80 overflow-y-auto">
          {suggestions.length === 0 && query.length >= 2 && !loading ? (
            <div className="px-4 py-3 font-[Outfit] text-sm text-gray-500">
              No results found
            </div>
          ) : (
            <>
              {papers.length > 0 && (
                <div>
                  <div className="px-3 py-2 font-[Outfit] text-xs font-medium text-[#4fc3f7] uppercase tracking-wider bg-[#0d1b2a]/50">
                    Papers
                  </div>
                  {papers.map((suggestion) => {
                    const globalIdx = suggestions.indexOf(suggestion);
                    return (
                      <button
                        key={suggestion.id}
                        type="button"
                        onClick={() => handleSelect(suggestion)}
                        onMouseEnter={() => setHighlightedIndex(globalIdx)}
                        className={`w-full text-left px-4 py-2.5 transition-colors ${
                          highlightedIndex === globalIdx
                            ? "bg-[#4fc3f7]/10"
                            : "hover:bg-white/5"
                        }`}
                      >
                        <p className="font-[Outfit] text-sm text-gray-200 truncate">
                          {suggestion.text}
                        </p>
                        <p className="font-[JetBrains_Mono] text-[10px] text-gray-500 mt-0.5">
                          Paper
                        </p>
                      </button>
                    );
                  })}
                </div>
              )}

              {authors.length > 0 && (
                <div>
                  <div className="px-3 py-2 font-[Outfit] text-xs font-medium text-[#2ed573] uppercase tracking-wider bg-[#0d1b2a]/50">
                    Authors
                  </div>
                  {authors.map((suggestion) => {
                    const globalIdx = suggestions.indexOf(suggestion);
                    return (
                      <button
                        key={suggestion.id}
                        type="button"
                        onClick={() => handleSelect(suggestion)}
                        onMouseEnter={() => setHighlightedIndex(globalIdx)}
                        className={`w-full text-left px-4 py-2.5 transition-colors ${
                          highlightedIndex === globalIdx
                            ? "bg-[#4fc3f7]/10"
                            : "hover:bg-white/5"
                        }`}
                      >
                        <p className="font-[Outfit] text-sm text-gray-200 truncate">
                          {suggestion.text}
                        </p>
                        <p className="font-[JetBrains_Mono] text-[10px] text-gray-500 mt-0.5">
                          Author
                        </p>
                      </button>
                    );
                  })}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
