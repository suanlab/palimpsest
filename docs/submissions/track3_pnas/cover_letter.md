# Cover Letter — PNAS

**Date**: May 2026

**To**: The Editorial Board, *Proceedings of the National Academy of Sciences*

**Re**: Submission of "Citation Palimpsests: Hindawi 2023 as a Natural Experiment for the Publisher-Mediated Paper-Mill Citation Crisis"

---

Dear Editors,

This letter accompanies "Citation Palimpsests: Hindawi 2023 as a Natural Experiment for the Publisher-Mediated Paper-Mill Citation Crisis" for consideration as a Research Article in *PNAS*, classified under **Social Sciences** (metascience). The submission is to the **Direct Submission Plus** track; the manuscript fits PNAS Plus's 10-page format with 6 main figures, an SI Appendix containing 12 supporting sections, 12 tables (S1–S12) and 10 figures (S1–S10), and 55 references.

## Summary

A growing literature has interpreted the persistence of citations to retracted papers — and especially to paper-mill content — as evidence of a content-driven crisis in the scientific correction system. Using a 479,290,642-paper Neo4j citation graph linked to 101,581 retracted papers, this paper exploits Hindawi's 2023 mass retraction of 9,675 papers in a single year — the largest retraction event in the historical record — as a natural experiment that distinguishes content-driven from publisher-driven explanations of post-retraction citation persistence. The analysis combines (i) a 64,458-pair matched-control design stratified by retraction reason, (ii) a stepwise stratified-OR decomposition of the apparent paper-mill effect, (iii) within-Hindawi mill vs. non-mill comparison, (iv) cross-publisher comparison against regular retraction flows, (v) a difference-in-differences design with synthetic control, (vi) a citation-cartel network analysis, (vii) a publisher-level early-warning classifier with two-year forward validation, and (viii) a counterfactual policy simulation.

## Key Findings

1. **The apparent paper-mill effect dissolves under publisher stratification.** The unadjusted mill-vs-non-mill zombie odds ratio is 3.66; after retraction-year and field stratification it falls to 1.5; after additional stratification on publisher it inverts to **0.61**. Mill content per se is not uniquely zombie-prone; the apparent effect was driven by which publisher retracted the paper.

2. **Hindawi natural experiment supports publisher-mediated mechanism.** Within Hindawi (responsible for 84% of its 11,524 retractions in 2023 alone), mill and non-mill retracted papers exhibit statistically indistinguishable zombie patterns (within-Hindawi mill vs. non-mill OR = **0.57**, *p* = 5 × 10⁻¹⁴), both at ~89% zombie rate. Both publisher and content arrive at the same outcome under batch retraction processing.

3. **Lag is the dominant determinant of zombie status.** Hindawi papers retracted within 0–1 years of publication show 12–18× zombie ratios; at lag 4–5 years the ratio falls to 1×. The lag–zombie relationship is monotonic and large.

4. **Cross-publisher comparison shows Hindawi is a clear outlier.** Hindawi batch retracted papers exhibit a 7.5× rate ratio versus matched controls; comparators with regular retraction flows (Wiley 1.4×, Elsevier 1.6×, Springer 1.9×, SAGE 2.5×) cluster three to five times lower.

5. **Difference-in-differences with synthetic control supports causal identification.** Two-way FE DiD on a 6-publisher × 8-year panel yields +0.27 (p=0.057); synthetic Hindawi (Springer 0.82 + Elsevier 0.18) projects 2023 counterfactual zombie rate of 0.47 vs observed 0.95 — a +0.47 treatment effect. Placebo on Wiley is null.

6. **Process-level evidence (smoking gun): editorial signals jump in 2022–23 within Hindawi.** Compromised peer review, AI-generated content, and third-party investigation tags rise from 0% in 2017–2021 to 65–95% in 2023 within Hindawi alone. No comparator publisher shows similar process-tag jumps.

7. **Forward prediction (2020–22 → 2023–24 hold-out) achieves ROC-AUC 0.95.** Random forest using only publisher and administrative signals (no content) forecasts mill labels in a future period; identifies Spandidos and Taylor & Francis as candidate next-batch-event publishers.

8. **Citation cartel network signature inside Hindawi.** The mill subgraph contains **20 dense citation cartels** (≥5 nodes, density ≥ 0.20) versus 9 in the non-mill subgraph — a 2.22× difference — consistent with multiple parallel paper-mill cells operating concurrently inside Hindawi rather than a single monolithic ring.

9. **Publisher-level early-warning classifier.** A 9-feature publisher-year classifier trained on 2018–2021 anticipates all 11 mass-retraction events (≥500 retractions/year) in the 2022–2024 hold-out at hold-out ROC-AUC **0.96** (logistic) / 0.88 (gradient boosting). Forward 2025 risk ranks **MDPI (0.47), Taylor & Francis (0.44), Frontiers (0.26), Spandidos (0.19)** as the top non-established candidates — operationalising the central finding as a deployable monitoring tool.

10. **External validity confirmed on PubMed-indexed subset.** Restricting to retracted papers indexed in PubMed (partial-independent biomedical corpus) reproduces key statistics within ±0.01 (publisher-MH OR = 0.46, within-Hindawi OR = 0.57).

## Why PNAS

This paper is a metascience-policy contribution at the centre of contemporary scientific-integrity debate. The dominant narrative in metascience literature attributes post-retraction citation persistence to features of the content (paper mills, generative-AI-produced manuscripts, fake-reviewer rings); the results redirect that narrative toward publisher infrastructure. The reframing is consequential: content-level interventions cost a great deal and target the wrong actors, while publisher-level interventions (lag-monitoring, accountability metrics, mandatory rapid-correction infrastructure) are within the direct authority of editorial boards and funding bodies. The natural-experimental approach (Hindawi 2023 as the largest single-publisher retraction event in history) provides causal inference that prior cross-sectional analyses of retraction-citation patterns have lacked.

The submission is **uniquely time-sensitive**. Wiley's 2023 acquisition of Hindawi and subsequent editorial overhaul places the natural experiment in a closing observation window: post-acquisition Hindawi will not generate further batch events of comparable scale. Spandidos, MDPI, Taylor & Francis, and Frontiers — the highest-risk publishers identified by our forward 2025 classifier — are actively under research-integrity scrutiny, and the publisher-level early-warning system is most actionable when published before, not after, the next batch event. Submission to PNAS as a Research Article puts the policy lever in front of NAS-affiliated decision-makers (NIH, NSF, ERC, NRF) at the moment it is most useful.

The work is methodologically rigorous (matched-control design plus stepwise stratified decomposition plus natural-experimental causal claim plus difference-in-differences with synthetic control plus citation-cartel network analysis plus 0.96-ROC-AUC forward-validation classifier plus PubMed-indexed independent replication), policy-relevant (five concrete actionable interventions specified in Discussion §Policy), and broadly interdisciplinary (network science + econometrics + sociology of science + publishing economics + machine learning).

## Suggested Editors

- **Susan Fitzpatrick** (NAS member, James S. McDonnell Foundation) — research integrity, science of science.
- **Carl Bergstrom** (NAS Section 51 chair-elect, University of Washington) — information ecology, scholarly publishing.
- **Jevin West** (University of Washington) — metascience, retraction-watch contributor.

## Suggested Reviewers (5)

- **Vincent Larivière** (Université de Montréal) — OpenAlex/bibliometric expert; matched-control retraction studies.
- **Scott Stern** (MIT Sloan) — co-author of the Azoulay et al. retraction-impact paper.
- **Lutz Bornmann** (Max Planck Society) — bibliometrics methodologist; field-rate retraction patterns.
- **Elisabeth Bik** (independent, microbiology research integrity) — paper-mill detection expertise.
- **Jodi Schneider** (University of Illinois Urbana-Champaign) — continued-citation-of-retracted-work literature.

## Reviewers to avoid

- Hindawi or Wiley editorial staff (recused parties).
- Authors of papers retracted in the Hindawi 2023 cohort (potential conflict).

## Data and Reproducibility

All primary data sources are openly available: Retraction Watch (68,870 records) and OpenAlex (479M works). The full Neo4j graph, bulk-import CSVs, classifier-validation tables, sensitivity analyses, ML-classifier weights, and a reproducing Jupyter notebook will be deposited with the manuscript. The companion code repository is at https://github.com/suanlab/palimpsest; an interactive graph-exploration platform (SciGraph Explorer) is hosted at http://suan.iptime.org:8300/ for reviewer use. The pre-print is concurrently posted at SocArXiv (DOI to be assigned at posting).

## Declarations

- This manuscript has not been published previously and is not under consideration at any other journal.
- The author is the sole author and has approved the submitted version.
- The work was supported by the Semyung University Research Grant of 2025; no other funding was received.
- No competing interests are declared.
- No human subjects or animal research was involved.

Thank you for considering this work.

Sincerely,

Suan Lee  
Semyung University  
ORCID: 0000-0002-3047-1167  
suanlee@semyung.ac.kr
