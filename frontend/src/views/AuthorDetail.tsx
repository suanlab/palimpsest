import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  fetchAuthorDetail,
  type AuthorDetailResponse,
  type AuthorPublication,
  type CoauthorSummary,
} from "../api/graphApi";

const ACCENT_COLOR = "#e056a0";

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

function PublicationRow({
  pub,
  onExplore,
}: {
  pub: AuthorPublication;
  onExplore: (id: string) => void;
}) {
  return (
    <tr className="border-b border-[#2a2a4a]/50 hover:bg-[#0d1b2a]/50 transition-colors">
      <td className="py-3 px-4">
        <div className="flex items-start gap-2">
          <button
            type="button"
            onClick={() => onExplore(pub.id)}
            className="font-[Outfit] text-sm text-gray-200 text-left hover:text-white transition-colors line-clamp-2"
          >
            {pub.title}
          </button>
          {pub.is_retracted && (
            <span className="shrink-0 px-1.5 py-0.5 rounded text-[10px] font-[Outfit] bg-[#ff4757]/20 text-[#ff4757] uppercase tracking-wider">
              Retracted
            </span>
          )}
        </div>
      </td>
      <td className="py-3 px-4 font-[JetBrains_Mono] text-xs text-gray-400">
        {pub.year ?? "—"}
      </td>
      <td className="py-3 px-4 font-[JetBrains_Mono] text-xs text-gray-400">
        {pub.cited_by_count.toLocaleString()}
      </td>
      <td className="py-3 px-4 font-[Outfit] text-xs text-gray-500 max-w-32 truncate">
        {pub.field ?? "—"}
      </td>
      <td className="py-3 px-4">
        <button
          type="button"
          onClick={() => onExplore(pub.id)}
          className="text-xs font-[Outfit] px-2 py-1 rounded border border-[#2a2a4a] hover:border-[#3a3a5a] hover:bg-[#1a1a2e] text-gray-400 hover:text-gray-200 transition-colors"
        >
          Explore
        </button>
      </td>
    </tr>
  );
}

function CoauthorPill({ coauthor }: { coauthor: CoauthorSummary }) {
  return (
    <Link
      to={`/author/${coauthor.id}`}
      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-[#2a2a4a] bg-[#0d1b2a] hover:border-[#e056a0]/50 hover:bg-[#e056a0]/5 transition-colors group"
    >
      <span className="font-[Outfit] text-sm text-gray-300 group-hover:text-white transition-colors">
        {coauthor.name}
      </span>
      <span className="font-[JetBrains_Mono] text-[10px] text-gray-500">
        {coauthor.shared_papers} shared
      </span>
    </Link>
  );
}

export function AuthorDetail() {
  const { id } = useParams<{ id: string }>();
  const [author, setAuthor] = useState<AuthorDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleExplore = (paperId: string) => {
    window.location.href = `/explore/${paperId}`;
  };

  useEffect(() => {
    if (!id) return;

    const controller = new AbortController();
    setLoading(true);
    setError(null);

    fetchAuthorDetail(id, controller.signal)
      .then((data) => {
        setAuthor(data);
        setLoading(false);
      })
      .catch((err) => {
        if (!controller.signal.aborted) {
          setError(err instanceof Error ? err.message : "Failed to load author");
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
            Loading author profile...
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

  if (!author) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="font-[Outfit] text-sm text-gray-500">Author not found</p>
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
            <span style={{ color: ACCENT_COLOR }}>Author</span>
          </div>
          <h1 className="font-[Outfit] text-3xl font-bold text-white tracking-tight">
            {author.name}
          </h1>
          {(author.institution || author.country) && (
            <p className="font-[Outfit] text-sm text-gray-500 mt-1">
              {[author.institution, author.country].filter(Boolean).join(" • ")}
            </p>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard label="Total Works" value={author.works_count.toLocaleString()} />
          <StatCard label="Total Citations" value={author.cited_by_count.toLocaleString()} />
          <StatCard label="h-index" value={author.h_index} />
          <StatCard label="Co-authors" value={author.coauthors.length} />
        </div>

        {/* Publications */}
        <div className="bg-[#16213e] border border-[#2a2a4a] rounded-xl mb-8 overflow-hidden">
          <div className="px-6 py-4 border-b border-[#2a2a4a]">
            <h2 className="font-[Outfit] text-base font-semibold text-gray-200">
              Recent Publications
            </h2>
            <p className="font-[Outfit] text-xs text-gray-500 mt-0.5">
              Top 20 most recent papers
            </p>
          </div>
          {author.publications.length > 0 ? (
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
                  {author.publications.map((pub) => (
                    <PublicationRow
                      key={pub.id}
                      pub={pub}
                      onExplore={handleExplore}
                    />
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="px-6 py-8 text-center">
              <p className="font-[Outfit] text-sm text-gray-500">
                No publications found
              </p>
            </div>
          )}
        </div>

        {/* Co-authors */}
        <div className="bg-[#16213e] border border-[#2a2a4a] rounded-xl p-6">
          <h2 className="font-[Outfit] text-base font-semibold text-gray-200 mb-4">
            Top Co-authors
          </h2>
          <p className="font-[Outfit] text-xs text-gray-500 mb-4">
            Collaborators ranked by shared publications
          </p>
          {author.coauthors.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {author.coauthors.map((coauthor) => (
                <CoauthorPill key={coauthor.id} coauthor={coauthor} />
              ))}
            </div>
          ) : (
            <p className="font-[Outfit] text-sm text-gray-500">
              No co-authors found
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
