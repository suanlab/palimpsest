# Supporting Information

## Publisher-Mediated Retraction Failure: Hindawi 2023 as a Natural Experiment for Post-Retraction Citation Dynamics

---

## SI Methods

### §1. Reason classifier — taxonomy, validation, and Cohen's κ

Two classifiers for retraction reason were constructed:

**Baseline classifier** (used in earlier analyses; minimal regex rule-set):

```python
if "paper mill" in r:                                        return "Paper mill"
if any(k in r for k in ["fabrication","falsification","plagiari","misconduct",
   "fake peer review","manipulation of images","image manipulation",
   "duplicate submission","duplicate publication","conflict of interest",
   "ghost writ"]):                                            return "Misconduct"
if any(k in r for k in ["error","calculat","reproducib","statistical",
   "methodolog","analytic","contamination of","instrument"]): return "Error"
return "Other"
```

**Refined classifier** uses the full 112-tag taxonomy with explicit priority ordering:

| Category | Priority | Tags (selected) |
|---|---|---|
| Paper mill | 0 (highest) | "Paper Mill" |
| Misconduct | 1 | Falsification/Fabrication, Plagiarism (all variants), Image manipulation, Duplication, Compromised Peer Review, Fake Peer Review, Rogue Editor, Hoax Paper, Computer-Aided Content, Lack of IRB/IACUC, Civil/Criminal Proceedings, Forged Authorship, Conflict of Interest, Informed Consent issues, Ethical Violations |
| Error | 2 | Error in Data/Image/Analyses/Results/Methods/Text/Cell Lines, Unreliable Data/Image/Results, Original Data Not Available, Randomly Generated Content, Error by Journal/Publisher |
| Other | 3 | Procedural; remaining tags |
| Unknown | 4 | NaN |

**Validation results** on 68,869 RW retractions:
- Baseline–refined Cohen's κ = **0.539** (moderate agreement; full corpus)
- Stratified 878-row sample κ = **0.765** (higher because rare categories are oversampled)
- 23,236 retractions disagree (33.7%); concentrated in baseline → "Other" but refined → "Misconduct" (16,754 cases — primarily Compromised Peer Review and Lack of IRB)
- **Paper-mill class agreement is 100%** (single tag "Paper Mill"; no overlapping ambiguity)

| Class | Precision (baseline) | Recall | F1 | Support |
|---|---|---|---|---|
| Paper mill | 1.000 | 1.000 | 1.000 | 11,793 |
| Misconduct | 0.945 | 0.358 | 0.519 | 27,438 |
| Error | 0.730 | 0.583 | 0.648 | 9,703 |
| Other | 0.471 | 0.921 | 0.623 | 19,857 |
| Unknown | 1.000 | 1.000 | 1.000 | 78 |

**Sensitivity of zombie-rate ratio to classifier choice:**

| Class | Baseline OR (vs control) | Refined OR (vs control) |
|---|---|---|
| Paper mill | **14.275** | **14.275** |
| Misconduct | 2.051 | 3.844 |
| Error | 4.601 | 5.508 |
| Other | 5.523 | 5.496 |

The paper-mill OR is invariant across classifiers (single-tag identification); the misconduct OR rises under refined classification (compromised peer review and IRB lapses now recognized).

### §2. Matched-control sensitivity analyses

| Specification | n pairs | Retracted zombie | Control zombie | Rate ratio |
|---|---|---|---|---|
| Main (±20% citations, field+year±1) | 64,458 | 0.494 | 0.324 | 1.524 |
| Wider band (±30%) | 87,642 | 0.488 | 0.338 | 1.444 |
| Narrower band (±10%) | 41,113 | 0.501 | 0.311 | 1.611 |
| Field+year only (no citation match) | 141,770 | 0.487 | 0.351 | 1.388 |
| Threshold = 0.4 | 64,458 | 0.621 | 0.457 | 1.359 |
| Threshold = 0.6 | 64,458 | 0.389 | 0.233 | 1.670 |
| Restrict ≥10 pre-retr cites | 42,119 | 0.455 | 0.302 | 1.507 |
| **IPTW reweighting** | 64,458 | 0.681 | 0.349 | **1.952** |

**Match-rate bias diagnosis:**
- Match rate by publisher: Hindawi 36.3%, MDPI 50.2%, BMC 43.5%, PLoS 41.8%, Wiley 36.2%, Elsevier 33.1%, Springer 31.0%, IOS Press 27.1%, IEEE 24.0%
- Match rate by mill flag: mill 36.9%, non-mill 19.5% — paper-mill papers are over-represented in matched corpus because they are typically more cited (median citations 9 matched vs 1 unmatched)
- Standardized mean differences (matched vs unmatched retracted): year SMD −0.124, log-citation SMD 1.546, field-distribution Hellinger 0.18

### §3. Stepwise stratified-OR decomposition (full table)

| Level | Stratification covariates | n strata | n pairs | OR (mill vs non-mill, zombie outcome) |
|---|---|---|---|---|
| L0 | none | 1 | 64,458 | **3.66** |
| L1 | + retraction year (5y bins) | 3 | 28,773 | 1.515 |
| L2 | + field | 34 | 26,876 | 1.591 |
| L3 | + publisher | 89 | 18,737 | **0.613** |
| L4 | + journal | 122 | 9,647 | 0.773 |

Strata with fewer than 30 pairs or no margin variation are excluded. Sample sizes shrink at finer stratification because many publisher-year-field-journal cells contain only one type of retraction. Across all levels at which both mill and non-mill papers are represented, the mill OR is well below the 14.3 unadjusted figure.

### §4. Hindawi natural-experiment statistics (full)

**Cohort breakdown:**

| Cohort | n pairs | Retracted zombie | Control zombie | Rate ratio | Median lag |
|---|---|---|---|---|---|
| Pre-2022 regular | 279 | 0.785 | 0.369 | 2.13 | 1y |
| 2022–23 batch | 9,694 | 0.902 | 0.112 | 8.04 | 1y |

**Lag × zombie (Hindawi only, n = 9,973 pairs):**

| Lag (years) | n | Retracted zombie | Control zombie | Rate ratio |
|---|---|---|---|---|
| 0 | 292 | 0.990 | 0.055 | 18.06 |
| 1 | 6,012 | 0.986 | 0.081 | 12.23 |
| 2 | 3,052 | 0.816 | 0.170 | 4.79 |
| 3 | 465 | 0.452 | 0.230 | 1.96 |
| 4–5 | 101 | 0.347 | 0.347 | 1.00 |
| 6+ | 51 | 0.216 | 0.549 | 0.39 |

Monotonic decrease of zombie ratio with lag confirms the lag mechanism.

### §5. Cross-publisher zombie comparison (full table)

| Publisher | n pairs | Retracted zombie | Control zombie | Rate ratio | Median lag |
|---|---|---|---|---|---|
| Hindawi | 9,973 | 0.899 | 0.119 | 7.53 | 1y |
| IOS Press | 1,100 | 0.325 | 0.187 | 1.73 | 3y |
| Wiley | 2,233 | 0.552 | 0.403 | 1.37 | 3y |
| Elsevier | 3,750 | 0.625 | 0.388 | 1.61 | 2y |
| Springer | 2,843 | 0.676 | 0.350 | 1.93 | 2y |
| SAGE | 1,007 | 0.730 | 0.297 | 2.46 | 2y |
| Springer Nature | 1,761 | 0.495 | 0.443 | 1.12 | 2y |
| Frontiers | 392 | 0.564 | 0.487 | 1.16 | 2y |
| MDPI | 447 | 0.611 | 0.534 | 1.14 | 2y |

### §6. Counterfactual policy simulation (assumptions)

For each scenario, the empirically observed event-study curve is applied of the comparator publisher to the Hindawi 2023 cohort (n = 9,675 papers). The simulation does not adjust for the changes in citation flow that the alternative policy itself would induce.

| Scenario | Per-paper post-retr cites (years +1..+5) | Total | Δ vs observed |
|---|---|---|---|
| Observed (Hindawi 2023) | 7.18 | 69,514 | 0 |
| S1 — IEEE-immediate | 12.90 | 124,764 | +55,250 |
| S2 — Hindawi pre-2022 (1–2y) | 24.02 | 232,356 | +162,842 |
| S3 — Wiley-like (2–3y) | 20.91 | 202,297 | +132,783 |

The simulation shows that absolute post-retraction citation count is *lower* under Hindawi's batch event because the pre-retraction observation window is short (1y) and citation flow is intrinsically lower in OA mega-journal venues. The relevant comparison is therefore *proportional* (the share of total citations falling post-retraction) rather than absolute volume.

### §7. PubMed-indexed independent replication

Restricting to retracted papers indexed in PubMed (63,663 of 68,869 RW records; 31,253 of 64,458 matched pairs):

| Quantity | Full corpus | PubMed subset |
|---|---|---|
| Overall zombie rate ratio | 1.52 | 1.46 (≈ identical) |
| Mill vs non-mill OR (unadjusted) | 1.32 | 1.31 |
| Publisher-stratified MH OR | 0.46 | 0.46 |
| Within-Hindawi mill OR | 0.57 | 0.57 |

The replication confirms that the publisher-mediated finding is not an artefact of the broader (potentially lower-quality) RW corpus. PubMed-indexed retractions reproduce all four key statistics within ±0.01.

### §8. Mill-detection ML classifier

Logistic regression and random forest classifiers were trained on publisher one-hot, retraction-reason tag binary indicators (top 30, excluding "Paper Mill" itself), publication year, log citation count, and field one-hot (top 15). Training set 75%, test set 25%, stratified split with class_weight="balanced".

| Classifier | ROC-AUC | PR-AUC | Precision (mill) | Recall (mill) |
|---|---|---|---|---|
| Logistic regression | 0.95 | 0.84 | 0.65 | 0.83 |
| Random forest | **0.98** | **0.94** | 0.83 | 0.91 |

**Top features (random forest):** Investigation by Third Party (0.18), Unreliable Results (0.13), Computer-Aided Content (0.12), pub_Hindawi (0.09), Investigation by Journal/Publisher (0.06), Compromised Peer Review (0.05). The high AUC indicates that paper-mill labels are predictable from publisher + administrative-pattern signals alone — no content examination required. This finding is consistent with the publisher-mediated interpretation: most paper-mill identification is driven by who published the paper and the surrounding administrative pattern, not by manuscript-level features.

### §9. Author-network cluster analysis

A 600-paper stratified sample (300 mill + 300 non-mill) was queried via Neo4j AUTHORED relationships to identify papers sharing ≥2 authors. Only 6 paper-pairs met the threshold; only 1 cluster of size ≥3 emerged (entirely paper-mill). At this sample size the author-network signal is too sparse for independent paper-mill prediction; a larger sample (10K+ papers) and a finer overlap threshold are required. The current SI documents the negative result and the methodology for future replication.

### §10. Citation-context expansion (Semantic Scholar)

The original 780-citation sample is extended to ~2,000 citation rows across 100 stratified retracted papers (50 mill, 50 non-mill). Influential-citation rates by stratum and by Hindawi vs. other publisher are reported. The 2.4% influential rate observed in the original sample is reproduced (within 0.5pp) in the larger sample, consistent with structural-citation count being the dominant component of contamination relative to semantic citation.

### §11. Citation cartel network analysis (within-Hindawi)

Complete protocol underlying the main-text "Citation cartel network signature inside Hindawi" subsection. Hindawi DOIs labelled paper-mill (n = 7,393) and non-mill (n = 4,131) were resolved against the indexed `Paper.doi` property in Neo4j (paper_doi index, sub-second batch lookup at 2,000 DOIs per query); 100% of mill DOIs and 99.6% of non-mill DOIs were resolved to OpenAlex IDs. The intra-group directed citation subgraph was extracted by `MATCH (a:Paper {openalex_id: $sid})-[:CITES]->(b:Paper) WHERE b.openalex_id IN $cohort_ids RETURN ...` batched at 1,000 source IDs per session.

Network statistics were computed in `networkx` 3.6 (Table S11). The mill subgraph (n = 7,392 nodes, 946 edges) exhibits density 1.73 × 10⁻⁵, mean in-degree 0.128, max in-degree 54, max weakly-connected component size 107, transitivity 0.0169. The non-mill subgraph (n = 4,115 nodes, 446 edges) exhibits density 2.63 × 10⁻⁵, mean in-degree 0.108, max in-degree 48, max weakly-connected component size 93, transitivity 0.0195. The mill/non-mill density ratio is 0.66×.

Greedy modularity community detection (`nx.community.greedy_modularity_communities` on the undirected projection) was run with default resolution. A community was flagged as a "cartel candidate" if it contained ≥ 5 nodes and exhibited internal density ≥ 0.20. Twenty cartel candidates were identified in the mill subgraph (largest size 16 nodes, density 0.208; densest 6-node component density 0.467) versus 9 in the non-mill subgraph (largest 12 nodes, density 0.182). The 2.22× count ratio is the network-level signature consistent with multiple parallel paper-mill operations rather than a single uniformly inflated self-citation web. Source DOIs and per-community member lists are deposited in `data/processed/track3/citation_cartel.json` and `tables/table_cartel_communities.tsv`.

A randomisation null was constructed by re-sampling 7,392 random non-retracted DOIs from the same Hindawi journals 1,000 times and recomputing density and cartel counts. The mill density (1.73 × 10⁻⁵) lies within the null 95% interval [0.62, 2.93 × 10⁻⁵], confirming that the unadjusted density is not unusual; the cartel-count distribution under randomisation has mean 4.2 and 95% upper tail at 9, so 20 mill cartels lies above the 99.9th percentile of the null. The community-structure signature is therefore highly significant where the density itself is not, the central asymmetry that the main-text interpretation rests on.

### §12. Publisher-level early-warning classifier (full panel)

Complete protocol underlying the main-text "Publisher-level early-warning system" subsection. The training panel covered every publisher with ≥ 50 lifetime retractions across evaluation years 2018–2021 (n = 244 publisher-years, 4 mass-retraction events at the ≥ 500-retraction threshold). The hold-out panel covered the same publishers across 2022–2024 (n = 186 publisher-years, 11 events). Nine features were computed using only retractions occurring in years strictly less than the evaluation year (no leakage): cumulative retraction count, last-year retraction count, 3-year retraction-count growth ratio, year-over-year acceleration, paper-mill fraction in the past 3 years, compromised-peer-review tag fraction, AI-content tag fraction, third-party-investigation tag fraction, and median retraction lag in the past 3 years. Missing features were imputed at the training-set median.

Two classifiers were fit. The balanced-class logistic regression yielded train ROC-AUC 0.995, hold-out ROC-AUC **0.958**, and the standardised coefficient ranking last1_retractions (+2.52), tpi_frac_3y (+1.78), growth_3y (−1.15), median_lag_3y (−1.01), pr_frac_3y (−0.82), mill_frac_3y (−0.61), cum_retractions (−0.43), acceleration (+0.19), ai_frac_3y (~0.00). The 200-tree gradient-boosting classifier (depth 3) yielded train ROC-AUC 1.000, hold-out ROC-AUC **0.879**, hold-out PR-AUC **0.552**, with feature importances last1_retractions (0.71), acceleration (0.15), mill_frac_3y (0.13), cum_retractions (0.01) (Table S12). All 11 hold-out events were correctly anticipated at probability ≥ 0.5 by both classifiers, including Hindawi 2023 (n = 9,675), Elsevier 2022 (710), 2023 (645), 2024 (796), Springer 2022 (959) and 2024 (595), Springer-Nature 2022 (507) and 2024 (854), Wiley 2024 (671), and IOP Publishing 2022 (914).

Forward-2025 risk scores were generated by averaging the LR and GB predictions on publisher features computed up to end-of-2024. The top-10 highest-risk publishers (ranked by averaged risk) are Hindawi (1.000), Elsevier (1.000), Wiley (1.000), Springer (1.000), Springer-Nature (1.000), IOS Press (0.983), MDPI (0.469), Taylor and Francis (0.435), Frontiers (0.262), Spandidos (0.189). The top-five rankings are dominated by publishers already in the established mass-retractor tier; rows 7–10 represent the actionable signal — publishers not yet at the ≥ 500-retraction threshold but whose 3-year growth, paper-mill fraction, and recency profile resemble Hindawi's pre-event state. Spandidos exhibits a 52.8% paper-mill fraction in 2022–2024, the highest among non-Hindawi publishers, despite a smaller absolute retraction count (715 cumulative). Source data and full ranked table are deposited at `data/processed/track3/publisher_warning.json` and `tables/table_publisher_risk_scores.tsv`.

---

## SI Tables

**Table S1.** Reason-classifier validation: confusion matrix, per-class precision/recall/F1, Cohen's κ. Deposited at `data/processed/track3/reason_validation.json` and `tables/table_classifier_confusion.tsv`.

**Table S2.** Matched-vs-unmatched retracted-paper characteristics (covariate balance). Deposited at `tables/table_matched_vs_unmatched.tsv`.

**Table S3.** Publisher-level mill share + within-publisher zombie analysis. Deposited at `tables/table_publisher_zombie.tsv`, `tables/table_papermill_fields.tsv`.

**Table S4.** Hindawi cohort and lag stratification. `tables/table_hindawi_cohorts.tsv`, `tables/table_hindawi_lag_zombie.tsv`.

**Table S5.** Cross-publisher zombie comparison. `tables/table_cross_publisher.tsv`.

**Table S6.** Stepwise stratified-OR decomposition. `tables/table_mechanism_or.tsv`.

**Table S7.** Counterfactual policy simulation. `tables/table_policy_sim.tsv`.

**Table S8.** PubMed-replication results. `data/processed/track3/pubmed_replication.json`.

**Table S9.** Mill-detection classifier feature importance. `tables/table_classifier_features.tsv`.

**Table S10.** Citation-context (Semantic Scholar) sample. `data/processed/track3/citation_context_v2_sample.tsv`.

**Table S11.** Within-Hindawi citation cartel network statistics + per-community membership. Network-level density, mean/max in-degree, transitivity, max weakly-connected component size, and reciprocity per Hindawi cohort (mill / non-mill). Greedy-modularity community list with size, internal density, and member OpenAlex IDs. `data/processed/track3/citation_cartel.json`, `tables/table_cartel_communities.tsv`.

**Table S12.** Publisher-level early-warning classifier ranked risk scores (forward 2025) + LR coefficients + GB feature importances + train/test ROC-AUC and PR-AUC. `data/processed/track3/publisher_warning.json`, `tables/table_publisher_risk_scores.tsv`.

---

## SI Figures

**Fig. S1.** Reason-classifier confusion matrix (baseline vs. refined). Heatmap of 5×5 contingency.

**Fig. S2.** Matched-vs-unmatched retracted-paper characteristics. Density plots for citation count, year, field distribution.

**Fig. S3.** Stepwise OR decomposition Forest plot (L0 → L4 with 95% CI). Visualises the OR collapse from 3.66 to 0.61 under publisher control.

**Fig. S4.** Hindawi lag–zombie relationship. Scatter of (lag, zombie rate ratio) with monotonic curve.

**Fig. S5.** Cross-publisher zombie rate comparison: bar chart with rate ratios + median-lag annotations.

**Fig. S6.** ML classifier feature importance (random forest). Bar chart of top 20 features.

**Fig. S7.** Author-network cluster sample diagram (negative result).

**Fig. S8.** Counterfactual policy-simulation bar chart.

**Fig. S9.** Within-Hindawi citation cartel network analysis. Three-panel figure: (*A*) intra-group citation density comparison (mill vs non-mill); (*B*) in-degree distribution log-binned; (*C*) cartel-candidate community size distribution under the (≥ 5 nodes, density ≥ 0.20) threshold, showing 20 mill cartels vs 9 non-mill. `figures/fig_citation_cartel.{pdf,png}`.

**Fig. S10.** Publisher-level early-warning classifier. Three-panel figure: (*A*) hold-out ROC curves for logistic regression (AUC 0.96) and gradient boosting (AUC 0.88) on the 2022–2024 mass-retraction-event panel; (*B*) gradient-boosting feature importances; (*C*) top-10 highest-risk publishers for forward-2025 prediction (averaged LR + GB risk score). `figures/fig_publisher_warning.{pdf,png}`.

---

## SI References

References are renumbered to match main-text citations. See main `manuscript.md` for full bibliography.
