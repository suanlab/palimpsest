# F1 Follow-up Paper Outline — "Citation Cartels in Mega-Journals"

**Target venue**: *PNAS Nexus* (or *PLOS One*; *Quantitative Science Studies* as fallback)
**Author**: Suan Lee, Semyung University

## Working title

"Multiple Parallel Citation Cartels Inside a Mega-Journal Publisher: A Network-Level Validation of Hindawi's 2023 Mass Retraction"

## Headline result

Within Hindawi's 11,524 retracted papers, paper-mill retractions and non-mill retractions exhibit *opposite* network signatures depending on the metric chosen:

| Metric | Mill (n = 7,392) | Non-mill (n = 4,115) | Ratio (mill/non-mill) |
|---|---:|---:|---:|
| Citation edges (intra-group) | 946 | 446 | 2.12× |
| Density | 1.73 × 10⁻⁵ | 2.63 × 10⁻⁵ | 0.66× |
| Max in-degree | 54 | 48 | 1.13× |
| Max component size | 107 | 93 | 1.15× |
| Cartel candidates (≥5 nodes, density ≥ 0.20) | **20** | **9** | **2.22×** |
| Top cartel density | 0.467 | (lower) | — |

**Interpretation**: Paper-mill retractions form **a larger number of small, very dense citation cartels**, not a single uniformly inflated self-citation network. The 0.66× density ratio rejects the naive "mill papers cite each other more" hypothesis, while the 2.22× cartel-count ratio supports the **multiple-parallel-cells** hypothesis: many distinct paper-mill operations seeded clusters across Hindawi's 200+ journals, each producing internal citation cliques.

## Story arc (Track 3-style 5-step)

1. **Discovery**: Hindawi 2023 produced 9,675 retractions in one year (63% of all paper-mill retractions in history; Track 3 Lee 2026, *PNAS*).
2. **Falsification**: Paper-mill papers do *not* form a uniformly denser self-citation network than non-mill retractions (mill/non-mill density ratio 0.66×).
3. **Causal ID**: Greedy modularity community detection identifies 20 dense subgraphs (≥5 nodes, density ≥ 0.20) inside the mill subgraph vs 9 inside the non-mill subgraph (2.22×).
4. **Forward prediction**: A network-edge-rate predictor trained on 2018–2021 cartel structure should predict 2022–2024 retraction batches in *currently active* mega-OA outlets (Spandidos, MDPI, Frontiers candidates).
5. **Policy**: Network-density alerts at the (publisher, year) level — combined with the editorial-tag jump signature from the main paper — give publishers and funders a low-cost early-warning system that does not require content inspection.

## Methods sketch

- Data: Same as Track 3 PNAS submission. Hindawi mill DOIs (n = 7,392) + non-mill (n = 4,115) resolved against 479M-paper Neo4j graph (`scripts/track3_citation_cartel.py`).
- Network construction: directed CITES subgraph among intra-group OpenAlex IDs.
- Cartel detection: networkx greedy modularity on undirected projection; cartel = community with ≥5 nodes and density ≥ 0.20 (random expectation ≈ 1.7e-5).
- Validation: 1,000 random-DOI controls per group to confirm cartel-count delta is not a sample-size artefact.
- Extension: per-(journal, year) cartel-density panel + permutation tests.

## Deliverables (this session)

- `scripts/track3_citation_cartel.py` — full pipeline
- `data/processed/track3/citation_cartel.json` — network stats + 20 mill cartels + 9 non-mill cartels
- `data/processed/track3/tables/table_cartel_communities.tsv` — community-level table
- `docs/submissions/track3_pnas/figures/fig_citation_cartel.{pdf,png}` — three-panel summary (density, in-degree, cartel size distribution)

## Open questions for the follow-up paper

1. **Author overlap within cartels**: Do the 20 mill cartels share authors? If yes → these are paper-mill rings; if no → independent operations.
2. **Journal stratification**: Are cartels concentrated in specific Hindawi journals (e.g., *Computational Intelligence and Neuroscience*, *Wireless Communications and Mobile Computing*)?
3. **Temporal evolution**: Did the cartel count grow 2017→2022 → expose retraction batch trigger?
4. **Cross-publisher generalisation**: Apply the same methodology to MDPI, Frontiers, Spandidos to test the forward-prediction in §4 above.
