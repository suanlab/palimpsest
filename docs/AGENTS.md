<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# docs

## Purpose
Research documentation, paper drafts, data source guides, and investigation notes for the science of science project.

## Key Files

| File | Description |
|------|-------------|
| `paper_outline.md` | Research paper framework — Track 1 (AI adoption), Track 3 (retraction contamination) |
| `track1_paper_draft.md` | Draft paper on AI adoption across scientific fields |
| `track3_paper_draft.md` | Draft paper on retraction propagation and contamination cascades |
| `graph_data_model.md` | Bibliographic graph schema (Paper/Author/Field nodes, citation edges) |
| `NEO4J.md` | Neo4j setup guide (Docker, credentials, connection) |
| `OAG_V3.1_DOWNLOAD_GUIDE.md` | Open Academic Graph v3.1 download instructions (~130M papers) |
| `AMINER_QUICK_START.md` | AMiner AI 2000 ranking API quick start |
| `AMINER_AI2000_INVESTIGATION.md` | Investigation notes on AMiner AI2000 ranking system |
| `semantic_scholar_api_application.md` | Semantic Scholar API application details |
| `oag_v3.1_urls.json` | Download URLs for OAG datasets |
| `statistical_verification_report.txt` | Statistical validation results |

## For AI Agents

### Working In This Directory
- Documentation is bilingual (Korean + English)
- Paper drafts follow the three research tracks: AI adoption, retraction contamination, field dynamics
- Data source guides document API access patterns and download procedures
- Keep `graph_data_model.md` in sync with Neo4j schema changes

### Common Patterns
- Markdown for all documentation
- Research tracks are numbered: Track 1 (AI adoption), Track 3 (retraction contamination)
- Data sources: OpenAlex, Semantic Scholar, AMiner, Retraction Watch, arXiv, DBLP

## Dependencies

### Internal
- `src/research/api/` — API implements the graph data model described here
- `scripts/` — Data collection scripts follow guides documented here

<!-- MANUAL: -->
