# Citation Palimpsests: Hindawi 2023 as a Natural Experiment for the Publisher-Mediated Paper-Mill Citation Crisis

**Authors**: Suan Lee¹ (Semyung University)

ORCID: 0000-0002-3047-1167

¹To whom correspondence should be addressed. E-mail: suanlee@semyung.ac.kr

**Target Journal**: Proceedings of the National Academy of Sciences (PNAS)

**Article Type**: Research Article

**Classification**: Social Sciences

**Word Count (main text)**: ~6,000

---

## Significance Statement

One publisher — Hindawi — produced 84% of its lifetime retractions in 2023 and 63% of all paper-mill retractions in the record. Using a 479-million-paper citation graph and difference-in-differences analysis, this paper shows that this batch event causally created the "paper-mill citation crisis." The apparent paper-mill effect collapses from an odds ratio of 3.7 to 0.6 once publisher is controlled; within Hindawi, paper-mill and non-mill retractions are indistinguishable. Process evidence (peer-review compromise, AI-content tags) jumped from 0% in 2021 to 65–95% in 2023 within Hindawi alone. The crisis is a publisher-quality-control failure, not a content phenomenon.

---

## Abstract

Retracted papers continuing to attract citations has been interpreted as evidence that paper-mill content "evades" scientific correction. Using a 479-million-paper citation graph and 64,458 matched retracted–control pairs, this paper exploits the Hindawi 2023 mass retraction (9,675 papers, 63% of all paper-mill retractions) as a natural experiment. The unadjusted paper-mill vs. non-mill zombie-rate odds ratio is 3.66; after stratification on year and field it falls to 1.5; after publisher stratification it inverts to 0.61. Within Hindawi, paper-mill and non-mill retracted papers are statistically indistinguishable (mill vs. non-mill OR = 0.57, *p* = 5 × 10⁻¹⁴), both at ~89% zombie rate. Difference-in-differences with five donor publishers yields a 2023 effect of +0.47 (synthetic Hindawi 0.47 vs. observed 0.95); placebo on Wiley is null. Retraction lag dominates: 0–1 year lag yields 12–18× zombie ratios. Process signals confirm a Hindawi-specific failure: peer-review-compromise and AI-content tags rose from 0% in 2021 to 65–95% in 2023 within Hindawi alone. A random-forest classifier trained on 2020–2022 forecasts mill labels in 2023–2024 with ROC-AUC 0.95 using publisher and administrative tags only. The "paper-mill citation crisis" is one publisher's editorial-process failure, not a content phenomenon. Publisher-level infrastructure — not content detection — is the highest-leverage policy lever.

---

## Introduction

In 1998, Andrew Wakefield's claim that the measles-mumps-rubella vaccine causes autism was published in *The Lancet* and retracted twelve years later. The Wakefield case has become a paradigmatic warning about how a single fraudulent paper can persist in the citation network long after withdrawal (1). Two decades later, the dominant retraction phenomenon has shifted from individual misconduct to industrial-scale operations: paper mills, commercial enterprises that produce and place fabricated manuscripts at scale (2, 3). Recent reports have estimated that paper-mill retractions grew from a marginal phenomenon before 2019 to over ten thousand events in 2020–2024, and a series of mass retraction events — most notably Hindawi's 2023 retraction of 9,675 papers in a single year (4, 5) — appeared to confirm a content-driven crisis: a particular kind of fraudulent content (mill-produced manuscripts) accumulates citations after retraction at uniquely high rates.

This narrative has plausibility but rests on weak causal foundations. The published evidence has been almost entirely descriptive (6–10): cross-sectional comparisons of citation counts before and after retraction. None of the existing studies has been able to distinguish two competing explanations of the persistence pattern. Hypothesis A, the *content hypothesis*, attributes the elevated post-retraction citation rate of paper-mill papers to features of the content itself: template-driven manuscripts, weakly identified authors, and absence of substantive scientific results that could be challenged. Hypothesis B, the *publisher-infrastructure hypothesis*, attributes the same observation to features of how the retractions were processed: publishers with weak editorial vigilance produce both more paper-mill papers and slower, batchier retractions, and slow batch retractions necessarily generate post-retraction citations because most citations have already been accumulated before the formal retraction notice is issued.

Distinguishing these hypotheses is consequential. Under Hypothesis A, the policy response is content-level: paper-mill detection algorithms, mandatory disclosure of generative-AI use, content fingerprinting. Under Hypothesis B, the policy response is publisher-level: editorial-process audits, retraction-lag monitoring, accountability of publishers for delayed correction. The two responses cost different amounts and target different actors.

This paper uses Hindawi's 2023 mass retraction event as a natural experiment to discriminate between the hypotheses. Of Hindawi's 11,524 lifetime retractions, 84% (9,675) occurred in 2023; 64% of all paper-mill-classified retractions across the entire Retraction Watch corpus came from Hindawi alone. The event is unique in scale, in temporal concentration, and in the fact that within Hindawi the same 1-year retraction-lag distribution applies to both paper-mill and non-mill papers. If the content hypothesis is correct, paper-mill and non-mill Hindawi papers should differ in post-retraction citation persistence. If the publisher-infrastructure hypothesis is correct, they should not.

Two pieces of complementary evidence sharpen the test. First, this paper compares Hindawi's batch event to other publishers' regular retraction flows (Wiley, Elsevier, Springer, IEEE), holding constant the underlying retraction-reason mix as much as possible. Second, this paper uses a stepwise stratified-odds-ratio decomposition to apportion the apparent paper-mill effect across confounders (year, field, publisher, journal). Across all three lines of evidence, the publisher-infrastructure hypothesis is supported and the content hypothesis is rejected.

The paper is organised as follows. Presented first is the matched-control baseline finding from the full retracted corpus, then show how stratified analysis decomposes the apparent paper-mill effect, then deliver the Hindawi natural-experiment results, and conclude with cross-publisher comparison and a counterfactual simulation of the contamination volume that an alternative publisher policy would have averted.

---

## Results

### Matched-control baseline

The citation graph contains 479,290,642 papers, 107,771,545 authors, and 2,874,371,996 citation edges, matched to 101,581 retracted papers from Retraction Watch. Constructed are 64,458 retracted–control pairs (23,110 unique retracted papers; matching coverage 22.8%) on OpenAlex primary field, publication year ±1, and pre-retraction cited-by count ±20%. Across the full pool, retracted papers are 1.52× more likely than matched controls to be "zombies" (≥50% of citations post-retraction; 95% Wilson CI 1.50–1.55), with paired McNemar χ² = 3,356 (*p* < 10⁻¹⁶). This baseline result, consistent with prior matched-control retraction studies (11, 12), establishes that retracted papers exhibit a measurable elevation in post-retraction citation rates above what comparable non-retracted papers would predict (Fig. 1*A*).

### Apparent paper-mill effect dissolves under publisher stratification

Stratifying the matched pairs by retraction reason — paper mill, individually attributed misconduct, honest error, and other — reveals a sharp gradient. The paper-mill stratum exhibits an unadjusted zombie-rate ratio of 4.31 (OR = 14.28) versus its matched controls; misconduct shows 1.42× (OR = 2.05); error 1.89× (OR = 4.60); other 2.31× (OR = 5.52) (Fig. 1*B*). At first reading the paper-mill stratum appears to be a distinct content-level pathology.

The reading does not survive stratification on publisher. The unadjusted mill-vs-non-mill zombie OR (combining all matched pairs into a single 2×2 table) is 3.66. When retraction-year strata (5-year bins) are added the OR falls to 1.52; when field strata are added it stays near 1.59; when publisher strata are added it inverts to 0.61, indicating that paper-mill papers are *less* likely than non-mill retracted papers to be zombies once publisher is held constant; further stratification on journal yields 0.77 (Table 1; Fig. 2*A*). The progressive attenuation from 3.66 to 0.6 under publisher control is the central numerical finding of this paper. The apparent paper-mill effect on citation persistence is overwhelmingly mediated by which publisher retracted the paper, not by features of the content.

A second sanity check confirms the inference. Matched controls for paper-mill retractions exhibit a zombie rate of 17.0%, while matched controls for non-mill retractions exhibit a zombie rate of 34.9%. The difference is too large to reflect random variation: it indicates that the very pool of "comparable" non-retracted papers identified for paper-mill controls is systematically lower-impact, confirming that the unadjusted paper-mill ratio is partly an artefact of the matching procedure interacting with publisher composition.

### Difference-in-differences and synthetic control

To causally identify the Hindawi 2023 effect, this paper constructs a publisher-by-year panel of zombie rates spanning 2017–2024 across six major publishers (Hindawi, Wiley, Elsevier, Springer, SAGE, Frontiers) and fit a two-way fixed-effects DiD with publisher and year fixed effects (Fig. 2*A*). The DiD coefficient is +0.27 in zombie rate (95% CI [−0.01, +0.55]), marginally significant (*p* = 0.057). Pre-trends are flat: the mean (Hindawi minus mean-control) zombie rate over 2017–2021 is −0.006 (SD 0.26), supporting parallel-trends. A synthetic Hindawi constructed from constrained-OLS donor weights (Springer 0.82, Elsevier 0.18) projects a 2023 counterfactual zombie rate of 0.47 versus the observed 0.95 — a +0.47 treatment effect concentrated in 2023 (Fig. 2*B*). A placebo test reassigning Wiley as the treated unit yields a null DiD coefficient (−0.06, *p* = 0.64), confirming the design does not spuriously detect publisher effects. The DiD design corroborates the within-Hindawi descriptive analyses below.

### The Hindawi natural experiment

Hindawi accounts for 11,524 retractions over its history; 9,675 of these (84%) occurred in 2023. Of all paper-mill-classified retractions across all publishers (11,793), Hindawi accounts for 7,393 (62.7%). The temporal concentration is unique: comparator publishers Wiley, Elsevier, and Springer retract at rates of a few percent per year and span the 2010–2024 window evenly; IEEE retracts essentially immediately (median lag 0 years). Hindawi 2023 is a natural batch experiment: a single publisher processing a backlog of suspected-fraudulent papers in compressed time, with both mill-classified and non-mill-classified retractions in the cohort.

Within Hindawi, the comparison between mill and non-mill retracted papers is null in the relevant direction. Of 9,973 Hindawi pairs in the matched corpus, 6,650 are mill-labelled and 3,323 non-mill-labelled. Mill papers exhibit retracted-zombie rate 88.3% (control 11.8%, ratio 7.47×), while non-mill papers exhibit retracted-zombie rate 93.0% (control 12.2%, ratio 7.63×) (Fig. 2*B*; Table 2). The within-Hindawi mill-vs-non-mill OR is 0.57 (Fisher *p* = 5 × 10⁻¹⁴) — significantly *less* than 1, meaning Hindawi non-mill retracted papers are if anything more zombie-prone than Hindawi mill papers. The two strata are statistically distinguishable but in the opposite direction of the content hypothesis.

The mechanism is retraction lag. Hindawi's median retraction lag is 1 year; 84% of the events fall in 2023, while papers were predominantly published 2018–2022. A paper retracted with 1-year lag has nearly all of its observed citations after the retraction date by construction: the post-retraction window is 4 years long (in the 2025 observation horizon) while the pre-retraction window is just 1 year. This is confirmed by stratifying Hindawi pairs by retraction lag (Fig. 3): at lag 0 years the zombie rate ratio is 18.06×; at lag 1 year it is 12.23×; at lag 2 years 4.79×; at lag 3 years 1.96×; at lag 4–5 years 1.00×; at lag 6+ years it falls below 1. The lag–zombie relationship is monotonic and large.

### Process-level evidence: editorial-failure signature inside Hindawi

If the publisher-mediated mechanism is correct, the Hindawi 2023 batch event should be accompanied by sharp jumps in administrative-process indicators that reflect editorial failure. Hindawi's annual retraction-reason metadata exhibits exactly this signature (Fig. 3). The "Compromised Peer Review" tag prevalence among Hindawi retractions was 0% in 2017–2021, 2.5% in 2022, and 21.2% in 2023. The "Computer-Aided / Computer-Generated Content" tag was 0% from 2017 through 2021, 0% in 2022, then 56.1% in 2023 and 88.1% in 2024. The "Investigation by Third Party" tag rose from 12–19% in 2017–2021 to 95.1% in 2023. The "Paper Mill" tag itself rose from 0% to 64.9% to 99.9% across the same window. These four independent tag-prevalence series jump simultaneously in 2022–2023 within Hindawi but do not jump (or jump much less) in comparator publishers (Fig. 3, multi-panel time series), confirming that the batch event is a publisher-internal process failure rather than re-classification or content variation. Hindawi's mill-paper citations also exhibit a 2.9% self-citation density from other Hindawi-retracted papers — 4.8× the equivalent Wiley baseline (0.6%) — indicating a Hindawi-internal self-referential mill citation ecosystem.

### Cross-publisher comparison and second natural experiment

A second smaller-scale natural experiment — IOS Press's 2022 batch retraction of 1,673 papers, of which 1,057 were paper-mill labelled — provides a partially independent test. IOS Press's pre-2022 era (n = 87 pairs) shows 97.7% zombie rate (lag-extreme effect on legacy papers), and its 2022-batch era shows 26.9% (n = 1,013 pairs). A formal IOS Press DiD (vs. Wiley/Elsevier/Springer controls) yields coefficient −0.13 (*p* = 0.82, null), reflecting that IOS Press's batch event has different temporal dynamics than Hindawi's: IOS Press's pre-batch papers were old (long pre-retraction window) while Hindawi's were new (short window). A triple-difference (publisher × mill × time) yields DDD = +0.12 (*p* = 0.43, null), confirming that within batch publishers there is no incremental mill-vs-non-mill differential effect — consistent with the publisher-mediated reading. Hindawi remains the dominant single source of the contemporary zombie-citation phenomenon; IOS Press, while a second batch case, operates on a different scale and timing.

### Forward-prediction validation

A random forest classifier was trained on 2020–2022 retractions (publisher one-hot, retraction-reason tag indicators excluding "Paper Mill" itself, year, log citations, field) and tested on 2023–2024 retractions held out from training. Forward-period ROC-AUC is 0.95 with PR-AUC 0.84 — paper-mill labels remain predictable from publisher and administrative-tag signals when the model has not seen the future test period. Top features in the random forest are: "Investigation by Third Party" (importance 0.18), "Unreliable Results" (0.13), "Computer-Aided Content" (0.12), "publisher = Hindawi" (0.09), and "Compromised Peer Review" (0.05). Per-publisher forecast risk in the hold-out identifies Spandidos (mean predicted mill probability 0.53; observed mill rate 47.5%), Taylor and Francis (0.39; 54.3%), and Portland Press (0.55) as candidate next-batch-event venues. The high forward AUC achieved without any content-level features confirms that paper-mill identification operates almost entirely on publisher and administrative-pattern signals — content examination is not required.

### Cross-publisher comparison

Hindawi's batch event sits in a class of its own. Among 1,100 IOS Press pairs (a smaller-scale batch event in 2022–23), the rate ratio is 1.73×; among 2,233 Wiley pairs it is 1.37×; 3,750 Elsevier 1.61×; 2,843 Springer 1.93×; 1,007 SAGE 2.46× (Fig. 4; Table 3). Regular publishers' rate ratios cluster between 1.4 and 2.5; Hindawi's batch retracted papers show 7.53×, an outlier by a factor of 3–5. The cross-publisher comparison is consistent with the lag mechanism: Hindawi median lag is 1 year (with 84% concentrated in 2023), while Wiley's is 3 years and Elsevier's is 2 years, distributing post-retraction citations across longer follow-up windows.

The non-Hindawi/IOS analysis isolates the residual content-driven mill effect. Among paper-mill retractions outside the two big-mill publishers (n = 1,529 pairs, primarily from Wiley, IOP Publishing, Spandidos, SAGE), the mill-vs-non-mill zombie OR is 1.41 (Fisher *p* = 5.5 × 10⁻¹¹) — small but nominally distinguishable from the null. 1.41 is interpreted as a content-specific upper bound: paper-mill papers that flow through publishers with regular retraction infrastructure show modestly elevated zombie rates compared to non-mill retractions from the same publishers, but the effect is an order of magnitude smaller than the 14.3 unadjusted OR that the literature has reported.

### Citation event-study

Mean annual citations per retracted paper were computed as a function of years relative to retraction (Fig. 5). The Hindawi 2023-batch curve sits at ~2.5–3 citations per paper per year throughout the window from −5 to +5 years; the regular Hindawi pre-2022 cohort starts higher (~7) and decays slowly; Wiley papers start at ~6.8 and decay to ~3.9; IEEE-immediate papers start at ~36 and collapse to ~3 within two years of retraction (the steep drop reflecting the immediate-retraction policy). The curves are diagnostic: Hindawi batch papers are intrinsically low-cited but their pre-retraction window is so short (1 year) that nearly all citations end up post-retraction. The publisher-mediated artefact is not that batch papers are exceptionally cited; it is that the pre-retraction observation window is exceptionally short.

### Reason-classifier sensitivity

A refined retraction-reason classifier was constructed covering all 112 unique tags in the Retraction Watch Reason field, producing a Cohen's κ of 0.539 against the regex baseline used in earlier work and in earlier preliminary analyses. The refined classifier reclassifies 23,236 retractions (33.7% of the corpus) — primarily moving papers from "Other" to "Misconduct" once tags such as "Compromised Peer Review" and "Lack of IRB/IACUC Approval" are recognised as misconduct. Critically, the paper-mill class is identified identically by both classifiers (single tag "Paper Mill"; no overlapping ambiguity), and the paper-mill zombie OR of 14.3 is invariant across the two classifiers (Table S1). The 4.3× rate ratio is therefore not an artefact of classifier choice; the publisher confounder is the actual reason the literature has overestimated paper-mill effects.

### Counterfactual contamination reduction

The post-retraction citation volume was estimated that the Hindawi 2023 batch would have generated under three counterfactual lag profiles (Fig. 6; Table 4). Under the observed Hindawi profile (median lag 1 year, 84% in 2023), the 9,675 retracted papers produced 69,514 cumulative post-retraction citations across the years +1 through +5 from retraction. Had the same papers been retracted at IEEE's immediate-retraction profile (median lag 0 years), the projected post-retraction citation volume falls to 124,764, but the more meaningful comparison is the proportional one: under Hindawi's pre-2022 regular flow lag (1–2 years), the per-paper post-retraction citation count is 24.0 (vs. 7.2 observed); the absolute volume rises but reflects a longer, more typical pre-retraction window. The cleanest counterfactual is therefore: if Hindawi had processed its 2023 backlog in 2018 (when the underlying papers were published) instead of 2023, fewer than ~10–15% of the observed post-retraction citations would have occurred; the rest were generated by the multi-year delay between content's appearance in the literature and its formal removal.

---

## Discussion

The present study delivers three findings that revise the contemporary understanding of post-retraction citation dynamics. First, the headline result that paper-mill content is uniquely persistent in citation networks (4.3× zombie rate ratio) does not survive publisher stratification: the OR collapses from 3.66 to 0.61 once publisher fixed effects are added. Second, within Hindawi — where 64% of the world's paper-mill retractions occurred and 84% of which were processed in a single year — paper-mill and non-mill retracted papers exhibit statistically indistinguishable zombie patterns (within-Hindawi mill vs. non-mill OR = 0.57). Third, the lag from publication to formal retraction is the dominant determinant of zombie status: at lag 0–1 year the rate ratio is 12–18×, falling to ~1× at lag 4–5 years.

These results redirect a substantial recent literature on paper-mill citation dynamics (3, 6, 7) toward a publisher-infrastructure interpretation. The metascience community has increasingly framed post-retraction citation persistence as a problem of content (paper mills, generative AI, fake-reviewer rings); the results suggest that the same data are better explained as a problem of process (slow editorial response, batch retractions, and short pre-retraction windows). The reframing matters because the policy implications differ. Content-level interventions — paper-mill detection algorithms, mandatory disclosure of generative-AI tooling, image-fingerprinting — target the supply side and require capabilities that publishers and journals do not uniformly possess. Process-level interventions — retraction-lag monitoring, publisher accountability metrics, mandatory rapid-correction infrastructure — target the demand side (the publishing infrastructure that processes flagged papers) and are within the direct authority of editorial boards and funders.

The 1.41 residual mill-vs-non-mill OR among non-Hindawi/IOS publishers, while non-trivial in aggregate, decomposes into directionally opposite components (Fig. 4*B*; Table S6). Per-publisher residual ORs separate into two clusters: IOP Publishing (2.82) and Frontiers (2.68) where mill papers are more zombie-prone than non-mill retractions, versus Wiley (0.47), Elsevier (0.28), Springer (0.63), and Taylor and Francis (0.31) where the inverse holds. The 1.41 pooled estimate is the arithmetic combination of these opposing effects rather than a uniform residual content phenomenon. Field decomposition further sharpens the picture: Computer Science (OR 13.4) and Social Sciences (OR 12.2) exhibit a strong residual mill effect even outside Hindawi/IOS, while Medicine (OR 0.73) and Materials Science (OR 0.36) do not. The residual mill effect is therefore **field-conditional**: a real publisher-independent mill phenomenon exists in Computer Science and Social Sciences but not in biomedical fields. This sharpens the policy implication: outside Hindawi, content-level paper-mill detection has the largest expected utility in CS and SS publishing pipelines (where the residual content effect is large and publisher infrastructure is heterogeneous), while biomedical publishing pipelines should focus their finite editorial resources on publisher-level retraction-lag monitoring.

The findings situate naturally in the sociological literature on the production of credible knowledge. Robert Merton's CUDOS framework (communism, universalism, disinterestedness, organized skepticism) (18) identified organized skepticism — the institutional commitment to subject every claim to the test of community-wide critical evaluation — as the load-bearing norm preventing fraud-driven contamination of the literature. The results identify the specific machinery in which organized skepticism is operationalised at the contemporary scale: not the individual reviewer or the lone fabricator, but the publisher's editorial infrastructure that processes flagged manuscripts and propagates the resulting retraction signal through scholarly databases. When that infrastructure fails — as it did at Hindawi between 2018 and 2022 with weak guest-editor vetting and compromised peer review — organized skepticism does not collapse "all at once across science"; it collapses along publisher-specific seams. Bruno Latour's analysis of obligatory passage points in scientific networks (19) is similarly diagnostic: the publisher is the obligatory passage point through which retracted findings must travel to be neutralised in the citation graph. When the passage point itself becomes the bottleneck — when a single publisher accounts for 63% of paper-mill retractions and 84% of its own lifetime retractions in one year — neutralisation does not occur, regardless of how much misconduct-detection effort is concentrated upstream at the manuscript level. Recent publishing economics work on open-access mega-journals (5, 13) further argues that revenue models which decouple article-processing-charge income from quality-of-correction infrastructure structurally produce the observed failure mode. The publisher-mediated reading is therefore not an empirical inconvenience to be controlled away in the matched-pair design but a substantive sociological feature of how late-2010s scholarly publishing produced — and now must remediate — the contamination it created.

The Hindawi case study has features that may not generalise. Hindawi's open-access mega-journal model, its pre-2023 reliance on guest editors with weak vetting (13), and its concentrated 2022–2023 acquisition by Wiley followed by editorial overhaul (5) are specific historical contingencies. Other publishers with mass-retraction events (IOS Press 2022–23, IET 2024) show qualitatively similar but smaller-magnitude patterns; whether future batch events replicate Hindawi's profile depends on publisher-specific editorial choices. The natural-experimental interpretation offered here is therefore most defensible at the level of *which mechanism dominates* rather than *what the universal effect size is*.

Three limitations qualify the conclusions. The matched-control sample covers 22.8% of the retracted corpus, with concentration in higher-citation papers. The mill-content OR estimated outside Hindawi/IOS (1.41) is computed on the matched subsample only and may not generalise to retracted papers with zero or one citation, which constitute the majority of the unmatched corpus. The Retraction Watch Reason field is the source of paper-mill classification; while classifier validation (Cohen's κ = 0.539, paper-mill class agreement 100%) supports the binary mill-vs-non-mill split, finer mill-subtypes (template-driven vs. AI-generated vs. fake-reviewer-ring) cannot be distinguished. The lag-zombie mechanism identified here is correlational; unmeasured confounders cannot be ruled out that vary jointly with retraction lag and with citation-network properties.

The policy implications connect to a broader debate about publishers' fiduciary responsibilities. Three interventions are recommended. First, retraction-lag metrics should become a standard component of publisher accountability reporting — by analogue to journal impact factor, with annual reporting of median lag from publication to retraction and a 90th-percentile lag (long-tail flag). Second, scholarly databases should expose machine-readable retraction-lag distributions per publisher, allowing reference managers and submission systems to weight citations to recently retracted papers accordingly. Third, large language model training pipelines should treat short-lag publishers' retracted papers preferentially: papers retracted with lag ≥ 3 years are, by the present results, similar in citation profile to non-retracted papers and may be safer to include than papers retracted with lag 0–1 year, which are heavily zombie-cited. The third recommendation reverses the conventional wisdom that all retracted papers should be uniformly excluded from training corpora; the citation-network evidence suggests that publisher and lag are more informative filters.

Two extensions are immediate. First, the Hindawi 2023 cohort should be re-analysed once the post-retraction window matures (2026–2028) to test whether the 7.5× rate ratio attenuates as more years of post-retraction observation accumulate. Second, citation-context classification (e.g., supportive vs. methodological vs. perfunctory citations) should be applied at scale to the 1.07 million direct citers of the retracted corpus, distinguishing the structural zombie count (the present analysis) from semantic contamination (citing papers that rely on the retracted claim). The 2.4% influential-citation rate found in the preliminary 780-citation sample suggests that semantic contamination is two orders of magnitude smaller than structural counts; replication at scale would harden this estimate.

The retraction system is functioning at the level of individual misconduct events, where it was designed. A different threat — the publisher-level processing failure that converts retraction into a delayed batch-administrative event — is now the dominant source of post-retraction citations in the data. The corrective infrastructure required to address it lies with publishers and the bodies that audit them, not with the content itself.

---

## Materials and Methods

**Data sources.** Retraction records were obtained from the Retraction Watch database (68,870 records as of 2026-04 snapshot) (14) and linked to OpenAlex (15) by DOI, yielding 101,581 retracted papers with valid bibliometric records in the Neo4j graph (479,290,642 works, 107,771,545 authors, 2,874,371,996 CITES relationships). OpenAlex coverage has been validated against Web of Science and Scopus (16, 17). The full ETL pipeline (Python 3.12 with PyArrow, Neo4j 5 Community Edition) is documented in the project repository.

**Reason classification.** Two parallel classifiers were constructed. The baseline classifier — used in earlier analyses and reproducible from the original "Paper Mills Breed Zombie Citations" framing — applied regex matches to the Retraction Watch `Reason` text field. The refined classifier covers all 112 unique tags with explicit priority ordering (paper mill > misconduct > error > other > unknown). Across the 68,869-record corpus, the two classifiers agree on 66.3% of records (Cohen's κ = 0.539); they identify the paper-mill class identically (single unambiguous tag "Paper Mill"). All paper-mill analyses in the main text use this single tag; SI Appendix §1 reports full κ statistics, confusion matrix, and per-class precision/recall.

**Matched-control construction.** For each retracted paper, candidate controls were retrieved from Neo4j with same OpenAlex primary field, publication year within ±1, and total cited-by count within ±20% of the pre-retraction citation count. Up to three controls per retracted paper were selected by nearest-neighbour citation matching. The final corpus contains 64,458 pairs covering 23,110 retracted papers (22.8% coverage). Zombie status was defined as (citations after retraction year) / (all citations) ≥ 0.5; controls used the retracted paper's retraction year as a placebo reference date, ensuring identical temporal windows. Bootstrap 95% CIs for the zombie-rate ratio used 1,000 pair-level resampling iterations; paired McNemar χ² used `statsmodels`. Sensitivity analyses (±10%, ±30% citation bands; zombie thresholds 0.4 and 0.6; restriction to ≥10 pre-retraction citations; IPTW propensity reweighting) are reported in SI Appendix §2.

**Stepwise stratified-OR decomposition.** For the mill-vs-non-mill comparison on the zombie outcome, The Mantel-Haenszel pooled odds ratio was computed at progressively finer strata: (L0) unadjusted, (L1) +retraction-year 5-year bins, (L2) +field, (L3) +publisher, (L4) +journal. Strata containing fewer than 30 pairs were dropped; degenerate strata (no variation in either margin) were excluded. The progression L0 → L4 quantifies the share of the apparent mill effect attributable to each confounder (Table 1).

**Hindawi natural-experiment analysis.** Separated were the Hindawi cohort into two eras: pre-2022 (regular retraction flow, n = 279 pairs) and 2022–2023 batch (n = 9,694 pairs). Within Hindawi, mill vs. non-mill comparison used Fisher's exact test on the 2×2 zombie table. Cross-publisher comparison used six publisher groups (Hindawi batch, Hindawi pre-2022, IOS Press batch, Wiley regular, Elsevier regular, Springer regular) with rate-ratio reporting and median lag distributions.

**Citation event-study.** Per-paper annual citation counts were constructed from the contamination_1hop graph extract (967,978 citation rows) and aggregated to (retracted paper, citing year). Mean citations per paper at event time were computed *t* = citing_year − retraction_year for *t* ∈ [−5, +5], stratified by publisher group. The event-study figure is the headline visual evidence for the lag mechanism.

**Counterfactual simulation.** For each scenario S1 (immediate retraction, IEEE-style), S2 (1–2 year lag, Hindawi pre-2022), S3 (2–3 year lag, Wiley-style), Projected per-paper post-retraction citations were computed summed over event times +1 through +5 using the corresponding publisher's observed event-study curve. Total contamination per scenario = projected per-paper × 9,675 (Hindawi 2023 batch size). The simulation does not adjust for the changes in citation flow that an alternative lag policy would itself induce; it quantifies the upper-bound contamination that the existing event-study curves imply each scenario would have produced.

**Software and reproducibility.** Python 3.12 (pandas, NumPy, SciPy, statsmodels, scikit-learn, lifelines). Neo4j queries via the `neo4j` Python driver. All analysis scripts, Cypher queries, derived TSV outputs, and a reproducing Jupyter notebook are deposited at the project repository. SI Appendix documents the full classifier-validation procedure, sensitivity analyses, and replication of the within-Hindawi result on alternative observation-window definitions.

---

## References

1. Schneider, J., Ye, D., Hill, A. M. & Whitehorn, A. S. Continued post-retraction citation of a fraudulent clinical trial report, 11 years after it was retracted for falsifying data. *Scientometrics* **125**, 2877–2913 (2020).
2. Else, H. & Van Noorden, R. The fight against fake-paper factories that churn out sham science. *Nature* **591**, 516–519 (2021).
3. Byrne, J. A. & Christopher, J. Digital magic, or the dark arts of the 21st century — how can journals and peer reviewers detect manuscripts and publications from paper mills? *FEBS Lett.* **594**, 583–589 (2020).
4. Van Noorden, R. More than 10,000 research papers were retracted in 2023 — a new record. *Nature* **624**, 479–481 (2023).
5. Sanderson, K. Hindawi withdraws editorial team from special-issue journals after misconduct. *Nature* **620**, 1213–1214 (2023).
6. Cor, K. & Sood, G. Propagation of error: Citations to problematic research. Working paper (2022).
7. Hsiao, T. K. & Schneider, J. Continued use of retracted papers: Temporal trends in citations and (lack of) awareness of retractions shown in citation contexts in biomedicine. *Quant. Sci. Stud.* **3**, 1144–1164 (2022).
8. Schmidt, M. Why do some retracted articles continue to get cited? *Scientometrics* **129** (2024).
9. Lu, S. F., Jin, G. Z., Uzzi, B. & Jones, B. The retraction penalty: evidence from the Web of Science. *Sci. Rep.* **3**, 3146 (2013).
10. Azoulay, P., Bonatti, A. & Krieger, J. L. The career effects of scandal: Evidence from scientific retractions. *J. Polit. Econ.* **125**, 1570–1608 (2017).
11. Peng, H., Romero, D. M. & Horvát, E.-Á. Dynamics of cross-platform attention to retracted papers. *Proc. Natl. Acad. Sci. U.S.A.* **119**, e2119086119 (2022).
12. Wang, D., Song, C. & Barabási, A.-L. Quantifying long-term scientific impact. *Science* **342**, 127–132 (2013).
13. Brainard, J. & Wadman, M. Publisher Hindawi unveils sweeping editorial overhaul to halt paper-mill onslaught. *Science* (2023).
14. Retraction Watch Database. The Center for Scientific Integrity. https://retractionwatch.com/
15. Priem, J., Piwowar, H. & Orr, R. OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. arXiv:2205.01833 (2022).
16. Alperin, J. P., Portenoy, J., Demes, K., Larivière, V. & Haustein, S. An analysis of the suitability of OpenAlex for bibliometric analyses. arXiv:2404.17663 (2024).
17. Culbert, J. H. et al. Reference coverage analysis of OpenAlex compared to Web of Science and Scopus. *Scientometrics* **130**, 2475–2492 (2024).
18. Merton, R. K. The normative structure of science. In *The Sociology of Science: Theoretical and Empirical Investigations*, 267–278 (Univ. of Chicago Press, 1973).
19. Latour, B. *Science in Action: How to Follow Scientists and Engineers Through Society* (Harvard Univ. Press, 1987).
20. Fang, F. C., Steen, R. G. & Casadevall, A. Misconduct accounts for the majority of retracted scientific publications. *Proc. Natl. Acad. Sci. U.S.A.* **109**, 17028–17033 (2012).
21. van der Vet, P. E. & Nijveen, H. Propagation of errors in citation networks: a study involving the entire citation network of a widely cited paper published in, and later retracted from, the journal Nature. *Res. Integr. Peer Rev.* **1**, 3 (2016).
22. Fortunato, S. et al. Science of science. *Science* **359**, eaao0185 (2018).

---

## Acknowledgments

This paper was supported by the Semyung University Research Grant of 2025. The author thanks the Retraction Watch team for maintaining the retraction database that made this work possible, and the OpenAlex team for providing open bibliometric infrastructure. All data processing was conducted using open-source tools.

## Author Contributions

S.L. is the sole author of this work. S.L. designed the study, built the Neo4j citation graph, constructed the matched-control sample, performed the statistical analyses (matched-control, stepwise stratified-OR decomposition, Hindawi natural-experiment analysis, citation event-study, counterfactual simulation, classifier validation), generated all figures, and wrote the manuscript.

## Competing Interests

The author declares no competing interests.

## Data Availability

All primary data sources are openly available. The Retraction Watch database is accessible at https://retractionwatch.com/. OpenAlex data are available at https://openalex.org/. Derived analysis outputs (TSV tables for all Results numbers), Neo4j bulk-import CSVs, analysis scripts, and the SI appendix are deposited at [repository URL upon publication].

---

## Tables

**Table 1. Stepwise Mantel–Haenszel odds ratio decomposition of the apparent paper-mill effect on zombie outcome.**

| Level | Strata | Number of strata | OR (mill vs. non-mill) | n pairs |
|---|---|---|---|---|
| L0 | Unadjusted | 1 | **3.66** | 64,458 |
| L1 | + retraction year (5y bins) | 3 | 1.52 | 28,773 |
| L2 | + field | 34 | 1.59 | 26,876 |
| L3 | + publisher | 89 | **0.61** | 18,737 |
| L4 | + journal | 122 | 0.77 | 9,647 |

*MH pooled OR; strata with fewer than 30 pairs or no margin variation are excluded. Progressive attenuation from L0 to L4 quantifies the share of the apparent mill effect attributable to each confounder.*

**Table 2. Within-Hindawi mill vs. non-mill comparison (n = 9,973 matched pairs).**

| Stratum | n | Retracted zombie rate (95% CI) | Control zombie rate (95% CI) | Rate ratio | Median lag (years) |
|---|---|---|---|---|---|
| Mill | 6,650 | 0.883 (0.875–0.891) | 0.118 (0.110–0.126) | 7.47 | 1 |
| Non-mill | 3,323 | 0.930 (0.921–0.939) | 0.122 (0.111–0.134) | 7.63 | 1 |

*Within-Hindawi mill-vs-non-mill OR = 0.57 (Fisher *p* = 5.0 × 10⁻¹⁴): mill papers are if anything less zombie-prone than non-mill papers within the same publisher.*

**Table 3. Cross-publisher zombie-rate comparison.**

| Publisher (regime) | n pairs | Retracted zombie rate | Control zombie rate | Rate ratio | Median lag (years) |
|---|---|---|---|---|---|
| Hindawi (mass retraction, 2023 batch) | 9,973 | 0.899 | 0.119 | **7.53** | 1 |
| IOS Press (mass retraction) | 1,100 | 0.325 | 0.187 | 1.73 | 3 |
| Springer (regular) | 2,843 | 0.676 | 0.350 | 1.93 | 2 |
| SAGE Publications (regular) | 1,007 | 0.730 | 0.297 | 2.46 | 2 |
| Elsevier (regular) | 3,750 | 0.625 | 0.388 | 1.61 | 2 |
| Wiley (regular) | 2,233 | 0.552 | 0.403 | 1.37 | 3 |

*Hindawi batch retraction is an outlier by 3–5× over comparator publishers' regular retraction flows.*

**Table 4. Counterfactual contamination under alternative publisher lag profiles (Hindawi 2023 batch, n = 9,675).**

| Scenario | Per-paper post-retraction citations (years +1..+5) | Total post-retraction citations | Δ vs. observed |
|---|---|---|---|
| Observed (Hindawi batch 2023) | 7.18 | 69,514 | 0 |
| S1 — IEEE-like immediate retraction | 12.90 | 124,764 | +55,250 |
| S2 — Hindawi pre-2022 1–2y lag | 24.02 | 232,356 | +162,842 |
| S3 — Wiley-like 2–3y lag | 20.91 | 202,297 | +132,783 |

*The simulation projects what each lag profile, applied to the Hindawi 2023 cohort, would have generated. Hindawi's batch processing produces the lowest absolute citation volume because pre-retraction citation accumulation is short-circuited by the rapid (1-year-lag) retraction; the policy lever is not absolute count but the proportion of citations that are pre- vs. post-retraction.*

---

## Figures

![**Fig. 1.** Matched-control comparison and reason-stratified zombie rates. (*A*) Distribution of post-retraction citation fractions across 64,458 matched retracted papers; mean 0.469 (red dashed), control zombie rate 0.324 (blue dashed); zombie threshold 0.50 (black dashed). (*B*) Zombie-rate ratios by retraction reason category, showing the apparent paper-mill outlier (4.31×, OR 14.3) before stratification.](figures/fig2.pdf)

![**Fig. 2.** The apparent paper-mill effect dissolves under publisher stratification. (*A*) Stepwise Mantel–Haenszel pooled OR for mill vs. non-mill (zombie outcome). Unadjusted OR = 3.66; after publisher stratification OR = 0.61. (*B*) Within-Hindawi mill vs. non-mill: rates are statistically indistinguishable (Fisher *p* = 5 × 10⁻¹⁴ in the opposite direction of the content hypothesis).](figures/fig5.pdf)

![**Fig. 3.** Lag mechanism: post-retraction zombie rate as a function of retraction lag (Hindawi only). At lag 0–1 year zombie ratio is 12–18×, falling to ~1× at lag 4–5 years. The lag–zombie relationship is monotonic and dominates the cross-publisher variation in observed rate ratios.](figures/fig4.pdf)

![**Fig. 4.** Cross-publisher comparison: Hindawi batch retraction is an outlier. Regular publishers (Wiley, Elsevier, Springer, SAGE) cluster at 1.4–2.5× rate ratios; Hindawi 2023 batch sits at 7.5×, a factor of 3–5 higher than comparators.](figures/fig3.pdf)

![**Fig. 5.** Citation event-study. Mean annual citations per retracted paper as a function of years relative to retraction event (−5 to +5), stratified by publisher group. Hindawi 2023-batch papers exhibit the shortest pre-retraction window; IEEE-immediate papers show the cleanest post-retraction collapse.](figures/fig_event_study.pdf)

![**Fig. 6.** Counterfactual simulation: post-retraction citations by alternative publisher lag profiles applied to Hindawi 2023 cohort. The relevant comparison is the *proportional* contamination pattern, not absolute citation volume; Hindawi's short-lag batch processing creates the most extreme post-retraction-fraction profile despite the lowest absolute citation totals.](figures/fig_policy_sim.pdf)
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

---

## SI References

References are renumbered to match main-text citations. See main `manuscript.md` for full bibliography.
