<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# AGENTS.md — src/palimpsest/networks/

**Scope**: Graph construction and analysis for citation and collaboration networks.

## Overview

Builds NetworkX graphs from OpenAlex-style work records. Supports directed citation networks and undirected co-authorship networks.

## Files

| File | Purpose |
|------|---------|
| `citation.py` | Directed citation graph builder |
| `collaboration.py` | Undirected co-authorship graph builder |
| `metrics.py` | Centrality and community metrics |
| `__init__.py` | Module exports |

## Key Abstractions

### CitationNetwork
- Graph type: `nx.DiGraph[str]`
- Edge direction: `citing_paper → cited_paper`
- Methods:
  - `build_from_works()` — construct from work records
  - `get_citing_papers(id)` — papers that cite the target
  - `get_references(id)` — papers cited by target
  - `get_subgraph(seed_ids, depth)` — BFS neighborhood extraction

### CollaborationNetwork
- Graph type: `nx.Graph[str]`
- Edge weight: number of co-authored papers
- Methods:
  - `build_from_works()` — construct from authorship records
  - `get_collaborators(id)` — direct co-authors
  - `get_collaboration_strength(a, b)` — weighted edge value

### Network Metrics
- Centrality: degree, betweenness, PageRank
- Communities: Louvain, connected components
- Traversal: shortest paths, k-cores

## WorkRecord TypedDict

Citation and collaboration builders expect records with:
```python
{
  "id": str,                    # OpenAlex work ID
  "title": str,
  "publication_year": int,
  "cited_by_count": int,
  "doi": str,
  "referenced_works": list[str],  # For citations
  "authorships": list[dict]       # For collaborations
}
```

## Conventions (This Module)

- Graphs are built from lists of work records (not single adds)
- Node IDs are OpenAlex identifiers (e.g., `W123456789`)
- Node attributes mirror OpenAlex fields (title, year, citations)
- Use `graph.nodes[id].get("attr")` for safe attribute access
- Subgraph extraction uses BFS with configurable depth

## Integration with Analysis

```python
from palimpsest.data.openalex import OpenAlexClient
from palimpsest.networks.citation import CitationNetwork

client = OpenAlexClient()
works = client.get_works(filters={"publication_year": 2023})

net = CitationNetwork()
net.build_from_works(works)
print(f"Built graph: {net.node_count} nodes, {net.edge_count} edges")
```
