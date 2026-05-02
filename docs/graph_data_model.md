# Bibliographic Graph Data Model

## Node Types

### Paper
- `id`: OpenAlex ID (e.g., `W3181579298`)
- `doi`: DOI string
- `title`: string
- `year`: int
- `cited_by_count`: int
- `is_retracted`: bool
- `source`: enum(openalex, arxiv, dblp, retraction_watch)
- `fields`: list[str] (OpenAlex field names)
- `primary_field`: str
- `ai_related`: bool (computed: has AI/ML concepts)
- `arxiv_categories`: list[str] (if from arXiv)
- `retraction_reason`: str (if retracted, from Retraction Watch)
- `retraction_date`: date (if retracted)

### Author
- `id`: OpenAlex author ID
- `name`: str
- `institution`: str (most recent)
- `country`: str

### Field
- `id`: OpenAlex field ID
- `name`: str
- `level`: int (0=domain, 1=field, 2=subfield)

### Venue
- `id`: OpenAlex source ID
- `name`: str (journal/conference name)
- `type`: enum(journal, conference, repository)

## Edge Types

### CITES (Paper → Paper)
- `source_id`: citing paper ID
- `target_id`: cited paper ID
- `year`: citing paper's publication year
- Properties: directed, no weight

### CO_AUTHORED (Author ↔ Author)
- `author1_id`, `author2_id`
- `paper_count`: int (number of co-authored papers)
- `first_year`: int, `last_year`: int
- Properties: undirected, weighted by paper_count

### AUTHORED (Author → Paper)
- `author_id`, `paper_id`
- `position`: int (author order)
- `is_corresponding`: bool

### PUBLISHED_IN (Paper → Venue)
- `paper_id`, `venue_id`

### BELONGS_TO (Paper → Field)
- `paper_id`, `field_id`
- `score`: float (concept relevance score from OpenAlex)

## Derived/Computed Edges

### CONTAMINATES (Paper → Paper) — Track 3 specific
- Subset of CITES where source is retracted
- `depth`: int (1=direct citation of retracted, 2=cites a paper that cites retracted, etc.)
- `time_since_retraction`: int (years between citation and retraction date)
- `post_retraction`: bool (citation occurred after retraction)

### AI_DIFFUSES (Field → Field) — Track 1 specific
- Aggregated from CITES edges where citing paper is AI-related
- `year`: int
- `citation_count`: int
- `direction`: str (which field adopted AI from which)

## Graph Views (for UI)

### View 1: Citation Network
- Nodes: Papers (sized by cited_by_count, colored by field)
- Edges: CITES
- Filters: year range, field, minimum citations
- Layout: force-directed or chronological (x=year)

### View 2: Co-authorship Network
- Nodes: Authors (sized by paper count, colored by field)
- Edges: CO_AUTHORED (weighted by paper_count)
- Filters: year range, field, minimum collaborations
- Layout: force-directed, community detection coloring

### View 3: Knowledge Contamination Cascade (Track 3)
- Nodes: Papers (retracted=red, citing=orange, 2nd-order=yellow)
- Edges: CONTAMINATES (thickness by depth)
- Root nodes: retracted papers
- Layout: tree/radial from retracted paper outward
- Highlight: post-retraction citations

### View 4: AI Diffusion Pathways (Track 1)
- Nodes: Fields (sized by total papers, colored by AI adoption rate)
- Edges: AI_DIFFUSES (directed, thickness by citation volume)
- Animation: year-by-year progression
- Drill-down: field → individual AI papers

## Data Sources Mapping

| Graph Element | Primary Source | Enrichment Sources |
|--------------|---------------|-------------------|
| Paper nodes | OpenAlex snapshot | arXiv (categories), DBLP (venues), Retraction Watch (retraction info) |
| Author nodes | OpenAlex authorships | DBLP (disambiguation) |
| CITES edges | OpenAlex referenced_works | Crossref (additional refs) |
| CO_AUTHORED | OpenAlex authorships | DBLP (co-author lists) |
| Retraction info | Retraction Watch CSV | OpenAlex is_retracted flag |
| Field/concept | OpenAlex concepts/topics | arXiv categories |

## Scale Estimates

| Element | Option A (Research) | Option B (Platform) |
|---------|-------------------|-------------------|
| Paper nodes | ~85K (491 retracted + citers + AI sample) | ~1M (full arXiv CS + enriched) |
| Author nodes | ~200K | ~2M |
| CITES edges | ~500K | ~10M |
| CO_AUTHORED edges | ~300K | ~5M |
