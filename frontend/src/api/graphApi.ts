import type {
  GraphResponse,
  StatsResponse,
  SearchResponse,
} from "../types/graph";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8300";
const API_KEY = import.meta.env.VITE_API_KEY ?? "";

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function fetchJson<T>(url: string, signal?: AbortSignal): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (API_KEY) {
    headers["X-API-Key"] = API_KEY;
  }
  const response = await fetch(`${API_BASE}${url}`, { headers, signal });

  if (!response.ok) {
    throw new ApiError(
      response.status,
      `API request failed: ${response.status} ${response.statusText}`,
    );
  }

  return response.json() as Promise<T>;
}

function buildQuery(params: Record<string, string | number | boolean>): string {
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, String(value));
    }
  }
  return searchParams.toString();
}

export function fetchCitationNetwork(
  seedPaperId: string,
  depth: number = 2,
  limit: number = 1000,
  signal?: AbortSignal,
): Promise<GraphResponse> {
  const query = buildQuery({
    seed_paper_id: seedPaperId,
    depth,
    limit,
  });
  return fetchJson<GraphResponse>(
    `/api/graph/citation-network?${query}`,
    signal,
  );
}

export function fetchCoauthorshipNetwork(
  seedAuthorId: string,
  depth: number = 2,
  limit: number = 1000,
  signal?: AbortSignal,
): Promise<GraphResponse> {
  const query = buildQuery({
    seed_author_id: seedAuthorId,
    depth,
    limit,
  });
  return fetchJson<GraphResponse>(
    `/api/graph/coauthorship-network?${query}`,
    signal,
  );
}

export function fetchContaminationCascade(
  retractedPaperId: string,
  maxDepth: number = 3,
  limit: number = 1000,
  signal?: AbortSignal,
): Promise<GraphResponse> {
  const query = buildQuery({
    retracted_paper_id: retractedPaperId,
    max_depth: maxDepth,
    limit,
  });
  return fetchJson<GraphResponse>(
    `/api/graph/contamination-cascade?${query}`,
    signal,
  );
}

export function fetchAiDiffusion(
  yearFrom: number = 2000,
  yearTo: number = 2024,
  method: "title" | "concept" = "title",
  signal?: AbortSignal,
): Promise<GraphResponse> {
  const query = buildQuery({ year_from: yearFrom, year_to: yearTo, method });
  return fetchJson<GraphResponse>(`/api/graph/ai-diffusion?${query}`, signal);
}

export function fetchStats(signal?: AbortSignal): Promise<StatsResponse> {
  return fetchJson<StatsResponse>("/api/graph/stats", signal);
}

export interface FieldYearlyExportRow {
  field_id: string;
  field_name: string;
  year: number;
  total_count: number;
  ai_title_count: number;
  ai_concept_count: number;
  ai_title_fraction: number;
  ai_concept_fraction: number;
}

export interface RetractionRateByField {
  field_id: string;
  field_name: string;
  total_papers: number;
  total_retractions: number;
  mean_ai_fraction: number;
  mean_retraction_rate: number;
  retraction_rate: number;
  retraction_per_million: number;
}

export interface RetractionStatsResponse {
  pre_post_distribution: {
    pre_retraction: number;
    same_year: number;
    post_retraction: number;
    total: number;
    post_retraction_pct: number;
  };
  citation_persistence: Array<{ years_after: number; count: number }>;
  top_fields: Array<{
    field: string;
    post_retraction_citations: number;
    total_papers: number;
    rate_per_million: number;
  }>;
  top_zombies: Array<{
    title: string;
    pub_year: number;
    total_citations: number;
    post_retraction_citations: number;
    field: string;
  }>;
  retraction_rate_by_field: RetractionRateByField[];
}

export function fetchRetractionStats(
  signal?: AbortSignal,
): Promise<RetractionStatsResponse> {
  return fetchJson<RetractionStatsResponse>("/api/graph/retraction-stats", signal);
}

export function fetchFieldYearlyExport(
  field: string,
  signal?: AbortSignal,
): Promise<FieldYearlyExportRow[]> {
  const query = buildQuery({ field, format: "json" });
  return fetchJson<FieldYearlyExportRow[]>(`/api/export/field-yearly?${query}`, signal);
}

export async function downloadFieldSummaryCsv(): Promise<void> {
  const query = buildQuery({ format: "csv" });
  const url = `${API_BASE}/api/export/field-summary?${query}`;
  const headers: Record<string, string> = {};
  if (API_KEY) {
    headers["X-API-Key"] = API_KEY;
  }

  const response = await fetch(url, { headers });
  if (!response.ok) {
    throw new ApiError(
      response.status,
      `API request failed: ${response.status} ${response.statusText}`,
    );
  }

  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = "field_summary.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(objectUrl);
}


export interface AutocompleteSuggestion {
  type: "paper" | "author";
  id: string;
  text: string;
}

export function fetchAutocomplete(
  q: string,
  limit: number = 8,
  signal?: AbortSignal,
): Promise<AutocompleteSuggestion[]> {
  const query = buildQuery({ q, limit });
  return fetchJson<AutocompleteSuggestion[]>(`/api/search/autocomplete?${query}`, signal);
}

export interface SearchFilters {
  yearFrom?: number;
  yearTo?: number;
  field?: string;
  retractedOnly?: boolean;
}

export function searchPapersWithFilters(
  q: string,
  filters?: SearchFilters,
  limit: number = 20,
  signal?: AbortSignal,
): Promise<SearchResponse> {
  const params: Record<string, string | number | boolean> = { q, limit };
  if (filters?.yearFrom !== undefined) params.year_from = filters.yearFrom;
  if (filters?.yearTo !== undefined) params.year_to = filters.yearTo;
  if (filters?.field) params.field = filters.field;
  if (filters?.retractedOnly) params.retracted_only = true;
  const query = buildQuery(params);
  return fetchJson<SearchResponse>(`/api/search/papers?${query}`, signal);
}

export function searchPapers(
  q: string,
  limit: number = 20,
  signal?: AbortSignal,
): Promise<SearchResponse> {
  const query = buildQuery({ q, limit });
  return fetchJson<SearchResponse>(`/api/search/papers?${query}`, signal);
}

export function searchAuthors(
  q: string,
  limit: number = 20,
  signal?: AbortSignal,
): Promise<SearchResponse> {
  const query = buildQuery({ q, limit });
  return fetchJson<SearchResponse>(`/api/search/authors?${query}`, signal);
}


export interface AuthorDetailResponse {
  id: string;
  name: string;
  openalex_id: string | null;
  institution: string | null;
  country: string | null;
  works_count: number;
  cited_by_count: number;
  h_index: number | null;
  publications: AuthorPublication[];
  coauthors: CoauthorSummary[];
}

export interface AuthorPublication {
  id: string;
  title: string;
  year: number | null;
  cited_by_count: number;
  is_retracted: boolean;
  field: string | null;
}

export interface CoauthorSummary {
  id: string;
  name: string;
  shared_papers: number;
}

export interface CitationGraphResponse {
  focal_paper: CitationGraphNode;
  nodes: CitationGraphNode[];
  edges: CitationGraphEdge[];
}

export interface CitationGraphNode {
  id: string;
  title: string;
  year: number | null;
  cited_by_count: number;
  field: string | null;
  is_retracted: boolean;
  is_focal: boolean;
}

export interface CitationGraphEdge {
  source: string;
  target: string;
}

export function fetchAuthorDetail(
  authorId: string,
  signal?: AbortSignal,
): Promise<AuthorDetailResponse> {
  return fetchJson<AuthorDetailResponse>(`/api/graph/author/${encodeURIComponent(authorId)}`, signal);
}

export function fetchCitationGraph(
  paperId: string,
  depth: number = 1,
  limit: number = 50,
  signal?: AbortSignal,
): Promise<CitationGraphResponse> {
  const query = buildQuery({ depth, limit });
  return fetchJson<CitationGraphResponse>(`/api/graph/citation-graph/${encodeURIComponent(paperId)}?${query}`, signal);
}


export interface PaperDetailAuthor {
  id: string;
  name: string;
  institution: string | null;
  country: string | null;
}

export interface PaperDetailReference {
  id: string;
  title: string;
  year: number | null;
  cited_by_count: number;
  field: string | null;
  is_retracted: boolean;
}

export interface PaperDetailResponse {
  id: string;
  title: string;
  year: number | null;
  doi: string | null;
  cited_by_count: number;
  field: string | null;
  is_retracted: boolean;
  abstract: string | null;
  authors: PaperDetailAuthor[];
  references: PaperDetailReference[];
  citers: PaperDetailReference[];
  references_count: number;
  citers_count: number;
}

export function fetchPaperDetail(
  paperId: string,
  signal?: AbortSignal,
): Promise<PaperDetailResponse> {
  return fetchJson<PaperDetailResponse>(
    `/api/graph/paper/${encodeURIComponent(paperId)}`,
    signal,
  );
}

export { ApiError };
