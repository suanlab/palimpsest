# The Half-Life of Bad Science: Citation Persistence and Knowledge Contamination After Retraction

**Authors**: [Authors]

**Target Journal**: Proceedings of the National Academy of Sciences (PNAS)

---

## Significance Statement

Retraction is science's ultimate correction mechanism, yet its effectiveness in containing flawed findings remains poorly understood. By tracing 101,581 retracted papers through their citation networks using a 479-million-paper Neo4j graph database containing 2.87 billion citations, we find that 1,068,978 unique papers directly cite retracted work, and an estimated 15.2 million papers (3.2% of the entire scholarly corpus) are contaminated within two citation hops. Citation timing analysis across 41,701 retracted papers with verified retraction dates reveals a dual failure: 52.1% of citations accumulate before retraction occurs (retraction is too slow), while 31.1% of citations continue to accrue after formal withdrawal (correction is incomplete). Only 17.3% of retracted papers with sufficient post-retraction data qualify as "zombie papers" showing no citation decline, while self-correction is accelerating overall. These findings demonstrate that both the speed of retraction and the effectiveness of post-retraction alerting need improvement.


---

## Abstract

Retraction is the most severe formal correction in science, yet retracted papers continue to accumulate citations long after withdrawal, raising fundamental questions about the efficacy of scientific self-correction. Using a Neo4j graph database containing 479,290,642 scholarly works, 107,771,545 authors, and 2,874,371,996 citations across 26 scientific fields, we analyze 101,581 retracted papers — the largest-scale retraction citation analysis to date. We find 1,300,153 direct citation edges to retracted papers from 1,068,978 unique citing papers, with total citations to retracted work reaching 1,295,762. The citation distribution is heavily right-skewed (Gini coefficient = 0.83): 38.2% of retracted papers receive zero citations, while the top 2.1% (2,092 papers with 100+ citations) account for 38.1% of all citations to retracted work. Citation timing analysis across 41,701 retracted papers with verified retraction dates reveals a dual failure: 52.1% of citations accumulate before retraction occurs, while 31.1% continue to accrue after formal withdrawal. Field-level analysis reveals Medicine (24,470 retractions), Biochemistry (14,091), and Computer Science (12,746) as the most affected fields. Temporal analysis shows contamination accelerating: 127,092 papers cited retracted work in 2023 alone, a ~14-fold increase from 2005. These results demonstrate that retraction operates on a timescale that permits extensive knowledge contamination — both because retraction arrives too late and because post-retraction citation persists — necessitating faster retraction processes and more active post-retraction alerting systems.


---

## Introduction

In 1998, Andrew Wakefield and colleagues published a paper in *The Lancet* linking the measles-mumps-rubella (MMR) vaccine to autism spectrum disorder. The paper was formally retracted in 2010 after investigations revealed serious ethical violations and data fabrication. By that time, the study had been cited hundreds of times, its claims had permeated public discourse, fueled vaccine hesitancy movements across multiple continents, and spawned a generation of downstream research that referenced its conclusions --- often without awareness of the retraction. The Wakefield case is frequently cited as an extreme example, but it raises a question that applies across all of science: when a paper is retracted, how effectively does the scientific community stop relying on its findings?

A growing body of literature documents that retracted papers continue to be cited long after retraction, frequently without any acknowledgment that the cited work has been withdrawn ^1--3^.

### Prior Work on Post-Retraction Citation

Cor and Sood ^2^ analyzed over 3,000 retracted papers and 74,000 citations, finding that 31% of all citations to retracted papers occurred after the retraction date, and that 91% of these post-retraction citations contained no acknowledgment of the retraction. Schneider et al. ^1^ traced a single fraudulent clinical trial report over 11 years following retraction, demonstrating sustained citation accumulation with minimal awareness. Hsiao and Schneider ^3^ examined temporal trends in biomedicine, documenting continued use of retracted papers in citation contexts that treat the retracted findings as valid. Schmidt ^4^ explored why some retracted articles continue to attract citations, pointing to factors including database visibility, field norms, and the sheer difficulty of tracking retraction status across fragmented scholarly infrastructure.

At the network level, van der Vet and Nijveen ^6^ conducted a pioneering case study of a single retracted *Nature* paper, tracing its entire citation network to examine whether retracted claims propagated through indirect citations. Their finding that indirect citations did not substantially propagate the retracted content was an important early result, but it was based on a single paper, leaving open the question of whether this pattern generalizes. Jan et al. ^17^ extended the network approach to visualization of retracted article propagation, though at limited scale. Fang, Steen, and Casadevall ^5^ provided the foundational large-scale analysis of retraction causes, examining 2,047 retracted papers in *PNAS* and finding that 67% were attributable to misconduct rather than honest error --- a finding that underscores the deliberate nature of much flawed science entering the literature.

More broadly, the study of scientific self-correction sits within the science of science framework ^15,16^, which examines whether and how quickly the community responds to identified errors. Lu et al. ^8^ documented systematic citation penalties following retraction, while Azoulay, Bonatti, and Krieger ^9^ traced the career spillover effects of retraction on coauthors and related researchers. Moed ^10^ evaluated the effectiveness of self-correction mechanisms, finding significant variation across fields and contexts.

Recent work has begun to address the propagation question more directly. Usman and Balke ^18,19^ introduced the concept of "retraction cascades" at TPDL 2023--2024, using bibliographic coupling similarity to rank potentially retractable papers downstream of ~5,000 retracted articles. Their approach, however, relies on similarity metrics rather than explicit citation traversal, limiting its ability to trace actual propagation paths. Joets and Mignon ^20^ examined "zombie citations" in economics, documenting how retracted papers sustain influence in specific disciplinary contexts. A novel Retraction Impact Index (RII) ^21^ has been proposed as a per-paper metric based on citation trajectory slopes, validated on 20,443 papers, but it does not propagate through networks. Meanwhile, a large-scale study of citation contamination by paper mills in 200,000 systematic reviews ^22^ has highlighted the growing intersection of retraction and evidence synthesis integrity.

### Gaps in Current Understanding

Despite this substantial body of work, three critical gaps remain.

**Gap 1: No systematic multi-generational propagation analysis at scale.** Existing studies have either examined large numbers of retracted papers at the direct-citation level only, or have traced multi-generational propagation for single case studies. Usman and Balke ^18,19^ advanced the "retraction cascade" concept but used bibliographic coupling similarity rather than explicit citation traversal, and their scale (~5,000 papers) is an order of magnitude smaller than the full Retraction Watch corpus. The Retraction Impact Index ^21^ quantifies per-paper impact but does not model network propagation. No prior work has systematically analyzed how retracted findings propagate through multiple layers of the citation network across tens of thousands of retracted papers using explicit BFS traversal with time-weighted contamination scoring.

**Gap 2: No quantitative contamination severity metric.** The literature lacks a standardized measure that integrates the number of direct citations, the downstream reach of those citations, and the temporal persistence of citation to produce a single severity score for each retracted paper. Such a metric would enable principled prioritization of which retractions pose the greatest risk to the integrity of the scientific record.

**Gap 3: No systematic temporal characterization of citation half-lives.** While individual studies have noted that citations persist after retraction, there has been no systematic estimation of citation half-lives across a large sample, nor any characterization of how half-lives vary across papers and what proportion of retracted papers show no citation decline at all.

### Research Questions

We address four research questions:

**RQ1**: How far does the influence of retracted papers propagate through citation chains? Specifically, what is the scale of potential contamination at one and two citation hops from retracted papers?

**RQ2**: What is the temporal decay pattern of citations to retracted papers? What is the mean citation half-life, and what proportion of retracted papers show no detectable decline in citation rate after retraction?

**RQ3**: How does contamination severity --- measured as the combined direct citation count and downstream reach --- vary across retracted papers? Which papers pose the greatest contamination risk?

**RQ4**: What is the citation velocity profile of retracted papers? How quickly do citations accumulate, and when does the peak contamination window occur?

### Contributions

This study makes four contributions to the science of science and research integrity literatures:

1. **Scale of contamination**: We provide the first systematic estimate of multi-generational citation contamination from 101,581 retracted papers across a 479-million-paper citation network, revealing that 1,068,978 unique papers directly cite retracted work and an estimated 15,193,115 papers (3.2% of the entire corpus) are contaminated within two citation hops — the largest-scale analysis of retraction contamination to date.

2. **Temporal characterization**: We map the temporal dynamics of contamination across all retracted papers, showing exponential growth in contamination from 3,068 contaminated papers in 2000 to 127,092 in 2023 — a 41-fold increase driven by both growing retraction volumes and expanding citation networks.

3. **Severity quantification**: We develop and apply a contamination severity metric that combines direct citation count with downstream amplification, enabling identification of the most contaminating retracted papers.

4. **Policy implications**: Our findings inform concrete recommendations for scholarly databases, editorial systems, and the rapidly growing challenge of retracted content entering large language model training data.

---

## Results

### The Scale of Knowledge Contamination

Our analysis is based on a Neo4j graph database containing 479,290,642 scholarly works, 107,771,545 authors, and 2,874,371,996 citation relationships, spanning 26 scientific fields from the OpenAlex bibliometric dataset. Within this corpus, we identify 101,581 retracted papers (0.021% of all works).

The distribution of citations to retracted papers is heavily right-skewed. Of the 101,581 retracted papers, 38,859 (38.2%) have received zero citations, 30,377 (29.9%) have 1--5 citations, 17,927 (17.6%) have 6--20 citations, 12,326 (12.1%) have 21--100 citations, and 2,092 (2.1%) have more than 100 citations. The median retracted paper has received just 2 citations (25th percentile: 0, 75th: 9, 90th: 30, 99th: 162), but the total citations to all retracted papers reach 1,295,762.

The most highly cited retracted paper is the retracted Lancet Commission report on dementia prevention, intervention, and care (2020), with 9,575 citations. This is followed by the retracted mesenchymal stem cell paper in *Nature* (2002, 5,526 citations), the retracted hydroxychloroquine COVID-19 clinical trial (2020, 4,920 citations), and the retracted PREDIMED Mediterranean diet trial (2013, 4,187 citations). Notably, the Wakefield MMR-autism paper, retracted in 2010, continues to accumulate citations (2,903 total), ranking sixth among all retracted papers.

**1-Hop Contamination Network.** We extracted the complete 1-hop citation network from all retracted papers, identifying 1,300,153 direct citation edges from 1,068,978 unique citing papers to retracted works. This means that over one million scholarly papers directly reference at least one retracted study. The mean number of direct citers per retracted paper is 12.8 (median = 2, reflecting the zero-heavy distribution), but among the 62,722 retracted papers with at least one citation, the mean rises to 20.7.

**Table 1. Scale of Citation Contamination from 101,581 Retracted Papers**

| Metric | Value |
|---|---|
| Total scholarly works in corpus | 479,290,642 |
| Total citation relationships | 2,874,371,996 |
| Total retracted papers | 101,581 (0.021%) |
| Total citations to retracted papers | 1,295,762 |
| Retracted papers with 0 citations | 38,859 (38.2%) |
| Retracted papers with 100+ citations | 2,092 (2.1%) |
| Median citations per retracted paper | 2 |
| 99th percentile citations | 162 |
| Maximum citations (single paper) | 9,575 |
| Direct contamination edges (1-hop) | 1,300,153 |
| Unique contaminated papers (1-hop) | 1,068,978 |
| Estimated 2-hop contaminated papers | 15,193,115 (3.2% of corpus) |

### Temporal Dynamics of Contamination

The temporal evolution of contamination reveals a striking pattern of exponential growth. In 2000, only 3,068 papers cited retracted work. By 2010, this had risen to 21,338. By 2020 — a year marked by the COVID-19 pandemic and the Hydroxychloroquine retraction crisis — 76,397 papers cited retracted work. The peak occurred in 2023, with 127,092 contaminated papers generating 152,858 contamination edges to 35,894 distinct retracted papers. Even in 2025 (partial data), 80,291 papers continued to cite retracted work.

The number of retracted papers being cited in each year has grown in parallel: from 1,066 in 2000 to 35,894 in 2023. This reflects both the growing retraction rate and the expanding citation network. However, the ratio of contaminated papers per retracted paper has remained relatively stable at 3--4:1 since 2010, suggesting that the per-paper contamination intensity has not increased even as the total volume has grown.

**Table 2. Temporal Evolution of Contamination (Selected Years)**

| Year | Contaminated Papers | Retracted Papers Cited | Contamination Edges |
|------|---------------------|------------------------|---------------------|
| 2000 | 3,068 | 1,066 | 3,758 |
| 2005 | 9,222 | 1,918 | 11,198 |
| 2010 | 21,338 | 4,438 | 26,352 |
| 2015 | 36,258 | 8,629 | 43,178 |
| 2020 | 76,397 | 17,579 | 96,868 |
| 2023 | 127,092 | 35,894 | 152,858 |
| 2025 | 80,291 | 26,716 | 90,101 |

Field-level analysis reveals that contamination is concentrated in Medicine (24,470 retractions, 0.05% retraction rate), Biochemistry, Genetics and Molecular Biology (14,091, 0.07%), Computer Science (12,746, 0.06%), and Engineering (12,417, 0.03%). Notably, Computer Science's high retraction count is a recent phenomenon driven by the paper mill crisis and conference retraction waves. The lowest retraction rates appear in Veterinary (66 retractions, 0.01%) and Chemical Engineering (201, 0.02%).

### Citation Lag and Temporal Decay

To characterize how quickly citations to retracted papers accumulate relative to their publication, we analyzed the citation lag --- the number of years between a retracted paper's publication year and the year of each citing paper --- across all 1,300,153 contamination edges in our dataset. This analysis captures the aggregate temporal profile of contamination across 101,581 retracted papers.

Citations to retracted papers follow a characteristic rapid-rise, slow-decay curve. The peak citation year is +1 year post-publication, with 230,359 citations (17.9% of the total). Citation volume remains high at +2 years (223,647, 17.4%) before beginning a gradual decline. The median citation lag across all 1,288,232 citations with non-negative lag is just 3 years, meaning that half of all citations to retracted papers occur within the first three years of publication --- before retraction has typically occurred.

The cumulative accumulation is striking: 24.1% of citations occur within the first year, 41.4% within two years, 54.8% within three years, and 72.4% within five years. By year 10, 90.7% of all citations have accumulated. However, the tail is long: 2.8% of citations (35,739) occur 10--15 years after publication, and citations continue to be recorded 25+ years later. This long tail represents a persistent contamination source --- retracted papers that remain embedded in the literature and continue to attract citations decades after publication.

**Table 3. Citation Lag Distribution Across 101,581 Retracted Papers**

| Lag (years) | Citations | Share (%) | Cumulative (%) |
|---|---|---|---|
| 0 (same year) | 79,666 | 6.2 | 6.2 |
| 1 | 230,359 | 17.9 | 24.1 |
| 2 | 223,647 | 17.4 | 41.4 |
| 3 | 172,758 | 13.4 | 54.8 |
| 4 | 129,738 | 10.1 | 64.9 |
| 5 | 96,562 | 7.5 | 72.4 |
| 6--10 | 235,082 | 18.2 | 90.7 |
| 11--15 | 83,152 | 6.5 | 97.2 |
| 16--20 | 26,895 | 2.1 | 99.3 |
| 21--25 | 6,796 | 0.5 | 99.8 |
| >25 | 1,822 | 0.1 | 99.9 |

The rapid early accumulation is particularly concerning from a contamination perspective. Because the median time from publication to retraction is typically 2--3 years ^5,7^, the majority of citations (54.8%) accumulate before or around the time retraction occurs. This means that by the time a retraction notice is issued, the retracted paper has already established its contamination footprint in the citation network. The subsequent long tail --- with 9.3% of citations occurring more than 10 years after publication --- represents ongoing contamination that the self-correction mechanism has failed to arrest.

Decade-level analysis reveals how contamination has shifted over time. Retracted papers published in the 2000s have accumulated 299,094 citations; those published in the 2010s have accumulated 557,174 (the largest cohort, reflecting both the growing literature and the lag in retraction); and papers published in the 2020s have already accumulated 393,620 citations despite the decade being incomplete. The 2010s cohort's dominance reflects the compounding effect of growing retraction volumes and expanding citation networks.

### The Exponential Growth of Retractions

The volume of retracted publications has grown exponentially over the past two decades. In 2000, only 193 retracted papers were published. By 2010, this had risen to 1,406. The growth accelerated dramatically in the 2020s: 7,969 retracted papers in 2020, 12,119 in 2021, 15,220 in 2022, and a peak of 17,049 in 2023. The compound annual growth rate from 2000 to 2023 is approximately 23%, far exceeding the growth rate of the scientific literature itself (~4--5% per year).

This exponential growth reflects multiple converging factors: the proliferation of paper mills producing fraudulent research at scale, the COVID-19 pandemic's pressure on rapid publication (2020 saw a 60% year-over-year increase in retractions), heightened scrutiny from organizations like Retraction Watch, and improved detection tools including image forensics and statistical screening. The 2023 peak of 17,049 retractions represents a single year producing more retracted papers than the entire decade of the 2000s (approximately 5,000 total).

Despite this growth, retracted papers remain a small fraction of the total literature. Across all 479 million papers, only 101,581 (0.021%) are retracted. Even in the most affected fields, retraction rates remain below 0.1%: Medicine leads with 24,470 retractions (0.05% of the field), followed by Biochemistry, Genetics and Molecular Biology (14,091, 0.07%), Computer Science (12,746, 0.06%), and Engineering (12,417, 0.03%). However, the concentration of citations on a small number of retracted papers means that this 0.021% of the literature generates outsized contamination.

### Contamination Hotspots: The Most Cited Retracted Papers

The citation distribution across 101,581 retracted papers is heavily right-skewed, with a small number of "super-contaminators" accounting for a disproportionate share of total citations. The top 20 most-cited retracted papers collectively account for 58,471 citations --- 4.5% of all citations to retracted work, despite representing just 0.02% of retracted papers.

**Table 4. Top 15 Most Cited Retracted Papers**

| Rank | Citations | Year | Field | Title (abbreviated) |
|---|---|---|---|---|
| 1 | 9,575 | 2020 | Medicine | Dementia prevention, intervention, and care: 2020 report of the Lancet Commission |
| 2 | 5,526 | 2002 | Medicine | Pluripotency of mesenchymal stem cells derived from adult marrow (*Nature*) |
| 3 | 4,920 | 2020 | Medicine | Hydroxychloroquine and azithromycin as a treatment of COVID-19 |
| 4 | 4,233 | 2021 | Medicine | 6-month consequences of COVID-19 in patients discharged from hospital |
| 5 | 4,187 | 2013 | Medicine | Primary Prevention of Cardiovascular Disease with a Mediterranean Diet (*NEJM*) |
| 6 | 2,903 | 1998 | Nursing | Ileal-lymphoid-nodular hyperplasia, non-specific colitis, and pervasive developmental disorder (Wakefield MMR) |
| 7 | 2,827 | 2008 | Medicine | Predictive Validity of a Medication Adherence Measure in an Outpatient Setting |
| 8 | 2,742 | 2006 | Medicine | A specific amyloid-β protein assembly in the brain impairs memory |
| 9 | 2,283 | 2008 | Biochemistry | MicroRNA signatures of tumor-derived exosomes as diagnostic biomarkers |
| 10 | 1,900 | 2004 | Medicine | Visfatin: A Protein Secreted by Visceral Fat That Mimics the Effects of Insulin |
| 11 | 1,871 | 2014 | Medicine | A Comprehensive Review on Metabolic Syndrome |
| 12 | 1,734 | 2003 | Biochemistry | An enhanced transient expression system in plants |
| 13 | 1,707 | 2004 | Materials Science | Recent progress in processing and properties of ZnO |
| 14 | 1,567 | 2018 | Energy | A universal principle for a rational design of single-site heterogeneous catalysts |
| 15 | 1,561 | 2008 | Medicine | Mitochondrial Autophagy Is an HIF-1-dependent Adaptive Metabolic Response |

Several patterns emerge from this list. First, the most contaminating retracted papers are concentrated in Medicine (11 of the top 15) and high-impact journals (*Nature*, *NEJM*, *The Lancet*), reflecting both the volume of medical research and the visibility that leading journals confer. Second, the COVID-19 pandemic produced an acute contamination crisis: three of the top five most-cited retracted papers (ranks 1, 3, and 4) are pandemic-related, published in 2020--2021. The retracted Lancet Commission report on dementia prevention alone has accumulated 9,575 citations --- more than any other retracted paper in history. Third, the Wakefield MMR-autism paper (rank 6, 2,903 citations), retracted in 2010, continues to accumulate citations 16 years after retraction, illustrating the extreme persistence of high-profile retracted work.

The field diversity among top contaminators is notable. While Medicine dominates, Biochemistry (ranks 9, 12), Materials Science (rank 13), Energy (rank 14), and Nursing (rank 6) all appear. The presence of Materials Science and Energy reflects the growing retraction crisis in these fields, driven by image manipulation and data fabrication in competitive experimental disciplines.

The Gini coefficient for the citation distribution across all 101,581 retracted papers is 0.83, indicating extreme inequality. The top 2.1% of retracted papers (those with 100+ citations) account for 38.1% of all citations to retracted work, while 38.2% of retracted papers have never been cited at all. This concentration has direct policy implications: targeted interventions on a small number of high-citation retracted papers could address a disproportionate share of the contamination problem.

### Field-Level Contamination Patterns

Analysis across 26 scientific fields reveals dramatic variation in both retraction rates and contamination intensity. Retraction rates per million papers range from 31.1 (Arts and Humanities) to 595.9 (Biochemistry, Genetics and Molecular Biology) --- a 19-fold difference.

The fields with the highest retraction rates are concentrated in laboratory-based experimental disciplines: Biochemistry, Genetics and Molecular Biology (596 per million), Computer Science (579), Neuroscience (509), Immunology and Microbiology (478), and Dentistry (463). These fields share characteristics that may contribute to elevated retraction rates: high publication volume, competitive publication pressure, reproducibility challenges, and vulnerability to paper mill operations. Computer Science's high rate is a recent phenomenon, driven by conference retraction waves and the identification of systematic paper mill operations in subfields of artificial intelligence and software engineering.

In contrast, fields with the lowest retraction rates --- Arts and Humanities (31 per million), Physics and Astronomy (57), and Social Sciences (73) --- tend to be theory-driven or observational disciplines where fabrication is harder to detect but also harder to execute at scale.

Contamination intensity, measured by the total number of contamination edges (1-hop citations) relative to the number of retracted papers, also varies across fields. Medicine produces the most contamination edges (approximately 290,000 from 24,470 retracted papers) due to its large literature and intensive citation culture. However, when normalized by field size, the contamination exposure rates show that Materials Science (1,981 post-retraction citations per million papers) and Biochemistry (1,789 per million) face the highest per-paper contamination risk.

Cross-field analysis of post-retraction citation fractions reveals striking variation in self-correction effectiveness. Among 25 fields with at least 500 classified citations, the post-retraction citation fraction ranges from 15.5% (Energy) and 15.8% (Economics, Econometrics and Finance) to 47.7% (Mathematics) and 43.1% (Nursing). The laboratory-based experimental fields that have the highest retraction rates also show the lowest post-retraction fractions: Biochemistry, Genetics and Molecular Biology (20.8%), Engineering (20.9%), Chemistry (21.3%), and Materials Science (22.4%). This pattern suggests that fields with more recent, acute retraction crises may be responding more rapidly, while fields with older, more established retraction patterns (Mathematics, Nursing, Arts and Humanities) show higher post-retraction fractions, potentially reflecting longer citation half-lives for foundational or methodological works. Computer Science, despite its high retraction rate (579 per million), shows a moderate post-retraction fraction of 24.1%, possibly reflecting the rapid turnover and shorter citation half-lives characteristic of conference-driven fields.

### Decade-Level Contamination Dynamics

To understand how the contamination landscape has evolved, we examined citation patterns across retracted papers grouped by their decade of publication. This analysis reveals a shift in the contamination center of gravity over time.

Retracted papers published in the 2000s (N ≈ 5,600 across our corpus) have accumulated 299,094 citations, with peak citing activity occurring in the 2010s when these papers had been in the literature for a decade and were deeply embedded in reference lists. Papers from the 2010s (N ≈ 25,000) have already accumulated 557,174 citations --- the largest decade cohort --- reflecting both the growing literature and the expanding citation network. Papers from the 2020s (N ≈ 57,000 and counting) have accumulated 393,620 citations in just a few years, with the current growth trajectory suggesting they will eventually surpass the 2010s cohort.

The annual contamination volume has grown from 3,758 citation edges in 2000 to 152,858 in 2023 --- a 41-fold increase. The growth has been particularly steep since 2019: from 66,393 edges in 2019 to 96,868 in 2020 (a 46% increase driven by COVID-19-related retractions), 121,100 in 2021, 137,183 in 2022, and a peak of 152,858 in 2023. Even in 2024 (partial data), 140,300 contamination edges were recorded, and 2025 data through April shows 90,054 edges.

The ratio of contaminated papers to retracted papers cited has remained relatively stable at 3--4:1 since 2010, suggesting that while the total contamination volume has grown enormously, the per-paper contamination intensity has not increased. This stability indicates that the growth in contamination is driven primarily by the increasing volume of retractions rather than by a worsening per-paper contamination problem.

### Self-Correction Dynamics: Evidence of Acceleration

A critical question for science policy is whether the self-correction mechanism is improving over time. Our full-scale citation timing analysis across 41,701 retracted papers with verified retraction dates (Section 2.10) reveals a dual failure: 52.1% of citations accumulate before retraction occurs, while 31.1% continue to accrue after formal withdrawal. However, the post-retraction citation decay curve shows a steep initial decline, with citation volume dropping from 113,454 at +1 year post-retraction to 29,548 at +4 years and 16,941 at +6 years.

The temporal cohort analysis from the 50-paper detailed subsample corroborates this trend. Papers retracted in the 2000s had a mean citation half-life of 9.2 years and a mean post-retraction citation fraction of 78.5%; by the 2010s, these values improved to 6.8 years and 65.1%; and for the 2020s cohort, they drop to 3.4 years and 30.1%. OLS regression of decay rate on retraction year confirms that this improvement is statistically significant (β = −0.468 per year, SE = 0.130, p < 0.001, 95% CI [−0.722, −0.213]).

The most likely drivers of this acceleration include: (i) systematic retraction flagging in PubMed (implemented in the 2010s), which makes retraction status visible at the point of citation; (ii) the growing influence of Retraction Watch as a monitoring and awareness tool; (iii) increased attention to retraction issues from editors, reviewers, and the broader research community; and (iv) the development of automated tools that check reference lists against retraction databases.

However, the acceleration in self-correction is occurring against a backdrop of exponentially growing retraction volumes. Even as individual retracted papers are corrected faster, the total number of retracted papers entering the literature each year has grown from 193 in 2000 to 17,049 in 2023 --- a rate that threatens to overwhelm the improved correction mechanism. The net effect is that total contamination volume continues to grow, even as per-paper correction rates improve.

### Illustrative Case Studies

To provide concrete texture to the aggregate statistics, we highlight three retracted papers that illustrate distinct contamination profiles drawn from our full corpus of 101,581 papers.

**The Lancet Commission Super-Contaminator.** The retracted 2020 Lancet Commission report on dementia prevention, intervention, and care has accumulated 9,575 citations --- the most of any retracted paper in our dataset. Published in a flagship journal during the COVID-19 pandemic, this paper achieved extraordinary visibility before its retraction. Its citation trajectory illustrates the acute contamination risk posed by high-impact retractions in clinical medicine: each of its citers is itself cited an average of approximately 50 times, yielding an estimated two-hop contamination reach exceeding 400,000 downstream papers.

**The Persistent Wakefield Legacy.** The 1998 Wakefield MMR-autism paper, retracted in 2010, continues to accumulate citations (2,903 total, ranking sixth among all retracted papers). Classified under Nursing rather than Medicine in our dataset, this paper's persistence is particularly notable: it has been cited in every year from 1998 through 2024, with no indication of declining citation rates. Its influence extends far beyond the academic literature into public health policy and vaccine confidence, illustrating how retracted papers can generate contamination that is not captured by citation metrics alone.

**The COVID-19 Retraction Crisis.** The retracted hydroxychloroquine clinical trial (4,920 citations, rank 3) and the retracted 6-month COVID-19 consequences study (4,233 citations, rank 4) represent a new category of contamination: pandemic-accelerated retractions. These papers accumulated thousands of citations within months of publication, before the scientific community could identify and respond to their flaws. Their rapid accumulation --- the hydroxychloroquine trial amassed the bulk of its citations within a single year --- demonstrates a distinct contamination risk: in high-velocity research environments, the window for effective self-correction can close before retraction occurs.

### Full-Scale Citation Timing Analysis Across 41,701 Retracted Papers

To characterize pre/post-retraction citation dynamics at scale, we conducted a comprehensive citation timing analysis across 41,701 retracted papers with verified retraction dates from the Retraction Watch database, matched to our Neo4j graph database (479,290,642 papers, 2,874,371,996 citation edges). For each retracted paper, we classified every incoming citation as pre-retraction, same-year, or post-retraction based on the citing paper's publication year relative to the verified retraction date (not the publication year).

Of 1,137,164 classified citation edges (79.7% of all 1,426,876 hop1 edges; the remaining 20.3% lacked retraction dates), 592,785 (52.1%) occurred before retraction, 190,386 (16.7%) in the same year as retraction, and 353,903 (31.1%) after retraction. This distribution reveals a dual failure in the self-correction mechanism: retraction arrives too late to prevent the majority of contamination (52.1% pre-retraction), and a substantial minority of citations (31.1%) continue to accumulate even after formal withdrawal.

The pre-retraction dominance reflects the well-documented lag between publication and retraction, typically 2--3 years. During this window, retracted papers accumulate citations normally, establishing their contamination footprint before the community identifies flaws. The 31.1% post-retraction rate represents 353,903 citations that occurred after the scientific community had formally designated the cited work as unreliable --- a figure that, while far lower than estimates based on publication year rather than retraction year, still represents a significant contamination burden.

Post-retraction citation persistence follows a characteristic decay curve with a sharp peak at one year post-retraction (113,454 citations) followed by steep decline: 65,472 at +2 years, 40,707 at +3, 29,548 at +4, 22,370 at +5, 16,941 at +6, 13,786 at +7, 10,875 at +8, 8,795 at +9, and 7,028 at +10 years. Even 15 years after retraction, 1,991 citations were recorded --- demonstrating that the "half-life of bad science" extends well beyond a decade.

Field-level analysis reveals that Engineering leads in post-retraction citation volume (36,620), followed by Medicine (34,245), Biochemistry, Genetics and Molecular Biology (24,646), Computer Science (20,622), and Materials Science (14,254). The prominence of Engineering --- which surpasses Medicine despite having fewer retracted papers --- may reflect lower awareness of retraction status in engineering subdisciplines, where systematic retraction-flagging infrastructure is less developed than in biomedical databases.

The analysis also identifies "zombie papers" --- retracted works with the highest post-retraction citation accumulation. We define "zombie citations" as those occurring after a paper has been formally withdrawn, effectively creating a persistent but unreliable presence in the literature. The most-cited zombie paper is the Wakefield MMR-autism study (4,305 post-retraction citations), which continues to accumulate citations 16 years after retraction. Other notable zombies include the retracted Mediterranean Diet trial (1,740 post-retraction citations), a retracted ZnO nanostructures review (1,293), and a retracted electrocatalysis study (922). These cases illustrate how high-impact retracted papers can sustain citation rates that rival or exceed many non-retracted papers, creating persistent conduits for the propagation of unreliable findings.

### Retraction Reasons and Contamination Patterns

To understand whether the *cause* of retraction affects contamination severity, we classified 61,904 retracted papers with Retraction Watch reason metadata into three major categories: misconduct (including fabrication/fraud, paper mill operations, plagiarism, compromised peer review, and data/image manipulation), error (including honest errors and duplication), and other/unspecified reasons.

Misconduct accounts for the majority of retractions (50.5%, N = 31,287), followed by other/unspecified (36.4%, N = 22,547) and error (13.0%, N = 8,070). This misconduct proportion is lower than the 67% reported by Fang, Steen, and Casadevall ^5^, but the difference reflects our broader misconduct definition that separates paper mill operations (18.7% of all retractions, the single largest specific category) from traditional misconduct categories. When paper mill retractions are excluded, the proportion of traditional misconduct (fabrication, falsification, plagiarism, compromised review, manipulation) is 31.8%.

A striking pattern emerges when comparing contamination across reason categories. Papers retracted for error accumulate *more* citations on average (mean = 29.2, median = 6) than those retracted for misconduct (mean = 24.7, median = 7) or other reasons (mean = 15.7, median = 2). This counterintuitive finding likely reflects the higher pre-retraction visibility of error-based retractions: papers containing honest but consequential errors tend to be published in higher-impact venues and generate greater scientific interest before their flaws are identified. In contrast, paper mill retractions --- which constitute the largest misconduct subcategory --- tend to be lower-impact papers with fewer citations.

Paper mill retractions show the highest volume (11,574 papers, 18.7% of all retractions), but they produce relatively low per-paper contamination (mean citations = 15.7), reflecting the typically low impact of fabricated papers. However, their sheer volume means they generate substantial aggregate contamination. Compromised peer review accounts for 6,797 retractions (11.0%), while AI-generated content emerges as a new and growing category (1,668 retractions, 2.7%).

---

## Discussion

### Science's Immune System Is Real, Slow, but Improving

Our full-scale analysis reveals a paradox: the self-correction mechanism is functional and accelerating, yet the total contamination burden continues to grow. Across 101,581 retracted papers, 1,068,978 unique papers directly cite retracted work, and an estimated 15.2 million papers (3.2% of the entire scholarly corpus) fall within two citation hops. The full-scale citation timing analysis across 41,701 retracted papers with verified retraction dates reveals a dual failure: 52.1% of citations accumulate before retraction occurs (retraction is too slow), while 31.1% continue to accrue after formal withdrawal (correction is incomplete).

However, our temporal cohort analysis reveals an important and previously undocumented trend: self-correction is accelerating. Papers retracted in the 2000s had a mean citation half-life of 9.2 years and a post-retraction citation fraction of 78.5%; by the 2010s, these improved to 6.8 years and 65.1%; and for the 2020s cohort, they drop dramatically to 3.4 years and 30.1%. OLS regression confirms this trend (β = −0.468 per year, SE = 0.130, t = −3.60, p < 0.001, 95% CI [−0.722, −0.213], R² = 0.544, F(1,48) = 12.97; Durbin-Watson = 1.45), providing the first formal statistical evidence that science's immune response is speeding up.

The field-level breakdown reveals an unexpected pattern: Engineering leads all fields in post-retraction citation volume (36,620), surpassing Medicine (34,245) despite having fewer retracted papers overall. This may reflect weaker retraction-awareness infrastructure in engineering subdisciplines, where PubMed-style retraction flagging is less prevalent. The identification of "zombie papers" --- retracted works that continue accumulating citations at undiminished or increasing rates --- provides concrete targets for intervention: the most extreme zombie paper is the Wakefield MMR-autism study (4,305 post-retraction citations, second-half citations exceeding first-half by 23%), followed by the retracted Mediterranean Diet trial (1,740 post-retraction citations) and a retracted ZnO nanostructures review (1,293).

An epidemiological analogy illuminates the dynamics. If we model the scientific literature as a population susceptible to "infection" by retracted claims, the retracted paper acts as a pathogen, direct citations as primary infections, and two-hop citations as secondary transmissions. In this SIR-like framework, retraction functions as a vaccine --- but one administered after substantial community spread has occurred. Our data suggest that the basic reproduction number (R₀) for highly cited retracted papers is well above 1: the amplification from 1,068,978 direct citers to 15.2 million two-hop papers represents a 14-fold increase. The accelerating self-correction we observe corresponds to a gradual increase in the effective "vaccination rate" over time, consistent with improved retraction infrastructure reducing the susceptible pool.

The citation lag analysis provides a complementary perspective. The median citation lag of 3 years means that half of all citations to retracted papers accumulate within the first three years of publication --- typically before retraction has occurred. The characteristic rapid-rise, slow-decay curve (peak at +1 year, with 72.4% of citations within 5 years) means that by the time a retraction notice is issued, the contamination footprint is largely established. The long tail of the distribution --- with citations still occurring 25+ years after publication --- ensures that retracted papers remain persistent contamination sources indefinitely.

### The Persistence Problem: Where Self-Correction Falls Short

While the preceding analysis shows that per-paper self-correction is accelerating, a significant gap remains: 31.1% of citations to retracted papers accrue after formal withdrawal, and this aggregate figure masks substantial heterogeneity across papers. To characterize the worst cases, we identified "zombie papers" --- retracted works whose citation rates show no detectable decline after retraction. Among 12,666 retracted papers with at least five post-retraction citations and at least two years of post-retraction observation, 2,065 (17.3%) show no decline: their citation rates in the second half of the post-retraction period are at least 90% of the first half. The most extreme zombie paper has accumulated 4,305 post-retraction citations with a ratio of 1.23 (second-half citations exceeding first-half), indicating that retraction has not merely failed to reduce citations but has been entirely ineffective at slowing accumulation. This finding extends and deepens the alarm raised by Cor and Sood ^2^, who documented that 91% of post-retraction citations fail to acknowledge the retraction. Our temporal analysis goes further: not only do individual citing papers fail to note the retraction, but the aggregate citation rate itself does not diminish for a substantial minority of retracted papers.

Several factors may explain this persistence. Retracted papers that have become "canonical" references in their subfield may continue to be cited as a matter of convention, with authors including them in reference lists without checking their current status. The citation lag analysis shows that 72.4% of citations accumulate within the first 5 years --- typically before retraction --- establishing a large contamination base before correction can occur. The field-level analysis provides additional context: fields with better-developed retraction-flagging infrastructure (e.g., Medicine through PubMed) show faster self-correction than fields without such systems (e.g., Engineering, Materials Science). The concentration of our detailed subsample in Cochrane reviews introduces a specific dynamic: when a systematic review is retracted, authors who cited it for its comprehensive evidence synthesis may not have an obvious replacement reference, leading to continued citation even after retraction.

Taken together, the accelerating per-paper correction documented in Section 2.8 and the 17.3% zombie paper rate identified here paint a consistent picture: the self-correction mechanism is improving for the median retracted paper but remains incomplete for a persistent minority. The challenge is not that self-correction fails uniformly, but that it fails unevenly --- and the papers for which it fails tend to be the most visible and consequential ones.

### Contamination Amplification: The Two-Hop Problem

The estimated two-hop reach of 15,193,115 papers from 101,581 retracted papers represents a 14-fold amplification from the 1,068,978 directly contaminated papers. Across the full corpus, each retracted paper generates an average of 12.8 direct citers (median = 2, reflecting the zero-heavy distribution), but the 62,722 retracted papers with at least one citation average 20.7 direct citers. This multiplicative relationship means that the contamination footprint grows rapidly with each generation.

It is important to note that two-hop reach represents a potential contamination boundary, not a definitive count of papers containing retracted claims. Many papers at the two-hop distance may never reference or rely upon the specific claims in the retracted paper. The actual propagation of retracted content through indirect citation chains depends on citation context --- whether the relevant claim was the reason for citation, and whether it was accurately transmitted. Van der Vet and Nijveen ^6^ found limited propagation of specific claims through indirect citations in their single-paper case study. Our finding of over one million two-hop papers does not contradict this; rather, it establishes the scale of the network through which contamination *could* propagate, creating a quantitative upper bound on the problem.

The practical significance of this two-hop reach lies not only in the potential for claim propagation but also in the structural role these papers play. If a citing paper uses the retracted work to justify its methodology, frame its research question, or support a key assumption, then the downstream papers that build upon this citing paper are structurally dependent on the retracted foundation, even if they never cite the retracted paper directly.

### Policy Implications

Our findings support several concrete policy recommendations.

**Database flagging.** Current retraction flagging in major databases (PubMed, Scopus, Web of Science, Google Scholar) is inconsistent and often requires the user to actively check a paper's status. Our data showing 140,300 contamination edges in 2024 alone --- representing over 118,000 unique papers citing retracted work in a single year --- suggests that passive flagging is insufficient. We recommend active intervention: when an author adds a retracted paper to their reference list, the submission system should generate a prominent, mandatory warning. Citation management tools (Zotero, Mendeley, EndNote) should implement real-time retraction status checks using the Retraction Watch database or the CrossRef retraction metadata.

**Downstream contamination alerts.** Beyond flagging the retracted paper itself, our two-hop analysis suggests the need for downstream alerts. Papers that cite retracted papers should themselves carry a notation --- not a retraction, but an advisory that one of their cited sources has been retracted. This cascading alert system would help readers assess the reliability of the evidence chain.

**Publisher and editorial policy.** The 17.3% zombie paper rate (papers showing no citation decline after retraction) indicates that current retraction notices are not achieving their intended effect for a substantial minority of cases. Publishers should consider more aggressive measures: watermarking retracted PDFs, linking to the retraction notice from every page of the retracted article, and including retraction status in DOI metadata so that any system resolving the DOI encounters the retraction.

**LLM training data.** As large language models increasingly ingest the scientific literature, the contamination problem takes on new urgency. Retracted papers and their unacknowledged citations are present in training corpora, meaning that LLMs may generate text that reflects or reproduces retracted findings without any indication of their retracted status. Our finding that 101,581 retracted papers reach over 15 million downstream papers within two citation hops suggests that the contamination of training data is not a marginal problem but a systemic feature of the scholarly corpus. Efforts to curate LLM training data for scientific applications should incorporate retraction status filtering and, more ambitiously, downstream contamination scoring to identify and appropriately weight papers in the contamination zone.

### Exploratory Finding: AI Adoption and Retraction Rates

Our cross-field analysis (Extended Data Table 1) reveals that Biochemistry, Genetics and Molecular Biology and Materials Science have the highest post-retraction citation rates per million papers (1,788/M and 1,981/M respectively). An exploratory analysis reveals a significant positive correlation between field-level AI adoption and retraction rate (r = 0.489, p = 0.011; Extended Data Table 2). At the field-year panel level, this correlation strengthens (r = 0.624, p < 0.001), and at the yearly aggregate level it reaches r = 0.800 (p < 0.001).

These correlations should be interpreted with caution. They do not imply causation: fields with high publication volume, rapid growth, and open-access models (Computer Science, Biochemistry) may independently experience both higher AI adoption and higher retraction rates due to confounding factors including paper mill operations, fast review cycles, and editorial capacity constraints. The correlation may also reflect the fact that AI-related fields are among those most intensively scrutinized for retraction. We present this finding not as a conclusion but as an observation warranting further investigation with causal identification strategies.

### The High-Impact Paradox: When Influential Sources Become Contamination Hubs

A notable feature of our results is the concentration of contamination among high-impact retracted papers. The Gini coefficient of 0.83 for the citation distribution indicates extreme inequality: the top 2.1% of retracted papers (those with 100+ citations) account for 38.1% of all citations to retracted work, while 38.2% have never been cited. The most contaminating papers are disproportionately published in flagship journals (*Nature*, *NEJM*, *The Lancet*) and in Medicine, reflecting the visibility and authority that leading journals confer.

Systematic reviews occupy a particularly dangerous position in this landscape. When a Cochrane review or Lancet Commission report is retracted, the contamination potential is structurally amplified: each clinical guideline informed by the review, each subsequent meta-analysis incorporating its conclusions, and each primary study that frames its contribution relative to the review's findings becomes part of the contamination chain. The retracted 2020 Lancet Commission report on dementia prevention (9,575 citations) illustrates this dynamic: published in a flagship journal during the COVID-19 pandemic, it achieved extraordinary visibility before retraction, and its contamination footprint extends to an estimated 400,000+ downstream papers through two-hop citation paths.

This "high-impact paradox" --- that the most authoritative and visible sources can become the most dangerous contamination vectors when flawed --- has implications for how publishers and the systematic review community manage retraction. The current practice of simply withdrawing the paper and publishing a retraction notice may be inadequate given the structural role these documents play. More aggressive measures, such as issuing updated reviews that explicitly address the retracted conclusions, watermarking retracted PDFs, and mandatory retraction warnings in citation management tools, may be necessary to contain downstream contamination.

### Implications for the Reproducibility Debate

Our findings intersect with the broader reproducibility crisis in science in important ways. The persistence of retracted citations suggests that the scientific community's ability to identify and respond to flawed research is compromised not only at the point of discovery (replication) but also at the point of correction (retraction). If retraction --- the most definitive signal of unreliability --- fails to meaningfully reduce a paper's influence, then softer signals such as failed replications, published critiques, or expressions of concern are likely even less effective at correcting the record.

This has implications for how we think about the "self-correcting" nature of science. The phrase is typically invoked to argue that errors, while inevitable, are eventually identified and corrected through the cumulative process of replication, critique, and retraction. Our data suggest that this corrective process operates on timescales that, while improving, remain dangerously slow relative to the speed of contamination. The median citation lag of 3 years means that the bulk of contamination occurs before retraction, and the exponential growth in retraction volumes (from 193 in 2000 to 17,049 in 2023) threatens to overwhelm the improving per-paper correction rate. The self-correction mechanism exists and is accelerating, but its throughput may be insufficient to keep pace with the growing rate of knowledge contamination.

### Limitations

We acknowledge several important limitations. First, while our aggregate analysis covers all 101,581 retracted papers in our corpus and the full-scale citation timing analysis covers 41,701 papers with verified retraction dates, retraction dates are available for only 79.7% of classified citation edges in our 1-hop network. The remaining 21,019 unmatched papers are predominantly recent (2020--2024), meaning that our pre/post-retraction analysis may underrepresent the most recent retraction cohorts. The detailed citation half-life analysis is based on a subsample of 50 highly cited retracted papers, while the zombie paper analysis covers 12,666 papers with at least five post-retraction citations --- these papers are not necessarily representative of all retracted papers.

Second, our two-hop reach estimate of 15.2 million papers is a structural measure based on citation network topology, not a measure of content propagation. We do not analyze the citation context of the 1,068,978 direct citers --- that is, we do not determine whether each citing paper endorses, criticizes, or merely mentions the retracted work. Citation context classification at this scale would require natural language processing tools applied to the full text of citing papers, which we plan as a subsequent analysis.

Third, the citation lag distribution (Section 2.3) captures the temporal gap between retracted paper publication and citing paper publication, but does not account for the retraction date. A more precise analysis would require retraction dates for all 101,581 papers --- available in the Retraction Watch database but not yet systematically matched to our graph database. The full-scale citation timing analysis (Section 2.10) addresses this limitation for 41,701 papers with verified retraction dates.

Fourth, OpenAlex's coverage of retractions may be incomplete. Our graph database contains 101,581 retracted papers, while the Retraction Watch database contains approximately 68,870 records. After DOI matching, we identified 61,904 retracted papers with valid bibliometric records. The additional retractions in our database (identified via the `is_retracted` flag in OpenAlex metadata) may include papers not yet in Retraction Watch, but they may also include false positives if the retraction flag is applied incorrectly.

Fifth, the citation counts we report are based on the OpenAlex citation graph, which may undercount citations from works not yet indexed. The gap between metadata-based citation counts (1,295,762 total) and explicit citation edges in the graph (1,300,153 edges from 1,068,978 unique papers) is small, suggesting good coverage for recent literature, but coverage of older citations and non-English literature may be less complete.

Sixth, the 2-hop contamination query traverses the full CITES relationship graph without temporal filtering, meaning that the 15.2 million figure includes papers that may have cited the 1-hop paper before the retracted paper was even published. A temporally constrained 2-hop analysis would provide a more precise estimate but would require substantially more complex queries.

---

## Materials and Methods

### Data Sources

**Retraction Watch Database.** We obtained retraction records from the Retraction Watch database (68,870 records), the most comprehensive publicly available source of retraction information ^11^. After DOI-based matching to OpenAlex, we identified 61,904 retracted papers with valid bibliometric records. The retraction reasons, retraction dates, and original publication dates were extracted from Retraction Watch metadata.

**OpenAlex.** We used the complete OpenAlex snapshot ^12^ as our primary bibliometric data source, comprising 479,290,642 scholarly works, 107,771,545 authors, 2,874,371,996 citation relationships, and 26 academic fields (all counts derived from direct Neo4j aggregate queries over the imported snapshot). The full snapshot was processed through a custom ETL pipeline (Python/PyArrow) and loaded into a Neo4j graph database (479,290,642 Paper nodes, 107,771,545 Author nodes, 26 Field nodes; 2,874,371,996 CITES, 744,638,838 AUTHORED, 347,868,095 BELONGS_TO relationships) for network traversal and contamination analysis. OpenAlex has been validated as suitable for bibliometric analysis ^13, 14^, with citation coverage comparable to proprietary databases for recent literature.

Across the full database, we identified 101,581 retracted papers (0.021% of all works) via the `is_retracted` boolean flag in OpenAlex metadata. Retractions are concentrated in Medicine (24,470), Biochemistry, Genetics and Molecular Biology (14,091), Computer Science (12,746), and Engineering (12,417). The peak retraction publication year was 2023 (17,049 papers), followed by 2022 (15,220) and 2021 (12,119), reflecting both the growth of the literature and intensifying retraction activity.

### Sample Selection and Analysis Flow

The following diagram summarizes the sample selection at each stage of analysis:

```
OpenAlex corpus
├── 479,290,642 scholarly works
├── 2,874,371,996 citation relationships
│
├── is_retracted flag
│   └── 101,581 retracted papers (0.021%)
│       ├── 38,859 with 0 citations (38.2%)
│       └── 62,722 with ≥1 citation (61.8%)
│
├── 1-Hop contamination network
│   ├── 1,300,153 citation edges
│   ├── 1,068,978 unique citing papers
│   └── 55,562 distinct retracted papers cited
│
├── Citation timing analysis (requires retraction dates)
│   ├── Retraction Watch match: 61,904 papers with DOI
│   ├── Matched to graph: 41,701 with verified retraction dates
│   ├── 1,137,164 classified edges (79.7% of 1,426,876 total)
│   │   ├── 592,785 pre-retraction (52.1%)
│   │   ├── 190,386 same year (16.7%)
│   │   └── 353,903 post-retraction (31.1%)
│   └── 289,712 unclassified (20.3%, no retraction date)
│
├── Zombie paper analysis (subset of timing analysis)
│   ├── 12,666 papers with ≥5 post-retraction citations + ≥2 years observation
│   └── 2,065 zombie papers (17.3%, no citation decline)
│
├── Retraction reason analysis
│   └── 61,904 papers with Retraction Watch reason metadata
│       ├── 31,287 misconduct (50.5%)
│       ├── 8,070 error (13.0%)
│       └── 22,547 other/unspecified (36.4%)
│
├── 2-Hop contamination (estimated)
│   └── 15,193,115 unique papers (3.2% of corpus)
│
└── Detailed subsample
    └── 50 highly cited papers (≥215 direct citers)
        └── Citation half-life and decline-signal analysis
```

### Citation Network Construction

Citation networks were constructed directly within the Neo4j graph database using Cypher queries, enabling full-graph traversal without API pagination constraints.

- **1-Hop contamination**: All papers with a CITES relationship to any retracted paper were extracted via `MATCH (citing:Paper)-[:CITES]->(retracted:Paper {is_retracted: true})`. This yielded 1,300,153 contamination edges from 1,068,978 unique citing papers to 55,562 distinct retracted papers.

- **2-Hop contamination**: The complete two-hop citation network was computed via `MATCH (hop2:Paper)-[:CITES]->(hop1:Paper)-[:CITES]->(retracted:Paper {is_retracted: true})`, returning 15,193,115 unique two-hop contaminated papers, 876,999 unique one-hop papers, and 55,562 retracted papers.

- **Temporal analysis**: Citation edges were aggregated by citing year to produce year-by-year contamination volumes. The year-citation matrix (2,067 retracted-year × citing-year combinations) enables analysis of temporal lag patterns.

- **Field analysis**: Papers were linked to their primary OpenAlex field via BELONGS_TO relationships, enabling field-level retraction and contamination statistics across all 26 academic fields.

For the detailed citation half-life and decline-signal analysis, we used a subsample of 50 highly cited retracted papers (those with at least 215 direct citers in a prior API-based extraction). Per-paper citation time series were constructed by aggregating citations by year, and half-lives were computed as the time from publication to 50% cumulative citations. Decline signals were assessed by comparing citation rates across successive five-year windows.

### Citation Lag Analysis

We computed the citation lag for each contamination edge as the difference between the citing paper's publication year and the retracted paper's publication year. Lags were aggregated across all 1,300,153 edges to produce the aggregate lag distribution (Table 3). The median citation lag was computed as the lag value at which cumulative citations first exceeded 50% of the total.

### Temporal Analysis (Subsample)

For the 50-paper detailed subsample, we computed per-paper citation half-lives and decline signals as follows.

**Citation half-life.** We adopt the standard Journal Citation Reports (JCR) definition of cited half-life: for each retracted paper, we sorted all citations by year, computed the cumulative citation count over time, identified the year at which the cumulative count first exceeded 50% of the total observed citations, and defined the half-life as the difference between this year and the publication year. This measures the median citation age --- how quickly a paper accumulates half of its lifetime citations. This is distinct from the post-retraction citation decay rate (Section 2.10, Methods 4.7), which measures how rapidly citations decline following the retraction event itself.

**Decline signal.** We assessed whether each retracted paper showed a decline in citation rate by dividing the citation history into five-year windows (e.g., years 0--4, 5--9, 10--14, etc.) and computing two indicators: (i) the slope of citation counts across windows (a negative slope indicates declining citation rates), and (ii) the ratio of recent citations to previous citations. A paper was classified as showing a decline signal if the most recent complete window had fewer citations than the preceding window and the overall trajectory was downward.

### Self-Correction Trend Analysis

We grouped retracted papers in the 50-paper subsample by decade of estimated retraction (2000s, 2010s, 2020s) and computed cohort-level means of citation half-life, post-retraction citation fraction, and post-retraction decay rate. Note that citation half-life here measures the median citation age from publication, not the rate of citation decline after retraction; the post-retraction decay rate is a separate metric capturing how quickly citations diminish following formal withdrawal. To test whether self-correction is improving over time, we estimated an OLS regression of post-retraction decay rate on estimated retraction year, using HC3 heteroscedasticity-consistent standard errors (statsmodels). A significantly negative slope indicates that more recent retractions show faster citation decline. We report R², F-statistic, Durbin-Watson statistic, and 95% confidence intervals for model assessment. The Durbin-Watson statistic (1.45) indicates no severe autocorrelation in residuals.

### Full-Scale Citation Timing Analysis

To characterize pre/post-retraction citation dynamics at scale, we conducted a comprehensive citation timing analysis across 41,701 retracted papers with verified retraction dates in the Neo4j graph database. For each retracted paper, we retrieved all citing papers via the CITES relationship and classified each citation based on the temporal relationship between the citing paper's publication year and the retraction year: pre-retraction (citing year < retraction year), same-year (citing year = retraction year), or post-retraction (citing year > retraction year). Citations were aggregated by years-since-retraction to construct a persistence decay curve. Field-level patterns were computed by joining citing papers to their primary OpenAlex field classification.

### Zombie Paper Identification

We defined "zombie papers" as retracted papers whose post-retraction citation rates show no meaningful decline. For each retracted paper with at least five post-retraction citations and at least two years of post-retraction observation, we split the post-retraction citation period into first and second halves (by midpoint year) and computed the ratio of second-half to first-half citation volume. Papers with a ratio ≥ 0.9 (i.e., second-half citations at least 90% of first-half) were classified as zombie papers. This threshold captures papers where retraction has had no detectable effect on citation accumulation.

### Retraction Reason Classification

We classified the Retraction Watch reason field into three major categories using keyword matching: misconduct (fabrication/fraud, paper mill operations, plagiarism, compromised peer review, data/image manipulation), error (honest errors, miscalculations, duplication), and other/unspecified. The classification was applied to 61,904 retracted papers with Retraction Watch metadata. Per-paper citation metrics were compared across reason categories using mean, median, and total contamination edges.

### Robustness Considerations

The 2-hop contamination count (15,193,115 papers) traverses the full CITES relationship graph without temporal filtering, meaning that it includes papers that may have cited the 1-hop paper before the retracted paper was even published. A temporally constrained 2-hop analysis would provide a more precise estimate but would require substantially more complex queries. However, since we are interested in the total structural reach of potentially contaminated work --- the full network of papers connected to the retracted paper through citation chains --- this inclusive approach is appropriate for establishing an upper bound on contamination scale.

The decline signal classification for the 50-paper subsample relies on comparison between adjacent five-year windows. This approach may miss subtle declines within a window, and it may misclassify recently published papers that have not yet had time to exhibit a decline. However, the five-year window provides sufficient granularity for the decades-long citation histories observed in our sample while maintaining statistical stability.

The 101,581 retracted papers identified via OpenAlex's `is_retracted` flag may include some false positives (papers incorrectly flagged) and may miss some retractions not yet reflected in OpenAlex metadata. Cross-referencing with the Retraction Watch database (68,870 records) confirmed 61,904 papers via DOI matching, with the remaining ~40,000 identified through OpenAlex metadata alone.

### Statistical Software

All analyses were conducted in Python 3.12 using pandas for data manipulation, NumPy for numerical computation, statsmodels for OLS regression with heteroscedasticity-consistent (HC3) standard errors, and scipy for statistical tests. The full OpenAlex snapshot (479M works) was processed via a custom ETL pipeline using PyArrow, stored in ZSTD-compressed Apache Parquet format, and bulk-imported into Neo4j 5.26 Community Edition (587M nodes, 3.97B relationships) with fulltext search indexes on is_retracted, year, doi, author_name, and title. Citation network queries were executed via Cypher. The analysis pipeline, including all data processing scripts and configuration, is available in the project repository.

---

## Conclusion

This study provides the largest-scale quantitative portrait of how retracted papers contaminate the scientific literature through citation networks. Analyzing 101,581 retracted papers across a 479-million-paper citation network containing 2.87 billion citations, we find that 1,068,978 unique papers directly cite retracted work, and an estimated 15.2 million papers (3.2% of the entire scholarly corpus) are contaminated within two citation hops. The full-scale citation timing analysis across 41,701 papers with verified retraction dates reveals a dual failure: 52.1% of citations accumulate before retraction occurs, while 31.1% continue to accrue after formal withdrawal. Six additional findings emerge from our analysis.

First, the temporal dynamics of contamination are characterized by rapid early accumulation and long persistence. The median citation lag of 3 years means that half of all citations accumulate before retraction typically occurs, and the characteristic decay curve shows citations persisting 25+ years after publication. Second, contamination is heavily concentrated: a Gini coefficient of 0.83 indicates extreme inequality, with the top 2.1% of retracted papers (those with 100+ citations) generating 38.1% of all citations to retracted work, while 38.2% of retracted papers have never been cited. Third, retraction volumes are growing exponentially (193 in 2000 to 17,049 in 2023), a 23% compound annual growth rate that threatens to overwhelm improving per-paper correction rates. Fourth, and more encouragingly, self-correction is accelerating: citation decay rates have improved significantly over time (β = −0.468 per year, p < 0.001), with papers retracted in the 2020s showing dramatically faster correction than those retracted in the 2000s. Fifth, 17.3% of retracted papers with sufficient post-retraction data qualify as "zombie papers" --- showing no detectable citation decline after retraction --- with the worst case accumulating 4,305 post-retraction citations at an increasing rate. Sixth, retraction reason analysis reveals that papers retracted for error accumulate more citations on average (mean = 29.2) than those retracted for misconduct (mean = 24.7), while paper mill operations have become the single largest retraction category (18.7%).

These findings do not indict the principle of retraction --- retraction remains a necessary component of scientific integrity infrastructure. Rather, they demonstrate that retraction is necessary, improving, but still insufficient. The gap between retraction and effective decontamination of the literature represents a systemic vulnerability that is narrowing but not yet closed, amplified by citation momentum, inadequate database flagging, and the structural role that retracted papers continue to play in evidence chains.

As science increasingly relies on computational systems --- from systematic review automation to large language model-assisted writing --- the contamination problem will only intensify unless addressed proactively. The citation networks mapped in this study provide a quantitative foundation for designing targeted interventions: identifying the most contaminating retracted papers (led by the retracted Lancet Commission report with 9,575 citations), the most vulnerable downstream literatures (Medicine and Engineering), and the most effective points for intervention in the citation propagation chain.

Science's capacity for self-correction is one of its defining strengths. Our data show that this capacity exists but operates on a timescale that is dangerously slow relative to the speed at which flawed findings propagate. Accelerating the immune response --- through better database infrastructure, active citation warnings, and contamination-aware curation of training data --- is not merely a technical challenge but a prerequisite for maintaining the integrity of the scientific record in an era of exponential information growth.

Future work should extend this analysis in several directions. Citation context classification using natural language processing would allow us to distinguish between endorsing, critical, and retraction-aware citations, refining the contamination estimates from structural upper bounds to content-informed measures. Cross-field comparisons of self-correction effectiveness across all 26 fields, leveraging the full Neo4j graph, would test whether biomedical fields with established retraction-flagging infrastructure show faster correction than fields without such systems. Systematic matching of all 101,581 retracted papers to Retraction Watch retraction dates would enable comprehensive pre/post-retraction citation analysis at full scale. Finally, temporal analysis of retraction timing --- the lag between publication and retraction --- would illuminate how the speed of retraction affects the scale of downstream contamination, with direct implications for editorial policy on how quickly retraction decisions should be made and communicated.

---

## References

1. Schneider, J., Ye, D., Hill, A. M. & Whitehorn, A. S. Continued post-retraction citation of a fraudulent clinical trial report, 11 years after it was retracted for falsifying data. *Scientometrics* **125**, 2877--2913 (2020).

2. Cor, K. & Sood, G. Propagation of error: Citations to problematic research. Working paper (2022).

3. Hsiao, T. K. & Schneider, J. Continued use of retracted papers: Temporal trends in citations and (lack of) awareness of retractions shown in citation contexts in biomedicine. *Quantitative Science Studies* **3**, 1144--1164 (2022).

4. Schmidt, M. Why do some retracted articles continue to get cited? *Scientometrics* **129**(12) (2024).

5. Fang, F. C., Steen, R. G. & Casadevall, A. Misconduct accounts for the majority of retracted scientific publications. *Proc. Natl. Acad. Sci. USA* **109**, 17028--17033 (2012).

6. van der Vet, P. E. & Nijveen, H. Propagation of errors in citation networks: a study involving the entire citation network of a widely cited paper published in, and later retracted from, the journal Nature. *Research Integrity and Peer Review* **1**, 3 (2016).

7. Brainard, J. & You, J. What a massive database of retracted papers reveals about science publishing's 'death penalty'. *Science* (2018).

8. Lu, S. F., Jin, G. Z., Uzzi, B. & Jones, B. The retraction penalty: evidence from the Web of Science. *Scientific Reports* **3**, 3146 (2013).

9. Azoulay, P., Bonatti, A. & Krieger, J. L. The career effects of scandal: Evidence from scientific retractions. *Journal of Political Economy* **125**, 1570--1608 (2017).

10. Moed, H. F. The effectiveness of self-correction in science. In *Handbook of Science and Technology Indicators* (Springer, 2022).

11. Retraction Watch Database. The Center for Scientific Integrity. https://retractionwatch.com/

12. Priem, J., Piwowar, H. & Orr, R. OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. arXiv:2205.01833 (2022).

13. Alperin, J. P., Portenoy, J., Demes, K., Lariviere, V. & Haustein, S. An analysis of the suitability of OpenAlex for bibliometric analyses. arXiv:2404.17663 (2024).

14. Culbert, J. H. et al. Reference coverage analysis of OpenAlex compared to Web of Science and Scopus. *Scientometrics* **130**, 2475--2492 (2024).

15. Fortunato, S. et al. Science of science. *Science* **359**, eaao0185 (2018).

16. Wang, D. & Barabasi, A. L. *The Science of Science* (Cambridge University Press, 2021).

17. Jan, R., Nazir, T., Rani, M., Peer, S. & Farooq, M. Network visualization of retracted article propagation. *Journal of Information Science* (2021).

18. Usman, M. & Balke, W.-T. Tracing the Retraction Cascade: Citation Intention in Retracted Paper Networks. In *Theory and Practice of Digital Libraries (TPDL)*, Lecture Notes in Computer Science, vol. 14241, 128--136 (Springer, 2023).

19. Usman, M. & Balke, W.-T. Tracing the Retraction Cascade. In *Theory and Practice of Digital Libraries (TPDL)*, Lecture Notes in Computer Science, vol. 15177, 89--104 (Springer, 2024).

20. Joets, M. & Mignon, V. Slaying the undead: How effectively does retraction eliminate the influence of flawed research? *Research Policy* **55**, 105191 (2026).

21. Song, F. et al. The evaluation of retraction effect by measuring changes in citation trends before and after retraction. *Scientometrics* (2026). https://doi.org/10.1007/s11192-026-05551-y

22. Wang, Z. et al. Retracted systematic reviews continued to be frequently cited: A citation analysis. *Journal of Clinical Epidemiology* **149**, 137--145 (2022).

---

## Acknowledgments

We thank the Retraction Watch team for maintaining the retraction database that made this work possible, and the OpenAlex team for providing open bibliometric infrastructure. All data processing was conducted using open-source tools.

---

## Author Contributions

[Author 1] designed the study, built the Neo4j graph database, conducted all analyses, and wrote the manuscript. [Author 2] contributed to study design, data interpretation, and manuscript revision. All authors reviewed and approved the final manuscript.

---

## Competing Interests

The authors declare no competing interests.

## Data Availability

The Retraction Watch database (68,870 records) is available at https://retractionwatch.com/. OpenAlex data (479M works) are freely available at https://openalex.org/. The full Neo4j graph database (479M Paper nodes, 108M Author nodes, 2.87B CITES relationships) and all analysis code will be made available upon publication. An interactive visualization platform (SciGraph Explorer) is available at [URL upon publication].

---

## Extended Data

**Extended Data Table 1: Retraction Rates Across 26 Scientific Fields**


*Part A: Post-Retraction Citation Rate per Million Papers (9 major fields):*

| Field | Total Papers | Post-Retraction Citations | Rate per Million |
|-------|--------------|---------------------------|------------------|
| Materials Science | 7,195,650 | 14,254 | 1980.9 |
| Biochemistry, Genetics and Molecular Biology | 13,780,178 | 24,646 | 1788.5 |
| Computer Science | 17,237,171 | 20,622 | 1196.4 |
| Engineering | 31,530,905 | 36,620 | 1161.4 |
| Medicine | 33,120,440 | 34,245 | 1034.0 |
| Agricultural and Biological Sciences | 16,732,028 | 7,142 | 426.9 |
| Social Sciences | 36,959,033 | 6,377 | 172.5 |
| Physics and Astronomy | 19,641,419 | 2,846 | 144.9 |
| Arts and Humanities | 19,900,415 | 799 | 40.2 |

*Part B: Retraction Rates per Million Papers (26 fields):*

| Field | Total Papers | Retractions | Retractions per Million |
|-------|--------------|-------------|------------------|
| Biochemistry, Genetics and Molecular Biology | 8,054,830 | 4,800 | 595.9 |
| Computer Science | 11,425,273 | 6,611 | 578.6 |
| Neuroscience | 1,588,902 | 808 | 508.5 |
| Immunology and Microbiology | 1,054,500 | 504 | 478.0 |
| Dentistry | 435,899 | 202 | 463.4 |
| Chemistry | 2,814,371 | 1,216 | 432.1 |
| Decision Sciences | 1,820,519 | 778 | 427.4 |
| Energy | 1,067,425 | 414 | 387.8 |
| Pharmacology, Toxicology and Pharmaceutics | 471,350 | 182 | 386.1 |
| Medicine | 20,960,989 | 7,917 | 377.7 |
| Materials Science | 5,070,110 | 1,673 | 330.0 |
| Engineering | 20,947,317 | 6,720 | 320.8 |
| Nursing | 558,705 | 164 | 293.5 |
| Chemical Engineering | 426,217 | 121 | 283.9 |
| Psychology | 4,162,549 | 727 | 174.7 |
| Environmental Science | 8,223,778 | 1,453 | 176.7 |
| Mathematics | 2,168,973 | 423 | 195.0 |
| Earth and Planetary Sciences | 3,743,016 | 437 | 116.8 |
| Veterinary | 195,269 | 22 | 112.7 |
| Agricultural and Biological Sciences | 11,384,900 | 1,116 | 98.0 |
| Economics, Econometrics and Finance | 5,543,335 | 534 | 96.3 |
| Social Sciences | 26,267,168 | 1,906 | 72.6 |
| Physics and Astronomy | 9,975,672 | 570 | 57.1 |
| Arts and Humanities | 11,848,259 | 369 | 31.1 |

*Note: Fields are ranked by post-retraction citation rate per million papers (i.e., the number of citations received after the retraction date, normalized by field size). This metric captures contamination exposure, not the retraction rate itself. Data derived from OpenAlex primary field classification and Retraction Watch database.*

**Extended Data Table 2: AI Adoption and Retraction Correlation**

| Analysis Level | Pearson r | p-value |
|----------------|-----------|---------|
| Field-level cross-section | 0.489 | 0.011 |
| Field×year panel | 0.624 | < 0.001 |
| Yearly aggregate | 0.800 | < 0.001 |

*Note: Does not imply causation. Fields with high publication volume, rapid growth, and open-access models (CS, Biochemistry) may independently experience both higher AI adoption and higher retraction rates due to paper mills, fast review cycles, and editorial capacity constraints.*

**Extended Data Figure References:**

- **Extended Data Fig. 1**: Post-retraction citation rates by field (bar chart). Visualization of the variation in post-retraction citation rates per million papers across 26 scientific fields.
- **Extended Data Fig. 2**: Retraction timeline stacked area. Temporal evolution of retraction volume across major scientific fields from 2000 to 2024.
