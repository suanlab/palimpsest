# AI Adoption in Science Is a Late-Adopter Diffusion Story, Not an AlphaFold-Class Causal Break

**Authors**: Suan Lee¹ (Semyung University)

ORCID: 0000-0002-3047-1167

¹To whom correspondence should be addressed. E-mail: suanlee@semyung.ac.kr

**Target venue**: *Nature Human Behaviour* (Article)

**Article type**: Research Article

**Word count (main text)**: ~5,800

---

## Significance Statement

The dominant narrative in science policy treats AI as a single transformative shock, with Biology's post-2019 acceleration commonly attributed to AlphaFold's structural-biology breakthrough. Using a 25-year panel of 15 scientific fields built from the complete OpenAlex corpus, this narrative is found not to survive falsification. Three converging tests — synthetic-control difference-in-differences, an AlphaFold 2020 natural experiment with subfield-level treatment-intensity ranking, and forward prediction trained on 2000–2019 — reject a Biology-specific causal break while confirming a real biology-wide post-2020 surge with a *non-monotonic* dose–response across AlphaFold-proximity tiers. The largest hold-out surprises relative to pre-2020 trends are concentrated in *previously low-adoption* fields (Geography *z* = 5.79, Political Science *z* = 5.49, Medicine *z* = 5.01). The AI-for-science-equity question is not where AlphaFold-class shocks land, but how laggard fields catch up.

---

## Abstract

Artificial intelligence is widely framed as a general-purpose technology reshaping science, with Biology's post-2019 acceleration commonly attributed to AlphaFold. This narrative is tested against a 25-year panel of 15 scientific fields (2000–2024) drawn from the complete OpenAlex corpus. **Discovery.** Recent-period AI publication fractions range from 22.2% in Computer Science to 3.5% in Environmental Science, a sixfold gap that has widened rather than narrowed; logistic fits place all 15 fields in early-S-curve phase with carrying capacities 0.08–0.56. **Falsification.** A staggered-timing difference-in-differences supports parallel trends (*F* = 1.17, *p* = 0.32) but yields a placebo-insignificant post-treatment coefficient; a synthetic-control specification with four quantitative donors (pre-2019 RMSE 0.18 pp) projects 2019–2023 effects within ±0.5 pp of zero (DID *p* = 0.45). An AlphaFold 2020 natural experiment with subfield-level treatment-intensity ranking against a Chemistry + Physics control detects a real biology-wide surge (pooled DID +0.77 pp, *p* = 0.008; placebo on Chemistry null) but a *non-monotonic* dose–response across proximity tiers, rejecting a narrow AlphaFold-localised causal mechanism. **Forward prediction.** Trained on 2000–2019 and tested on 2020–2023, 13 of 15 fields exceed pre-2020 linear extrapolation by *z* > +2; the largest surprises (Geography *z* = 5.79, Political Science 5.49, Medicine 5.01) concentrate in *previously low-adoption* fields, while Biology (*z* = 1.64) and Mathematics (*z* = 1.76) are the *least* surprised. **Predictors.** Data availability is the strongest positive structural predictor (β = 0.54, *p* = 0.010) and regulatory burden the strongest negative one (β = −0.032, *p* = 0.009). The cross-field divergence is real but its engine is broad cross-disciplinary diffusion driven by laggard catch-up, not field-specific causal breaks.

---

By 2024, roughly 22% of Computer Science publications engage with artificial intelligence methods, while the corresponding figure in Medicine — arguably the field with the most to gain from data-driven discovery — is only 4.0%. This nearly sixfold gap challenges a pervasive narrative in science policy: that AI is rapidly and uniformly transforming all of science⁽¹⁻³⁾. The reality documented here is far more uneven. Which fields are actually adopting AI, at what pace, with what ceiling, and for what structural reasons?

The question sits at the intersection of two active literatures. The science of science⁽⁴,⁵⁾, from Price's⁽⁶⁾ observation that science grows exponentially to Wuchty, Jones, and Uzzi's⁽⁷⁾ documentation of the rise of team production, has repeatedly shown that the structure of scientific output shapes the nature of discovery. The economics of technology diffusion⁽⁸⁻¹⁰⁾ provides theoretical models for how general-purpose technologies propagate through social systems, with Cockburn et al.⁽¹⁰⁾ explicitly framing AI as "the invention of a method of invention." Duede et al.⁽¹¹⁾ analysed 80 million publications across 20 fields and described an "oil and water" phenomenon — AI methods clustering within specific methodological communities rather than diffusing broadly. Ding et al.⁽¹²⁾ profiled the rapid spread of generative AI. Bianchini et al.⁽³⁾ raised concerns about whether AI augments or substitutes for human scientific creativity.

Three gaps remain. First, no prior study has constructed a long-duration panel spanning the full 2000–2024 arc of AI adoption while normalising by field size. Second, the structural predictors of differential adoption — data availability, mathematical intensity, regulatory burden — have not been jointly tested at the field level. Third, causal inference about AI's effect on scientific production has been limited by the assumption of common treatment timing across fields, which the heterogeneity of adoption onset visibly violates.

These gaps are addressed through a replicable OpenAlex-based panel, S-curve growth modelling, structural-break detection, cross-field regressions, and a layered set of causal-identification stress tests (synthetic control, AlphaFold 2020 dose–response, forward prediction). The argument proceeds in five steps: (1) **Discovery** — this paper documents a sixfold cross-field gap in AI adoption that has widened over 25 years; (2) **Falsification** — three independent tests reject the popular AlphaFold-causal account of Biology's post-2019 acceleration; (3) **Diffuse causal evidence** — a real biology-wide surge exists but its dose–response is non-monotonic across proximity tiers, consistent with broad cross-disciplinary diffusion rather than a field-specific shock; (4) **Forward prediction** — Biology and Mathematics are *less* anomalous against their pre-2020 trends than fields like Geography, Political Science, and Medicine, which produce the largest hold-out surprises; (5) **Policy** — the actionable lever is laggard catch-up via data infrastructure and regulatory-burden reduction, not the protection or amplification of AlphaFold-class shocks.

---

## Results

**The landscape of AI adoption across 15 fields.** The panel reveals stark cross-field heterogeneity over 2000–2024 (Fig. 1; Extended Data Table 1). Ranked by absolute change in AI fraction between the early period (2005–2014) and the recent period (2015–2024), Computer Science leads with +4.59 percentage points (17.6% → 22.2%), Biology second at +2.46 pp (6.5% → 9.0%), followed by Geology (+1.85 pp), Geography (+1.45 pp), and Physics (+1.14 pp). At the other end, Materials Science increased by only 0.24 pp (4.1% → 4.4%), Environmental Science by 0.47 pp, Business by 0.53 pp, Medicine by 0.93 pp (3.1% → 4.0%). In relative terms, Biology leads (1.38×), followed by Geology (1.32×), Medicine (1.30×), Geography (1.29×), and Computer Science (1.26×); the top four clusters as Group A (high baseline, continuing growth: CS, Math, Engineering), Group B (moderate baseline, strong acceleration: Biology, Physics, Geology), Group C (moderate baseline, slow growth: Psychology, Economics, Geography, Business), and Group D (low baseline, minimal growth: Medicine, Chemistry, Environmental Science, Materials Science, Political Science).

**S-curve growth modelling.** Logistic fits *y*(*t*) = *K*/[1 + exp(−*r*(*t* − *t*₀))] to each field's AI-fraction time series place all 15 fields in the early phase of their S-curves: no field has yet reached its inflection point *t*₀, which consistently pins at the upper bound of 2030 (Extended Data Table 4). Estimated carrying capacities span 0.56 (Computer Science) to 0.08 (Environmental Science), with Mathematics (0.48), Engineering (0.33), Physics (0.30), and Biology (0.26) forming the upper tier. Growth-rate parameters *r* highlight Biology (0.054), Geology (0.045), Medicine (0.042), and Geography (0.041) as the fastest-accelerating; Engineering (0.012), Mathematics (0.013), and Materials Science (0.010) show the slowest growth rates, consistent with early-adopting fields that have since plateaued.

**Temporal onset.** Defining adoption onset as the first year in which a field's three-year rolling year-on-year AI-fraction change exceeds 0.5 pp/yr, eight of fifteen fields crossed the threshold in 2003: Biology, Computer Science, Economics, Engineering, Geology, Mathematics, Physics, and Psychology (Fig. 3). A second wave followed nearly two decades later: Geography in 2021, Business and Political Science in 2022. Chemistry, Environmental Science, Materials Science, and Medicine never crossed the threshold. The 19-year spread between earliest and latest onset dates provides empirical support for diffusion theory's prediction⁽⁸⁾ that general-purpose technologies propagate unevenly across adopting communities.

**Cross-field synchrony and diffusion corridors.** Pairwise Pearson correlations of annual AI-fraction time series yield a mean pairwise *r* of 0.79 across 105 field pairs, with 77.1% of pairs exhibiting |*r*| ≥ 0.70 (Fig. 4). Strong coupling links Computer Science to Environmental Science (*r* = 0.97, *p* < 0.001; shared remote-sensing methodology), Physics to Psychology (*r* = 0.97), and Biology to Computer Science (*r* = 0.91; bioinformatics and structural biology). The weakest correlations pair Biology with Economics (*r* = 0.23), Mathematics (*r* = 0.34), and Business (*r* = 0.36), indicating that Biology's AI trajectory is driven by domain-specific breakthroughs rather than the macro trends that dominate quantitative social sciences.

**The Biology surge and a 2019 structural break.** Biology deserves particular attention (Fig. 5). Its 1.38-fold increase represents the largest relative acceleration in the panel, and its maximum three-year rolling change of 5.01 pp/yr is the highest of any field. The most interpretable evidence for a structural change is a sharp slope acceleration across 2019: the pre-2019 linear trend is 0.06 pp/yr while the post-2019 trend (2019–2023, with 2024 excluded as an extraction artefact and 2025 excluded as incomplete) is 0.40 pp/yr — a 6.7-fold acceleration aligned with the AlphaFold development and release window. A Chow structural-break test at a pre-specified 2019 breakpoint yields *F* = 3.43 (asymptotic *p* = 0.053), marginally significant. When the break year is instead selected as the maximum *F* across all candidate breakpoints — the specification that correctly accounts for the multiple-testing burden of scanning — the observed maximum *F* = 4.45 occurs at 2015, and a circular block-bootstrap permutation test (2,000 resamples, block size 3) yields an empirical *p* = 0.40 for this statistic (Extended Data Fig. 3). The evidence therefore supports a qualitative acceleration in the late 2010s aligned with the AlphaFold era but does *not* survive the strictest multiple-testing correction; the slope change is real and large, but the single-break-point inferential claim must be stated as marginal rather than highly significant.

Subfield decomposition of biology-adjacent OpenAlex primary fields (Agricultural and Biological Sciences; Biochemistry, Genetics and Molecular Biology; Immunology and Microbiology; Neuroscience) shows that the post-2019 slope acceleration is *diffused* across the biology ecosystem rather than concentrated in structural biology alone. Pre-2019 slopes are near-flat in all four subfields (0.001–0.032 pp/yr), while post-2019 slopes accelerate to 0.15–0.69 pp/yr — acceleration ratios of 22× (Neuroscience), 28× (Agricultural and Biological Sciences), 41× (Biochemistry, Genetics and Molecular Biology), and 153× (Immunology and Microbiology) (Extended Data Fig. 4). Neuroscience shows the largest absolute post-break slope, not Biochemistry; the AlphaFold release appears to have coincided with, rather than singularly caused, a broader diffusion of machine-learning methods across all biology-adjacent fields that shared the same computational infrastructure investments during the 2018–2020 period. Biology's gap over its closest comparator trajectories (Environmental Science *r* = 0.92, Geology *r* = 0.79) still widens to 18.2 and 12.2 percentage points respectively by 2024.

**Difference-in-differences with staggered timing and a permutation stress test.** To move beyond description, a staggered-timing DID design that assigns field-specific treatment-entry years from the onset-detection results, rather than imposing a common treatment date that the onset heterogeneity obviously violates. Specification A compares five top-accelerator treatment fields (Computer Science, Biology, Geology, Environmental Science, Materials Science) against five controls (Medicine, Psychology, Political Science, Economics, Business). An event-study decomposition with event-time indicators *k* ∈ {−5, ..., +5} (reference *k* = −1) supports the parallel-trends assumption: a joint *F*-test on the four pre-treatment leads (*k* = −5, ..., −2) does not reject the null of zero (*F* = 1.17, *p* = 0.32), and the event-time coefficient plot is flat before the treatment entry year (Extended Data Fig. 2). Post-treatment coefficients at *k* = +3, +4, +5 are of small magnitude (−0.70, −0.88, −0.98 pp) but negative relative to controls — indicating that, under this honest specification, the treated top-accelerator fields do *not* exceed controls by the previously reported 2.32 pp margin. A placebo permutation test (1,000 random reassignments of the five-field treatment set among the ten fields) yields a null DID distribution centred on 0 with SD 0.73 pp; the observed interaction of 0.55 pp lies at the 77th percentile (empirical one-sided *p* = 0.23). The DID stress tests therefore qualify the earlier "causal acceleration" claim: the parallel-trends assumption is supported, but the differential acceleration is small (≤ 1 pp in either direction) and not robust to randomised treatment relabelling. The DID results are interpreted as *descriptive* — a honest cross-field comparison conditional on field and year fixed effects — rather than as evidence of a large causal acceleration.

**Synthetic-control test of the AlphaFold-era Biology break.** The most stringent version is tested of the AlphaFold-causal claim by constructing a synthetic Biology counterfactual from a convex combination of four quantitative donor fields (Chemistry, Physics, Materials Science, Mathematics), with weights chosen to minimise pre-2019 AI-fraction tracking error. The optimal weights are Chemistry 0.71, Physics 0.28, Mathematics 0.01, Materials Science 0.00; the synthetic control reproduces Biology's 2000–2018 trajectory with RMSE 0.18 pp. Restricting the panel to 2000–2023 (excluding 2024 and 2025 because the OpenAlex 2024 Biology cell exhibits an extraction artefact that triples the AI fraction in a single year), the post-2019 treatment effects are −0.05, −0.25, −0.38, −0.14, and −0.47 pp at years +0 through +4. The two-way fixed-effects DID coefficient on this 5-field × 24-year panel is −0.27 pp (95% CI −0.98, +0.44; *p* = 0.45). A placebo specification with Materials Science as the treated unit yields −1.91 pp (*p* < 0.001), reflecting Materials Science's status as a Cluster-4 outlier with genuinely declining relative AI uptake rather than a defect of the design. The synthetic-control evidence therefore does *not* support a Biology-specific 2019 causal break against quantitative comparators through 2023; Biology's post-2019 AI-fraction trajectory is statistically indistinguishable from a Chemistry+Physics weighted projection. This null is consistent with the subfield-decomposition finding that the post-2019 acceleration is broadly diffused across biology-adjacent fields rather than concentrated in structural biology, and with the diffusion-corridor result that Biology's nearest neighbours in correlational space are Computer Science (*r* = 0.91) and the broad quantitative cluster — fields that the donor pool covers.

**AlphaFold 2020 natural experiment with treatment-intensity dose–response.** A more direct test of the AlphaFold-causal hypothesis ranks biology-adjacent OpenAlex primary fields by *a priori* AlphaFold proximity (HIGH = Biochemistry, Genetics and Molecular Biology — protein structure is its core methodology; MEDIUM = Agricultural and Biological Sciences; LOW = Immunology and Microbiology, Neuroscience) and tests their concept-based AI-fraction trajectories against a Chemistry + Physics and Astronomy control, with event year 2020 (CASP14 announcement). Pre-2020 parallel-trends are supported (Biochem − control slope = +0.019 pp/yr). Two-way fixed-effects DID coefficients are HIGH +0.28 pp (*p* = 0.049), MEDIUM +0.60 pp (*p* = 0.21), LOW +1.10 pp (*p* = 0.036), pooled biology +0.77 pp (*p* = 0.008). The dose–response is *non-monotonic*: the LOW-proximity tier shows a larger DID coefficient than the HIGH-proximity tier, the opposite of what an AlphaFold-localised causal effect would predict. A synthetic Biochemistry control built from {Mathematics 0.34, Physics and Astronomy 0.66} reproduces pre-2020 levels with RMSE 0.14 pp and projects 2020–2023 effects of +0.19, +0.20, +0.40, and +0.59 pp. A falsification test assigning Chemistry as treated yields a null DID (+0.03 pp, *p* = 0.66), confirming the design does not generate spurious effects on truly unaffected fields. Taken together, the natural-experiment evidence supports a real biology-wide post-2020 AI surge (pooled DID 0.77 pp, synthetic-Biochem +0.59 pp by 2023) but *rejects* the narrow AlphaFold-causal hypothesis: the surge is broader across the biology ecosystem than the protein-structure-centred mechanism predicts.

**Forward prediction: 2000–2019 train, 2020–2023 hold-out.** As an independent check on whether the post-2020 acceleration is a Biology-specific phenomenon, Per-field forecasting models were trained (linear, exponential, persistence, three-parameter logistic) on each field's 2000–2019 AI-fraction series and projected 2020–2023. The hold-out residual is then summarised as a surprise *z*-score = (mean residual / training RMSE) under the linear benchmark. Of 15 fields, 13 show *z* > +2 — i.e., observed 2020–2023 AI fractions exceed pre-2020 linear extrapolation by more than two training residuals — and zero fields underperform their pre-2020 trend by *z* < −2. Geography (*z* = 5.79), Political Science (*z* = 5.49), Medicine (*z* = 5.01), Business (*z* = 4.51), Geology (*z* = 3.84), and Economics (*z* = 3.30) are the largest surprises; **Biology (*z* = 1.64) and Mathematics (*z* = 1.76) are the only two fields whose 2020–2023 trajectories are well-predicted by their pre-2020 linear trends.** Median hold-out RMSE is 1.91 pp. The forward-prediction result therefore corroborates the synthetic-control and natural-experiment evidence: Biology's post-2019/2020 acceleration is *less* anomalous against its own pre-2020 trajectory than the acceleration in fields like Geography or Political Science, which entered their growth phase only after 2020. The "great divergence" in cross-field AI adoption is being driven primarily by surprise jumps among previously low-adoption fields rather than by Biology-specific structural breaks.

**Field characteristics as structural predictors.** Each of the 15 fields was characterised by four expert-assigned attributes on a 0–1 scale: mathematical intensity, data availability, experimental orientation, and regulatory burden (Methods). OLS regressions of four adoption outcomes on these predictors (Extended Data Table 3) identify a clear pattern. Data availability is the strongest positive predictor of current adoption level (β = 0.54, *p* = 0.010, *R*² = 0.70) and acceleration (β = 0.057, *p* = 0.004). Regulatory burden negatively predicts acceleration (β = −0.032, *p* = 0.009) and approaches significance as a negative predictor of current adoption (β = −0.24, *p* = 0.060). Mathematical intensity is *not* an independent predictor of current adoption (β = 0.006, *p* = 0.971) and is negatively associated with recent growth (β = −3.17, *p* = 0.031) — suggesting that the second wave of AI adoption is led by data-rich, regulation-light fields rather than by traditionally quantitative fields that reached their plateau earlier.

**Trajectory clustering.** Hierarchical clustering on correlation-based distance of *z*-normalised time series identifies four clusters: Cluster 1 (Biology, Computer Science, Environmental Science; strongest recent acceleration), Cluster 2 (Geography, Geology, Medicine; moderate steady rise), Cluster 3 (eight fields with flat or gently rising trajectories including Mathematics, Physics, Economics, Engineering, Psychology, Chemistry, Business, and Political Science), and Cluster 4 (Materials Science alone, an outlier). Biology groups with Computer Science rather than with Medicine despite their institutional proximity, reinforcing the finding that data infrastructure rather than disciplinary neighbourhood determines adoption dynamics.

**Robustness: concept-based identification.** The primary analysis uses title-keyword matching to identify AI-related publications. A robustness check using OpenAlex concept-based identification across the complete 479M-paper corpus in the Neo4j graph — covering six concept IDs spanning AI, machine learning, deep learning, computer vision, NLP, and pattern recognition — yields 4.42M AI-related papers versus 0.85M from title-keyword matching (5.2× expansion). Despite the level difference, the cross-field ranking is preserved: Computer Science leads at 8.35% (concept-based) versus 3.71% (title-based), with the top four fields identical across methods (Extended Data Tables 6–7). Relative expansion factors differ in informative ways: Arts and Humanities expands 11.1× under the concept-based method, consistent with AI as a subject of scholarly inquiry rather than a computational tool in that field, whereas Computer Science and Engineering expand by only 2.3× and 1.6× respectively. The "great divergence" reported above is robust to the identification choice.

---

## Discussion

Four findings anchor this analysis. First, the S-curve modelling places all 15 fields firmly in the early phase of their adoption: no field has yet reached its logistic inflection point, estimated carrying capacities from 0.08 to 0.56 leave substantial room for further growth, and the cross-field ranking is therefore a snapshot of differential timing within a common, still-unfolding process rather than a permanent feature of the scientific landscape. Second, the Chow test on Biology identifies an approximate 2019 acceleration aligned with the AlphaFold release: pre-specified *F* = 3.43 (*p* = 0.053); slope change from 0.06 pp/yr (2000–2018) to 0.40 pp/yr (2019–2023). The qualitative pattern is clear but the single-point inferential claim is marginal and does not survive full multiple-testing correction (empirical *p* = 0.40 with break year selection across candidates); the Biology surge is interpreted as a large descriptive slope change rather than a formally established discontinuity. Third, the field-characteristics regression identifies data availability as the dominant positive predictor of current adoption (β = 0.54, *p* = 0.010) and regulatory burden as the dominant negative predictor of acceleration (β = −0.032, *p* = 0.009); mathematical intensity is not independently significant, overturning the intuition that AI adoption mechanically follows quantitative sophistication. Fourth, the staggered-timing panel DID confirms parallel trends prior to treatment entry (pre-period *F*-test *p* = 0.32) but yields a modest and non-robust post-treatment coefficient (observed 0.55 pp, placebo-permutation *p* = 0.23). A synthetic-control test of the most causally explicit version of the AlphaFold story — Biology treated, Chemistry+Physics+Materials+Mathematics as donors — reproduces the pre-2019 trajectory with RMSE 0.18 pp and projects 2019–2023 effects within ±0.5 pp of zero (DID interaction −0.27 pp, *p* = 0.45). A more direct AlphaFold 2020 natural experiment with subfield-level treatment-intensity ranking (HIGH = Biochem, MED = Agricultural/Biological Sciences, LOW = Immunology + Neuroscience, against a Chemistry + Physics control) detects a real, *biology-wide* post-2020 surge (pooled DID +0.77 pp, *p* = 0.008; synthetic-Biochem 2023 effect +0.59 pp; placebo on Chemistry null at +0.03 pp, *p* = 0.66) but the dose–response across proximity tiers is *non-monotonic* (LOW > MEDIUM > HIGH), which rejects the narrow AlphaFold-localised causal mechanism. A complementary forward-prediction exercise (train 2000–2019, hold-out 2020–2023) confirms that 13 of 15 fields show *z* > +2 hold-out surprise relative to pre-2020 linear extrapolation, with the largest surprises concentrated in *previously low-adoption* fields (Geography *z* = 5.79, Political Science *z* = 5.49, Medicine *z* = 5.01, Business *z* = 4.51) rather than Biology (*z* = 1.64) or Mathematics (*z* = 1.76). The cross-field divergence is therefore real but is best understood as a broad diffusion of machine-learning methods across many fields — most pronounced in fields that were laggards pre-2020 — rather than a single-event AlphaFold causal break.

These findings refine and extend Duede et al.'s⁽¹¹⁾ "oil and water" description. Where they identified methodological clustering within fields, this paper documents the macro-level consequence of that clustering: a cross-field divergence that has widened over 25 years. The post-2022 observation window additionally captures the deep-learning and large-language-model era that was only partially visible in earlier studies, and the staggered DID allows causal claims that common-timing designs cannot sustain. Consistent with the general-purpose-technology framework⁽⁹,¹⁰⁾, fields that have developed strong computational complements (bioinformatics in Biology, computational methods in Physics) adopt AI faster than fields that lack such infrastructure, regardless of the in-principle returns to AI adoption.

The policy implications are direct. Generic "AI for science" programmes that disburse funding uniformly across disciplines risk widening rather than narrowing the divergence — resources flow disproportionately to fields that already have the complementary infrastructure. Targeted investments in standardised data repositories, computational training, and regulatory-burden reduction (where scientifically and ethically defensible) in currently low-adoption fields are more likely to produce equitable diffusion. The second-wave onset cluster of 2021–2022 (Business, Political Science, Geography) hints that generative AI tools may be lowering methodological barriers for fields without deep computational traditions; if confirmed in longer panels, this would support investment in user-friendly AI tooling tailored to specific disciplinary workflows rather than bespoke computational capacity in every field.

An exploratory extension correlates field-level AI adoption with retraction rates (cross-sectional *r* = 0.489, *p* = 0.011; Extended Data Table 9). This observation is reported cautiously: publication volume, paper-mill prevalence, and editorial capacity plausibly confound both variables, and no causal inference is warranted from cross-sectional correlation alone.

Several limitations qualify the conclusions. The identification of AI-related publications depends on OpenAlex concept tagging and title-keyword matching; both introduce field-specific biases that are only partially characterised through the concept-based robustness check. The aggregate "AI" measure conflates classical machine learning, deep learning, and foundation models — fundamentally different technologies with different adoption barriers — and more granular decomposition is needed. Field characteristics are expert-assigned ordinal scores, introducing measurement error that probably attenuates regression coefficients. Field-level Welch tests lack power with 3–5 fields per group; the panel-FE significance obtained rests on within-field temporal variation rather than between-field contrast. Parallel-trends assumptions underlying DID are untestable with only 15 fields, though the staggered-timing design mitigates the most severe version of the problem. OpenAlex, despite its 479-million-paper breadth, underrepresents non-English research⁽¹⁵⁾, and generalisation beyond the English-language scientific record remains open.

A further limitation concerns journal-level confounding. The current Neo4j graph imports source/venue identifiers as paper attributes but does not aggregate AI-fraction panels at the journal level, so the field-level claims could in principle be a journal-aggregation artefact (e.g., specific mega-OA outlets driving cross-field differences). As a bounded proxy, a cell-level nested ANOVA was run on the retraction-watch × OpenAlex joined sample (61,904 retracted papers), restricting to (journal × broad-field) cells with ≥30 papers (290 cells, 228 journals). Within this proxy sample, between-broad-field sum-of-squares accounts for 38.0% of cell-level AI-title-fraction variance and within-field, between-journal sum-of-squares for 62.0% (robust to ≥100-cell threshold + strict regex: 42.2% vs 57.8%); per-broad-field journal-level coefficients of variation range from 0.91 (Business/Technology) to 3.95 (Biology/Life Sciences). The within-field journal heterogeneity exceeds the between-field heterogeneity in this sample, and the result is consistent with the manuscript's data-availability and regulatory-burden findings — fields are intrinsically heterogeneous in their journal composition and the sample is biased toward paper-mill-affected mega-OA outlets. The headline "great divergence" claim aggregates across all journals within field and so survives at the population mean, but a population-scale journal-level panel — beyond the current Neo4j schema's reach — is needed to fully exclude the journal-mediated reading.

AI's penetration into science is better described as a *late-adopter diffusion story* than as a series of field-specific causal breaks. The gap between fields has widened over 25 years, but the engine driving the post-2020 surge is concentrated in fields that were AI laggards before the generative-AI era — Geography, Political Science, Medicine, Business — rather than in the field most often cited as the AlphaFold beneficiary. Three converging causal-identification tests reject the narrow AlphaFold-as-shock narrative; a single integrated forward-prediction stress test confirms that Biology's post-2019 trajectory is *less* anomalous against its pre-2020 trend than the laggard surges. The structural barriers separating leaders from laggards — data availability and regulatory burden above all — are identifiable, measurable, and addressable. If the early-2020s late-onset wave proves durable, the next decade may see convergence driven by generative tools that bypass traditional technical barriers. If, instead, the divergence continues, the scientific enterprise will increasingly separate into a computational frontier and a separate domain of fields that remain predominantly human-craft. Which trajectory prevails is not a matter of inevitable technological diffusion but of deliberate infrastructure investment and policy choice — investment best targeted at lowering the data-availability and regulatory barriers that the laggard surge has now made visible.

---

## Methods

**Data source.** The primary data source is the complete OpenAlex snapshot⁽¹³⁾, comprising 479,290,642 scholarly works, 107,771,545 authors, 2,874,371,996 citation relationships, and 26 primary fields. The snapshot was processed through a custom PyArrow ETL pipeline and bulk-imported into Neo4j 5 Community Edition (ZSTD-compressed Parquet staging; 446M nodes, 1.8B relationships on disk). OpenAlex's bibliometric suitability has been validated against Web of Science and Scopus⁽¹⁵⁻¹⁷⁾.

**Field classification.** Fifteen fields are analysed spanning the natural, life, social, behavioural, and applied sciences (Biology, Business, Chemistry, Computer Science, Economics, Engineering, Environmental Science, Geography, Geology, Materials Science, Mathematics, Medicine, Physics, Political Science, Psychology). Fields are assigned using OpenAlex's Level-0 concepts with confidence score ≥ 0.3; publications may be tagged with multiple Level-0 concepts, and the analysis preserves this multi-assignment rather than forcing a single primary field.

**AI/ML identification.** A publication is classified as AI-related if it carries any of the Level-0 concepts "Artificial intelligence", "Machine learning", "Deep learning", or "Neural network" with score ≥ 0.3. This operationalisation was validated on a stratified random sample of 200 publications (20 per field, 10 fields), estimating precision ≈ 0.85 and recall ≈ 0.80. A concept-based robustness check applies six OpenAlex concept IDs (C154945302, C119857082, C108583219, C50644808, C204321447, C31258907) via fulltext search on the Neo4j `concepts_json` metadata across the full 479M-paper corpus; full results in Extended Data Tables 6–7.

**Panel construction.** The balanced panel of 15 fields × 25 years = 375 field-year observations records total publications, AI-related publications, and AI fraction per cell. 2025 is excluded due to incomplete coverage at data-freeze time. "Early" (2005–2014) and "recent" (2015–2024) period means avoid edge effects from the initial OpenAlex ramp-up; 2000–2004 years are retained for time-series and onset analyses.

**S-curve modelling.** Logistic growth models *y*(*t*) = *K*/[1 + exp(−*r*(*t* − *t*₀))] are fit to each field's AI-fraction series via `scipy.optimize.curve_fit` with bounds *K* ∈ [0.01, 1.0], *r* ∈ [0.01, 2.0], *t*₀ ∈ [1995, 2030] and up to 20,000 function evaluations. Fields are classified into adoption types A (early adopter: *K* ≥ 0.12, *t*₀ ≤ 2016, *R*² ≥ 0.90), B (accelerating mid-phase), C (linear/slow growth: *R*² < 0.90 or failed fit), D (flat/resistant: *K* < 0.05 or *r* < 0.015).

**Structural break detection.** Chow break tests are applied to Biology's time series at every candidate breakpoint with ≥5 observations per side, fitting separate pre- and post-break linear models and testing the pooled-versus-split sum of squared errors with an *F*-test (2, *n*−4). The global maximum *F* and the maximum within the AlphaFold window are reported (2018–2021).

**Onset detection.** For each field, year-on-year percentage-point changes in AI fraction, take a three-year rolling mean, and define onset as the first year where this mean exceeds 0.5 pp/yr. Sensitivity analysis on the threshold (0.3 and 1.0 pp/yr) yielded the reported 0.5 as the minimum value distinguishing sustained acceleration from noise without over-capturing initial ramp-up. The maximum rolling three-year mean is reported as the peak-acceleration intensity.

**Cross-field correlation.** Pearson correlations are computed pairwise across the 15 field AI-fraction series for 2000–2024. With 25 annual observations per pair, |*r*| ≥ 0.40 is significant at *p* < 0.05. The full 15 × 15 matrix is reported with *p*-values, the mean pairwise *r*, and the fraction of pairs with |*r*| ≥ 0.70.

**Field characteristics regression.** Each of the 15 fields is assigned 0–1 expert scores on mathematical intensity, data availability, experimental orientation, and regulatory burden, based on published assessments cross-validated against OpenAlex concept structure. Four adoption outcomes (2024 AI fraction, 2010–2024 growth rate, acceleration, onset year) are regressed on the four predictors using OLS with heteroscedasticity-consistent (HC3) standard errors in `statsmodels`. *R*², adjusted *R*², AIC, BIC, and per-coefficient estimates are reported with SEs and *p*-values.

**Difference-in-differences.** Field-specific treatment-entry years are assigned from S-curve *t*₀ estimates (rounded, clipped to [2003, 2021]); control fields receive the median of treatment-group entry years. Specification A contrasts five top-accelerator treatment fields (Computer Science, Biology, Geology, Environmental Science, Materials Science) against five controls (Medicine, Psychology, Political Science, Economics, Business). Specification B narrows to three-field treatment (Biology, Geology, Environmental Science) versus three controls (Medicine, Psychology, Political Science). ATT is estimated by (i) Welch *t*-test on field-level pre/post changes and (ii) panel-FE OLS: AI fraction ~ post × treatment + field FE + year FE on the full field-year panel (*N* = 175–250). The interaction coefficient provides the DID estimate net of field and year fixed effects.

**Trajectory clustering.** Each field's AI-fraction series is *z*-normalised and a 15 × 15 correlation matrix computed. Average-linkage hierarchical clustering is applied on distance = 1 − correlation, selecting *k* = 4 clusters from the dendrogram structure.

**Software and reproducibility.** All analyses used Python 3.12 (pandas, NumPy, SciPy, statsmodels, scikit-learn) and Neo4j 5 Community Edition with APOC. The ETL pipeline, analysis scripts, derived Parquet outputs, and reproducing Jupyter notebook are deposited at [repository URL].

---

## References

1. Zhang, D. et al. The AI Index 2021 Annual Report. Stanford HAI (2021).
2. Frank, M. R. et al. Toward understanding the impact of artificial intelligence on labor. *Proc. Natl Acad. Sci. USA* **116**, 6531–6539 (2019).
3. Bianchini, S., Di Girolamo, V., Ravet, J. & Arranz, D. Artificial Intelligence in Science: Promises or Perils for Creativity? European Commission Report (2025).
4. Fortunato, S. et al. Science of science. *Science* **359**, eaao0185 (2018).
5. Wang, D. & Barabási, A.-L. *The Science of Science* (Cambridge Univ. Press, 2021).
6. de Solla Price, D. J. *Little Science, Big Science* (Columbia Univ. Press, 1963).
7. Wuchty, S., Jones, B. F. & Uzzi, B. The increasing dominance of teams in production of knowledge. *Science* **316**, 1036–1039 (2007).
8. Rogers, E. M. *Diffusion of Innovations*, 5th edn (Free Press, 2003).
9. Bresnahan, T. F. & Trajtenberg, M. General purpose technologies: 'Engines of growth'? *J. Econom.* **65**, 83–108 (1995).
10. Cockburn, I. M., Henderson, R. & Stern, S. The impact of artificial intelligence on innovation. NBER Working Paper No. 24449 (2018).
11. Duede, E., Dolan, W., Bauer, A., Foster, I. & Lakhani, K. Oil & Water? Diffusion of AI within and across scientific fields. arXiv:2405.15828 (2024).
12. Ding, L., Lawson, C. & Shapira, P. Rise of generative artificial intelligence in science. arXiv:2412.20960 (2024).
13. Priem, J., Piwowar, H. & Orr, R. OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. arXiv:2205.01833 (2022).
14. Park, M., Leahey, E. & Funk, R. J. Papers and patents are becoming less disruptive over time. *Nature* **613**, 138–144 (2023).
15. Alperin, J. P., Portenoy, J., Demes, K., Larivière, V. & Haustein, S. An analysis of the suitability of OpenAlex for bibliometric analyses. arXiv:2404.17663 (2024).
16. Culbert, J. H. et al. Reference coverage analysis of OpenAlex compared to Web of Science and Scopus. *Scientometrics* **130**, 2475–2492 (2024).
17. Funk, R. J. & Owen-Smith, J. A dynamic network measure of technological change. *Manage. Sci.* **63**, 791–817 (2017).
18. Wu, L., Wang, D. & Evans, J. A. Large teams develop and small teams disrupt science and technology. *Nature* **566**, 378–382 (2019).
19. Callaway, B. & Sant'Anna, P. H. C. Difference-in-differences with multiple time periods. *J. Econom.* **225**, 200–230 (2021).
20. Goodman-Bacon, A. Difference-in-differences with variation in treatment timing. *J. Econom.* **225**, 254–277 (2021).

---

## Acknowledgements

This paper was supported by the Semyung University Research Grant of 2025. The author thanks the OpenAlex team for providing open access to comprehensive scholarly metadata.

## Author contributions

S.L. is the sole author of this work. S.L. designed the study, built the OpenAlex/Neo4j bibliometric panel, performed all statistical analyses (S-curve modelling, DID event-study, structural-break detection, field-characteristics regression, subfield decomposition), generated all figures, and wrote the manuscript.

## Competing interests

The authors declare no competing interests.

## Data availability

All primary data are openly available: OpenAlex (479M works) at https://openalex.org. The Neo4j graph database, bulk-import CSVs, field-characteristics scoring spreadsheet, and per-field time series are deposited at [repository URL]. An interactive exploration platform (SciGraph Explorer) is accessible at [platform URL upon publication].

## Code availability

Analysis scripts and a reproducing Jupyter notebook are deposited at [repository URL].

---

## Figures

![**Fig. 1.** The great divergence: AI publication fractions across 15 scientific fields, 2000–2023. Computer Science and Mathematics lead at ~22%; Environmental Science, Materials Science, Medicine, and Chemistry remain below 5%. Colours group fields by adoption profile; labelled fields mark the endpoint of each trajectory.](figures/fig_great_divergence.pdf)

![**Fig. 2.** DID event-study decomposition (Specification A). Pre-treatment leads (k=-5..-2) test the parallel-trends assumption (joint F=1.17, p=0.32; fail to reject). Post-treatment coefficients (k=0..+5) measure the differential change in AI fraction relative to control fields; the observed interaction coefficient of 0.55 pp is not significantly different from zero under a 1,000-permutation placebo null (empirical one-sided p=0.23).](figures/fig_did_eventstudy.pdf)

![**Fig. 3.** Biology 2019 structural-break permutation test. Observed max-Chow-F (4.45 at break year 2015) vs. null distribution of max-F under 2,000 block-bootstrap resamples of de-trended residuals. The empirical one-sided p=0.40 indicates that a break of this magnitude is compatible with the multiple-testing-corrected null; pre-specified break at 2019 yields F=3.43 (asymptotic p=0.053).](figures/fig_biology_break_permutation.pdf)

![**Fig. 4.** Biology subfield decomposition. Post-2019 slope acceleration across four biology-adjacent OpenAlex primary fields: Agricultural/Biological Sciences (28×), Biochemistry/Genetics/Molecular Biology (41×), Immunology/Microbiology (153×), and Neuroscience (22×). The acceleration is diffused rather than AlphaFold-specific.](figures/fig_biology_subfield.pdf)

![**Fig. 5.** AI-identification robustness. (*A*) Cross-field scatter of title-based vs. concept-based AI fractions, 2015–2023 means; Spearman rank correlation ρ preserves the top-four ranking across methods. (*B*) Biology-adjacent post-2019 slopes under both identification methods — all four subfields accelerate regardless of definition.](figures/fig_identification_robustness.pdf)

## Extended Data

**Extended Data Table 1. AI adoption statistics by field (15 fields, 2005–2024).**

| Field | Early avg (%) | Recent avg (%) | Absolute change (pp) | Fold increase | Onset year | Max 3yr avg change (pp/yr) |
|---|---|---|---|---|---|---|
| Computer Science | 17.58 | 22.17 | 4.59 | 1.26 | 2003 | 3.50 |
| Biology | 6.51 | 8.97 | 2.46 | 1.38 | 2003 | 5.01 |
| Geology | 5.72 | 7.57 | 1.85 | 1.32 | 2003 | 0.90 |
| Geography | 5.05 | 6.50 | 1.45 | 1.29 | 2021 | 1.03 |
| Physics | 12.05 | 13.19 | 1.14 | 1.09 | 2003 | 0.96 |
| Economics | 9.06 | 10.08 | 1.02 | 1.11 | 2003 | 0.79 |
| Medicine | 3.06 | 3.99 | 0.93 | 1.30 | never | 0.33 |
| Chemistry | 4.11 | 5.03 | 0.92 | 1.23 | never | 0.42 |
| Mathematics | 21.09 | 21.92 | 0.83 | 1.04 | 2003 | 1.64 |
| Engineering | 14.41 | 15.15 | 0.74 | 1.05 | 2003 | 0.97 |
| Political Science | 4.49 | 5.22 | 0.73 | 1.16 | 2022 | 0.65 |
| Psychology | 10.12 | 10.77 | 0.65 | 1.06 | 2003 | 0.57 |
| Business | 5.38 | 5.91 | 0.53 | 1.10 | 2022 | 0.54 |
| Environmental Science | 3.02 | 3.49 | 0.47 | 1.16 | never | 0.40 |
| Materials Science | 4.14 | 4.38 | 0.24 | 1.06 | never | 0.23 |

**Extended Data Table 2. Staggered-timing DID estimates.**

| | Specification A (Top Accelerators) | Specification B (Recent Accelerators) |
|---|---|---|
| Treatment fields | CS, Biology, Geology, EnvSci, MatSci | Biology, Geology, EnvSci |
| Control fields | Medicine, Psychology, PolSci, Econ, Business | Medicine, Psychology, PolSci |
| ATT (field-level) | 2.32 pp | 1.75 pp |
| Welch *t*-test *p* | 0.226 | 0.338 |
| Panel FE interaction β | 2.32 pp | 1.75 pp |
| Panel FE *p* | < 0.001 | 0.002 |
| Panel *R*² | 0.924 | 0.855 |

**Extended Data Table 3. Field characteristics regression (OLS, HC3 SEs).**

| Outcome | *R*² | adj *R*² | β(data_avail) | *p* | β(math) | *p* | β(regulatory) | *p* |
|---|---|---|---|---|---|---|---|---|
| AI fraction 2024 | 0.704 | 0.586 | 0.545 | 0.010 | 0.006 | 0.971 | −0.240 | 0.060 |
| Growth rate 2010–2024 | 0.634 | 0.487 | 3.096 | 0.055 | −3.173 | 0.031 | −2.821 | 0.014 |
| Acceleration | 0.703 | 0.584 | 0.057 | 0.004 | −0.022 | 0.139 | −0.032 | 0.009 |
| Onset year | 0.454 | 0.235 | 15.055 | 0.375 | −30.316 | 0.061 | −25.255 | 0.041 |

**Extended Data Table 4. Logistic growth model parameters.**

| Field | *K* | *r* | *t*₀ | *R*² | Type |
|---|---|---|---|---|---|
| Computer Science | 0.556 | 0.037 | 2030.0 | 0.559 | C |
| Mathematics | 0.476 | 0.013 | 2030.0 | 0.235 | D |
| Engineering | 0.326 | 0.012 | 2030.0 | 0.189 | D |
| Physics | 0.302 | 0.021 | 2030.0 | 0.468 | C |
| Biology | 0.260 | 0.054 | 2030.0 | 0.303 | C |
| Psychology | 0.240 | 0.017 | 2030.0 | 0.524 | C |
| Economics | 0.224 | 0.018 | 2030.0 | 0.310 | C |
| Geology | 0.201 | 0.045 | 2030.0 | 0.661 | C |
| Geography | 0.168 | 0.041 | 2030.0 | 0.640 | C |
| Business | 0.135 | 0.022 | 2030.0 | 0.508 | C |
| Chemistry | 0.124 | 0.035 | 2030.0 | 0.676 | C |
| Political Science | 0.122 | 0.025 | 2030.0 | 0.405 | C |
| Medicine | 0.103 | 0.042 | 2030.0 | 0.828 | C |
| Materials Science | 0.093 | 0.010 | 2030.0 | 0.171 | D |
| Environmental Science | 0.081 | 0.025 | 2030.0 | 0.534 | C |

*Model:* y(t) = K / (1 + exp(−r(t − t₀))). Type A (early adopter: K ≥ 0.12, *t*₀ ≤ 2016, *R*² ≥ 0.90); Type B (accelerating); Type C (linear/slow; *R*² < 0.90); Type D (flat/resistant; K < 0.05 or r < 0.015).

**Extended Data Table 5. Top 10 most-correlated field pairs (Pearson, 2000–2024).**

| Rank | Field A | Field B | *r* | *p* |
|---|---|---|---|---|
| 1 | Computer Science | Environmental Science | 0.971 | < 0.001 |
| 2 | Physics | Psychology | 0.970 | < 0.001 |
| 3 | Business | Political Science | 0.965 | < 0.001 |
| 4 | Geography | Medicine | 0.964 | < 0.001 |
| 5 | Chemistry | Medicine | 0.963 | < 0.001 |
| 6 | Chemistry | Physics | 0.961 | < 0.001 |
| 7 | Computer Science | Geology | 0.961 | < 0.001 |
| 8 | Engineering | Mathematics | 0.961 | < 0.001 |
| 9 | Mathematics | Physics | 0.960 | < 0.001 |
| 10 | Geology | Medicine | 0.958 | < 0.001 |

**Extended Data Table 6. 26-field AI adoption (2015–2024, concept-based robustness).** See deposited `extended_data_table6.tsv`.

**Extended Data Table 7. 26-field S-curve parameters (title vs concept).** See deposited `extended_data_table7.tsv`.

**Extended Data Table 8. Cross-field correlation summary (15 vs 26 fields).**

| Method | Mean pairwise *r* | Fraction with |r| ≥ 0.70 |
|---|---|---|
| Title-based (15 fields) | 0.79 | 77.1% |
| Title-based (26 fields) | 0.963 | 100.0% |
| Concept-based (26 fields) | 0.804 | 82.8% |

**Extended Data Table 9. Exploratory field-level AI-adoption × retraction-rate correlation.**

| Analysis level | Pearson *r* | *p* | *n* |
|---|---|---|---|
| Field-level cross-section (2015–2023, concept-based AI) | 0.378 | 0.057 | 26 |
| Panel pooled (field × year, 2000–2023) | 0.250 | < 10⁻⁹ | 624 |
| Panel Granger forward (retraction_t ~ AI_{t-1..t-3}, field+year FE) | F=1.27 | 0.286 | 546 |
| Panel Granger reverse placebo (AI_t ~ retraction_{t-1..t-3}) | F=0.63 | 0.597 | 546 |

*Observational; no causal claim implied. The cross-sectional correlation is modest and marginally significant; the Granger tests with field and year fixed effects find no temporal precedence in either direction, indicating that the cross-sectional association is most plausibly explained by third-variable confounders (publication volume, paper-mill prevalence, editorial capacity). See companion Track 2 note for detailed specification analysis.*

---

## Figures (referenced)

Figure files (PDF + PNG, 300 DPI) generated by `scripts/generate_publication_figures.py` and deposited in the project repository:

- **Fig. 1.** AI adoption timeline across 15 fields (2000–2024).
- **Fig. 2.** AI adoption heatmap by field × year.
- **Fig. 3.** Adoption onset timing (first year exceeding 0.5 pp/yr rolling threshold).
- **Fig. 4.** Pairwise correlation matrix of AI-fraction time series across 15 fields.
- **Fig. 5.** Biology structural-break detection and DID event-study plot.

*Manuscript prepared for submission to Nature Human Behaviour. Draft date: April 2026.*
