# AI Adoption and Retraction Rates: A Correlation Without a Direction

**Authors**: Suan Lee¹ (Semyung University)

ORCID: 0000-0002-3047-1167

¹To whom correspondence should be addressed. E-mail: suanlee@semyung.ac.kr

**Target venue**: *Nature* Brief Communication / *Scientometrics* / preprint

**Article type**: Research note / Brief communication

**Word count (main text)**: ~1,400

---

## Abstract

A widely cited cross-sectional correlation between field-level artificial intelligence adoption and retraction rates (*r* = 0.489, *p* = 0.011) has been used to support the claim that AI-augmented research is associated with higher rates of error or misconduct. Using a panel of 26 OpenAlex primary fields observed annually from 2000 to 2023, this claim is tested under three progressively stricter specifications. The cross-sectional correlation weakens to *r* = 0.378 (*p* = 0.057) when computed on the most recent AI-identification method and the full retraction-count panel. Pooled panel correlation is *r* = 0.250 (*p* < 10⁻⁹, *n* = 624), small but statistically significant. Panel Granger-style fixed-effects regression of retraction rate on three-year-lagged AI fraction yields *F* = 1.27 (*p* = 0.29), failing to reject the null of no lead–lag predictive relationship; the reverse-direction placebo (retractions predicting subsequent AI adoption) is similarly null (*F* = 0.63, *p* = 0.60). The AI–retraction association replicates at the cross-sectional level but does not carry a temporal direction: fields with higher AI adoption do not systematically show subsequent increases in retraction rates, nor vice versa. The observed cross-sectional correlation is therefore most plausibly explained by third-variable confounders — publication volume, paper-mill prevalence, open-access adoption, and field-specific editorial capacity — rather than by a causal effect of AI on research integrity. This is reported as a null result that qualifies the emerging "AI causes more retractions" narrative and recommend against using the cross-sectional correlation as evidence for causal claims.

---

## Introduction

A recent strand of metascience literature has observed a positive cross-sectional correlation between field-level AI adoption and retraction rates, interpreting this as evidence that AI-augmented research pipelines may coincide with weakened quality control. The correlation has appeared in policy reports on research integrity and in discussions of paper-mill prevalence. Because cross-sectional associations cannot distinguish causation from shared confounding, the claim invites scrutiny: is the correlation a genuine signal of AI introducing errors, a byproduct of common field-level characteristics (publication volume, paper-mill pressure, editorial capacity), or an artefact of particular specifications of AI identification and retraction counting?

A balanced 26-field × 24-year panel is used (2000–2023) built from OpenAlex concept-based AI identification and Retraction Watch subject mappings to test the correlation under three specifications: cross-sectional, pooled panel, and temporally ordered (Granger-style) with field and year fixed effects. A reverse-direction placebo is also run to check whether temporal ordering runs in the opposite direction.

## Methods

AI adoption per field-year is the OpenAlex concept-based fraction (concepts: Artificial intelligence, Machine learning, Deep learning, Computer vision, Natural language processing, Pattern recognition) computed from the full 479M-paper Neo4j graph. Retraction counts per field-year come from Retraction Watch (68,870 records), mapped from RW `Subject` strings to OpenAlex primary fields using a deterministic subject→field dictionary covering the 26 primary fields. Retraction rate is retractions per million field papers in the same year. The panel is restricted to 2000–2023 (2024 is excluded as an OpenAlex extraction artefact; 2025 is excluded as incomplete). All regressions use OLS with HC3 robust standard errors. Field fixed effects and year fixed effects absorb time-invariant field heterogeneity and global year trends. Granger-style specification regresses retraction rate at time *t* on AI fraction at *t*−1, *t*−2, *t*−3; the joint *F*-test on the three lag coefficients is reported. The reverse placebo regresses AI fraction at *t* on retraction rate at *t*−1, *t*−2, *t*−3 under the same field+year FE.

## Results

**Cross-sectional.** At the 26-field level using 2015–2023 period means, Pearson *r* between AI adoption fraction and retraction rate is 0.378 (*p* = 0.057, *n* = 26). This is below the 0.489 reported in a previous specification; the difference is attributable to use of OpenAlex concept-based identification (broader than title-keyword identification) and to the full 2015–2023 period (versus earlier 2015–2022 windows).

**Panel pooled.** Pooled across 624 field-year observations, Pearson *r* = 0.250 (*p* = 2.24 × 10⁻¹⁰). The panel correlation is smaller than the cross-sectional because within-field time variation is smaller than between-field variation, but it is highly statistically significant.

**Panel Granger (forward).** Regressing retraction rate at year *t* on AI fraction at *t*−1, *t*−2, *t*−3 with field and year fixed effects yields a joint *F*-test of 1.27 (*p* = 0.29, *R*² = 0.64). Individual lag coefficients are positive (ai_lag1 = 128.6 per million per pp of AI fraction, *p* = 0.21; ai_lag2 = 86.5, *p* = 0.40; ai_lag3 = 19.7, *p* = 0.83) but none reach conventional significance, and the joint test fails to reject the null of no predictive relationship.

**Reverse-direction placebo.** Regressing AI fraction at year *t* on retraction rate at *t*−1, *t*−2, *t*−3 yields joint *F* = 0.63 (*p* = 0.60). Neither direction carries a temporally ordered predictive signal.

**Per-field heterogeneity.** Within-field time-series correlations are large in several fields (Computer Science *r* = 0.68; Biochemistry, Genetics and Molecular Biology *r* = 0.67; Chemistry *r* = 0.41) but null or undefined in others; the sign is consistently positive where defined.

## Discussion

The cross-sectional AI–retraction correlation replicates under OpenAlex concept-based AI identification and Retraction Watch subject mapping, at modest strength (*r* ≈ 0.25–0.38). However, panel fixed-effects specifications that explicitly test temporal precedence — either AI adoption leading to retractions, or retractions leading to AI adoption — fail to reject the null of no lead–lag relationship. Within-field time-series correlations are large in specific fields (Computer Science, Biochemistry), but this reflects parallel trends rather than causation: both AI adoption and retraction counts have risen monotonically in those fields, and field+year fixed effects absorb most of the shared trend.

Three alternative explanations for the cross-sectional correlation survive the panel evidence. First, publication-volume confounding: fields that publish more papers per year both adopt AI more rapidly (more opportunity for computational work) and accumulate more retractions in absolute terms (more opportunity for flawed work). Retractions per million normalises for this somewhat, but paper-mill fields (where many published papers are low-quality) compound the issue because paper-mill retractions have risen sharply post-2019 in fields that also adopted AI. Second, editorial-capacity confounding: fields with rapid growth and open-access models (Computer Science, Materials Science, Biochemistry) combine high AI adoption with overloaded review systems that miss errors that become retractions. Third, selection into retraction: fields with more sophisticated methodological scrutiny (often the same fields that have adopted AI to automate parts of that scrutiny) may also be the fields that detect and retract errors at higher rates, producing a spurious positive correlation.

None of these confounders implies that AI causes retractions. Equally, the null Granger finding does not rule out a localised causal pathway — AI-augmented paper mills, or specific types of AI misuse in specific subfields — but it does rule out the broad claim that cross-sectional correlation alone supports.

**Recommendation.** Subsequent work should distinguish (a) AI-augmented paper mills, which produce fraudulent manuscripts at scale, from (b) honest AI-augmented research, which may or may not have elevated error rates. The first is a tractable policy target (detection tools, mandatory disclosure of AI tool use); the second requires careful subfield-level analysis with valid instruments. The cross-sectional AI–retraction correlation, in its current form, supports neither target unambiguously and should not be used as evidence for policy proposals that conflate the two.

## Data and Code

All primary data are openly available (OpenAlex 479M works, Retraction Watch 68,870 records). Panel construction, Granger regressions, and figure code are deposited at [repository URL].

---

## Figure

![**Fig. 1.** AI adoption and retraction rates across 26 OpenAlex primary fields. (*A*) Cross-sectional scatter of 2015–2023 mean AI publication fraction vs. retractions per million papers; Pearson r=0.378, p=0.057, n=26. (*B*) Panel fixed-effects coefficients on 1-, 2-, and 3-year lagged AI fraction predicting retraction rate; joint F=1.27, p=0.29 (field and year fixed effects included). Neither direction of the temporal Granger test rejects the null of no lead-lag relationship.](fig_ai_retraction.pdf)
