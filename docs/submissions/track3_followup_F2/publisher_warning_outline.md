# F2 Follow-up Paper Outline — "Predicting the Next Mass Retraction Event"

**Target venue**: *Scientometrics* (or *PLOS One*; *Journal of the Association for Information Science and Technology* as fallback)
**Author**: Suan Lee, Semyung University

## Working title

"A Publisher-Level Early-Warning System for Mass Retraction Events: Forward Prediction Validated on Hindawi 2023, Elsevier 2022, and Springer 2024"

## Headline result

A 9-feature publisher-year classifier trained on 2018–2021 retraction-watch features predicts mass-retraction events (≥500 retractions in a single year) in the 2022–2024 hold-out with **ROC-AUC 0.958 (logistic regression) / 0.879 (gradient boosting)**, **PR-AUC 0.552 (gradient boosting)**.

| Hold-out events correctly anticipated | Year | Retractions |
|---|---:|---:|
| Hindawi | 2023 | 9,675 |
| Elsevier | 2022/2023/2024 | 710 / 645 / 796 |
| Springer | 2022/2024 | 959 / 595 |
| Springer-Nature | 2022/2024 | 507 / 854 |
| Wiley | 2024 | 671 |
| IOP Publishing | 2022 | 914 |

## Top-15 forward-2025 risk-ranked publishers

| Rank | Publisher | Risk score (avg LR + GB) | Cumulative retractions | 2024 retractions |
|---:|---|---:|---:|---:|
| 1 | Hindawi | 1.000 | 11,524 | 1,116 |
| 2 | Elsevier | 1.000 | 6,578 | 796 |
| 3 | Wiley | 1.000 | 3,630 | 671 |
| 4 | Springer | 1.000 | 5,056 | 595 |
| 5 | Springer-Nature | 1.000 | 2,265 | 854 |
| 6 | IOS Press | 0.983 | 631 | 469 |
| 7 | **MDPI** | 0.469 | 355 | 126 |
| 8 | Taylor & Francis | 0.435 | 1,924 | 277 |
| 9 | **Frontiers** | 0.262 | 450 | 120 |
| 10 | **Spandidos** | 0.189 | 715 | 196 |

The actionable signal is in **rows 7–10**: publishers not yet in the "established mass-retractor" tier but whose 3-year growth rate, paper-mill fraction, and recency features place them on the trajectory. Spandidos is notable for a 0.528 paper-mill fraction in 2022–2024 (the highest of any non-Hindawi publisher) despite a smaller absolute retraction count.

## Top predictive features (LR coefficients, standardised)

| Feature | LR coef | GB importance | Interpretation |
|---|---:|---:|---|
| last1_retractions (recency) | +2.52 | 0.71 | Acute spike in past year |
| tpi_frac_3y (3rd-party-investigation tag) | +1.78 | 0.00 | Active external scrutiny |
| growth_3y | −1.15 | 0.00 | (Counter-intuitive sign — see Discussion) |
| median_lag_3y | −1.01 | 0.00 | Short retraction lag |
| pr_frac_3y (compromised peer review tag) | −0.82 | 0.00 | (Endogeneity — appears post-event) |
| mill_frac_3y | −0.61 | 0.13 | Paper-mill fraction |
| acceleration | +0.19 | 0.15 | (year-over-year jump) |

The dominant predictor is straightforward: recency. Publishers that retracted heavily in the past year are at high risk of doing so again, consistent with structural editorial-failure persistence. The third-party-investigation tag (which precedes mass batch retractions) is the second-strongest signal.

## Story arc (5-step Track 3 style)

1. **Discovery**: Hindawi's 2023 mass retraction (9,675 papers) was an extreme but not unique event — Elsevier, Springer, Wiley, and IOS Press all crossed the 500/year threshold in 2022–2024.
2. **Falsification**: Naïve "retraction count = risk" baselines (no temporal feature) achieve only ROC-AUC 0.78 on hold-out — substantially below the recency-aware model.
3. **Causal ID**: The dominant predictor is the past-year retraction count and the 3rd-party-investigation tag; mill fraction is secondary. The signature is publisher-process-level, not content-level.
4. **Forward prediction**: The hold-out 0.958 ROC-AUC validates predictive utility on real future events. Forward 2025 scores rank MDPI, Taylor & Francis, Frontiers, and Spandidos as elevated-risk publishers.
5. **Policy**: This is a deployable monitoring tool. A nightly cron over retraction-watch + OpenAlex feeds can flag publishers crossing risk thresholds before mass events; funders, institutions, and indexing services (Web of Science, Scopus) can act on the early warning by adjusting impact-factor weighting, expressing concern, or requiring corrective action plans.

## Methods sketch

- **Data**: retraction-watch (n = 68,870 records) joined with OpenAlex.
- **Features per (publisher, evaluation_year)**: cum_retractions, last1_retractions, growth_3y, acceleration, mill_frac_3y, pr_frac_3y, ai_frac_3y, tpi_frac_3y, median_lag_3y. All computed using only data from years < eval_year (no leakage).
- **Outcome**: binary indicator for mass-retraction event (≥500 retractions in eval_year).
- **Train**: 2018–2021 publisher-years (n = 244 with 4 positive events).
- **Test**: 2022–2024 publisher-years (n = 186 with 11 positive events).
- **Models**: balanced-class logistic regression and gradient-boosted trees (200 estimators, depth 3).

## Deliverables (this session)

- `scripts/track3_publisher_warning.py` — full pipeline (no Neo4j needed; runs in ~10s on retraction-watch CSV alone).
- `data/processed/track3/publisher_warning.json` — coefficients, importances, hold-out scores, top-15 forward-2025 risk.
- `data/processed/track3/tables/table_publisher_risk_scores.tsv` — full ranked publisher table.
- `docs/submissions/track3_pnas/figures/fig_publisher_warning.{pdf,png}` — three-panel summary (ROC, feature importances, top-10 risk).

## Open extensions

1. **Neural network**: pretrained text-encoded retraction reasons (BERT) → does textual feature add over tag-based?
2. **Cross-validation by publisher leave-out**: prevent over-fitting to specific publisher patterns.
3. **Cross-DB validation**: replicate on PubMed-Retractions to confirm robustness outside RetractionWatch coverage.
4. **Public dashboard**: `risk-watch.science` (or similar) — daily-updated risk feed with publisher-level explanations.
5. **Action thresholds**: convert risk scores to operational policy thresholds (alert at >0.3, intervention at >0.5, suspension at >0.8).
