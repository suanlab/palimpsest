export interface GraphNode {
  id: string;
  label: string;
  type: "paper" | "author" | "field" | "institution";
  cited_by_count?: number;
  paper_count?: number;
  year?: number;
  is_retracted?: boolean;
  is_ai_related?: boolean;
  depth?: number;
  field?: string;
  doi?: string;
  authors?: string[];
  abstract?: string;
  institution?: string;
  h_index?: number;
  collaboration_count?: number;
  retraction_year?: number;
  cascade_depth?: number;
  ai_adoption_score?: number;
  is_focal?: boolean;
  is_expanded?: boolean;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  weight?: number;
  year?: number;
  type?: "cites" | "coauthor" | "contaminates" | "diffuses";
}

export interface CytoscapeNodeData {
  data: GraphNode;
}

export interface CytoscapeEdgeData {
  data: GraphEdge;
}

export type CytoscapeElement = CytoscapeNodeData | CytoscapeEdgeData;

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata?: GraphMetadata;
}

export interface GraphMetadata {
  total_nodes: number;
  total_edges: number;
  query_time_ms: number;
  truncated: boolean;
}

export interface StatsResponse {
  total_papers: number;
  total_authors: number;
  total_citations: number;
  total_fields: number;
  total_retracted: number;
  ai_related_papers: number;
  ai_concept_papers: number;
  fields: FieldStat[];
  yearly_publications?: YearlyCount[];
}

export interface FieldStat {
  name: string;
  paper_count: number;
  color: string;
}

export interface YearlyCount {
  year: number;
  count: number;
}

export interface SearchResult {
  id: string;
  title: string;
  type: "paper" | "author";
  year?: number;
  cited_by_count?: number;
  authors?: string[];
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
}

export type LayoutName =
  | "fcose"
  | "cose-bilkent"
  | "breadthfirst"
  | "concentric"
  | "circle"
  | "grid";

export type ViewType =
  | "citation"
  | "coauthorship"
  | "contamination"
  | "ai-diffusion";

export interface GraphFilters {
  minCitations: number;
  yearFrom: number;
  yearTo: number;
  showRetracted: boolean;
  showAiRelated: boolean;
}

export const DEFAULT_FILTERS: GraphFilters = {
  minCitations: 0,
  yearFrom: 1990,
  yearTo: new Date().getFullYear(),
  showRetracted: true,
  showAiRelated: true,
};

export const FIELD_COLORS: Record<string, string> = {
  "Computer Science": "#00d4ff",
  Medicine: "#ff6b6b",
  Biology: "#51cf66",
  Physics: "#ffd43b",
  Chemistry: "#ff922b",
  Mathematics: "#cc5de8",
  Engineering: "#20c997",
  Psychology: "#f06595",
  Economics: "#868e96",
  "Materials Science": "#a9e34b",
};

export const DEPTH_COLORS: Record<number, string> = {
  0: "#ff4757",
  1: "#ff7f50",
  2: "#ffa502",
  3: "#a4a4a4",
  4: "#636e72",
};
