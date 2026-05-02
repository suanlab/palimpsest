import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  fetchPaperDetail,
  type PaperDetailResponse,
  type PaperDetailAuthor,
  type PaperDetailReference,
} from "../api/graphApi";

const ACCENT_COLOR = "#ffa502";

function StatCard({
  label,
  value,
}: {
  label: string;
  value: string | number | null;
}) {
  return (
    <div className="bg-[#16213e] border border-[#2a2a4a] rounded-xl p-4 text-center">
      <p className="font-[Outfit] text-xs text-gray-500 uppercase tracking-wider">
        {label}
      </p>
      <p
        className="font-[JetBrains_Mono] text-xl font-bold mt-1"
        style={{ color: ACCENT_COLOR }}
      >
        {value ?? "—"}
      </p>
    </div>
  );
}

function AuthorPill({ author }: { author: PaperDetailAuthor }) {
  return (
    <Link
      to={`/author/${author.id}`}
      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-[#2a2a4a] bg-[#0d1b2a] hover:border-[#ffa502]/50 hover:bg-[#ffa502]/5 transition-colors group"
    >
      <span className="font-[Outfit] text-sm text-gray-300 group-hover:text-white transition-colors">
        {author.name}
      </span>
      {author.institution && (
        <span className="font-[JetBrains_Mono] text-[10px] text-gray-500">
          {author.institution}
        </span>
      )}
    </Link>
  );
}

function ReferenceRow({
  paper,
  onExplore,
}: {
  paper: PaperDetailReference;
  onExplore: (id: string) => void;
}) {
  return (
    <tr className="border-b border-[#2a2a4a]/50 hover:bg-[#0d1b2a]/50 transition-colors">
      <td className="py-3 px-4">
        <div className="flex items-start gap-2">
          <button
            type="button"
            onClick={() => onExplore(paper.id)}
            className="font-[Outfit] text-sm text-gray-200 text-left hover:text-white transition-colors line-clamp-2"
          >
            {paper.title}
          </button>
          {paper.is_retracted && (
            <span className="shrink-0 px-1.5 py-0.5 rounded text-[10px] font-[Outfit] bg-[#ff4757]/20 text-[#ff4757] uppercase tracking-wider">
              Retracted
            </span>
          )}
        </div>
      </td>
      <td className="py-3 px-4 font-[JetBrains_Mono] text-xs text-gray-400">
        {paper.year ?? "—"}
      </td>
      <td className="py-3 px-4 font-[JetBrains_Mono] text-xs text-gray-400">
        {paper.cited_by_count.toLocaleString()}
      </td>
      <td className="py-3 px-4 font-[Outfit] text-xs text-gray-500 max-w-32 truncate">
        {paper.field ?? "—"}
      </td>
      <td className="py-3 px-4">
        <button
          type="button"
          onClick={() => onExplore(paper.id)}
          className="text-xs font-[Outfit] px-2 py-1 rounded border border-[#2a2a4a] hover:border-[#3a3a5a] hover:bg-[#1a1a2e] text-gray-400 hover:text-gray-200 transition-colors"
        >
          View
        </button>
      </td>
    </tr>
  );
}

function PaperTable({
  title,
  subtitle,
  papers,
  onExplore,
}: {
  title: string;
  subtitle: string;
  papers: PaperDetailReference[];
  onExplore: (id: string) => void;
}) {
  return (
    <div className="bg-[#16213e] border border-[#2a2a4a] rounded-xl mb-8 overflow-hidden">
      <div className="px-6 py-4 border-b border-[#2a2a4a]">
        <h2 className="font-[Outfit] text-base font-semibold text-gray-200">
          {title}
        </h2>
        <p className="font-[Outfit] text-xs text-gray-500 mt-0.5">
          {subtitle}
        </p>
      </div>
      {papers.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#2a2a4a]">
                <th className="py-3 px-4 text-left font-[Outfit] text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th className="py-3 px-4 text-left font-[Outfit] text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Year
                </th>
                <th className="py-3 px-4 text-left font-[Outfit] text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Citations
                </th>
                <th className="py-3 px-4 text-left font-[Outfit] text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Field
                </th>
                <th className="py-3 px-4 text-left font-[Outfit] text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {papers.map((p) => (
                <ReferenceRow key={p.id} paper={p} onExplore={onExplore} />
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="px-6 py-8 text-center">
          <p className="font-[Outfit] text-sm text-gray-500">
            No papers found
          </p>
        </div>
      )}
    </div>
  );
}

export function PaperDetail() {
  const { id } = useParams<{ id: string }>();
  const [paper, setPaper] = useState<PaperDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleExplore = (paperId: string) => {
    window.location.href = `/paper/${paperId}`;
  };

  const handleCitationGraph = () => {
    if (id) {
      window.location.href = `/explore/${id}`;
    }
  };

  useEffect(() => {
    if (!id) return;

    const controller = new AbortController();
    setLoading(true);
    setError(null);

    fetchPaperDetail(id, controller.signal)
      .then((data) => {
        setPaper(data);
        setLoading(false);
      })
      .catch((err) => {
        if (!controller.signal.aborted) {
          setError(err instanceof Error ? err.message : "Failed to load paper");
          setLoading(false);
        }
      });

    return () => controller.abort();
  }, [id]);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div
            className="w-10 h-10 border-2 rounded-full animate-spin mx-auto"
            style={{ borderColor: `${ACCENT_COLOR}30`, borderTopColor: ACCENT_COLOR }}
          />
          <p className="font-[Outfit] text-sm text-gray-500 mt-4">
            Loading paper details...
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
            <svg
              className="w-6 h-6 text-[#ff4757]"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <title>Error indicator</title>
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
              />
            </svg>
          </div>
          <p className="font-[Outfit] text-sm text-gray-400 mt-3">{error}</p>
        </div>
      </div>
    );
  }

  if (!paper) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="font-[Outfit] text-sm text-gray-500">Paper not found</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto bg-[#0d1b2a]">
      <div className="max-w-6xl mx-auto p-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
            <Link to="/" className="hover:text-gray-300 transition-colors">
              Dashboard
            </Link>
            <span>/</span>
            <span style={{ color: ACCENT_COLOR }}>Paper</span>
          </div>
          <h1 className="font-[Outfit] text-2xl md:text-3xl font-bold text-white tracking-tight leading-snug">
            {paper.title}
          </h1>
          <div className="flex flex-wrap items-center gap-3 mt-3">
            {paper.field && (
              <span
                className="px-2.5 py-0.5 rounded-full text-xs font-[Outfit] font-medium"
                style={{
                  backgroundColor: `${ACCENT_COLOR}20`,
                  color: ACCENT_COLOR,
                }}
              >
                {paper.field}
              </span>
            )}
            {paper.is_retracted && (
              <span className="px-2.5 py-0.5 rounded-full text-xs font-[Outfit] font-medium bg-[#ff4757]/20 text-[#ff4757] uppercase tracking-wider">
                Retracted
              </span>
            )}
            {paper.doi && (
              <a
                href={`https://doi.org/${paper.doi}`}
                target="_blank"
                rel="noopener noreferrer"
                className="font-[JetBrains_Mono] text-xs text-gray-500 hover:text-gray-300 transition-colors"
              >
                DOI: {paper.doi}
              </a>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard label="Year" value={paper.year} />
          <StatCard label="Citations" value={paper.cited_by_count.toLocaleString()} />
          <StatCard label="References" value={paper.references_count.toLocaleString()} />
          <StatCard label="Authors" value={paper.authors.length} />
        </div>

        {/* Action Button */}
        <div className="mb-8">
          <button
            type="button"
            onClick={handleCitationGraph}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-[#2a2a4a] bg-[#16213e] hover:border-[#ffa502]/50 hover:bg-[#ffa502]/10 transition-colors"
          >
            <svg
              className="w-4 h-4"
              style={{ color: ACCENT_COLOR }}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <title>Graph icon</title>
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z"
              />
            </svg>
            <span className="font-[Outfit] text-sm text-gray-200">
              Explore Citation Graph
            </span>
          </button>
        </div>

        {/* Abstract */}
        {paper.abstract && (
          <div className="bg-[#16213e] border border-[#2a2a4a] rounded-xl p-6 mb-8">
            <h2 className="font-[Outfit] text-base font-semibold text-gray-200 mb-3">
              Abstract
            </h2>
            <p className="font-[Outfit] text-sm text-gray-400 leading-relaxed">
              {paper.abstract}
            </p>
          </div>
        )}

        {/* Authors */}
        <div className="bg-[#16213e] border border-[#2a2a4a] rounded-xl p-6 mb-8">
          <h2 className="font-[Outfit] text-base font-semibold text-gray-200 mb-3">
            Authors
          </h2>
          <p className="font-[Outfit] text-xs text-gray-500 mb-4">
            Click an author to view their profile
          </p>
          {paper.authors.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {paper.authors.map((author) => (
                <AuthorPill key={author.id} author={author} />
              ))}
            </div>
          ) : (
            <p className="font-[Outfit] text-sm text-gray-500">
              No authors found
            </p>
          )}
        </div>

        {/* References */}
        <PaperTable
          title="References"
          subtitle={`Papers this work cites (top 50 of ${paper.references_count.toLocaleString()})`}
          papers={paper.references}
          onExplore={handleExplore}
        />

        {/* Citers */}
        <PaperTable
          title="Citing Papers"
          subtitle={`Papers that cite this work (top 50 of ${paper.citers_count.toLocaleString()})`}
          papers={paper.citers}
          onExplore={handleExplore}
        />
      </div>
    </div>
  );
}
