import { useEffect, useMemo, useState, useRef, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import {
  fetchAiDiffusion,
  fetchFieldYearlyExport,
  fetchRetractionStats,
  fetchStats,
  type FieldYearlyExportRow,
} from "../api/graphApi";
import type { StatsResponse } from "../types/graph";

type DiffusionSnapshot = {
  fraction: number;
};

function toPercent(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}

function formatRatePerMillion(value: number): string {
  return `${value.toFixed(1)} / 1M`;
}

function buildTimelinePoints(
  series: FieldYearlyExportRow[],
  key: "ai_title_fraction" | "ai_concept_fraction",
): Array<{ year: number; value: number }> {
  return series
    .filter((row) => row.year >= 2000 && row.year <= 2025)
    .map((row) => ({ year: row.year, value: row[key] * 100 }));
}

function MultiLineChart({
  selectedFields,
  seriesByField,
  colors,
  keyName,
  title,
}: {
  selectedFields: string[];
  seriesByField: Record<string, FieldYearlyExportRow[]>;
  colors: Record<string, string>;
  keyName: "ai_title_fraction" | "ai_concept_fraction";
  title: string;
}) {
  const W = 900;
  const H = 220;
  const PAD = { top: 16, right: 16, bottom: 34, left: 50 };

  const allPoints = selectedFields.flatMap((field) =>
    buildTimelinePoints(seriesByField[field] ?? [], keyName),
  );

  if (allPoints.length === 0) {
    return (
      <div className="rounded-xl border border-[#2a2a4a] bg-[#16213e] p-5">
        <p className="font-[Outfit] text-sm text-gray-500">No timeline data available.</p>
      </div>
    );
  }

  const minYear = Math.min(...allPoints.map((point) => point.year));
  const maxYear = Math.max(...allPoints.map((point) => point.year));
  const maxValue = Math.max(0.1, ...allPoints.map((point) => point.value));
  const yearSpan = maxYear - minYear || 1;

  const x = (year: number) =>
    PAD.left + ((year - minYear) / yearSpan) * (W - PAD.left - PAD.right);
  const y = (value: number) =>
    PAD.top + (1 - value / maxValue) * (H - PAD.top - PAD.bottom);

  const yTicks = [0, maxValue / 2, maxValue];
  const xTicks = allPoints
    .filter((point) => point.year % 5 === 0)
    .map((point) => point.year)
    .filter((year, index, arr) => arr.indexOf(year) === index);

  return (
    <div className="rounded-xl border border-[#2a2a4a] bg-[#16213e] p-5">
      <h3 className="mb-3 font-[Outfit] text-sm font-semibold text-gray-200">{title}</h3>
      <svg viewBox={`0 0 ${W} ${H}`} className="h-auto w-full" role="img" aria-label={title}>
        {yTicks.map((tick) => (
          <g key={tick}>
            <line
              x1={PAD.left}
              y1={y(tick)}
              x2={W - PAD.right}
              y2={y(tick)}
              stroke="#2a2a4a"
              strokeDasharray="3,3"
            />
            <text
              x={PAD.left - 8}
              y={y(tick) + 4}
              textAnchor="end"
              className="fill-gray-500"
              style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 10 }}
            >
              {tick.toFixed(1)}%
            </text>
          </g>
        ))}

        {xTicks.map((tick) => (
          <text
            key={tick}
            x={x(tick)}
            y={H - 8}
            textAnchor="middle"
            className="fill-gray-500"
            style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 10 }}
          >
            {tick}
          </text>
        ))}

        {selectedFields.map((field) => {
          const points = buildTimelinePoints(seriesByField[field] ?? [], keyName);
          if (points.length === 0) return null;
          const polyline = points.map((point) => `${x(point.year)},${y(point.value)}`).join(" ");
          return (
            <polyline
              key={field}
              points={polyline}
              fill="none"
              stroke={colors[field] ?? "#2ed573"}
              strokeWidth={2}
            />
          );
        })}
      </svg>
    </div>
  );
}

function ComparisonBarChart({
  selectedFields,
  data,
  colors,
  title,
  formatValue,
}: {
  selectedFields: string[];
  data: Record<string, number>;
  colors: Record<string, string>;
  title: string;
  formatValue: (v: number) => string;
}) {
  const maxVal = Math.max(0.001, ...selectedFields.map((f) => data[f] ?? 0));

  return (
    <div className="rounded-xl border border-[#2a2a4a] bg-[#16213e] p-5">
      <h3 className="mb-3 font-[Outfit] text-sm font-semibold text-gray-200">{title}</h3>
      <div className="space-y-2.5">
        {selectedFields.map((field) => {
          const val = data[field] ?? 0;
          const pct = (val / maxVal) * 100;
          return (
            <div key={field} className="flex items-center gap-3">
              <span className="font-[Outfit] text-xs text-gray-400 w-28 truncate shrink-0">
                {field}
              </span>
              <div className="flex-1 bg-[#0d1b2a] rounded-full h-4 overflow-hidden relative">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{
                    width: `${pct}%`,
                    backgroundColor: colors[field] ?? "#2ed573",
                    minWidth: val > 0 ? "4px" : "0px",
                  }}
                />
              </div>
              <span className="font-[JetBrains_Mono] text-[11px] text-gray-300 w-20 text-right shrink-0">
                {formatValue(val)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function AnimatedTimeline({
  selectedFields,
  seriesByField,
  colors,
  keyName,
  title,
}: {
  selectedFields: string[];
  seriesByField: Record<string, FieldYearlyExportRow[]>;
  colors: Record<string, string>;
  keyName: "ai_title_fraction" | "ai_concept_fraction";
  title: string;
}) {
  const [playing, setPlaying] = useState(false);
  const [currentYear, setCurrentYear] = useState(2000);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const allPoints = selectedFields.flatMap((field) =>
    buildTimelinePoints(seriesByField[field] ?? [], keyName),
  );

  const minYear = allPoints.length > 0 ? Math.min(...allPoints.map((p) => p.year)) : 2000;
  const maxYear = allPoints.length > 0 ? Math.max(...allPoints.map((p) => p.year)) : 2025;

  const togglePlay = useCallback(() => {
    setPlaying((prev) => {
      if (!prev) {
        setCurrentYear((y) => (y >= maxYear ? minYear : y));
      }
      return !prev;
    });
  }, [maxYear, minYear]);

  useEffect(() => {
    if (playing) {
      timerRef.current = setInterval(() => {
        setCurrentYear((y) => {
          if (y >= maxYear) {
            setPlaying(false);
            return maxYear;
          }
          return y + 1;
        });
      }, 400);
    } else if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [playing, maxYear]);

  if (allPoints.length === 0) {
    return (
      <div className="rounded-xl border border-[#2a2a4a] bg-[#16213e] p-5">
        <p className="font-[Outfit] text-sm text-gray-500">No timeline data available.</p>
      </div>
    );
  }

  const W = 900;
  const H = 250;
  const PAD = { top: 16, right: 16, bottom: 50, left: 50 };
  const maxValue = Math.max(0.1, ...allPoints.map((p) => p.value));
  const yearSpan = maxYear - minYear || 1;

  const xScale = (year: number) =>
    PAD.left + ((year - minYear) / yearSpan) * (W - PAD.left - PAD.right);
  const yScale = (value: number) =>
    PAD.top + (1 - value / maxValue) * (H - PAD.top - PAD.bottom);

  const yTicks = [0, maxValue / 2, maxValue];
  const xTicks = Array.from({ length: Math.floor((maxYear - minYear) / 5) + 1 }, (_, i) => minYear + i * 5).filter((y) => y <= maxYear);

  return (
    <div className="rounded-xl border border-[#2a2a4a] bg-[#16213e] p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-[Outfit] text-sm font-semibold text-gray-200">{title}</h3>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={togglePlay}
            className="flex items-center gap-1.5 px-3 py-1 rounded-lg border border-[#2a2a4a] bg-[#0d1b2a] text-gray-300 hover:text-white hover:border-[#3a3a5a] transition-colors"
          >
            {playing ? (
              <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                <title>Pause</title>
                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
              </svg>
            ) : (
              <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                <title>Play</title>
                <path d="M8 5v14l11-7z" />
              </svg>
            )}
            <span className="font-[Outfit] text-xs">{playing ? "Pause" : "Play"}</span>
          </button>
          <span className="font-[JetBrains_Mono] text-sm text-[#ffa502] font-bold w-12 text-center">
            {currentYear}
          </span>
        </div>
      </div>

      <input
        type="range"
        min={minYear}
        max={maxYear}
        value={currentYear}
        onChange={(e) => { setCurrentYear(Number(e.target.value)); setPlaying(false); }}
        className="w-full mb-3 accent-[#ffa502] h-1.5"
      />

      <svg viewBox={`0 0 ${W} ${H}`} className="h-auto w-full" role="img" aria-label={title}>
        {yTicks.map((tick) => (
          <g key={tick}>
            <line x1={PAD.left} y1={yScale(tick)} x2={W - PAD.right} y2={yScale(tick)} stroke="#2a2a4a" strokeDasharray="3,3" />
            <text x={PAD.left - 8} y={yScale(tick) + 4} textAnchor="end" className="fill-gray-500" style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 10 }}>
              {tick.toFixed(1)}%
            </text>
          </g>
        ))}

        {xTicks.map((tick) => (
          <text key={tick} x={xScale(tick)} y={H - 16} textAnchor="middle" className="fill-gray-500" style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 10 }}>
            {tick}
          </text>
        ))}

        {selectedFields.map((field) => {
          const points = buildTimelinePoints(seriesByField[field] ?? [], keyName)
            .filter((p) => p.year <= currentYear);
          if (points.length === 0) return null;
          const polyline = points.map((p) => `${xScale(p.year)},${yScale(p.value)}`).join(" ");
          const lastPt = points[points.length - 1];
          return (
            <g key={field}>
              <polyline points={polyline} fill="none" stroke={colors[field] ?? "#2ed573"} strokeWidth={2} />
              <circle cx={xScale(lastPt.year)} cy={yScale(lastPt.value)} r={4} fill={colors[field] ?? "#2ed573"} />
              <text x={xScale(lastPt.year) + 8} y={yScale(lastPt.value) + 4} className="fill-gray-300" style={{ fontFamily: "Outfit, sans-serif", fontSize: 10 }}>
                {lastPt.value.toFixed(1)}%
              </text>
            </g>
          );
        })}

        {/* Playback position line */}
        <line x1={xScale(currentYear)} y1={PAD.top} x2={xScale(currentYear)} y2={H - PAD.bottom} stroke="#ffa502" strokeWidth={1.5} strokeDasharray="4,3" opacity={0.7} />
      </svg>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 mt-3">
        {selectedFields.map((field) => (
          <div key={field} className="flex items-center gap-1.5">
            <div className="w-3 h-1 rounded-full" style={{ backgroundColor: colors[field] ?? "#2ed573" }} />
            <span className="font-[Outfit] text-[10px] text-gray-400">{field}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function FieldComparison() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [selectedFields, setSelectedFields] = useState<string[]>(() => {
    const fromUrl = searchParams.get("fields");
    return fromUrl ? fromUrl.split(",").filter(Boolean) : [];
  });
  const [seriesByField, setSeriesByField] = useState<Record<string, FieldYearlyExportRow[]>>({});
  const [titleSnapshot, setTitleSnapshot] = useState<Record<string, DiffusionSnapshot>>({});
  const [conceptSnapshot, setConceptSnapshot] = useState<Record<string, DiffusionSnapshot>>({});
  const [retractionRateByField, setRetractionRateByField] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [timelineLoading, setTimelineLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    const load = async () => {
      try {
        const [statsData, titleData, conceptData, retractionData] = await Promise.all([
          fetchStats(controller.signal),
          fetchAiDiffusion(2000, 2025, "title", controller.signal),
          fetchAiDiffusion(2000, 2025, "concept", controller.signal),
          fetchRetractionStats(controller.signal),
        ]);

        const titleMap = Object.fromEntries(
          titleData.nodes
            .map((node) => {
              const raw = node as unknown as Record<string, unknown>;
              const fieldName = String(raw.name ?? raw.label ?? "");
              const fraction = Number(raw.ai_fraction ?? 0);
              return [fieldName, { fraction }] as const;
            })
            .filter(([fieldName]) => fieldName.length > 0),
        );

        const conceptMap = Object.fromEntries(
          conceptData.nodes
            .map((node) => {
              const raw = node as unknown as Record<string, unknown>;
              const fieldName = String(raw.name ?? raw.label ?? "");
              const fraction = Number(raw.ai_fraction ?? 0);
              return [fieldName, { fraction }] as const;
            })
            .filter(([fieldName]) => fieldName.length > 0),
        );

        const retractionRates = Object.fromEntries(
          retractionData.retraction_rate_by_field.map((item) => [
            item.field_name,
            item.retraction_per_million,
          ]),
        );

        setStats(statsData);
        setTitleSnapshot(titleMap);
        setConceptSnapshot(conceptMap);
        setRetractionRateByField(retractionRates);

        // Only set default fields if no URL params provided
        if (selectedFields.length === 0) {
          const initialFields = statsData.fields.slice(0, 2).map((field) => field.name);
          setSelectedFields(initialFields);
        }
      } catch (err: unknown) {
        if (!controller.signal.aborted) {
          setError(err instanceof Error ? err.message : "Failed to load field comparison");
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    };

    load();
    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (selectedFields.length === 0) return;
    const controller = new AbortController();
    const loadTimeline = async () => {
      setTimelineLoading(true);
      try {
        const rows = await Promise.all(
          selectedFields.map((field) =>
            fetchFieldYearlyExport(field, controller.signal).then((series) => [field, series] as const),
          ),
        );
        if (!controller.signal.aborted) {
          setSeriesByField(Object.fromEntries(rows));
        }
      } catch (err: unknown) {
        if (!controller.signal.aborted) {
          setError(err instanceof Error ? err.message : "Failed to load yearly data");
        }
      } finally {
        if (!controller.signal.aborted) {
          setTimelineLoading(false);
        }
      }
    };

    loadTimeline();
    return () => controller.abort();
  }, [selectedFields]);

  const fieldColors = useMemo(() => {
    return Object.fromEntries((stats?.fields ?? []).map((field) => [field.name, field.color]));
  }, [stats]);

  const toggleField = (fieldName: string) => {
    setSelectedFields((prev) => {
      if (prev.includes(fieldName)) {
        if (prev.length <= 2) return prev;
        return prev.filter((item) => item !== fieldName);
      }
      if (prev.length >= 5) return prev;
      return [...prev, fieldName];
    });
  };

  // P4-18: Sync selected fields to URL
  useEffect(() => {
    if (selectedFields.length > 0) {
      setSearchParams({ fields: selectedFields.join(",") }, { replace: true });
    }
  }, [selectedFields, setSearchParams]);

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <div className="h-9 w-9 animate-spin rounded-full border-2 border-[#2ed573]/25 border-t-[#2ed573]" />
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="font-[Outfit] text-sm text-[#ff6b6b]">{error ?? "Failed to load data"}</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto bg-[#0d1b2a] p-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex items-end justify-between">
          <div>
            <h1 className="font-[Outfit] text-3xl font-bold text-white">Field Comparison</h1>
            <p className="mt-1 font-[Outfit] text-sm text-gray-500">
              Compare publication volume, AI adoption, and retraction rates across fields.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => {
                const url = window.location.href;
                navigator.clipboard.writeText(url);
              }}
              className="rounded-lg border border-[#2a2a4a] bg-[#16213e] px-3 py-1.5 font-[Outfit] text-xs text-gray-400 hover:text-white hover:border-[#3a3a5a] transition-colors"
            >
              Share Link
            </button>
            <div className="rounded-lg border border-[#2ed573]/30 bg-[#2ed573]/10 px-3 py-1.5 font-[JetBrains_Mono] text-xs text-[#2ed573]">
              Select 2-5 fields
            </div>
          </div>
        </div>

        <div className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-5">
          {stats.fields.map((field) => {
            const active = selectedFields.includes(field.name);
            return (
              <button
                key={field.name}
                type="button"
                onClick={() => toggleField(field.name)}
                className={`rounded-lg border px-3 py-2 text-left transition-all ${
                  active
                    ? "border-[#2ed573] bg-[#2ed573]/10"
                    : "border-[#2a2a4a] bg-[#16213e] hover:border-[#3b4b6c]"
                }`}
              >
                <p className="truncate font-[Outfit] text-sm text-gray-200">{field.name}</p>
                <p className="mt-1 font-[JetBrains_Mono] text-[11px] text-gray-500">
                  {field.paper_count.toLocaleString()}
                </p>
              </button>
            );
          })}
        </div>

        <div className="mb-6 grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-3">
          {selectedFields.map((fieldName) => {
            const fieldStats = stats.fields.find((field) => field.name === fieldName);
            const title = titleSnapshot[fieldName];
            const concept = conceptSnapshot[fieldName];
            const retractionRate = retractionRateByField[fieldName] ?? 0;

            return (
              <div key={fieldName} className="rounded-xl border border-[#2a2a4a] bg-[#16213e] p-5">
                <div className="mb-3 flex items-center justify-between">
                  <h2 className="font-[Outfit] text-base font-semibold text-white">{fieldName}</h2>
                  <span
                    className="h-2 w-2 rounded-full"
                    style={{ backgroundColor: fieldColors[fieldName] ?? "#2ed573" }}
                  />
                </div>
                <div className="space-y-2 font-[JetBrains_Mono] text-xs text-gray-400">
                  <div className="flex items-center justify-between">
                    <span>Publications</span>
                    <span className="text-gray-200">{fieldStats?.paper_count.toLocaleString() ?? "0"}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>AI Adoption (Title)</span>
                    <span className="text-[#2ed573]">{toPercent(title?.fraction ?? 0)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>AI Adoption (Concept)</span>
                    <span className="text-[#2ed573]">{toPercent(concept?.fraction ?? 0)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Retraction Rate</span>
                    <span className="text-[#ff6b6b]">{formatRatePerMillion(retractionRate)}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* P4-16: Comparison Bar Charts */}
        <div className="mb-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
          <ComparisonBarChart
            selectedFields={selectedFields}
            data={Object.fromEntries(selectedFields.map((f) => [f, stats.fields.find((s) => s.name === f)?.paper_count ?? 0]))}
            colors={fieldColors}
            title="Publication Volume"
            formatValue={(v) => v.toLocaleString()}
          />
          <ComparisonBarChart
            selectedFields={selectedFields}
            data={Object.fromEntries(selectedFields.map((f) => [f, (titleSnapshot[f]?.fraction ?? 0) * 100]))}
            colors={fieldColors}
            title="AI Adoption % (Title)"
            formatValue={(v) => `${v.toFixed(2)}%`}
          />
          <ComparisonBarChart
            selectedFields={selectedFields}
            data={Object.fromEntries(selectedFields.map((f) => [f, retractionRateByField[f] ?? 0]))}
            colors={fieldColors}
            title="Retraction Rate (/1M)"
            formatValue={(v) => v.toFixed(1)}
          />
        </div>

        {timelineLoading && (
          <div className="mb-4 rounded-xl border border-[#2a2a4a] bg-[#16213e] p-4">
            <p className="font-[Outfit] text-sm text-gray-500">Loading timeline data...</p>
          </div>
        )}

        {/* P4-17: Animated Timeline Charts */}
        <div className="space-y-4">
          <AnimatedTimeline
            selectedFields={selectedFields}
            seriesByField={seriesByField}
            colors={fieldColors}
            keyName="ai_title_fraction"
            title="AI Adoption Timeline — Title Method (Animated)"
          />
          <AnimatedTimeline
            selectedFields={selectedFields}
            seriesByField={seriesByField}
            colors={fieldColors}
            keyName="ai_concept_fraction"
            title="AI Adoption Timeline — Concept Method (Animated)"
          />
        </div>
      </div>
    </div>
  );
}
