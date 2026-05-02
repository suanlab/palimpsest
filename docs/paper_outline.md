# Paper Outline & Research Framework
# 논문 구조 설계 및 연구 로드맵

> **프로젝트**: Science of Science — 과학의 과학
> **작성일**: 2025-02-14
> **상태**: Outline / Pre-writing
> **데이터 기반**: OpenAlex, Retraction Watch

---

## Table of Contents

1. [Title Options](#1-title-options)
2. [Abstract Templates](#2-abstract-templates)
3. [Track 1: AI의 불균등 침투](#3-track-1-ai의-불균등-침투)
4. [Track 3: 철회 논문의 지식 오염](#4-track-3-철회-논문의-지식-오염)
5. [Combined Paper Option](#5-combined-paper-option)
6. [Related Work — Shared Literature Foundation](#6-related-work--shared-literature-foundation)
7. [Data and Methods](#7-data-and-methods)
8. [Results Structure](#8-results-structure)
9. [Discussion Framework](#9-discussion-framework)
10. [Target Venues](#10-target-venues)
11. [Timeline](#11-timeline)
12. [Key References](#12-key-references)

---

## 1. Title Options

### Track 1: AI Adoption Across Science

| # | Title | 비고 |
|---|-------|------|
| T1-A | **"Oil or Water? The Uneven Penetration of AI Across Scientific Disciplines, 2000–2024"** | Duede et al. (2024)와의 대화를 명시적으로 설정; 25년 시계열이 차별점 |
| T1-B | **"The Great Divergence: Heterogeneous AI Adoption and Its Consequences for Scientific Production"** | 경제사 메타포 활용; 'consequences'가 DID 분석을 암시 |
| T1-C | **"Who Adopts AI and Why? A 25-Year Panel Analysis of Artificial Intelligence Diffusion Across 15 Scientific Fields"** | 가장 기술적/구체적; panel data 강조 |
| T1-D | **"From Niche to Norm? Mapping the Disciplinary Landscape of AI in Science"** | 짧고 캐치한 제목; Nature 스타일 |

### Track 3: Retracted Paper Contamination

| # | Title | 비고 |
|---|-------|------|
| T3-A | **"Knowledge Contamination: How Retracted Papers Propagate Through Citation Networks"** | 직관적이고 강렬한 메타포 |
| T3-B | **"The Half-Life of Bad Science: Citation Persistence and Knowledge Contamination After Retraction"** | 'half-life' 메타포가 temporal decay를 암시 |
| T3-C | **"How Deep Does the Rot Go? Tracing the Multi-Generational Impact of Retracted Research"** | 도발적; Nature/Science 스타일 |
| T3-D | **"Self-Correction Under the Microscope: A Large-Scale Analysis of Retraction Propagation in Science"** | 가장 중립적/학술적 |

### Combined Paper (두 Track을 하나로)

| # | Title | 비고 |
|---|-------|------|
| C-A | **"The Health of Science: AI Adoption, Knowledge Contamination, and the Evolving Landscape of Scientific Production"** | 포괄적이지만 두 주제의 연결 근거가 명확해야 함 |
| C-B | **"Disruption and Contamination: Two Challenges to the Scientific Ecosystem"** | 짧지만 연결 논리가 약할 수 있음 |

> **내부 판단**: 두 트랙은 별도 논문이 훨씬 강함. Combined option은 "science of science의 computational 도구를 이용한 과학 생태계 진단"이라는 프레이밍이 필요하나, 각 트랙의 contribution이 희석될 위험이 있음. **추천: 별도 2편**.

---

## 2. Abstract Templates

### Track 1 Abstract (~300 words)

```
[CONTEXT] The integration of artificial intelligence into scientific research is widely
celebrated as transformative, yet the extent and pattern of AI adoption across
disciplines remains poorly understood.

[GAP] While recent work has documented the overall growth of AI-engaged publications
(Duede et al., 2024), no study has systematically quantified cross-disciplinary
adoption rates over a multi-decade period or examined what field-level characteristics
predict adoption speed and depth.

[METHOD] Using OpenAlex data covering {X million} publications across 15 scientific
fields from 2000 to 2024, we construct field-year panel data on AI adoption rates
and apply a difference-in-differences framework to estimate the causal effect of
AI adoption on scientific productivity and impact.

[KEY RESULTS] We find dramatic heterogeneity: Computer Science reaches {35%} AI
fraction by 2024, while Biology exhibits the fastest growth trajectory ({3.5×}
increase from 6.5% to 23.2%, 2010–2024). In contrast, Medicine ({4.75%}),
Psychology ({~10%}), and Economics ({~10%}) show strikingly low or flat adoption
despite large publication volumes. [DID 분석 결과 placeholder: AI 채택이 높은
분야에서 논문 영향력/생산성에 미치는 효과 기술]

[SIGNIFICANCE] These findings reveal that AI diffusion in science follows a
pattern more akin to uneven technological adoption than universal transformation,
with implications for science policy, funding allocation, and the future structure
of interdisciplinary research.
```

### Track 3 Abstract (~300 words)

```
[CONTEXT] Retraction is the most severe correction mechanism in science, yet
retracted papers continue to be cited long after retraction, raising concerns
about knowledge contamination in the scientific record.

[GAP] Prior studies have examined post-retraction citation counts, but the
multi-generational propagation of retracted claims through indirect citation
chains—and the effectiveness of science's self-correction mechanism at each
generation—remains largely uncharacterized.

[METHOD] Using Retraction Watch data linked to OpenAlex citation networks, we
trace the propagation of {491} retracted papers through {16,842} direct citers
and their downstream citation chains using breadth-first search. We develop a
contamination score that quantifies the depth and breadth of knowledge pollution
at each generation.

[KEY RESULTS] [Placeholder: 주요 발견 기술 — e.g., X% of direct citers cite
the retracted paper positively post-retraction; contamination persists to
generation N; the half-life of contaminated citations is Y years; field Z
shows the strongest/weakest self-correction]

[SIGNIFICANCE] Our large-scale network analysis provides the first systematic
measurement of how deep retracted knowledge penetrates the scientific literature,
offering actionable insights for publishers, databases, and the design of
early-warning systems for knowledge contamination.
```

---

## 3. Track 1: AI의 불균등 침투

### 3.1 Introduction (~1,500 words / 3 pages)

#### Opening Hook (1 paragraph)
- 시작점: "AI가 과학을 변화시키고 있다"는 narrative의 보편성 vs. 실제 데이터의 불균등성 대비
- 구체적 수치로 시작: "By 2024, 35% of all Computer Science publications engage with AI methods, while in Medicine—arguably the field with the most to gain—the figure is just 4.75%."
- 왜 이것이 문제인가: 과학정책, 연구비 배분, 학제간 격차

#### Literature Context (2-3 paragraphs)
- Science of science의 프레임워크 (Fortunato et al., 2018; Wang & Barabási, 2021)
- 기술 확산 이론: S-curve diffusion models (Rogers, 1962), General Purpose Technology (GPT) theory
- AI in science 기존 연구:
  - Duede et al. (2024): AI-engaged publications across 20 fields, "oil and water" 현상 발견 — 가장 직접적인 선행연구
  - Ding, Lawson & Shapira (2024): Generative AI 확산 분석
  - Frank et al. (2019): AI's labor market impact 프레임 차용 가능
- 기존 연구의 한계: (1) 시계열이 짧음, (2) 채택률의 원인 분석 부재, (3) 생산성/영향력과의 인과관계 미분석

#### Gap Identification (1 paragraph)
- **Gap 1**: 25년 장기 시계열로 S-curve 전체를 포착한 연구 없음
- **Gap 2**: 분야별 특성(수리적 전통, 데이터 가용성, 실험 문화)이 AI 채택 속도를 설명하는지 분석한 연구 없음
- **Gap 3**: AI 채택이 분야 내 과학적 생산(논문 수, 인용, disruption)에 미치는 인과적 효과를 추정한 연구 없음

#### Research Questions (formal)

> **RQ1**: How has AI/ML adoption varied across 15 scientific fields between 2000 and 2024, and what temporal patterns (linear, exponential, S-curve, plateau) characterize adoption in each field?
>
> **RQ2**: What field-level characteristics (mathematical maturity, data availability, experimental vs. theoretical orientation, field size) predict the speed and ceiling of AI adoption?
>
> **RQ3**: Does increased AI adoption cause measurable changes in a field's scientific productivity and impact, as measured by publication volume, citation rates, and the disruption index?

#### Hypotheses (testable)

| ID | Hypothesis | Rationale |
|----|-----------|-----------|
| H1 | Fields with stronger quantitative/mathematical traditions adopt AI faster | 수리적 인프라가 ML 도구 활용을 용이하게 함 |
| H2 | AI adoption follows an S-curve in most fields, with inflection points varying by 5-10 years across disciplines | 기술 확산 이론의 예측 |
| H3 | Biology's rapid AI growth (3.5×) is driven by structural biology and genomics subfields, not uniformly distributed | AlphaFold (2020) 등 breakout moment가 특정 하위분야에 집중 |
| H4 | Medicine's low adoption reflects regulatory barriers and clinical validation requirements, not lack of data | 의학 고유의 구조적 제약 |
| H5 | AI adoption increases publication volume but has ambiguous effects on disruption index | Park et al. (2023)의 disruption decline과 연결 |

#### Contributions (bullet list)

1. **Data contribution**: 15 fields × 25 years의 AI 채택률 패널 데이터 구축 (OpenAlex 기반, 재현 가능)
2. **Descriptive contribution**: 분야별 AI 확산 궤적의 유형 분류 (taxonomy of adoption patterns)
3. **Explanatory contribution**: 분야 특성과 채택 속도의 관계를 정량적으로 분석
4. **Causal contribution**: DID 프레임워크를 통한 AI 채택 → 과학적 생산 영향의 인과 추정

### 3.2 Related Work (~1,000 words / 2 pages)

#### 3.2.1 Science of Science and Scientometrics
- Fortunato et al. (2018): SciSci의 종합 리뷰 — 본 연구의 학문적 위치 설정
- de Solla Price (1963): 과학 성장의 정량적 분석의 원형
- Wuchty, Jones & Uzzi (2007): 팀 사이즈 증가와 과학 생산
- Wu, Wang & Evans (2019): 소규모 팀의 disruptive 연구

#### 3.2.2 Technology Diffusion and General Purpose Technologies
- Rogers (1962): Diffusion of Innovations — S-curve 이론
- Bresnahan & Trajtenberg (1995): General Purpose Technologies 개념
- Cockburn, Henderson & Stern (2018): AI as a GPT — AI가 과학 방법론의 GPT라는 주장

#### 3.2.3 AI in Scientific Research
- Duede, Dolan, Bauer, Foster & Lakhani (2024): 가장 직접적 선행연구; 20개 분야, 1985-2022, 13× 성장, "oil and water" 현상
  - **본 연구와의 차이**: (1) 2024까지 확장, (2) adoption rate 정량화 (not just counts), (3) 인과 분석 추가
- Ding, Lawson & Shapira (2024): Generative AI 확산; 본 연구는 전체 AI/ML을 포괄
- Bianchini, Di Girolamo, Ravet & Arranz (2025): EC 보고서, AI in science의 창의성 영향
- Zhang et al. (2021): AI Index Report — 연도별 AI 연구 현황 통계

#### 3.2.4 Disruption in Science
- Funk & Owen-Smith (2017): CD index 제안 (원 논문)
- Park, Leahey & Funk (2023): Nature 논문, disruption 감소 추세 — 본 연구의 H5와 직접 연결
- Bornmann & Tekles (2019): CD index의 방법론적 논의

### 3.3 Data & Methods (Track 1) (~1,500 words / 3 pages)

#### 3.3.1 Data Source: OpenAlex
- OpenAlex 개요: 250M+ scholarly works, open, Priem et al. (2022)
- OpenAlex 타당성: Alperin et al. (2024), Culbert et al. (2024)의 coverage 분석 참조
- 데이터 수집 기간: 2000-2024 (25년)

#### 3.3.2 Field Classification
- 15 fields 목록 및 OpenAlex concept mapping:
  - **STEM core**: Computer Science, Mathematics, Physics, Chemistry, Engineering
  - **Life sciences**: Biology, Medicine, Neuroscience
  - **Social/behavioral**: Psychology, Economics, Sociology, Political Science
  - **Other**: Environmental Science, Materials Science, Earth Science
- Concept hierarchy 사용 (Level 0/1 concepts)
- 한 논문이 복수 분야에 속할 수 있음 → 처리 방법 명시

#### 3.3.3 AI/ML Paper Identification
- **Operational definition**: OpenAlex concepts에서 "Artificial intelligence", "Machine learning", "Deep learning", "Neural network" 등 AI 관련 concept이 태깅된 논문
- Concept score threshold 설정 (e.g., ≥ 0.3)
- Validation: 수작업 샘플 검증 (precision/recall 보고)
- group_by API를 활용한 집계

#### 3.3.4 Variables

| Variable | Type | Definition | Source |
|----------|------|-----------|--------|
| `ai_fraction_{field,year}` | DV/IV | AI-tagged 논문 수 / 전체 논문 수 | OpenAlex |
| `pub_count_{field,year}` | DV | 해당 분야-연도의 총 논문 수 | OpenAlex |
| `mean_citations_{field,year}` | DV | 평균 피인용 수 (normalized) | OpenAlex |
| `mean_disruption_{field,year}` | DV | 평균 CD5 index | Computed |
| `math_intensity_{field}` | Control | 분야의 수리적 전통 지표 | Derived |
| `data_availability_{field}` | Control | 공개 데이터셋 가용성 지표 | Derived |
| `field_size_{field,year}` | Control | 활동 연구자 수 | OpenAlex |

#### 3.3.5 Statistical Methods

**Descriptive analysis:**
- 분야별 AI adoption time series 시각화
- S-curve fitting (logistic growth model): `y(t) = K / (1 + exp(-r(t - t₀)))`
- 분야 간 adoption trajectory 유형 분류 (clustering)

**Causal analysis — Difference-in-Differences (DID):**
- Treatment: AI adoption의 급격한 증가 (분야별로 시점이 다름)
- Outcome: 생산성 지표, 인용 지표, disruption index
- 핵심 가정: Parallel trends (pre-treatment)
- Robustness: Staggered DID (Callaway & Sant'Anna, 2021)
  - 분야마다 treatment timing이 다르므로 classical two-way FE의 bias 회피

**Panel regression:**
- `Y_{ft} = α_f + γ_t + β · AI_fraction_{ft} + X_{ft}′δ + ε_{ft}`
- Fixed effects: field, year
- Clustering: field level

#### 3.3.6 Limitations & Threats to Validity
- **Construct validity**: OpenAlex concept tagging의 정확성 (false positives/negatives)
- **Internal validity**: AI 채택은 endogenous — field-level shocks가 동시에 생산성에 영향
- **External validity**: OpenAlex coverage bias (영어 중심, 특정 분야 편중 가능)
- **Measurement**: Disruption index 자체의 한계 (Park et al. 2023에 대한 비판 문헌)

### 3.4 Results Structure (Track 1) (~2,500 words / 5 pages)

#### Section 4.1: Descriptive Landscape of AI Adoption

**Table 1**: Summary statistics by field (2024 기준)
- Columns: Field | Total papers (2024) | AI papers (2024) | AI fraction (%) | Growth rate (2010-2024) | Inflection year

**Figure 1**: 15개 분야의 AI adoption rate time series (2000-2024)
- Spaghetti plot with highlighted groups (fast adopters, moderate, flat)
- 핵심 발견: CS (35%), Biology (23.2%), Medicine (4.75%), Psychology (~10%)

**Figure 2**: Adoption trajectories clustered into types
- Type A (Exponential/early saturation): Computer Science, Mathematics
- Type B (Accelerating/S-curve mid-phase): Biology, Neuroscience, Materials Science
- Type C (Linear/slow): Physics, Chemistry, Engineering
- Type D (Flat/resistant): Medicine, Psychology, Economics, Sociology, Political Science

#### Section 4.2: What Predicts Adoption Speed?

**Table 2**: Regression of adoption growth rate on field characteristics
- Math intensity, data availability, field size, experimental orientation

**Figure 3**: Scatter plot — math intensity vs. AI adoption ceiling

**핵심 발견**: (예상)
- 수리적 전통이 강한 분야일수록 빠른 채택
- 데이터 가용성은 예상보다 약한 predictor (Medicine은 데이터 풍부하지만 채택 낮음)
- 규제/임상 요구사항이 Medicine의 낮은 채택을 설명

#### Section 4.3: The Biology Surge — A Closer Look

**Figure 4**: Biology 내 하위분야별 AI adoption (Genomics, Structural Biology, Ecology, etc.)
- AlphaFold moment (2020) 전후 비교
- H3 검증: 하위분야 간 이질성 분석

#### Section 4.4: AI Adoption and Scientific Production (DID)

**Table 3**: DID estimates — AI adoption → publication volume
**Table 4**: DID estimates — AI adoption → citation impact
**Table 5**: DID estimates — AI adoption → disruption index

**Figure 5**: Event study plot — treatment 전후 outcome trajectory
- Parallel trends 검증 포함

**핵심 발견 (placeholder)**:
- AI 채택 ↑ → 논문 수 ↑ (likely positive)
- AI 채택 ↑ → 인용 ? (ambiguous)
- AI 채택 ↑ → disruption ↓ ? (Park et al.과 일관?)

#### Section 4.5: Robustness Checks
- Alternative AI concept thresholds
- Staggered DID vs. classical two-way FE 비교
- Leave-one-field-out sensitivity
- Alternative disruption metrics (DI1, DI5, DEP)

---

## 4. Track 3: 철회 논문의 지식 오염

### 4.1 Introduction (~1,500 words / 3 pages)

#### Opening Hook (1 paragraph)
- 시작점: 구체적 사례 — "In 1998, Andrew Wakefield published a paper in *The Lancet* linking the MMR vaccine to autism. The paper was retracted in 2010, but by then it had been cited over 900 times, and its claims had permeated public discourse, policy debates, and downstream research."
- Broader question: 과학의 자기교정 메커니즘은 얼마나 효과적인가?
- Scale: 매년 수천 건의 논문이 철회되지만, 그 영향의 전파 범위는 체계적으로 연구되지 않았음

#### Literature Context (2-3 paragraphs)
- 철회 연구의 기존 문헌: post-retraction citation이 지속된다는 발견 (Cor & Sood, 2022; Schneider et al., 2020; Hsiao & Schneider, 2022)
- Citation network을 통한 error propagation: van der Vet & Nijveen (2016)의 사례 연구 — 단일 논문의 전체 citation network 추적
- Self-correction: Moed (2022)의 retraction의 효과 분석
- 한계: (1) 대부분 사례 연구 또는 소규모, (2) 간접 인용의 전파 미측정, (3) 분야별 self-correction 능력 비교 없음

#### Gap Identification (1 paragraph)
- **Gap 1**: 수백 건 규모의 체계적 multi-generation propagation 분석 없음
- **Gap 2**: "contamination score"와 같은 정량적 오염 측정 도구 부재
- **Gap 3**: 분야 간 self-correction 속도와 효과의 비교 연구 없음

#### Research Questions (formal)

> **RQ1**: How far does the influence of retracted papers propagate through citation chains (direct citers → citers of citers → ...)?
>
> **RQ2**: What is the temporal decay pattern of contaminated citations, and what is the "half-life" of knowledge contamination?
>
> **RQ3**: How do contamination patterns vary across scientific fields, and what field-level factors predict more effective self-correction?
>
> **RQ4**: What proportion of citing papers acknowledge the retraction, and does this proportion change with citation generation?

#### Hypotheses

| ID | Hypothesis | Rationale |
|----|-----------|-----------|
| H1 | >50% of direct citers post-retraction do not acknowledge the retraction | Cor & Sood (2022)의 91% 무인지 발견 기반 |
| H2 | Contamination depth reaches at least 3 generations (citing → citing → citing) | Error propagation은 citation chain을 따라 전파 |
| H3 | Contamination decays exponentially with generation, with a half-life of 2-3 generations | Indirect citation의 내용 희석 |
| H4 | Biomedical fields show stronger self-correction (faster decay) than social sciences | 생의학의 reproducibility 문화와 PubMed의 retraction 표시 시스템 |
| H5 | High-profile retractions (more media coverage) show faster contamination decay | 가시성이 자기교정을 촉진 |

#### Contributions

1. **Scale**: 491 retracted papers × multi-generational citation network의 체계적 분석 (기존 최대 규모)
2. **Method**: Contamination score — 인용 세대, 인용 맥락, 시간을 통합하는 새로운 지표 제안
3. **Empirical**: 분야별 self-correction 속도의 최초 비교 분석
4. **Policy**: 학술 데이터베이스와 출판사를 위한 오염 조기 경보 시스템 설계 함의

### 4.2 Related Work (~1,000 words / 2 pages)

#### 4.2.1 Retractions in Science
- Fang, Steen & Casadevall (2012): PNAS, 2,047 retracted papers 분석, 67% misconduct
- Brainard & You (2018): Science, retraction 증가 추세 보고
- Retraction Watch database: 가장 포괄적인 retraction 데이터 (Oransky & Marcus)

#### 4.2.2 Post-Retraction Citation
- Cor & Sood (2022): 3,000+ retracted papers, 74,000+ citations; 31% post-retraction, 91% no acknowledgment
- Schneider, Ye, Hill & Whitehorn (2020): 단일 사례의 11년 추적; post-retraction citation 지속
- Hsiao & Schneider (2022): Quantitative Science Studies; biomedicine에서의 temporal trend
- Schmidt (2024): Scientometrics; 왜 일부 철회 논문이 계속 인용되는가

#### 4.2.3 Error Propagation in Networks
- van der Vet & Nijveen (2016): 단일 Nature 논문의 전체 citation network; 직접 인용은 전파하지만 간접 인용은 전파하지 않는다는 발견
  - **본 연구와의 차이**: 단일 사례 vs. 491건의 체계적 분석
- Jan, Nazir, Rani, Peer & Farooq (2021): Network visualization of retracted article propagation

#### 4.2.4 Scientific Self-Correction
- Lu, Jin, Uzzi & Jones (2013): 철회 후 인용 감소 패턴 분석
- Moed (2022): Self-correction mechanism의 효과성 평가
- Azoulay, Bonatti & Krieger (2017): Retraction이 관련 분야 연구자에 미치는 영향 (spillover)

### 4.3 Data & Methods (Track 3) (~1,500 words / 3 pages)

#### 4.3.1 Data Sources

**Retraction Watch Database:**
- 491 retracted papers 선정 기준:
  - 철회 시점: 2005-2020 (post-retraction citation 관찰 기간 확보)
  - 최소 인용 수 요건 (propagation 분석을 위해)
  - 다양한 분야 포함
- 메타데이터: 철회 사유, 철회 날짜, 원 출판 날짜

**OpenAlex Citation Network:**
- 16,842 direct citers (Generation 1)
- 23,938 references of retracted papers
- Generation 2+ citers: BFS로 수집 (depth limit 설정)

#### 4.3.2 Citation Network Construction

```
Retracted Paper (Gen 0)
    ├── Direct Citers (Gen 1): 16,842 papers
    │   ├── Citers of citers (Gen 2): ~X papers
    │   │   └── Gen 3: ~Y papers
    │   └── ...
    └── References (backward): 23,938 papers
```

- BFS (Breadth-First Search) propagation
- Depth limit: 3-4 generations (computational feasibility)
- Time window: Gen 0 publication year ~ 2024

#### 4.3.3 Contamination Score

**Definition**: 각 citing paper에 대해 retracted content에 의한 "오염 정도"를 정량화

```
ContaminationScore(paper_i) = f(generation, citation_context, time_since_retraction)
```

**Components:**
1. **Generation weight**: `w_gen = 1/g` (g = generation distance) — 세대가 멀수록 감쇠
2. **Temporal weight**: `w_time = exp(-λ · Δt)` (Δt = years since retraction) — 시간이 지날수록 감쇠
3. **Context weight**: 인용 맥락 분류
   - Positive/supportive citation (오염 기여)
   - Negative/critical citation (자기교정 기여)
   - Neutral/methodological citation (부분 오염)
   - Retraction-aware citation (자기교정 완료)

**Aggregate field-level contamination:**
```
FieldContamination(f) = Σ ContaminationScore(paper_i) for all papers in field f
```

#### 4.3.4 Self-Correction Metrics

| Metric | Definition |
|--------|-----------|
| **Retraction awareness rate** | Post-retraction 인용 중 retraction을 언급하는 비율 |
| **Citation decay rate** | 철회 후 연간 인용 감소율 |
| **Contamination half-life** | Contamination score가 50% 감소하는데 걸리는 시간 |
| **Self-correction index** | (Retraction-aware citations) / (Total post-retraction citations) |

#### 4.3.5 Analytical Approach

1. **Descriptive**: 오염 규모 매핑 — 총 세대별 citing papers 수, post-retraction citation 비율
2. **Temporal analysis**: 철회 시점 전후의 citation trajectory (event study)
3. **Cross-field comparison**: 분야별 self-correction index 비교
4. **Regression**: 어떤 요인이 self-correction을 예측하는가
   - Journal impact factor of retracted paper
   - Retraction reason (fraud vs. honest error)
   - Media attention
   - Field characteristics

#### 4.3.6 Limitations & Threats to Validity
- **Citation context classification**: 자동 분류의 정확도 한계 (NLP 기반 vs. 수작업)
- **Coverage**: Retraction Watch의 completeness; OpenAlex의 citation coverage
- **Selection bias**: 분석 대상 491건이 전체 retraction을 대표하는가
- **Indirect propagation measurement**: Gen 2+ 인용이 실제로 retracted content를 참조하는지 확인 어려움

### 4.4 Results Structure (Track 3) (~2,500 words / 5 pages)

#### Section 4.1: The Scale of Knowledge Contamination

**Table 1**: Descriptive statistics
- 491 retracted papers의 분야별 분포
- Gen 1 citers: 16,842 (median per retracted paper: X)
- Gen 2 citers: Y
- Post-retraction citation rate: Z%

**Figure 1**: Distribution of post-retraction citations per retracted paper (histogram)
- Long-tailed distribution 예상 — 소수의 retracted papers가 대다수의 post-retraction citations을 축적

**Figure 2**: Citation network visualization (대표 사례 2-3건)
- Node color: generation, Edge thickness: citation count
- 시각적으로 오염 전파 범위를 보여줌

#### Section 4.2: Temporal Patterns

**Figure 3**: Event study — 철회 시점 전후 연간 citation trajectory
- Average across 491 papers ± confidence interval
- Pre-retraction growth → retraction shock → post-retraction persistence

**Figure 4**: Contamination half-life distribution
- 분야별 half-life 비교 boxplot

**핵심 발견 (placeholder)**:
- 철회 후 citation 감소는 있으나 완전히 사라지지 않음
- Half-life는 X년으로, 상당 기간 오염 지속

#### Section 4.3: Severity Ranking — Which Retractions Contaminate Most?

**Table 2**: Top 20 most contaminating retracted papers
- Columns: Paper | Field | Retraction year | Reason | Direct citers | Contamination score

**Figure 5**: Contamination score by retraction reason (fraud vs. error vs. duplication)
- 학술 사기로 인한 철회가 더 높은 오염?

#### Section 4.4: Field-Level Self-Correction

**Table 3**: Self-correction metrics by field
- Columns: Field | Retraction awareness rate | Citation decay rate | Contamination half-life | Self-correction index

**Figure 6**: Self-correction index by field (bar chart with CI)

**핵심 발견 (placeholder)**:
- 생의학 분야가 다른 분야보다 빠른 자기교정? (H4 검증)
- PubMed의 retraction flagging이 기여?

#### Section 4.5: What Predicts Effective Self-Correction?

**Table 4**: Regression — self-correction index predictors
- Journal IF, retraction reason, media attention, field, time since retraction

---

## 5. Combined Paper Option

> **내부 판단**: 별도 논문 2편을 강력 추천하나, 만약 합치는 경우의 프레이밍:

### Unifying Frame: "과학 생태계의 건강 진단"

- AI 채택 = 과학이 새로운 도구를 흡수하는 능력 (growth/adaptation)
- 철회 오염 = 과학이 오류를 제거하는 능력 (immune system/self-correction)
- 두 가지를 종합하면: **과학의 적응력과 자정력을 동시에 측정**

### Combined Structure

1. Introduction: 과학 생태계의 이중 도전
2. Study 1: AI adoption (Track 1, 축약)
3. Study 2: Retraction contamination (Track 3, 축약)
4. Synthesis: 두 현상의 교차점
   - AI를 빠르게 채택하는 분야가 자기교정도 빠른가?
   - 또는 AI 과잉 생산이 오히려 quality control을 약화시키는가?
5. Discussion: 과학 정책 함의

### Risks of Combining
- 두 contribution이 모두 약해질 수 있음
- Reviewer가 "왜 이 두 주제가 한 논문에?" 라고 의문
- 분량 제한 (Nature은 ~3,500 words main text)

---

## 6. Related Work — Shared Literature Foundation

### 6.1 Science of Science (SciSci)

| Paper | Key Contribution | 활용 |
|-------|-----------------|------|
| Fortunato et al. (2018), *Science* | SciSci의 종합 리뷰: collaboration networks, citation dynamics, career trajectories | 두 Track 모두의 학문적 위치 설정 |
| de Solla Price (1963), *Little Science, Big Science* | 과학 성장의 정량적 분석의 원형; exponential growth of publications | Track 1의 이론적 기반 |
| Wang & Barabási (2021), *The Science of Science* | SciSci 교과서: 발견의 과학, 경력 역학, 팀 과학 | 두 Track 모두의 프레이밍 |

### 6.2 AI and Technology in Science

| Paper | Key Contribution | 활용 |
|-------|-----------------|------|
| Duede et al. (2024), arXiv | 20개 분야에서 AI 확산의 "oil and water" 현상; 80M publications | Track 1의 가장 직접적 선행연구 |
| Ding, Lawson & Shapira (2024), arXiv | Generative AI의 과학 내 확산 프로파일링 | Track 1 context |
| Cockburn, Henderson & Stern (2018), *NBER* | AI as a "method of invention" — GPT 프레임 | Track 1 이론적 기반 |

### 6.3 Disruption and Innovation

| Paper | Key Contribution | 활용 |
|-------|-----------------|------|
| Funk & Owen-Smith (2017), *Management Science* | CD index (Consolidation-Disruption index) 최초 제안 | Track 1 방법론 |
| Park, Leahey & Funk (2023), *Nature* | 45M papers/3.9M patents에서 disruption 감소 추세 발견 | Track 1의 H5 검증 |
| Wu, Wang & Evans (2019), *Nature* | 소규모 팀은 disruptive, 대규모 팀은 consolidating | Track 1 context |

### 6.4 Retractions and Self-Correction

| Paper | Key Contribution | 활용 |
|-------|-----------------|------|
| Fang, Steen & Casadevall (2012), *PNAS* | 2,047 retracted papers; 67% misconduct | Track 3 background |
| Cor & Sood (2022), working paper | 3,000+ retracted, 74K+ citations; 31% post-retraction, 91% no acknowledgment | Track 3의 핵심 선행연구 |
| van der Vet & Nijveen (2016), *Res Integrity Peer Rev* | 단일 Nature 논문의 전체 citation network 추적; 간접 인용은 전파 안함 | Track 3 방법론 대화 |
| Schneider, Ye, Hill & Whitehorn (2020), *Scientometrics* | 단일 사례의 11년 추적 | Track 3 context |
| Hsiao & Schneider (2022), *Quantitative Science Studies* | Biomedicine에서 post-retraction citation의 temporal trend | Track 3 직접 선행 |
| Azoulay, Bonatti & Krieger (2017), *JPE* | Retraction이 coauthors와 관련 연구자에 미치는 spillover 효과 | Track 3 broader impact |

### 6.5 Bibliometric Data Sources

| Paper | Key Contribution | 활용 |
|-------|-----------------|------|
| Priem, Piwowar & Orr (2022) | OpenAlex 소개 논문 | 두 Track의 데이터 소스 정당화 |
| Alperin, Portenoy, Demes, Larivière & Haustein (2024), arXiv | OpenAlex의 bibliometric 분석 적합성 평가 | 데이터 품질 논의 |
| Culbert et al. (2024), *Scientometrics* | OpenAlex vs. WoS vs. Scopus reference coverage | 데이터 품질 논의 |

---

## 7. Data and Methods — Shared Infrastructure

### 7.1 OpenAlex as Primary Data Source

두 Track 모두 OpenAlex를 primary data source로 사용:

**장점:**
- Open, free, comprehensive (250M+ works)
- Structured API with concept tagging
- DOI-based linking with Retraction Watch
- Citation network data 내장
- 재현성 확보

**한계 및 대응:**
- Coverage gap (특히 non-English, 사회과학): Scopus/WoS와 비교 검증
- Concept tagging accuracy: 수작업 validation sample
- Citation completeness: Culbert et al. (2024)의 결과 참조

### 7.2 Computational Infrastructure

```
data pipeline:
  OpenAlex API → raw JSON → Pydantic validation → pandas DataFrame → Parquet
  Retraction Watch DB → DOI matching → merged dataset

analysis:
  Track 1: panel data → statsmodels (DID, FE regression)
  Track 3: networkx (BFS, graph metrics) → contamination scoring
  
reproducibility:
  - All code in src/research/
  - Configuration via pydantic-settings
  - Cached API responses in data/raw/
```

---

## 8. Results Structure — Summary

### Track 1 결과 흐름 (논리적 순서)

```
① 무엇이 일어나고 있는가?   → Descriptive: 15개 분야의 AI adoption landscape
② 어떤 패턴인가?           → Trajectory classification: S-curve, linear, flat
③ 왜 다른가?               → Predictors: field characteristics → adoption speed
④ 특이 사례 심층 분석       → Biology surge (AlphaFold effect)
⑤ 그래서 무슨 의미인가?    → Causal: AI adoption → scientific production (DID)
⑥ 결과가 견고한가?         → Robustness checks
```

### Track 3 결과 흐름 (논리적 순서)

```
① 얼마나 큰 문제인가?      → Scale: 오염 규모 매핑
② 시간에 따라 어떻게 변하나? → Temporal: citation trajectory, half-life
③ 어떤 철회가 가장 해로운가? → Severity: contamination ranking
④ 분야별로 다른가?          → Cross-field: self-correction comparison
⑤ 무엇이 자기교정을 돕는가? → Predictors: regression on self-correction
```

---

## 9. Discussion Framework

### Track 1 Discussion (~1,000 words / 2 pages)

#### 9.1.1 Key Findings Interpretation
- AI 확산은 "universal transformation"이 아니라 "uneven penetration"
- Duede et al. (2024)의 "oil and water"와 본 연구의 "uneven penetration"은 보완적 발견
- Biology의 급성장은 특정 breakthrough (AlphaFold)에 의한 것인가, 구조적 변화인가?
- Medicine의 낮은 채택은 실패인가, 합리적 신중함인가?

#### 9.1.2 Policy Implications
- **과학 정책**: AI 채택이 낮은 분야에 대한 targeted investment 필요? 또는 유기적 확산을 기다려야?
- **연구비**: AI-related funding이 이미 AI-intense 분야에 집중되어 불균형 심화?
- **교육**: 비CS 분야 연구자의 AI literacy 향상 프로그램
- **학제간 연구**: AI "oil and water" 현상 해소를 위한 구조적 인센티브

#### 9.1.3 Limitations
- OpenAlex concept-based classification의 한계
- AI의 정의가 넓음 (traditional ML vs. deep learning vs. GenAI)
- DID의 인과 해석에 대한 caveat
- 25년이 충분한가? 일부 분야는 아직 S-curve 초기

### Track 3 Discussion (~1,000 words / 2 pages)

#### 9.2.1 Key Findings Interpretation
- 과학의 자기교정 메커니즘은 작동하지만 느림
- "Knowledge contamination"은 실재하며 정량적으로 측정 가능
- Generation 2 이상의 간접 오염은 van der Vet & Nijveen (2016)의 발견과 일치/상충?
- 분야별 self-correction 차이의 원인: 인프라? 문화? 인센티브?

#### 9.2.2 Policy Implications
- **학술 출판**: Retraction notice의 가시성 강화 — 현재 시스템 불충분
- **데이터베이스**: Retracted paper 인용 시 자동 경고 시스템 (OpenAlex, Google Scholar에 구현)
- **AI 시스템**: LLM 학습 데이터에서 retracted papers의 영향 (Klote, 2025)
- **연구 윤리**: 인용 시 cited paper의 retraction status 확인 책임

#### 9.2.3 Limitations
- Citation context의 자동 분류 정확도
- Generation 2+ 인용이 실제 retracted content를 propagate하는지 확인 불가
- 491건의 대표성
- Contamination score의 weight 설정이 임의적 → sensitivity analysis 필요

---

## 10. Target Venues

### Tier 1: High-Impact Generalist (IF > 30)

| Venue | Fit | Format | Notes |
|-------|-----|--------|-------|
| **Nature** | Track 1 ★★★★ / Track 3 ★★★★★ | Article (~3,500 words + Methods + Extended Data) | Park et al. (2023)이 여기 게재; retraction contamination은 높은 뉴스 가치 |
| **Science** | Track 1 ★★★ / Track 3 ★★★★ | Research Article (~4,500 words) | SciSci 논문 게재 전례 (Fortunato et al., 2018) |

> **현실적 판단**: Nature/Science는 결과의 "wow factor"에 크게 의존. Track 3의 시각적 임팩트(오염 네트워크 지도)가 높을 수 있음. Track 1은 descriptive analysis 비중이 높아 부족할 수 있음 (DID 결과가 강력해야 함).

### Tier 2: High-Impact Specialized (IF 10-30)

| Venue | Fit | Format | Notes |
|-------|-----|--------|-------|
| **Nature Human Behaviour** | Track 1 ★★★★★ / Track 3 ★★★★ | Article (~5,000 words) | SciSci 논문의 최적 venue; Wu et al. (2019) 게재 |
| **PNAS** | Track 1 ★★★★ / Track 3 ★★★★★ | Research Article (~6 pages) | Fang et al. (2012) retraction 논문 게재; 넓은 audience |

> **추천 전략**: Nature Human Behaviour를 Track 1의 primary target으로, PNAS를 Track 3의 primary target으로.

### Tier 3: Top Disciplinary (IF 3-10)

| Venue | Fit | Format | Notes |
|-------|-----|--------|-------|
| **Quantitative Science Studies (QSS)** | ★★★★★ both | Article | MIT Press; SciSci 전문 저널; open access |
| **Scientometrics** | ★★★★★ both | Article | SciSci의 전통적 핵심 저널; Springer |
| **Research Policy** | Track 1 ★★★★ | Article | 과학 정책 관점이 강할 경우 |
| **Journal of Informetrics** | ★★★★ both | Article | 계량서지학 전문 |

> **현실적 전략**: Tier 1 reject → Nature Human Behaviour/PNAS → QSS/Scientometrics. QSS가 방법론적으로 가장 적합한 home.

### Submission Strategy (cascading)

```
Track 1:
  1차: Nature Human Behaviour
  2차: PNAS  
  3차: Quantitative Science Studies
  4차: Scientometrics

Track 3:
  1차: Nature (if results are visually/narratively compelling)
  2차: PNAS
  3차: Quantitative Science Studies  
  4차: Scientometrics
```

---

## 11. Timeline

### Track 1: AI의 불균등 침투

| Phase | Task | Target Date | Status |
|-------|------|------------|--------|
| **데이터 수집** | 15 fields × 25 years AI fraction data from OpenAlex | 완료 | ✅ |
| **기술 통계** | Descriptive analysis, visualization, trajectory classification | +2주 | 🔲 |
| **Predictor 분석** | Field characteristics → adoption speed regression | +4주 | 🔲 |
| **DID 설계** | Treatment definition, parallel trends check, staggered DID | +6주 | 🔲 |
| **DID 실행** | Main results + robustness | +8주 | 🔲 |
| **집필 1차** | Full draft | +12주 | 🔲 |
| **내부 리뷰** | Feedback and revision | +14주 | 🔲 |
| **투고** | Submission to target venue | +16주 | 🔲 |

**예상 투고일**: 2025년 6월

### Track 3: 철회 논문의 지식 오염

| Phase | Task | Target Date | Status |
|-------|------|------------|--------|
| **데이터 수집** | Retraction Watch + OpenAlex linking | 완료 | ✅ |
| **네트워크 구축** | BFS citation propagation, Gen 1-3 | +3주 | 🔲 |
| **오염 점수** | Contamination score 계산, citation context 분류 | +6주 | 🔲 |
| **분석** | Temporal analysis, cross-field comparison, regression | +9주 | 🔲 |
| **시각화** | Network visualization, event study plots | +10주 | 🔲 |
| **집필 1차** | Full draft | +14주 | 🔲 |
| **내부 리뷰** | Feedback and revision | +16주 | 🔲 |
| **투고** | Submission to target venue | +18주 | 🔲 |

**예상 투고일**: 2025년 6-7월

### 병렬 진행 전략

```
         Feb    Mar    Apr    May    Jun    Jul
Track 1: [===데이터===][===분석===][===DID===][===집필===][투고]
Track 3: [===네트워크===][===오염점수===][===분석===][======집필======][투고]
                                                 ↑
                                        두 논문 동시 내부 리뷰 가능
```

---

## 12. Key References

### 핵심 참고문헌 (중요도 순, 총 30편)

#### Foundation — Science of Science

1. **Fortunato, S., Bergstrom, C.T., Börner, K., Evans, J.A., Helbing, D., Milojević, S., ... & Barabási, A.L. (2018).** Science of science. *Science*, 359(6379), eaao0185.
   - *SciSci 분야의 정의적 리뷰. 두 트랙 모두의 학문적 프레이밍에 필수.*

2. **Wang, D. & Barabási, A.L. (2021).** *The Science of Science*. Cambridge University Press.
   - *교과서. Career dynamics, citation networks, disruption 등의 이론적 기반.*

3. **de Solla Price, D.J. (1963).** *Little Science, Big Science*. Columbia University Press.
   - *과학의 양적 성장을 최초로 정량 분석. 역사적 맥락 설정.*

#### Track 1 — AI Diffusion

4. **Duede, E., Dolan, W., Bauer, A., Foster, I., & Lakhani, K. (2024).** Oil & Water? Diffusion of AI Within and Across Scientific Fields. arXiv:2405.15828.
   - *가장 직접적 선행연구. 20 fields, 1985-2022, 13× growth, "oil and water." 본 연구의 출발점이자 대화 상대.*

5. **Ding, L., Lawson, C., & Shapira, P. (2024).** Rise of Generative Artificial Intelligence in Science. arXiv:2412.20960.
   - *GenAI에 초점; OpenAlex 기반. Track 1과 데이터/방법론 비교 가능.*

6. **Cockburn, I.M., Henderson, R., & Stern, S. (2018).** The Impact of Artificial Intelligence on Innovation. *NBER Working Paper* No. 24449.
   - *AI as "invention of a method of invention" — GPT 프레임. Track 1의 이론적 뼈대.*

7. **Frank, M.R., Autor, D., Bessen, J.E., Brynjolfsson, E., Cebrian, M., Deming, D.J., ... & Rahwan, I. (2019).** Toward understanding the impact of artificial intelligence on labor. *PNAS*, 116(14), 6531-6539.
   - *AI의 노동시장 영향 프레임. 과학 노동에 유비 적용 가능.*

8. **Bianchini, S., Di Girolamo, V., Ravet, J., & Arranz, D. (2025).** Artificial Intelligence in Science: Promises or Perils for Creativity? European Commission Report.
   - *AI와 과학 창의성. Track 1 discussion의 이론적 맥락.*

#### Track 1 — Disruption

9. **Funk, R.J. & Owen-Smith, J. (2017).** A dynamic network measure of technological change. *Management Science*, 63(3), 791-817.
   - *CD index 원 논문. Track 1에서 outcome variable로 사용.*

10. **Park, M., Leahey, E., & Funk, R.J. (2023).** Papers and patents are becoming less disruptive over time. *Nature*, 613, 138-144.
    - *45M papers에서 disruption 감소. H5의 직접적 대화 상대.*

11. **Wu, L., Wang, D., & Evans, J.A. (2019).** Large teams develop and small teams disrupt science and technology. *Nature*, 566, 378-382.
    - *팀 사이즈와 disruption. AI 팀의 사이즈가 disruption에 영향?*

12. **Wuchty, S., Jones, B.F., & Uzzi, B. (2007).** The increasing dominance of teams in production of knowledge. *Science*, 316(5827), 1036-1039.
    - *팀 과학의 부상. Track 1의 배경.*

#### Track 3 — Retraction & Citation Persistence

13. **Cor, K. & Sood, G. (2022).** Propagation of Error: Citations to Problematic Research. Working paper.
    - *3,000+ retracted, 74K+ citations. 31% post-retraction, 91% no acknowledgment. Track 3의 핵심 선행 발견.*

14. **Fang, F.C., Steen, R.G., & Casadevall, A. (2012).** Misconduct accounts for the majority of retracted scientific publications. *PNAS*, 109(42), 17028-17033.
    - *2,047 retractions 분석; 67% misconduct. Track 3의 배경 통계.*

15. **van der Vet, P.E. & Nijveen, H. (2016).** Propagation of errors in citation networks: a study involving the entire citation network of a widely cited paper published in, and later retracted from, the journal Nature. *Research Integrity and Peer Review*, 1, 3.
    - *단일 논문 전체 citation network. 간접 인용은 전파 안함 — 본 연구에서 대규모로 검증.*

16. **Schneider, J., Ye, D., Hill, A.M., & Whitehorn, A.S. (2020).** Continued post-retraction citation of a fraudulent clinical trial report, 11 years after it was retracted for falsifying data. *Scientometrics*, 125, 2877-2913.
    - *단일 사례의 장기 추적. Track 3의 case study 맥락.*

17. **Hsiao, T.K. & Schneider, J. (2022).** Continued use of retracted papers: Temporal trends in citations and (lack of) awareness of retractions shown in citation contexts in biomedicine. *Quantitative Science Studies*, 3(4), 1144-1164.
    - *Biomedicine 초점. Track 3의 citation context 분석 방법론 참조.*

18. **Schmidt, M. (2024).** Why do some retracted articles continue to get cited? *Scientometrics*, 129(12).
    - *철회 후 지속 인용의 원인 탐구. Track 3의 해석 프레임.*

19. **Azoulay, P., Bonatti, A., & Krieger, J.L. (2017).** The career effects of scandal: Evidence from scientific retractions. *Journal of Political Economy*, 125(5), 1570-1608.
    - *Retraction의 spillover 효과. Track 3 discussion.*

20. **Lu, S.F., Jin, G.Z., Uzzi, B., & Jones, B. (2013).** The retraction penalty: evidence from the Web of Science. *Scientific Reports*, 3, 3146.
    - *철회 후 인용 감소의 체계적 분석.*

#### Methodology — Bibliometrics & Data

21. **Priem, J., Piwowar, H., & Orr, R. (2022).** OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. arXiv:2205.01833.
    - *OpenAlex 소개. 데이터 소스 정당화 필수 인용.*

22. **Alperin, J.P., Portenoy, J., Demes, K., Larivière, V., & Haustein, S. (2024).** An analysis of the suitability of OpenAlex for bibliometric analyses. arXiv:2404.17663.
    - *OpenAlex 품질 평가. 데이터 한계 논의 시 인용.*

23. **Culbert, J.H., Hobert, A., Jahn, N., Haupka, N., Schmidt, M., Donner, P., & Mayr, P. (2024).** Reference Coverage Analysis of OpenAlex compared to Web of Science and Scopus. *Scientometrics*, 130, 2475-2492.
    - *OpenAlex citation coverage. Track 3의 데이터 completeness 논의.*

#### Methodology — Causal Inference

24. **Callaway, B. & Sant'Anna, P.H.C. (2021).** Difference-in-Differences with multiple time periods. *Journal of Econometrics*, 225(2), 200-230.
    - *Staggered DID. Track 1의 핵심 방법론.*

25. **Goodman-Bacon, A. (2021).** Difference-in-differences with variation in treatment timing. *Journal of Econometrics*, 225(2), 254-277.
    - *Two-way FE의 bias. Callaway & Sant'Anna와 함께 Track 1 방법론 정당화.*

#### Technology Diffusion Theory

26. **Rogers, E.M. (1962/2003).** *Diffusion of Innovations* (5th ed.). Free Press.
    - *기술 확산의 고전. S-curve 이론. Track 1.*

27. **Bresnahan, T.F. & Trajtenberg, M. (1995).** General purpose technologies 'Engines of growth'? *Journal of Econometrics*, 65(1), 83-108.
    - *GPT 개념. AI-as-GPT 논의. Track 1.*

#### Additional Context

28. **Brainard, J. & You, J. (2018).** What a massive database of retracted papers reveals about science publishing's 'death penalty'. *Science*.
    - *Retraction 추세 보도. Track 3 introduction.*

29. **Bornmann, L. & Tekles, A. (2019).** Disruption index depends on length of citation window. *El Profesional de la Información*, 28(2).
    - *CD index의 window length sensitivity. Track 1 robustness.*

30. **Zhang, D., Mishra, S., Brynjolfsson, E., Etchemendy, J., Ganguli, D., Grosz, B., ... & Perrault, R. (2021).** The AI Index 2021 Annual Report. Stanford HAI.
    - *AI 연구 현황 통계. Track 1 배경 데이터.*

---

## Appendix: Section Word Count Estimates

### Track 1 (Nature Human Behaviour 타겟)

| Section | Words | Pages (approx.) |
|---------|-------|-----------------|
| Abstract | 300 | 0.5 |
| Introduction | 1,500 | 3 |
| Related Work | 1,000 | 2 |
| Data & Methods | 1,500 | 3 |
| Results | 2,500 | 5 |
| Discussion | 1,000 | 2 |
| Conclusion | 300 | 0.5 |
| **Total main text** | **~8,100** | **~16** |
| Methods (extended) | 2,000 | 4 |
| Supplementary | 3,000+ | — |

### Track 3 (PNAS 타겟)

| Section | Words | Pages (approx.) |
|---------|-------|-----------------|
| Abstract | 300 | 0.5 |
| Introduction | 1,500 | 3 |
| Related Work | 1,000 | 2 |
| Data & Methods | 1,500 | 3 |
| Results | 2,500 | 5 |
| Discussion | 1,000 | 2 |
| Conclusion | 300 | 0.5 |
| **Total main text** | **~8,100** | **~16** |
| SI Appendix | 5,000+ | — |

> **Note**: Nature은 ~3,500 words main text로 줄여야 함. 위는 full-length 기준이며, venue에 따라 축약 필요.

---

## Appendix: Checklist Before Writing

### Track 1
- [ ] 15개 분야 × 25년 데이터 완성 확인
- [ ] AI concept 분류 precision/recall 검증
- [ ] S-curve fitting 완료
- [ ] DID parallel trends check 통과
- [ ] Staggered DID 구현 (R의 `did` 패키지 또는 Python equivalent)
- [ ] Disruption index 계산 완료
- [ ] 모든 figure draft 완성

### Track 3
- [ ] 491 retracted papers의 OpenAlex 매칭 확인
- [ ] BFS propagation Gen 1-3 완료
- [ ] Citation context 분류 파이프라인 구축 (NLP or manual sample)
- [ ] Contamination score 계산
- [ ] Self-correction index 계산
- [ ] Network visualization 완성
- [ ] Event study plot 완성

---

*Last updated: 2025-02-14*
*Author: [연구자]*
*Project: Science of Science (과학의 과학)*
