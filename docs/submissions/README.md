# Submission Packages

## Structure

```
submissions/
├── README.md                              ← This file
├── statistical_verification_report.txt    ← Cross-check of all paper statistics
├── track1_nhb/                            ← Nature Human Behaviour submission
│   ├── manuscript.md                      ← Final manuscript draft
│   ├── cover_letter.md                    ← Cover letter
│   └── checklist.md                       ← Submission checklist
└── track3_pnas/                           ← PNAS submission
    ├── manuscript.md                      ← Final manuscript draft
    ├── cover_letter.md                    ← Cover letter
    └── checklist.md                       ← Submission checklist
```

## Papers

### Track 1: The Great Divergence (Nature Human Behaviour)
- **Title**: The Great Divergence: Heterogeneous AI Adoption and Its Consequences for Scientific Production
- **Word count**: ~8,000 (main text) + Extended Methods
- **References**: 29
- **Extended Data**: Tables 1--9, Figures 1--7

### Track 3: The Half-Life of Bad Science (PNAS)
- **Title**: The Half-Life of Bad Science: Citation Persistence and Knowledge Contamination After Retraction
- **Word count**: ~7,970
- **References**: 17
- **Extended Data**: Tables 5--6, Figures 6--7

## Statistical Verification

All 70 verifiable statistics across both papers have been cross-checked against the underlying data files:
- `data/processed/ai_adoption_analysis.json`
- `data/processed/ai_adoption_deep_analysis.json`
- `data/processed/retraction_analysis/retraction_citation_analysis.json`
- `data/processed/neo4j_field_analysis.json`

**Result**: 70/70 passed, 0 failures, 4 warnings (flagged for author review).

## Before Submission

See each paper's `checklist.md` for journal-specific requirements. Key items:
1. Fill in author names, affiliations, and ORCID IDs
2. Complete Author Contributions and Acknowledgements
3. Add repository and platform URLs
4. Prepare figure files (PDF/TIFF, 300+ DPI)
5. Review flagged warnings in verification report

## Source Data

- **Neo4j Database**: 446M nodes, 1.8B relationships (272GB)
- **OpenAlex Snapshot**: 360,515,260 works, 86,009,932 authors
- **Retraction Watch**: 68,870 retraction records
- **Processed Data**: `data/processed/` (JSON, Parquet)
- **Figures**: `data/processed/figures/pub/` and `data/processed/figures/neo4j/`
- **Platform**: Palimpsest at http://192.168.1.100:8300
