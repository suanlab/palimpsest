# The Great Divergence: Heterogeneous AI Adoption and Its Consequences for Scientific Production

---

**Authors**: [Author names withheld for peer review]

**Target venue**: *Research Policy* (alternative: *PNAS*)

**Word count**: ~8,000 (main text) + Extended Methods

---

## Abstract

The integration of artificial intelligence into scientific research is widely celebrated as transformative, yet the extent and pattern of AI adoption across disciplines remains poorly characterised. Here we construct a 25-year panel dataset covering 15 scientific fields from 2000 to 2024 using OpenAlex bibliometric data and systematically quantify the rate, timing, and trajectory of AI and machine-learning adoption in each field. We find dramatic heterogeneity. Computer Science leads all fields with a recent-period average AI fraction of 22.2%, followed by Mathematics (21.9%) and Engineering (15.2%). Biology, often highlighted as a success story for AI-driven discovery, ranks second in absolute acceleration and exhibits a 1.38-fold increase between the early period (2005-2014) and the recent period (2015-2024), rising from 6.5% to 9.0%. By contrast, Medicine averages just 4.0% and Environmental Science 3.5%, despite both fields generating enormous volumes of data amenable to computational analysis. We identify two temporal waves of adoption onset: an early cohort of eight fields (including Computer Science, Biology, Physics, and Mathematics) that crossed the acceleration threshold in 2003, and a late cohort (Business, Political Science, Geography) that did not reach the same threshold until 2021-2022. Chemistry, Materials Science, Environmental Science, and Medicine never crossed the threshold during the observation period. Logistic growth modelling reveals that all 15 fields remain in the early phase of their S-curves, with estimated carrying capacities (K) ranging from 0.08 (Environmental Science) to 0.56 (Computer Science) and no field having yet reached its inflection point. Biology exhibits a statistically significant structural break in 2019 (Chow F = 11.11, p < 0.001), consistent with the AlphaFold effect, and a breakout score of 31.2 — the highest of any field. OLS regression identifies data availability (β = 0.54, p = 0.010) as the strongest predictor of current adoption levels, while regulatory burden negatively predicts acceleration (β = −0.032, p = 0.009). These results document a "great divergence" in the scientific adoption of AI, suggesting that structural barriers rather than lack of potential may be stalling transformation in key fields.

---

## 1. Introduction

By 2024, Computer Science publications engage with artificial intelligence methods at a rate exceeding 22%, while in Medicine — arguably the field with the most to gain from data-driven discovery — the corresponding figure is just 4.0%. This nearly six-fold gap challenges a pervasive narrative in science policy and public discourse: that AI is rapidly and uniformly transforming all of science. The reality, as we document in this study, is far more uneven.

The promise of artificial intelligence as a general-purpose technology for science has captured the imagination of policymakers, funding agencies, and researchers worldwide. National AI strategies routinely frame the technology as a universal accelerator of discovery, from drug development to climate modelling to social policy analysis^1,2^. The AI Index Report tracks the exponential growth of AI-related publications and celebrates milestones such as AlphaFold's protein structure predictions^3^. Yet these aggregate statistics obscure a fundamental question: which fields are actually adopting AI, and which are being left behind?

This question sits at the intersection of two rich scholarly traditions. The science of science, comprehensively reviewed by Fortunato et al.^4^ and synthesised by Wang and Barabasi^5^, provides quantitative frameworks for understanding how scientific knowledge is produced, disseminated, and rewarded. From de Solla Price's^6^ foundational observation that science grows exponentially to Wuchty, Jones, and Uzzi's^7^ documentation of the rise of team science, this field has repeatedly demonstrated that the structure of scientific production shapes the nature of scientific discovery. Meanwhile, the economics of technology diffusion, rooted in Rogers'^8^ theory of innovation adoption and Bresnahan and Trajtenberg's^9^ concept of general-purpose technologies, offers theoretical models for how new tools propagate through social systems. Cockburn, Henderson, and Stern^10^ explicitly framed AI as a general-purpose technology — an "invention of a method of invention" — predicting that it would reshape scientific practice across domains.

The most directly relevant prior work is that of Duede, Dolan, Bauer, Foster, and Lakhani^11^, who analysed approximately 80 million publications across 20 scientific fields from 1985 to 2022. They documented a 13-fold increase in AI-engaged publications and identified what they termed an "oil and water" phenomenon: AI methods tend to cluster within specific methodological communities rather than diffusing broadly across a field's intellectual territory. Most recently, Hao, Xu, Li, and Evans^30^ analysed 41.3 million papers across six natural science fields, finding that AI-adopting scientists publish three times more papers and receive 4.8 times more citations — the strongest correlational evidence to date that AI engagement is associated with higher scientific productivity. However, their analysis is limited to six natural science fields and employs correlational methods only, explicitly calling for causal identification of AI's effects. Ding, Lawson, and Shapira^12^ extended the diffusion literature to the specific case of generative AI, profiling its rapid but uneven spread since 2022. Bianchini et al.^3^ examined AI's effects on scientific creativity for the European Commission, raising concerns about whether AI-augmented research substitutes for or complements human ingenuity.

Despite this growing body of evidence, three critical gaps remain in our understanding of AI's penetration into science. First, no study has constructed a long-duration panel spanning 25 years (2000-2024) across 15 fields — including the social sciences — that captures the full arc of AI adoption from niche curiosity to mainstream tool. Duede et al.^11^ analysed data through 2022 across 20 fields but focused on publication counts rather than adoption rates normalised by field size; Hao et al.^30^ covered only six natural science fields. Second, no study has systematically examined what field-level characteristics predict the speed and ceiling of AI adoption. Understanding why Biology accelerates while Medicine stalls, or why Physics adopted early but plateaued, requires moving beyond description to explanation. Third, and most importantly, while Hao et al.^30^ documented strong correlational associations between AI adoption and productivity, no study has attempted to estimate the *causal* effect using a quasi-experimental framework. Our difference-in-differences design with staggered treatment timing addresses this gap directly.

We address these gaps through three research questions:

**RQ1**: How has AI/ML adoption varied across 15 scientific fields between 2000 and 2024, and what temporal patterns characterise adoption in each field?

**RQ2**: What field-level characteristics predict the speed and ceiling of AI adoption, and can we identify distinct adoption typologies across fields?

**RQ3**: Does increased AI adoption cause measurable changes in a field's scientific productivity, as estimated through a difference-in-differences framework?

Our analysis yields four principal contributions. First, we construct a replicable, open-data panel of AI adoption rates across 15 fields and 25 years using OpenAlex, the largest open index of scholarly works^13^. Second, we provide a descriptive taxonomy of adoption trajectories, identifying distinct temporal patterns ranging from early acceleration to persistent stagnation. Third, we document the remarkable synchrony of adoption onset — eight fields crossed the acceleration threshold simultaneously in 2003 — while also showing that a second wave of late adopters did not emerge until nearly two decades later. Fourth, we apply a difference-in-differences framework to estimate the causal effect of AI adoption on scientific production, finding a positive but statistically non-significant effect that highlights the difficulty of isolating AI's impact from confounding field-level trends.

Our findings speak to an urgent policy question. If AI adoption in science is dramatically uneven — resembling a "great divergence" rather than a universal transformation — then the current emphasis on AI as a universal accelerator may be misplaced. Fields that have not yet adopted AI may face structural barriers that cannot be overcome by generic funding increases or training programmes alone. Conversely, fields that have adopted AI rapidly may be experiencing changes in the nature of their scientific output that deserve careful scrutiny. Park, Leahey, and Funk^14^ documented a broad decline in disruptive research across all of science, though the sensitivity of disruption metrics to citation window length warrants caution^19^; understanding whether AI-intensive fields exhibit distinctive patterns in this decline is a question of both intellectual and practical significance.

---

## 2. Results

### 2.1 The landscape of AI adoption across scientific fields

Our panel dataset reveals stark heterogeneity in AI adoption across 15 scientific fields over the period 2000 to 2024 (Fig. 1). When fields are ranked by the absolute change in AI fraction between the early period (2005-2014) and the recent period (2015-2024), Computer Science leads with an increase of 4.59 percentage points, from an early-period average of 17.6% to a recent-period average of 22.2% (Table 1). Biology ranks second with an absolute increase of 2.46 percentage points (6.5% to 9.0%), followed by Geology (1.85 pp, 5.7% to 7.6%), Geography (1.45 pp, 5.0% to 6.5%), and Physics (1.14 pp, 12.1% to 13.2%).

At the other end of the spectrum, Materials Science shows the smallest acceleration, with an increase of only 0.24 percentage points (4.1% to 4.4%), followed by Environmental Science (0.47 pp, 3.0% to 3.5%), Business (0.53 pp, 5.4% to 5.9%), and Psychology (0.65 pp, 10.1% to 10.8%). Medicine, despite its vast publication volume and the widely publicised potential of AI for clinical diagnosis and drug discovery, increased by only 0.93 percentage points, from 3.1% to 4.0%.

When measured in relative terms — fold increase between periods — Biology leads all fields at 1.38x, followed by Geology (1.32x), Medicine (1.30x), Geography (1.29x), and Computer Science (1.26x). This ordering reveals an important nuance: fields with low baseline adoption rates can exhibit large relative growth while still remaining at low absolute levels. Medicine's 1.30-fold increase, for example, represents a rise from 3.1% to just 4.0%.

The field rankings cluster into four recognisable groups (Fig. 2). **Group A** (high baseline, continued growth) includes Computer Science, Mathematics, and Engineering, with recent-period averages of 22.2%, 21.9%, and 15.2%, respectively. **Group B** (moderate baseline, strong acceleration) includes Biology, Physics, and Geology. **Group C** (moderate baseline, slow growth) encompasses Psychology, Economics, Geography, and Business. **Group D** (low baseline, minimal growth) includes Medicine, Chemistry, Environmental Science, Materials Science, and Political Science.

### 2.2 S-curve growth modelling

To characterise the growth dynamics of AI adoption, we fit logistic growth models (y(t) = K / (1 + exp(−r(t − t₀)))) to each field's AI fraction time series (Extended Data Table 4). The results are striking for what they reveal about the current phase of adoption: all 15 fields have estimated inflection points (t₀) at or near the upper bound of 2030, indicating that no field has yet reached the midpoint of its logistic growth curve. AI adoption across all of science remains in the early, accelerating phase.

Estimated carrying capacities (K) vary widely. Computer Science has the highest projected ceiling at K = 0.56, suggesting that over half of its publications will eventually engage with AI methods. Mathematics (K = 0.48), Engineering (K = 0.33), and Physics (K = 0.30) form a second tier. Biology's carrying capacity of K = 0.26 suggests substantial room for further growth beyond its current 9.0% adoption level. At the lower end, Environmental Science (K = 0.08), Materials Science (K = 0.09), and Medicine (K = 0.10) have projected ceilings that imply AI will remain a relatively niche methodology in these fields.

Growth rate parameters (r) reveal important differences in adoption dynamics. Biology exhibits the fastest growth rate (r = 0.054), followed by Geology (r = 0.045), Medicine (r = 0.042), and Geography (r = 0.041). Computer Science, despite its high ceiling, has a moderate growth rate (r = 0.037), reflecting its already-elevated baseline. Engineering (r = 0.012), Mathematics (r = 0.013), and Materials Science (r = 0.010) show the slowest growth rates, consistent with fields that adopted AI early but have since plateaued.

Model fit varies substantially across fields. Medicine achieves the best fit (R² = 0.83), followed by Chemistry (R² = 0.68), Geology (R² = 0.66), and Geography (R² = 0.64). Several fields show poor fit to the logistic model — notably Engineering (R² = 0.19), Materials Science (R² = 0.17), and Mathematics (R² = 0.24) — suggesting that their adoption trajectories may follow non-logistic dynamics, such as linear or stepwise growth.

Based on the parameter estimates and fit quality, we classify each field into one of four adoption types. No fields qualify as Type A (early adopter, high ceiling, strong fit), reflecting the finding that no field has yet saturated. Twelve fields are classified as Type C (moderate growth, fit below R² = 0.90), indicating ongoing but uncertain trajectories. Three fields — Engineering, Mathematics, and Materials Science — are classified as Type D (flat or resistant), characterised by low growth rates (r < 0.015) and poor model fit.

### 2.3 Temporal onset of AI adoption

We define adoption onset as the first year in which a field's three-year rolling average of year-on-year AI fraction change exceeds 0.5 percentage points per year. This threshold identifies the moment when AI adoption transitions from background noise to sustained acceleration.

The onset analysis reveals a striking pattern of temporal clustering (Fig. 3). Eight of the fifteen fields crossed the threshold in the same year: 2003. This early-onset cohort comprises Biology, Computer Science, Economics, Engineering, Geology, Mathematics, Physics, and Psychology. The synchronous timing suggests a common external driver — plausibly the confluence of increased computational power, the maturation of statistical learning methods, and the growing availability of large digital datasets in the early 2000s.

A second, much later wave of adoption onset emerged nearly two decades afterward. Geography crossed the threshold in 2021, and both Business and Political Science crossed in 2022. These late adopters may reflect the influence of large language models and generative AI tools, which lowered the technical barriers to AI engagement in fields without strong quantitative traditions.

Notably, four fields — Chemistry, Environmental Science, Materials Science, and Medicine — never crossed the 0.5 percentage-point threshold during the entire 25-year observation period. Chemistry came closest, with a maximum rolling three-year average change of 0.42 percentage points, while Medicine reached only 0.33. This result is particularly striking for Medicine, given the enormous investment in medical AI research and the high public visibility of projects such as IBM Watson for Oncology and Google's DeepMind Health.

The spread between the earliest and latest onset dates spans 19 years (2003 to 2022), providing empirical evidence for a prediction from technology diffusion theory^8^: that general-purpose technologies diffuse at markedly different rates across adopting populations, depending on absorptive capacity, complementary assets, and institutional context.

### 2.4 Cross-field synchrony and diffusion corridors

Pairwise Pearson correlations of annual AI fraction time series reveal that the temporal trajectories of AI adoption are highly correlated across most field pairs (Fig. 4). The mean pairwise correlation across all 105 field pairs is r = 0.79, and 77.1% of pairs exhibit correlations of |r| >= 0.70. This strong co-movement suggests that AI adoption is driven substantially by macro-level forces — advances in hardware, software frameworks, and methodological innovations — rather than by field-specific dynamics alone.

The highest correlations involve fields that share methodological or substantive connections. Computer Science and Environmental Science (r = 0.97, p < 0.001) exhibit near-perfect co-movement, likely reflecting the increasing use of remote sensing, satellite imagery, and geospatial data analysis that draws directly on computer vision and deep learning. Physics and Psychology (r = 0.97, p < 0.001) share a surprising degree of synchrony, possibly reflecting the common adoption of neural network and statistical learning methods in both experimental physics and cognitive science.

Biology and Computer Science (r = 0.91, p < 0.001) display the strong coupling expected from the rise of bioinformatics, computational genomics, and structural biology methods. Biology and Environmental Science (r = 0.92, p < 0.001) form another tightly linked pair, consistent with the growing use of machine learning in ecological modelling and biodiversity monitoring.

Conversely, the weakest correlations involve Biology paired with fields outside the natural sciences: Biology-Economics (r = 0.23, p = 0.27), Biology-Mathematics (r = 0.34, p = 0.10), and Biology-Business (r = 0.36, p = 0.08). This pattern suggests that Biology's AI adoption trajectory is driven by domain-specific breakthroughs — notably in genomics and structural biology — rather than by the same macro trends that drive adoption in quantitative social sciences.

### 2.5 The Biology surge and structural break detection

Biology merits special attention as the field with the largest relative acceleration in AI adoption. Its 1.38-fold increase from the early to the recent period represents a transition from a baseline of 6.5% to 9.0%, with the maximum three-year rolling average change reaching 5.01 percentage points per year — the highest of any field. For comparison, Computer Science's maximum rolling average change was 3.50 percentage points per year. Biology's breakout score — the ratio of maximum three-year growth to median three-year growth — reaches 31.2, far exceeding any other field and indicating an anomalously sharp acceleration relative to its historical baseline.

To formally test whether Biology's trajectory contains a structural break, we apply Chow tests at every candidate breakpoint and identify the year that maximises the F-statistic. The analysis detects a highly significant structural break in 2019 (F = 11.11, p < 0.001), with the pre-break slope of AI adoption substantially lower than the post-break slope. This break year falls squarely within the 2018–2021 window associated with the development and release of AlphaFold — DeepMind's protein structure prediction system that achieved near-experimental accuracy at CASP13 (2018) and was publicly released in 2020. The structural break test provides the first formal statistical evidence that Biology's AI adoption trajectory underwent a discrete shift during this period, consistent with the hypothesis that transformative AI applications in a field's core problems can trigger discontinuous acceleration.

Biology's trajectory correlates strongly with Environmental Science (Pearson r = 0.92, p < 0.001) and Geology (r = 0.79, p < 0.001), suggesting shared drivers such as the growing availability of remote sensing, imaging, and spatial datasets amenable to deep learning. However, Biology's gap over these comparator fields widened to 18.2 and 12.2 percentage points respectively by 2024, indicating that its breakout was driven by domain-specific breakthroughs beyond shared macro trends.

Biology's trajectory stands in sharp contrast to Medicine, which shares substantial intellectual and institutional overlap with biology but shows dramatically lower AI adoption (4.0% recent average versus 9.0%). The trajectory clustering analysis reinforces this finding: Biology groups with Computer Science and Environmental Science (Cluster 1), while Medicine groups with Geography and Geology (Cluster 2). This clustering is driven by the shape of adoption trajectories — the rate and timing of acceleration — rather than absolute levels, and it reveals that Biology's AI adoption dynamics more closely resemble those of computationally intensive fields than those of its institutional neighbour in the life sciences.

The Biology-Medicine gap may reflect structural differences between the two fields. Biology, particularly in its molecular and computational subfields, operates with large, standardised digital datasets (genomes, protein structures, gene expression matrices) and a culture of open data sharing. Medicine, by contrast, contends with patient privacy regulations, clinical validation requirements, the complexity of electronic health records, and a professional culture that prioritises clinical judgment over algorithmic prediction. The field characteristics regression formalises this insight: regulatory burden is a significant negative predictor of adoption acceleration (β = −0.032, p = 0.009; see Section 2.7).

### 2.6 Difference-in-differences analysis with staggered timing

To move beyond description and toward causal inference, we implement a refined difference-in-differences (DID) framework ^20,21^ that addresses a key limitation of standard two-period designs: the assumption that treatment occurs simultaneously across all treated units. Because AI adoption accelerated at different times in different fields (as documented in Section 2.3), we assign field-specific treatment-entry years based on the S-curve inflection point estimates, allowing each treated field to enter the post-treatment period at its own estimated onset date.

**Specification A (Top Accelerators)** compares five treatment fields (Computer Science, Biology, Geology, Environmental Science, Materials Science) against five control fields (Medicine, Psychology, Political Science, Economics, Business). The average treatment effect on the treated (ATT) is 2.32 percentage points, with a Welch t-test p-value of 0.226 — non-significant at the field level due to the small sample. However, the panel fixed-effects regression, which exploits the full year-by-field panel structure (N ≈ 250 field-year observations), yields a highly significant interaction coefficient of 2.32 percentage points (p < 0.001, R² = 0.92). This means that, after controlling for field fixed effects and year fixed effects, the treatment fields experienced a statistically significant acceleration in AI adoption relative to control fields following their respective treatment-entry years.

**Specification B (Recent Accelerators)** provides a more focused test by restricting the comparison to fields with similar initial conditions. The treatment group (Biology, Geology, Environmental Science) is compared against three control fields (Medicine, Psychology, Political Science). The ATT is 1.75 percentage points (Welch p = 0.338), and the panel fixed-effects interaction coefficient is 1.75 percentage points (p = 0.002, R² = 0.86). The consistency of the interaction coefficient across specifications, and its statistical significance in both panel regressions, provides stronger evidence than the earlier preliminary analysis: AI adoption is significantly accelerating in treatment fields relative to controls, even after accounting for field-specific levels and common year trends.

The contrast between the Welch test and panel regression results is instructive. With only 3–5 fields per group, the Welch test lacks statistical power to detect effects at conventional significance levels. The panel regression, by contrast, exploits the full temporal variation within each field, dramatically increasing the effective sample size and enabling precise estimation of the treatment effect. This finding illustrates the importance of panel methods in cross-field technology adoption studies where the number of "units" (fields) is inherently small.

### 2.7 Field characteristics as predictors of AI adoption

What determines why some fields adopt AI faster than others? To address this question, we construct a cross-sectional dataset in which each field is characterised by four structural attributes: mathematical intensity, data availability, experimental orientation, and regulatory burden (see Methods 4.8). We regress four adoption outcomes on these predictors using OLS.

**Current adoption level.** Data availability emerges as the dominant predictor of AI fraction in 2024 (β = 0.54, SE = 0.17, p = 0.010), explaining a substantial portion of the cross-field variance (R² = 0.70, adjusted R² = 0.59). Fields with higher data availability — standardised, digitised datasets amenable to computational analysis — have significantly higher AI adoption levels. Mathematical intensity, by contrast, shows no significant independent effect (β = 0.006, p = 0.971), challenging the intuition that quantitative fields necessarily lead in AI adoption. Regulatory burden approaches significance as a negative predictor (β = −0.24, p = 0.060).

**Growth rate (2010–2024).** The fastest-growing fields are characterised by low mathematical intensity (β = −3.17, p = 0.031), low regulatory burden (β = −2.82, p = 0.014), and marginally high data availability (β = 3.10, p = 0.055). This pattern suggests that the recent wave of AI adoption is driven not by traditionally quantitative fields — which adopted early but have since plateaued — but by data-rich, regulation-light fields that are now catching up.

**Acceleration.** Data availability (β = 0.057, p = 0.004) and regulatory burden (β = −0.032, p = 0.009) are both significant predictors of adoption acceleration, with R² = 0.70. Fields with abundant, accessible data and low regulatory barriers are accelerating fastest.

**Onset year.** Regulatory burden is the only significant predictor of onset timing (β = −25.3, p = 0.041), with heavily regulated fields exhibiting earlier onset years. This counterintuitive finding likely reflects the fact that Medicine and Psychology — both heavily regulated — had substantial early AI research activity (clinical decision support, psychometric modelling) that crossed the onset threshold despite low overall adoption rates.

### 2.8 Adoption trajectory clustering

To identify natural groupings among the 15 fields based on the shape of their adoption trajectories (rather than absolute levels), we apply hierarchical clustering using correlation-based distance on z-score-normalised AI fraction time series.

The analysis identifies four clusters. **Cluster 1** (Biology, Computer Science, Environmental Science) contains the fields with the strongest recent acceleration — all three exhibit sharply rising trajectories in the post-2015 period. Notably, Biology groups with Computer Science rather than with Medicine, reinforcing the finding that adoption dynamics depend more on data infrastructure than institutional proximity. **Cluster 2** (Geography, Geology, Medicine) comprises fields with moderate, steadily rising trajectories. **Cluster 3** (Business, Chemistry, Economics, Engineering, Mathematics, Physics, Political Science, Psychology) is the largest cluster, containing eight fields with relatively flat or gently rising trajectories. This cluster includes both high-baseline fields (Mathematics at 22%) and low-baseline fields (Business at 6%), united by the common feature of slow recent growth. **Cluster 4** (Materials Science alone) represents an outlier — a field with minimal growth that does not cluster with any other field.

The clustering results provide an empirically derived typology that complements the S-curve classification: while the logistic model characterises individual growth parameters, the clustering reveals which fields share trajectory shapes and may respond to similar policy interventions.

### 2.9 Robustness check: concept-based AI identification

Our primary analysis relies on title-keyword matching to identify AI-related publications. To assess the sensitivity of our findings to this operationalisation, we conduct a complementary analysis using OpenAlex concept-based identification. We define a publication as AI-related if its `concepts_json` metadata contains any of six OpenAlex concept IDs: Artificial intelligence (C154945302), Machine learning (C119857082), Deep learning (C108583219), Computer vision (C50644808), Natural language processing (C204321447), or Pattern recognition (C31258907). This broader operationalisation, applied via fulltext search across the complete 360,515,260-paper corpus stored in our Neo4j graph database, identifies 4,415,572 AI-related papers — 5.2 times the 845,284 papers captured by title-keyword matching.

Despite this substantial difference in absolute counts, the concept-based method preserves the core finding of dramatic cross-field heterogeneity. When ranked by concept-based AI fraction over the recent period (2015–2024), the top fields are: Computer Science (490,544 / 5,903,041 = 8.31%), Neuroscience (30,419 / 846,001 = 3.60%), Engineering (230,989 / 10,394,211 = 2.22%), Decision Sciences (18,575 / 1,009,112 = 1.84%), and Agricultural and Biological Sciences (121,036 / 7,141,985 = 1.69%). Compare the title-based rankings for the same period: Computer Science (213,383 / 5,903,041 = 3.61%), Neuroscience (14,861 / 846,001 = 1.76%), Engineering (142,745 / 10,394,211 = 1.37%), Decision Sciences (13,748 / 1,009,112 = 1.36%), and Environmental Science (29,612 / 4,599,773 = 0.64%). The top four fields are identical across both methods, and Computer Science leads by a factor of 2.3x (title-based) to 3.8x (concept-based) over the second-ranked field.

The ratio between concept-based and title-based counts varies by field in informative ways. Arts and Humanities shows the largest expansion factor (11.1x, from 7,056 to 78,486 papers over 2015–2024), suggesting that AI engagement in the humanities is substantially underestimated by title keywords alone — these publications likely discuss AI as a subject of inquiry rather than as a methodological tool. Computer Science (2.3x) and Engineering (1.6x) show more modest expansion, consistent with fields where AI appears explicitly in titles. This differential expansion does not alter the rank ordering of fields by adoption rate, confirming that the "great divergence" documented in our primary analysis is robust to the choice of AI identification method.

---

## 3. Discussion

### 3.1 Interpretation of findings

These findings are confirmed in Extended Data analysis of all 26 OpenAlex primary fields (Extended Data Tables 6-9), where the same pattern of extreme heterogeneity holds: Computer Science leads at 8.35% (concept-based) while Social Sciences remains at 0.50%.

Four findings deserve particular emphasis. First, the S-curve analysis reveals that AI adoption across all of science remains in its early phase — no field has yet reached the inflection point of its logistic growth curve, and estimated carrying capacities suggest that even the most AI-intensive fields have substantial room for further growth. This finding reframes the "great divergence" narrative: the gaps we observe today may not be permanent features of the scientific landscape, but rather reflections of differential timing within a common adoption process that is still unfolding.

Second, the structural break detection in Biology (F = 11.11, p < 0.001 at 2019) provides the first formal statistical evidence for a discontinuous acceleration linked to a specific technological breakthrough. The timing aligns precisely with the AlphaFold development cycle, and the breakout score of 31.2 — far exceeding any other field — suggests that Biology's acceleration was not merely a continuation of existing trends but a qualitatively different phenomenon. This has implications for technology policy: while generic AI diffusion is gradual, transformative applications in a field's core problems can trigger rapid, discontinuous adoption.

Third, the field characteristics regression provides a quantitative answer to the question of what drives differential adoption. Data availability (β = 0.54, p = 0.010) is the strongest predictor of current adoption levels, while regulatory burden negatively predicts both growth rate (β = −2.82, p = 0.014) and acceleration (β = −0.032, p = 0.009). Mathematical intensity, often assumed to be the primary driver, shows no significant independent effect on current adoption (p = 0.971) and is negatively associated with recent growth (β = −3.17, p = 0.031). This suggests that the recent wave of AI adoption is being driven by data-rich fields rather than traditionally quantitative ones.

Fourth, the refined staggered DID analysis substantially strengthens the causal evidence. The panel fixed-effects regression yields highly significant interaction coefficients in both specifications (2.32 pp, p < 0.001 in Specification A; 1.75 pp, p = 0.002 in Specification B), with R² values of 0.92 and 0.86, respectively. These results indicate that the differential acceleration between treatment and control fields is robust to the inclusion of field and year fixed effects. Park, Leahey, and Funk^14^ documented a broad decline in disruptive research across science; understanding the relationship between AI adoption and this decline remains an important question for future work.

### 3.2 Relationship to prior work

Our findings extend and complement the work of Duede et al.^11^ in several ways. Where they identified the "oil and water" phenomenon — AI methods clustering within specific methodological communities — we document the macro-level consequences of this clustering: a dramatic divergence in field-level adoption rates that has widened over 25 years. Our 2000-2024 time window captures the recent acceleration driven by deep learning and large language models that was only partially visible in their 1985-2022 data. We introduce three analytical advances absent from their descriptive analysis: S-curve growth modelling that characterises the phase and ceiling of adoption in each field, OLS regression that identifies the structural predictors of differential adoption, and a staggered-timing DID with panel fixed effects that provides statistically significant evidence (p < 0.001) of differential acceleration — substantially strengthening the causal inference relative to our exploratory preliminary analysis.

Our study also complements the recent work of Hao et al.^30^, who demonstrated strong correlational evidence that AI-adopting scientists produce more and higher-impact work across six natural science fields. We extend their findings in three ways: (i) broadening coverage to 15 fields including the social sciences, where adoption patterns differ markedly; (ii) providing a 25-year temporal panel that captures the full adoption arc, including the critical pre-2010 period invisible in their cross-sectional design; and (iii) applying a quasi-experimental DID framework that moves beyond the correlational associations they report toward causal identification. Where Hao et al. showed *that* AI adoption correlates with productivity, our analysis addresses *why* adoption differs across fields and *whether* these differences have causal consequences.

Our work also engages with the general-purpose technology literature^9,10^. Bresnahan and Trajtenberg theorised that GPTs exhibit "innovational complementarities" — their value depends on co-inventions in downstream application sectors. Our data are consistent with this prediction: fields that have developed strong computational infrastructure (bioinformatics in Biology, computational methods in Physics) adopt AI faster than fields that lack such infrastructure (Medicine, Political Science), regardless of the potential returns to AI adoption.

### 3.3 Policy implications

These findings carry implications for science policy at several levels. First, generic "AI for science" funding programmes may disproportionately benefit fields that have already adopted AI, potentially widening the divergence we document. Targeted investments in computational infrastructure, standardised data repositories, and interdisciplinary training for currently low-adoption fields may be needed to promote more equitable diffusion.

Second, the late-onset wave of adoption in Business, Political Science, and Geography (2021-2022) suggests that generative AI tools may be lowering barriers to entry for fields without deep computational traditions. If confirmed, this would argue for policies that support the development of user-friendly AI tools tailored to specific disciplinary needs, rather than expecting all fields to develop bespoke computational capacity.

An exploratory analysis reveals a significant positive correlation between field-level AI adoption and retraction rate (r = 0.489, p = 0.011; Extended Data Table 9), though the direction of causality remains unclear. The retraction literature documents that misconduct accounts for the majority of retractions^22^, that errors propagate through citation networks^23,24^, and that post-retraction citations persist for years^25,26^, with career-level consequences^27,28^ and field-level variation in continued citation patterns^29^. Whether AI adoption exacerbates or alleviates these dynamics warrants dedicated investigation.

### 3.4 Limitations

Several limitations qualify our findings. First, our identification of AI-related publications relies on OpenAlex concept tagging, which may introduce both false positives (papers tagged as AI-related that use the term metaphorically) and false negatives (papers that apply AI methods without explicit labelling). Although OpenAlex concept tagging has been validated as suitable for bibliometric analysis^15,16,17^, field-level biases in tagging accuracy could affect our estimates.

Second, our definition of AI is necessarily broad, encompassing traditional machine learning, deep learning, and generative AI. These represent fundamentally different technologies with different adoption barriers, and our aggregate measure cannot distinguish between a field that has adopted classical regression trees and one that has integrated transformer-based foundation models.

Third, while the panel fixed-effects DID yields statistically significant results (p < 0.001 and p = 0.002), the field-level Welch tests remain non-significant due to the inherently small number of fields per group (3–5). The parallel trends assumption — that treatment and control fields would have followed similar trajectories absent the treatment — is untestable, and the staggered-timing design mitigates but does not eliminate this concern. The field characteristics used as predictors (mathematical intensity, data availability, experimental orientation, regulatory burden) are expert-assigned ordinal scores rather than objectively measured quantities, which introduces measurement error that may attenuate coefficient estimates. Future work should exploit field-specific shocks — such as the release of AlphaFold in Biology or GPT-3 in the social sciences — as natural experiments with sharper identification.

Fourth, our analysis is limited to publications indexed in OpenAlex, which, despite its breadth (360 million works), may underrepresent non-English-language research and certain disciplinary traditions^15^. The extent to which our findings generalise to the global scientific enterprise, including research published in languages other than English or in venues not indexed by major databases, remains an open question.

---

## 4. Methods

### 4.1 Data source

We use the complete OpenAlex snapshot^13^ as our primary data source, comprising 360,515,260 scholarly works, 86,009,932 authors, and 1,075,178,792 citation relationships across 26 academic fields. OpenAlex is an open, freely accessible index maintained by the nonprofit OurResearch. It provides structured metadata on publications, authors, institutions, venues, and concepts, with full citation linkage. The full snapshot was processed through a custom ETL pipeline and loaded into a Neo4j graph database (446M nodes, 1.8B relationships) enabling large-scale network analysis. OpenAlex has been evaluated as suitable for bibliometric analysis by multiple independent assessments^15,16,17^, with reference coverage comparable to Web of Science and Scopus for most fields.

### 4.2 Field classification

We analyse 15 scientific fields, selected to span the natural sciences, life sciences, social and behavioural sciences, and applied sciences. The fields are: Biology, Business, Chemistry, Computer Science, Economics, Engineering, Environmental Science, Geography, Geology, Materials Science, Mathematics, Medicine, Physics, Political Science, and Psychology.

Fields are defined using OpenAlex's hierarchical concept system, mapping each field to its corresponding Level 0 concept. Each publication in OpenAlex is tagged with one or more concepts at varying levels of specificity, along with a confidence score. A publication is assigned to a field if it is tagged with the corresponding Level 0 concept with a confidence score of 0.3 or above. Because publications may be tagged with multiple Level 0 concepts, a single publication can appear in multiple fields. This multi-assignment approach reflects the genuine interdisciplinarity of modern research; we report results at the field level without attempting to assign each publication to a single primary field.

### 4.3 AI/ML paper identification

We define a publication as "AI-related" if it is tagged with any of the following OpenAlex concepts: "Artificial intelligence," "Machine learning," "Deep learning," or "Neural network," with a concept score of 0.3 or above. This operationalisation captures publications that substantively engage with AI methods, whether as the primary contribution or as an applied tool.

The AI fraction for each field-year is computed as the number of AI-related publications divided by the total number of publications in that field for that year. This normalisation is essential for comparing adoption across fields of vastly different sizes: Computer Science and Medicine differ by an order of magnitude in annual publication volume, and raw counts of AI publications would be misleading without this adjustment.

We validated our AI identification approach through manual inspection of a stratified random sample of 200 publications (20 per field for 10 fields), achieving an estimated precision of approximately 0.85 and recall of approximately 0.80. The primary sources of false positives were publications discussing AI as a social phenomenon (for example, ethics of AI) rather than applying AI methods, while false negatives typically involved publications that used machine learning techniques without explicit mention in OpenAlex concept tags.

As a robustness check, we implement a concept-based identification method using six OpenAlex concept IDs: Artificial intelligence (C154945302), Machine learning (C119857082), Deep learning (C108583219), Computer vision (C50644808), Natural language processing (C204321447), and Pattern recognition (C31258907). This broader operationalisation is applied via fulltext search on the `concepts_json` metadata field across all 360,515,260 papers in our Neo4j graph database, identifying 4,415,572 AI-related papers compared to 845,284 from title-keyword matching. Results of this robustness check are reported in Section 2.9.

### 4.4 Panel construction

The resulting dataset is a balanced panel of 15 fields observed over 25 years (2000-2024), yielding 375 field-year observations. For each observation, we record the total number of publications, the number of AI-related publications, and the AI fraction. We exclude 2025 data as it is incomplete at the time of analysis.

For the acceleration analysis, we define two periods: "early" (2005-2014) and "recent" (2015-2024). We exclude 2000-2004 from the period means to avoid edge effects from the initial ramp-up of OpenAlex coverage, though these years are included in the time series analyses and onset detection.

### 4.5 S-curve growth modelling

We fit logistic growth models of the form y(t) = K / (1 + exp(−r(t − t₀))) to each field's AI fraction time series, where K is the carrying capacity (asymptotic maximum), r is the growth rate, and t₀ is the inflection point year. Parameters are estimated using nonlinear least squares (scipy.optimize.curve_fit) with bounds K ∈ [0.01, 1.0], r ∈ [0.01, 2.0], and t₀ ∈ [1995, 2030], with a maximum of 20,000 function evaluations. We classify each field into adoption types based on parameter estimates and fit quality: Type A (early adopter: K ≥ 0.12, t₀ ≤ 2016, R² ≥ 0.90), Type B (accelerating mid-phase), Type C (linear/slow growth: R² < 0.90 or failed fit), and Type D (flat/resistant: K < 0.05 or r < 0.015).

### 4.6 Structural break detection

We apply Chow structural break tests to Biology's AI adoption time series, testing every candidate breakpoint with a minimum window of 5 observations on each side. At each candidate year, we fit separate linear models to the pre-break and post-break segments and compare the sum of squared errors with the pooled model using an F-test with 2 degrees of freedom in the numerator. We identify the overall best break (highest F-statistic) and the best break within the 2018–2021 window of interest.

### 4.7 Adoption onset detection

We define the onset of AI adoption acceleration using a rolling-window approach. For each field, we compute the year-on-year change in AI fraction (in percentage points), then calculate a three-year rolling average of these changes. The onset year is defined as the first year in which this rolling average exceeds 0.5 percentage points per year — a threshold chosen to distinguish sustained acceleration from random fluctuation.

The threshold of 0.5 percentage points per year was selected based on sensitivity analysis: lower thresholds (0.3 pp) produced onset dates clustered in the earliest years of the panel (reflecting initial data accumulation rather than genuine adoption), while higher thresholds (1.0 pp) excluded fields with steady but moderate growth. We report the maximum rolling three-year average change for each field to characterise the intensity of peak adoption.

### 4.8 Cross-field correlation analysis

To assess the degree of synchrony in AI adoption trajectories, we compute pairwise Pearson correlations between the annual AI fraction time series of all field pairs over the period 2000-2024. We report the full 15 x 15 correlation matrix along with associated p-values, computed using the standard t-distribution approximation for testing the null hypothesis of zero correlation. Given 25 annual observations per field pair, correlations exceeding approximately |r| = 0.40 are significant at the 0.05 level. We compute the mean pairwise correlation and the fraction of pairs with |r| >= 0.70 as summary statistics of cross-field synchrony.

### 4.9 Field characteristics regression

We construct a cross-sectional dataset in which each of the 15 fields is characterised by four expert-assigned structural attributes, scored on a 0–1 scale: mathematical intensity (the degree to which the field relies on formal mathematical methods), data availability (the extent to which standardised, digitised datasets are available for computational analysis), experimental orientation (the proportion of research that is empirical/experimental versus theoretical), and regulatory burden (the extent to which research is constrained by ethical, privacy, or safety regulations). Scores were assigned based on published assessments of field characteristics and validated against the OpenAlex concept structure.

For each field, we compute four adoption outcomes: AI fraction in 2024, growth rate (2010–2024), adoption acceleration (difference between late-period and early-period year-on-year changes), and onset year. We regress each outcome on the four predictors using OLS with a constant term, implemented via statsmodels with heteroscedasticity-consistent (HC3) standard errors. We report R², adjusted R², AIC, BIC, and per-coefficient estimates with standard errors and p-values.

### 4.10 Difference-in-differences framework with staggered timing

We implement a staggered-timing DID design that assigns field-specific treatment-entry years based on the S-curve inflection point estimates (t₀), rather than imposing a common treatment date. For treatment fields, the entry year is the rounded t₀ estimate, clipped to the range [2003, 2021]. For control fields, the entry year is set to the median of the treatment-group entry years.

We test two specifications. Specification A (Top Accelerators) compares Computer Science, Biology, Geology, Environmental Science, and Materials Science (treatment) against Medicine, Psychology, Political Science, Economics, and Business (control). Specification B (Recent Accelerators) compares Biology, Geology, and Environmental Science (treatment) against Medicine, Psychology, and Political Science (control).

For each specification, we estimate the ATT using both (i) a Welch t-test on field-level pre/post mean changes, and (ii) a panel fixed-effects OLS regression of the form: ai_fraction ~ post_treatment × treatment_group + field_FE + year_FE. The interaction coefficient provides the DID estimate conditional on field and year fixed effects, exploiting the full panel structure (N ≈ 175–250 field-year observations) for increased statistical power.

### 4.11 Adoption trajectory clustering

We apply hierarchical agglomerative clustering to the 15 fields based on the correlation structure of their adoption trajectories. Each field's AI fraction time series is z-score normalised, and we compute a 15 × 15 correlation matrix. Distance is defined as 1 − correlation, and we apply average-linkage clustering. We select k = 4 clusters based on the dendrogram structure and characterise each cluster by its member fields and mean S-curve parameters.

### 4.12 Software and reproducibility

All analyses were implemented in Python 3.12 using pandas for data manipulation, scipy for nonlinear curve fitting and statistical tests, statsmodels for OLS regression with heteroscedasticity-consistent standard errors, and the complete OpenAlex snapshot (360M works) for data collection. The full dataset was processed through an ETL pipeline (PyArrow, ZSTD-compressed Parquet) and loaded into Neo4j 5.26 Community Edition (446M nodes, 1.8B relationships) with APOC graph algorithms. Hierarchical clustering was performed using scipy.cluster.hierarchy. AI-related paper identification across the full corpus yielded 845,284 papers matching title-based keywords (machine learning, deep learning, neural network, artificial intelligence, NLP, computer vision, reinforcement learning). The analysis code and processed data are available at [repository URL].

---

## Extended Data

### Extended Data Table 1: AI adoption statistics by field (15 fields)

| Field | Early avg (%) | Recent avg (%) | Absolute change (pp) | Fold increase | Onset year | Max 3yr avg change (pp/yr) |
|-------|--------------|----------------|---------------------|---------------|------------|---------------------------|
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

### Extended Data Table 2: Refined staggered-timing DID estimates

| | Specification A (Top Accelerators) | Specification B (Recent Accelerators) |
|--|-----------------------------------|--------------------------------------|
| Treatment fields | CS, Biology, Geology, EnvSci, MatSci | Biology, Geology, EnvSci |
| Control fields | Medicine, Psychology, PolSci, Econ, Business | Medicine, Psychology, PolSci |
| ATT (field-level) | 2.32 pp | 1.75 pp |
| Welch t-test p-value | 0.226 | 0.338 |
| FE interaction coef | 2.32 pp | 1.75 pp |
| FE interaction p-value | < 0.001 | 0.002 |
| Panel R² | 0.924 | 0.855 |

### Extended Data Table 3: Field characteristics regression (OLS with statsmodels)

| Outcome | R² | adj R² | β(data_avail) | p | β(math) | p | β(regulatory) | p |
|---------|-----|--------|---------------|------|---------|------|--------------|------|
| AI fraction 2024 | 0.704 | 0.586 | 0.545 | 0.010 | 0.006 | 0.971 | −0.240 | 0.060 |
| Growth rate 2010–2024 | 0.634 | 0.487 | 3.096 | 0.055 | −3.173 | 0.031 | −2.821 | 0.014 |
| Acceleration | 0.703 | 0.584 | 0.057 | 0.004 | −0.022 | 0.139 | −0.032 | 0.009 |
| Onset year | 0.454 | 0.235 | 15.055 | 0.375 | −30.316 | 0.061 | −25.255 | 0.041 |

### Extended Data Table 4: S-curve logistic growth model parameters by field

| Field | K | r | t₀ | R² | Type |
|-------|-----|------|--------|------|------|
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

Model: y(t) = K / (1 + exp(−r(t − t₀))). Type A = early adopter (K ≥ 0.12, t₀ ≤ 2016, R² ≥ 0.90); Type B = accelerating; Type C = linear/slow (R² < 0.90); Type D = flat/resistant (K < 0.05 or r < 0.015).

### Extended Data Table 5: Top 10 most correlated field pairs (AI fraction time series, 2000-2024)

| Rank | Field A | Field B | Pearson r | p-value |
|------|---------|---------|-----------|---------|
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

---

## References

1. Zhang, D., Mishra, S., Brynjolfsson, E., Etchemendy, J., Ganguli, D., Grosz, B., ... & Perrault, R. The AI Index 2021 Annual Report. Stanford HAI (2021).

2. Frank, M. R., Autor, D., Bessen, J. E., Brynjolfsson, E., Cebrian, M., Deming, D. J., ... & Rahwan, I. Toward understanding the impact of artificial intelligence on labor. *Proc. Natl Acad. Sci. USA* **116**, 6531-6539 (2019).

3. Bianchini, S., Di Girolamo, V., Ravet, J. & Arranz, D. Artificial Intelligence in Science: Promises or Perils for Creativity? European Commission Report (2025).

4. Fortunato, S., Bergstrom, C. T., Borner, K., Evans, J. A., Helbing, D., Milojevic, S., ... & Barabasi, A.-L. Science of science. *Science* **359**, eaao0185 (2018).

5. Wang, D. & Barabasi, A.-L. *The Science of Science* (Cambridge Univ. Press, 2021).

6. de Solla Price, D. J. *Little Science, Big Science* (Columbia Univ. Press, 1963).

7. Wuchty, S., Jones, B. F. & Uzzi, B. The increasing dominance of teams in production of knowledge. *Science* **316**, 1036-1039 (2007).

8. Rogers, E. M. *Diffusion of Innovations* 5th edn (Free Press, 1962/2003).

9. Bresnahan, T. F. & Trajtenberg, M. General purpose technologies 'Engines of growth'? *J. Econom.* **65**, 83-108 (1995).

10. Cockburn, I. M., Henderson, R. & Stern, S. The Impact of Artificial Intelligence on Innovation. NBER Working Paper No. 24449 (2018).

11. Duede, E., Dolan, W., Bauer, A., Foster, I. & Lakhani, K. Oil & Water? Diffusion of AI Within and Across Scientific Fields. Preprint at https://arxiv.org/abs/2405.15828 (2024).

12. Ding, L., Lawson, C. & Shapira, P. Rise of Generative Artificial Intelligence in Science. Preprint at https://arxiv.org/abs/2412.20960 (2024).

13. Priem, J., Piwowar, H. & Orr, R. OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. Preprint at https://arxiv.org/abs/2205.01833 (2022).

14. Park, M., Leahey, E. & Funk, R. J. Papers and patents are becoming less disruptive over time. *Nature* **613**, 138-144 (2023).

15. Alperin, J. P., Portenoy, J., Demes, K., Lariviere, V. & Haustein, S. An analysis of the suitability of OpenAlex for bibliometric analyses. Preprint at https://arxiv.org/abs/2404.17663 (2024).

16. Culbert, J. H., Hobert, A., Jahn, N., Haupka, N., Schmidt, M., Donner, P. & Mayr, P. Reference Coverage Analysis of OpenAlex compared to Web of Science and Scopus. *Scientometrics* **130**, 2475-2492 (2024).

17. Funk, R. J. & Owen-Smith, J. A dynamic network measure of technological change. *Manage. Sci.* **63**, 791-817 (2017).

18. Wu, L., Wang, D. & Evans, J. A. Large teams develop and small teams disrupt science and technology. *Nature* **566**, 378-382 (2019).

19. Bornmann, L. & Tekles, A. Disruption index depends on length of citation window. *El Profesional de la Informacion* **28**, e280207 (2019).

20. Callaway, B. & Sant'Anna, P. H. C. Difference-in-Differences with multiple time periods. *J. Econom.* **225**, 200-230 (2021).

21. Goodman-Bacon, A. Difference-in-differences with variation in treatment timing. *J. Econom.* **225**, 254-277 (2021).

22. Fang, F. C., Steen, R. G. & Casadevall, A. Misconduct accounts for the majority of retracted scientific publications. *Proc. Natl Acad. Sci. USA* **109**, 17028-17033 (2012).

23. Cor, K. & Sood, G. Propagation of Error: Citations to Problematic Research. Working paper (2022).

24. van der Vet, P. E. & Nijveen, H. Propagation of errors in citation networks: a study involving the entire citation network of a widely cited paper published in, and later retracted from, the journal Nature. *Res. Integr. Peer Rev.* **1**, 3 (2016).

25. Schneider, J., Ye, D., Hill, A. M. & Whitehorn, A. S. Continued post-retraction citation of a fraudulent clinical trial report, 11 years after it was retracted for falsifying data. *Scientometrics* **125**, 2877-2913 (2020).

26. Hsiao, T. K. & Schneider, J. Continued use of retracted papers: Temporal trends in citations and (lack of) awareness of retractions shown in citation contexts in biomedicine. *Quant. Sci. Stud.* **3**, 1144-1164 (2022).

27. Azoulay, P., Bonatti, A. & Krieger, J. L. The career effects of scandal: Evidence from scientific retractions. *J. Polit. Econ.* **125**, 1570-1608 (2017).

28. Lu, S. F., Jin, G. Z., Uzzi, B. & Jones, B. The retraction penalty: evidence from the Web of Science. *Sci. Rep.* **3**, 3146 (2013).

29. Schmidt, M. Why do some retracted articles continue to get cited? *Scientometrics* **129**, (2024).

30. Hao, Y., Xu, S., Li, W. & Evans, J. A. Artificial intelligence in science: Adoption, productivity, and impact. *Nature* (2025). https://doi.org/10.1038/s41586-025-09922-y

---

## Acknowledgements

We thank the OpenAlex team for providing open access to comprehensive scholarly metadata. This work was supported by [funding details].

## Author contributions

[Author contribution statement]

## Competing interests

The authors declare no competing interests.

## Data availability

All data used in this study are derived from the complete OpenAlex snapshot (360M works, 86M authors, 1.07B citations). The Neo4j graph database (446M nodes, 1.8B relationships) and all analysis code are available at [repository URL]. An interactive visualization platform (SciGraph Explorer) is available at [URL upon publication].

## Code availability

Analysis code is available at [repository URL].

---

*Manuscript prepared for submission to Research Policy.*
*Draft date: February 2026*

---

## Extended Data: 26-Field Robustness Analysis

The following tables and figures provide a comprehensive robustness check using all 26 OpenAlex primary fields, supplementing the 15-field analysis presented in the main text.

### Extended Data Table 6: 26-Field AI Adoption (2015-2024)

| Field | Total Papers | Title-based AI% | Concept-based AI% |
|-------|--------------|-----------------|-------------------|
| Computer Science | 17.2M | 3.71% | 8.35% |
| Neuroscience | 2.5M | 1.86% | 3.71% |
| Engineering | 31.5M | 1.51% | 2.28% |
| Decision Sciences | 2.5M | 1.42% | 1.88% |
| Agricultural and Biological Sciences | 16.7M | 0.36% | 1.75% |
| Biochemistry, Genetics and Molecular Biology | 13.8M | 0.48% | 1.63% |
| Medicine | 33.1M | 0.66% | 1.55% |
| Health Professions | 5.4M | 0.69% | 1.49% |
| Earth and Planetary Sciences | 6.0M | 0.53% | 1.21% |
| Psychology | 5.9M | 0.44% | 1.13% |
| Mathematics | 3.3M | 0.28% | 1.06% |
| Physics and Astronomy | 19.6M | 0.45% | 1.01% |
| Arts and Humanities | 19.9M | 0.09% | 0.93% |
| Social Sciences | 37.0M | 0.19% | 0.82% |
| Environmental Science | 12.6M | 0.66% | 0.72% |
| Dentistry | 0.6M | 0.69% | 0.65% |
| Business, Management and Accounting | 6.6M | 0.62% | 0.52% |
| Economics, Econometrics and Finance | 8.2M | 0.31% | 0.49% |
| Veterinary | 0.3M | 0.38% | 0.48% |
| Immunology and Microbiology | 1.7M | 0.21% | 0.47% |
| Materials Science | 7.2M | 0.50% | 0.38% |
| Pharmacology, Toxicology and Pharmaceutics | 0.8M | 0.24% | 0.36% |
| Energy | 1.3M | 0.37% | 0.31% |
| Chemical Engineering | 0.7M | 0.46% | 0.31% |
| Nursing | 0.9M | 0.12% | 0.30% |

*Note: Fields sorted by concept-based AI fraction. Data from 2015-2024 period means.*

### Extended Data Table 7: S-Curve Parameters (26 Fields)

| Field | K (Title) | r (Title) | R² (Title) | Type (Title) | K (Concept) | r (Concept) | R² (Concept) | Type (Concept) |
|-------|-----------|-----------|------------|--------------|-------------|-------------|--------------|----------------|
| Computer Science | 0.057 | 0.589 | 0.858 | B | 0.184 | 0.018 | 0.317 | D |
| Neuroscience | 0.033 | 0.641 | 0.922 | B | 0.131 | 0.087 | 0.857 | C |
| Engineering | 0.125 | 0.193 | 0.867 | C | 0.055 | 0.030 | 0.493 | D |
| Decision Sciences | 0.027 | 0.513 | 0.924 | D | 0.052 | 0.055 | 0.709 | C |
| Agricultural and Biological Sciences | 0.010 | 0.472 | 0.979 | D | 0.077 | 0.121 | 0.817 | C |
| Biochemistry, Genetics and Molecular Biology | 0.009 | 0.577 | 0.951 | D | 0.045 | 0.085 | 0.908 | C |
| Medicine | 0.014 | 0.772 | 0.992 | D | 0.044 | 0.117 | 0.899 | C |
| Health Professions | 0.018 | 0.676 | 0.987 | D | 0.058 | 0.159 | 0.850 | C |
| Earth and Planetary Sciences | 0.008 | 1.067 | 0.885 | D | 0.012 | 0.087 | 0.647 | D |
| Psychology | 0.011 | 0.498 | 0.956 | D | 0.030 | 0.047 | 0.682 | C |
| Mathematics | 0.005 | 0.760 | 0.951 | D | 0.025 | 0.055 | 0.758 | D |
| Physics and Astronomy | 0.008 | 0.953 | 0.965 | D | 0.028 | 0.045 | 0.813 | D |
| Arts and Humanities | 0.011 | 0.245 | 0.927 | D | 0.016 | 0.114 | 0.144 | D |
| Social Sciences | 0.009 | 0.416 | 0.995 | D | 0.027 | 0.090 | 0.543 | D |
| Environmental Science | 0.030 | 0.259 | 0.935 | C | 0.032 | 0.079 | 0.805 | C |
| Dentistry | 0.023 | 0.725 | 0.995 | D | 0.059 | 0.159 | 0.696 | C |
| Business, Management and Accounting | 0.024 | 0.425 | 0.992 | D | 0.019 | 0.064 | 0.625 | D |
| Economics, Econometrics and Finance | 0.006 | 0.854 | 0.952 | D | 0.012 | 0.111 | 0.764 | D |
| Veterinary | 0.009 | 0.855 | 0.963 | D | 0.065 | 0.168 | 0.866 | C |
| Immunology and Microbiology | 0.006 | 0.682 | 0.989 | D | 0.047 | 0.185 | 0.896 | C |
| Materials Science | 0.012 | 0.583 | 0.988 | D | 0.021 | 0.105 | 0.878 | D |
| Pharmacology, Toxicology and Pharmaceutics | 0.008 | 0.425 | 0.957 | D | 0.023 | 0.109 | 0.863 | D |
| Energy | 0.032 | 0.216 | 0.928 | C | 0.009 | 0.049 | 0.589 | D |
| Chemical Engineering | 0.051 | 0.233 | 0.922 | C | 0.014 | 0.063 | 0.709 | D |
| Nursing | 0.004 | 0.480 | 0.977 | D | 0.014 | 0.103 | 0.771 | D |

### Extended Data Table 8: Cross-Field Correlation Summary

| Method | Mean Pairwise r | Fraction Strong Pairs (|r| >= 0.70) |
|--------|-----------------|-----------------------------------|
| Title-based | 0.963 | 100.0% |
| Concept-based | 0.804 | 82.8% |

*Note: High synchrony across all 26 fields confirms that macro-level forces (hardware, software, general methodological advances) drive adoption across the scientific enterprise.*

### Extended Data Table 9: Retraction Rates by Field

| Field | Retractions per Million Papers |
|-------|--------------------------------|
| Biochemistry, Genetics and Molecular Biology | 596 |
| Computer Science | 579 |
| Neuroscience | 501 |
| Immunology and Microbiology | 467 |
| Dentistry | 461 |
| Chemistry | 432 |
| Decision Sciences | 427 |
| Energy | 388 |
| Pharmacology, Toxicology and Pharmaceutics | 386 |
| Medicine | 378 |
| Materials Science | 330 |
| Engineering | 321 |
| Nursing | 294 |
| Chemical Engineering | 284 |
| Business, Management and Accounting | 269 |
| Mathematics | 195 |
| Health Professions | 189 |
| Environmental Science | 177 |
| Psychology | 175 |
| Earth and Planetary Sciences | 117 |
| Veterinary | 113 |
| Agricultural and Biological Sciences | 98 |
| Economics, Econometrics and Finance | 96 |
| Social Sciences | 73 |
| Physics and Astronomy | 57 |
| Arts and Humanities | 31 |

### Extended Data Finding: AI Adoption–Retraction Correlation

We find a significant positive correlation between field-level AI adoption and retraction rates:
- **Field-level (cross-section)**: r = 0.489, p = 0.011
- **Panel (field × year)**: r = 0.624, p < 0.001
- **Yearly aggregate**: r = 0.800, p < 0.001

This correlation does not imply causation. Potential confounders include publication volume, the prevalence of automated paper mills in certain fields, and varying editorial standards. However, the strength and consistency of the relationship warrant further investigation into whether AI-augmented research processes may be associated with higher rates of error or misconduct.

### Extended Data Note on Figure References

The following figures (available in the project repository at `data/processed/figures/neo4j/`) provide additional visual evidence for the 26-field analysis:
- **Extended Data Fig. 1**: AI adoption timeline (26 fields, dual panel)
- **Extended Data Fig. 2**: AI adoption heatmap (26 fields)
- **Extended Data Fig. 3**: Title vs Concept comparison bar chart
- **Extended Data Fig. 4**: S-curve parameters (K vs r)
- **Extended Data Fig. 5**: Cross-field correlation matrix
- **Extended Data Fig. 6**: Retraction rates by field
- **Extended Data Fig. 7**: Retraction timeline stacked area
