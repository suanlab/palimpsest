import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import type { StatsResponse, YearlyCount } from "../types/graph";
import { downloadFieldSummaryCsv, fetchStats } from "../api/graphApi";

function StatCard({
  label,
  value,
  color,
  onClick,
}: {
  label: string;
  value: string;
  color: string;
  onClick?: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={!onClick}
      className="bg-[#16213e] border border-[#2a2a4a] rounded-xl p-5 text-left transition-all hover:border-[#3a3a5a] hover:shadow-lg hover:shadow-black/20 disabled:cursor-default group"
    >
      <p className="font-[Outfit] text-xs text-gray-500 uppercase tracking-wider">
        {label}
      </p>
      <p
        className="font-[JetBrains_Mono] text-2xl font-bold mt-1"
        style={{ color }}
      >
        {value}
      </p>
    </button>
  );
}

function YearlyTimeline({ data }: { data: YearlyCount[] }) {
  const filtered = useMemo(
    () => data.filter((d) => d.year >= 1950 && d.year <= 2025),
    [data],
  );

  if (filtered.length === 0) return null;

  const W = 700;
  const H = 160;
  const PAD = { top: 10, right: 10, bottom: 30, left: 60 };
  const plotW = W - PAD.left - PAD.right;
  const plotH = H - PAD.top - PAD.bottom;

  const maxCount = Math.max(...filtered.map((d) => d.count));
  const minYear = filtered[0].year;
  const maxYear = filtered[filtered.length - 1].year;
  const yearSpan = maxYear - minYear || 1;

  const x = (year: number) =>
    PAD.left + ((year - minYear) / yearSpan) * plotW;
  const y = (count: number) =>
    PAD.top + plotH - (count / maxCount) * plotH;

  const linePts = filtered.map((d) => `${x(d.year)},${y(d.count)}`).join(" ");
  const areaPts = `${x(minYear)},${PAD.top + plotH} ${linePts} ${x(maxYear)},${PAD.top + plotH}`;

  const yTicks = [0, Math.round(maxCount / 2), maxCount];
  const xTicks = filtered.filter((d) => d.year % 10 === 0);

  return (
    <div className="bg-[#16213e] border border-[#2a2a4a] rounded-xl p-6 mb-6">
      <h2 className="font-[Outfit] text-base font-semibold text-gray-300 mb-4">
        Yearly Publications (1950–2025)
      </h2>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto" role="img" aria-labelledby="yearly-chart-title">
        <title id="yearly-chart-title">Yearly publication count trend from 1950 to 2025</title>
        <defs>
          <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#00d4ff" stopOpacity={0.3} />
            <stop offset="100%" stopColor="#00d4ff" stopOpacity={0.02} />
          </linearGradient>
        </defs>
        {yTicks.map((tick) => (
          <g key={tick}>
            <line
              x1={PAD.left}
              y1={y(tick)}
              x2={W - PAD.right}
              y2={y(tick)}
              stroke="#2a2a4a"
              strokeDasharray="4,4"
            />
            <text
              x={PAD.left - 8}
              y={y(tick) + 4}
              textAnchor="end"
              className="fill-gray-500"
              style={{ fontSize: 10, fontFamily: "JetBrains Mono, monospace" }}
            >
              {tick >= 1_000_000
                ? `${(tick / 1_000_000).toFixed(1)}M`
                : tick >= 1_000
                  ? `${(tick / 1_000).toFixed(0)}K`
                  : tick}
            </text>
          </g>
        ))}
        {xTicks.map((d) => (
          <text
            key={d.year}
            x={x(d.year)}
            y={H - 5}
            textAnchor="middle"
            className="fill-gray-500"
            style={{ fontSize: 10, fontFamily: "JetBrains Mono, monospace" }}
          >
            {d.year}
          </text>
        ))}
        <polygon points={areaPts} fill="url(#areaGrad)" />
        <polyline
          points={linePts}
          fill="none"
          stroke="#00d4ff"
          strokeWidth={1.5}
        />
      </svg>
    </div>
  );
}

export function Dashboard() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);
  const navigate = useNavigate();

  const handleExportFieldSummary = async () => {
    try {
      setExporting(true);
      await downloadFieldSummaryCsv();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to export field summary";
      setError(message);
    } finally {
      setExporting(false);
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    fetchStats(controller.signal)
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (!controller.signal.aborted) {
          const message =
            err instanceof Error ? err.message : "Failed to load stats";
          setError(message);
          setLoading(false);
        }
      });
    return () => controller.abort();
  }, []);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="w-10 h-10 border-2 border-[#00d4ff]/30 border-t-[#00d4ff] rounded-full animate-spin mx-auto" />
          <p className="font-[Outfit] text-sm text-gray-500 mt-4">
            Loading platform statistics...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="w-12 h-12 rounded-full bg-[#ff4757]/10 flex items-center justify-center mx-auto">
            <svg className="w-6 h-6 text-[#ff4757]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <title>Error indicator</title>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
          </div>
          <p className="font-[Outfit] text-sm text-gray-400 mt-3">{error}</p>
          <p className="font-[JetBrains_Mono] text-xs text-gray-600 mt-1">
            Ensure the backend is running at{" "}
            {import.meta.env.VITE_API_URL ?? "http://localhost:8300"}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="font-[Outfit] text-3xl font-bold text-white tracking-tight">
            SuanAI SciGraph
          </h1>
          <p className="font-[Outfit] text-sm text-gray-500 mt-1">
            Science of Science research platform
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-10">
          <StatCard
            label="Total Papers"
            value={stats?.total_papers.toLocaleString() ?? "—"}
            color="#00d4ff"
            onClick={() => navigate("/citation")}
          />
          <StatCard
            label="Total Authors"
            value={stats?.total_authors.toLocaleString() ?? "—"}
            color="#2ed573"
            onClick={() => navigate("/coauthorship")}
          />
          <StatCard
            label="Citations"
            value={stats?.total_citations.toLocaleString() ?? "—"}
            color="#ffa502"
          />
          <StatCard
            label="Retracted"
            value={stats?.total_retracted.toLocaleString() ?? "—"}
            color="#ff4757"
            onClick={() => navigate("/contamination")}
          />
          <StatCard
            label="AI Papers (Title)"
            value={stats?.ai_related_papers.toLocaleString() ?? "—"}
            color="#a855f7"
            onClick={() => navigate("/ai-diffusion")}
          />
          <StatCard
            label="AI Papers (Concept)"
            value={stats?.ai_concept_papers.toLocaleString() ?? "—"}
            color="#c084fc"
            onClick={() => navigate("/ai-diffusion")}
          />
        </div>

        {stats?.yearly_publications && stats.yearly_publications.length > 0 && (
          <YearlyTimeline data={stats.yearly_publications} />
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-[#16213e] border border-[#2a2a4a] rounded-xl p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-[Outfit] text-base font-semibold text-gray-300">
                Fields Overview
              </h2>
              <button
                type="button"
                onClick={() => void handleExportFieldSummary()}
                disabled={exporting}
                className="rounded-md border border-[#2a2a4a] bg-[#0d1b2a] px-2.5 py-1 font-[Outfit] text-xs text-gray-300 transition-colors hover:border-[#3a3a5a] hover:text-white disabled:cursor-not-allowed disabled:opacity-60"
              >
                {exporting ? "Exporting..." : "Export"}
              </button>
            </div>
            {stats?.fields && stats.fields.length > 0 ? (
              <div className="space-y-3">
                {stats.fields.map((field) => {
                  const maxCount = Math.max(
                    1,
                    ...stats.fields.map((f) => f.paper_count),
                  );
                  const width = (field.paper_count / maxCount) * 100;
                  return (
                    <div key={field.name} className="flex items-center gap-3">
                      <span className="font-[Outfit] text-xs text-gray-400 w-32 truncate shrink-0">
                        {field.name}
                      </span>
                      <div className="flex-1 bg-[#0d1b2a] rounded-full h-2 overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-500"
                          style={{
                            width: `${width}%`,
                            backgroundColor: field.color,
                          }}
                        />
                      </div>
                      <span className="font-[JetBrains_Mono] text-[11px] text-gray-500 w-16 text-right shrink-0">
                        {field.paper_count.toLocaleString()}
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="font-[Outfit] text-sm text-gray-600">
                No field data available
              </p>
            )}
          </div>

          <div className="bg-[#16213e] border border-[#2a2a4a] rounded-xl p-6">
            <h2 className="font-[Outfit] text-base font-semibold text-gray-300 mb-4">
              Quick Navigation
            </h2>
            <div className="grid grid-cols-2 gap-3">
              {[
                {
                  label: "Citation Network",
                  desc: "Paper citation relationships",
                  path: "/citation",
                  color: "#00d4ff",
                },
                {
                  label: "Co-authorship",
                  desc: "Author collaboration graph",
                  path: "/coauthorship",
                  color: "#2ed573",
                },
                {
                  label: "Retraction Cascade",
                  desc: "Contamination spread analysis",
                  path: "/contamination",
                  color: "#ff4757",
                },
                {
                  label: "AI Diffusion",
                  desc: "Cross-field AI adoption flow",
                  path: "/ai-diffusion",
                  color: "#a855f7",
                },
                {
                  label: "Field Comparison",
                  desc: "Side-by-side field metrics",
                  path: "/field-comparison",
                  color: "#2ed573",
                },
              ].map((item) => (
                <button
                  key={item.path}
                  type="button"
                  onClick={() => navigate(item.path)}
                  className="text-left p-4 bg-[#0d1b2a] rounded-lg border border-[#2a2a4a]/50 hover:border-[#3a3a5a] transition-all group"
                >
                  <p
                    className="font-[Outfit] text-sm font-medium"
                    style={{ color: item.color }}
                  >
                    {item.label}
                  </p>
                  <p className="font-[Outfit] text-xs text-gray-600 mt-0.5">
                    {item.desc}
                  </p>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
