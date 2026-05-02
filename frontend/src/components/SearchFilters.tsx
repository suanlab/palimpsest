import { useState, useEffect } from "react";
import { fetchStats } from "../api/graphApi";
import type { SearchFilters as SearchFiltersType } from "../api/graphApi";
import type { FieldStat } from "../types/graph";

interface SearchFiltersProps {
  filters: SearchFiltersType;
  onFiltersChange: (filters: SearchFiltersType) => void;
  onApply: () => void;
  className?: string;
}

export function SearchFilters({
  filters,
  onFiltersChange,
  onApply,
  className = "",
}: SearchFiltersProps) {
  const [fields, setFields] = useState<FieldStat[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    const loadFields = async () => {
      try {
        const stats = await fetchStats();
        setFields(stats.fields ?? []);
      } catch {
        // Ignore errors
      }
    };
    loadFields();
  }, []);

  const handleYearFromChange = (value: string) => {
    const year = value === "" ? undefined : parseInt(value, 10);
    if (year === undefined || (!isNaN(year) && year >= 1800 && year <= 2100)) {
      onFiltersChange({ ...filters, yearFrom: year });
    }
  };

  const handleYearToChange = (value: string) => {
    const year = value === "" ? undefined : parseInt(value, 10);
    if (year === undefined || (!isNaN(year) && year >= 1800 && year <= 2100)) {
      onFiltersChange({ ...filters, yearTo: year });
    }
  };

  const handleFieldChange = (field: string) => {
    onFiltersChange({
      ...filters,
      field: filters.field === field ? undefined : field,
    });
  };

  const handleRetractedOnlyChange = (checked: boolean) => {
    onFiltersChange({ ...filters, retractedOnly: checked });
  };

  const hasActiveFilters =
    filters.yearFrom !== undefined ||
    filters.yearTo !== undefined ||
    filters.field !== undefined ||
    filters.retractedOnly === true;

  const handleClearFilters = () => {
    onFiltersChange({});
  };

  return (
    <div className={`bg-[#16213e] border border-[#2a2a4a] rounded-lg ${className}`}>
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-3"
      >
        <div className="flex items-center gap-2">
          <svg
            className="w-4 h-4 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 01-.659 1.591l-5.432 5.432a2.25 2.25 0 00-.659 1.591v2.927a2.25 2.25 0 01-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 00-.659-1.591L3.659 7.409A2.25 2.25 0 013 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0112 3z"
            />
          </svg>
          <span className="font-[Outfit] text-sm font-medium text-gray-300">
            Advanced Filters
          </span>
          {hasActiveFilters && (
            <span className="px-1.5 py-0.5 bg-[#4fc3f7]/20 text-[#4fc3f7] font-[Outfit] text-[10px] font-medium rounded-full">
              Active
            </span>
          )}
        </div>
        <svg
          className={`w-4 h-4 text-gray-500 transition-transform ${
            isExpanded ? "rotate-180" : ""
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isExpanded && (
        <div className="px-4 pb-4 space-y-4 border-t border-[#2a2a4a] pt-3">
          {/* Year Range */}
          <div>
            <label className="font-[Outfit] text-xs font-medium text-gray-400 uppercase tracking-wider">
              Publication Year
            </label>
            <div className="flex items-center gap-2 mt-2">
              <input
                type="number"
                placeholder="From"
                value={filters.yearFrom ?? ""}
                onChange={(e) => handleYearFromChange(e.target.value)}
                className="w-24 px-3 py-1.5 bg-[#0d1b2a] border border-[#2a2a4a] rounded font-[JetBrains_Mono] text-xs text-gray-300 placeholder:text-gray-600 focus:outline-none focus:border-[#4fc3f7]/50"
                min={1800}
                max={2100}
              />
              <span className="font-[Outfit] text-xs text-gray-500">to</span>
              <input
                type="number"
                placeholder="To"
                value={filters.yearTo ?? ""}
                onChange={(e) => handleYearToChange(e.target.value)}
                className="w-24 px-3 py-1.5 bg-[#0d1b2a] border border-[#2a2a4a] rounded font-[JetBrains_Mono] text-xs text-gray-300 placeholder:text-gray-600 focus:outline-none focus:border-[#4fc3f7]/50"
                min={1800}
                max={2100}
              />
            </div>
          </div>

          {/* Field Filter */}
          <div>
            <label className="font-[Outfit] text-xs font-medium text-gray-400 uppercase tracking-wider">
              Field
            </label>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {fields.slice(0, 10).map((field) => (
                <button
                  key={field.name}
                  type="button"
                  onClick={() => handleFieldChange(field.name)}
                  className={`px-2.5 py-1 rounded-full font-[Outfit] text-xs transition-all ${
                    filters.field === field.name
                      ? "bg-[#4fc3f7]/20 text-[#4fc3f7] border border-[#4fc3f7]/50"
                      : "bg-[#0d1b2a] text-gray-400 border border-[#2a2a4a] hover:border-[#3a3a5a]"
                  }`}
                >
                  {field.name}
                </button>
              ))}
            </div>
          </div>

          {/* Retracted Only Toggle */}
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.retractedOnly ?? false}
                onChange={(e) => handleRetractedOnlyChange(e.target.checked)}
                className="w-4 h-4 rounded border-[#2a2a4a] bg-[#0d1b2a] text-[#ff4757] focus:ring-[#4fc3f7]/50 focus:ring-offset-0"
              />
              <span className="font-[Outfit] text-sm text-gray-300">
                Retracted papers only
              </span>
            </label>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-2 border-t border-[#2a2a4a]">
            <button
              type="button"
              onClick={handleClearFilters}
              disabled={!hasActiveFilters}
              className="font-[Outfit] text-xs text-gray-500 hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Clear filters
            </button>
            <button
              type="button"
              onClick={() => {
                onApply();
                setIsExpanded(false);
              }}
              className="px-4 py-1.5 bg-[#4fc3f7] hover:bg-[#4fc3f7]/80 text-[#0d1b2a] font-[Outfit] text-xs font-medium rounded transition-colors"
            >
              Apply Filters
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
