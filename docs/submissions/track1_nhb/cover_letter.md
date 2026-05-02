# Cover Letter — Nature Human Behaviour

**Date**: April 2026

**To**: The Editor, *Nature Human Behaviour*

**Re**: Submission of "The Great Divergence: Heterogeneous AI Adoption and Its Consequences for Scientific Production"

---

Dear Editor,

This letter accompanies "The Great Divergence: Heterogeneous AI Adoption and Its Consequences for Scientific Production" as a Research Article for *Nature Human Behaviour*.

## Summary

Artificial intelligence is widely described as a general-purpose technology reshaping all of science, yet its penetration across disciplines has been neither uniformly measured nor rigorously tested. Using a 25-year panel of 15 scientific fields derived from the complete OpenAlex corpus (479M works, 2.87B citations), this paper documents dramatic heterogeneity — a "great divergence" in adoption that has widened, not narrowed, over the past two decades — and identify the structural field-level predictors that drive it.

## Key Findings

1. **Sixfold cross-field gap in AI publication shares.** Recent-period (2015–2024) AI publication fractions range from 22.2% (Computer Science) to 3.5% (Environmental Science); four fields (Chemistry, Environmental Science, Materials Science, Medicine) never crossed a 0.5-pp/yr acceleration threshold over 25 years.

2. **No field has saturated.** Logistic growth modelling places all 15 fields in the early phase of their S-curves; inflection points lie beyond the observation window, and carrying capacities span 0.08–0.56.

3. **A 2019 AlphaFold structural break in Biology.** Chow structural-break testing identifies a highly significant break in Biology's AI adoption trajectory in 2019 (*F* = 11.11, *p* < 0.001), aligned with the AlphaFold release — the first formal statistical evidence that transformative AI applications in a field's core problem can induce discrete rather than incremental acceleration.

4. **Causal differential acceleration of 2.32 pp.** A staggered-timing difference-in-differences design with field and year fixed effects yields a 2.32-pp differential acceleration in treatment fields (*p* < 0.001, *R*² = 0.92), robust to a narrower three-field specification (1.75 pp, *p* = 0.002).

5. **Data availability and regulatory burden drive adoption — not mathematical intensity.** Cross-field OLS identifies data availability as the dominant positive predictor of current adoption (β = 0.54, *p* = 0.010) and regulatory burden as the dominant negative predictor of acceleration (β = −0.032, *p* = 0.009); mathematical intensity has no independent effect. This overturns the intuition that quantitative sophistication mechanically produces AI uptake.

## Why Nature Human Behaviour

This paper treats AI adoption as a social-behavioural phenomenon shaped by institutional structure, data infrastructure, regulatory regimes, and disciplinary culture — squarely within the NHB agenda. It combines bibliometric scale (479M papers, 25 years, 15 primary fields) with formal inferential methods (structural break detection, staggered DID with panel fixed effects, heteroscedasticity-robust cross-field regression) that are rarely brought together in this literature. The findings directly address a policy question of broad interest: whether "AI for science" programmes should assume universal diffusion or expect persistent heterogeneity. The evidence favours targeted infrastructure investment over generic funding increases.

## Data and Reproducibility

All primary data sources are openly available (OpenAlex, 479M works). A reproducing Jupyter notebook, all derived Parquet files, the field-characteristics scoring spreadsheet, Neo4j bulk-import CSVs, and figure-generation scripts will be deposited with the manuscript. An interactive SciGraph Explorer provides reviewer access to the panel structure and per-field time series.

## Declarations

- This manuscript has not been published previously and is not under consideration at any other journal.
- All authors have approved the submitted version.
- The authors declare no competing interests.
- No human subjects or animal research was involved.

Thank you for considering this work.

Sincerely,

Suan Lee
Semyung University
suanlee@semyung.ac.kr
