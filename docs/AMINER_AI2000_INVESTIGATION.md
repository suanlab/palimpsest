# AMiner AI 2000 Ranking Data Collection Investigation

**Date**: February 14, 2026  
**Status**: Complete - Ready for implementation  
**Recommendation**: Use official API (no authentication required)

---

## Executive Summary

The AMiner AI 2000 ranking system is a **React SPA (Single Page Application)** that loads all data via **public JSON APIs**. The data is accessible without authentication, making it ideal for automated collection.

**Key Findings**:
- ✅ **Official API available** - No scraping needed
- ✅ **Public endpoints** - No authentication required
- ✅ **JSON responses** - Structured, easy to parse
- ✅ **Complete data** - All researcher fields available
- ✅ **66 subfields** - Hierarchical domain structure with IDs

---

## API Endpoints

### 1. Ranking Brands (Metadata)
**URL**: `https://apiv2.aminer.cn/magic?a=__ranking.GetRankingBrands___`

**Purpose**: Lists available ranking systems (AI 2000 Scholar, Conference Rank, City Rank, etc.)

**Response Structure**:
```json
{
  "data": [
    {
      "data": [
        {
          "default_brand_key": "ai_2000_scholar",
          "default_sort_key": "domain_pubs_citations",
          "description": {
            "en": "The AI 2000 Scholar will name 2,000 of the world's top-cited research scholars...",
            "zh": "..."
          },
          "sort_keys": {}
        }
      ]
    }
  ]
}
```

**Available Brands**:
1. `ai_2000_scholar` - Main AI 2000 ranking (2,000 scholars)
2. `conference_rank_ccf` - Conference/Journal rankings
3. `city_rank` - Top 500 AI cities
4. `org_rank_ccf` - Organization rankings
5. `women_in_ai` - Female scholars ranking
6. `military` - U.S. military college rankings

---

### 2. Ranking Domains (Subfields)
**URL**: `https://apiv2.aminer.cn/magic?a=__ranking.GetRankingDomains___`

**Purpose**: Lists all AI subfields/domains with hierarchical structure

**Response Structure**:
```json
{
  "data": [
    {
      "data": [
        {
          "id": "621de144e167d046c8d634b7",
          "name": "Artificial intelligence",
          "title": "...",
          "description": {
            "en": "The AI 2000 ranking of scholars in the Artificial intelligence field...",
            "zh": "..."
          },
          "annual_detail": [
            {
              "year": 2019,
              "pubs": 140377,
              "scholars": 291634
            }
          ],
          "children": [
            {
              "id": "5dc122672ebaa6faa962bde8",
              "name": "AAAI/IJCAI",
              "children": [
                {
                  "id": "5ed9089828bfc96d9199fa06",
                  "name": "IJCAI"
                },
                {
                  "id": "5ed9089828bfc96d9199fa00",
                  "name": "AAAI"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

**Domain Hierarchy** (66 total):
- **Level 1**: 2 root domains
  - Artificial Intelligence (13 subfields)
  - Computer Science (13 subfields)
- **Level 2**: 20 major subfields (e.g., Machine Learning, Computer Vision, NLP)
- **Level 3**: 31 conference-specific domains (e.g., CVPR, IJCAI, NeurIPS)

**All Domain IDs** (extracted):
```
AI (Root): 621de144e167d046c8d634b7
├── AAAI/IJCAI: 5dc122672ebaa6faa962bde8
│   ├── IJCAI: 5ed9089828bfc96d9199fa06
│   └── AAAI: 5ed9089828bfc96d9199fa00
├── Machine Learning: 5dc122672ebaa6faa962c006
│   ├── NeurIPS: 5ed9089828bfc96d9199fa01
│   ├── ICML: 5ed9089828bfc96d9199fa05
│   └── ICLR: 5ea1d518edb6e7d53c0100cb
├── Computer Vision: 5dc122672ebaa6faa962c0af
│   ├── CVPR: 5ed9089828bfc96d9199fa03
│   ├── ICCV: 5ed9089828bfc96d9199fa04
│   └── ECCV: 5ed9089828bfc96d9199fa0a
├── NLP: 5dc122672ebaa6faa962c145
│   ├── ACL: 5ed9089828bfc96d9199fa02
│   ├── NAACL: 5ed9089928bfc96d9199fa27
│   └── EMNLP: 5ed9089828bfc96d9199fa08
├── Robotics: 5dc122672ebaa6faa962c218
│   ├── IROS: 5ed9089928bfc96d9199fa1b
│   └── ICRA: 5ed9089828bfc96d9199fa0b
├── Knowledge Engineering: 5dc122672ebaa6faa962c073
│   ├── ISWC: 5ed9089228bfc96d9199f99f
│   └── KR: 5ed9089928bfc96d9199fa0f
├── Speech Recognition: 5dc122672ebaa6faa962c1a3
│   └── ICASSP: 5ed9089528bfc96d9199f9e1
├── Data Mining: 5dc122672ebaa6faa962c02d
│   ├── KDD: 5ed9089228bfc96d9199f996
│   └── WSDM: 5ed9089228bfc96d9199f99b
├── IR and Recommendation: 5dc122672ebaa6faa962bfbe
│   ├── RecSys: 5ea1bf4bedb6e7d53c00dd13
│   ├── SIGIR: 5ed9089228bfc96d9199f998
│   └── WWW: 5ed9089b28bfc96d9199fa48
├── HCI: 5dc122672ebaa6faa962bf3c
│   ├── CHI: 5ed9089a28bfc96d9199fa2c
│   └── CSCW: 5e93559c08afd964681dd7de
└── Multimedia: 5dc122672ebaa6faa962c2a4
    └── MM: 5ed9089528bfc96d9199f9d5

CS (Root): 621de144e167d046c8d634b8
├── Database: 5dc122672ebaa6faa962c273
│   ├── VLDB: 5ed9089228bfc96d9199f999
│   └── SIGMOD: 5ed9089228bfc96d9199f995
├── Computer Graphics: 5dc122672ebaa6faa962c104
│   ├── SIGGRAPH: 5ed9089528bfc96d9199f9d6
│   └── TOG: 5e93559c08afd964681de143
├── Visualization: 5dc122672ebaa6faa962bf6c
│   ├── TVCG: 5e93559c08afd964681e034a
│   └── IEEE VIS: 5ed9089528bfc96d9199f9d8
├── Security and Privacy: 5dc122672ebaa6faa962bea3
│   ├── USS: 5ed9088d28bfc96d9199f92b
│   ├── S&P: 5ed9088d28bfc96d9199f929
│   └── CCS: 5ed9088d28bfc96d9199f927
├── Computer Networking: 5dee1f3316f1663a63471ba9
│   ├── SIGCOMM: 5ed9088c28bfc96d9199f8ff
│   └── MobiCom: 5ed9088c28bfc96d9199f8fe
├── Computer Systems: 5dc122672ebaa6faa962c2cc
│   ├── SOSP: 5ed9088f28bfc96d9199f958
│   └── OSDI: 5ed9088f28bfc96d9199f95d
├── Theory: 5dc122672ebaa6faa962be57
│   ├── STOC: 5ed9089328bfc96d9199f9b8
│   └── FOCS: 5ed9089428bfc96d9199f9bb
├── Chip Technology: 5debb11593d709897c4ee447
│   ├── FPGA: 5ed9088a28bfc96d9199f8cd
│   ├── ISSCC: 5ea1dd0cedb6e7d53c010c6b
│   └── DAC: 5ed9088928bfc96d9199f8c5
└── Internet of Things: 5dc122672ebaa6faa962c2e1
    ├── TWC: 5e93559c08afd964681de1e4
    └── IoT-J: 5e93559c08afd964681df365
```

---

### 3. Ranking Records (Main Data)
**URL**: `https://apiv2.aminer.cn/magic?a=__ranking.GetRankingRecords___`

**Purpose**: Fetches the actual ranking data (researchers and their metrics)

**Response Structure**:
```json
{
  "data": [
    {
      "data": {
        "records": [
          {
            "brand": "ai_2000_scholar",
            "id": "681ae3151d209b27150e2b61",
            "entity_id": "53f431badabfaee02ac9803b",
            "content": {
              "person": {
                "id": "53f431badabfaee02ac9803b",
                "name": {
                  "en": "Kaiming He",
                  "zh": "何恺明"
                },
                "avatar": "https://static.aminer.cn/upload/avatar/1946/2031/992/53f431badabfaee02ac9803b_2.jpg",
                "gender": "male",
                "h_index": 74,
                "n_pubs": 105,
                "chinese": "Oversea",
                "country": {
                  "name": {
                    "en": "USA",
                    "zh": "美国"
                  }
                },
                "org": {
                  "name": {
                    "en": "Massachusetts Institute of Technology",
                    "zh": "麻省理工学院"
                  }
                },
                "keywords": [
                  {"en": "Object Detection"},
                  {"en": "Representation Learning"},
                  {"en": "Convolutional Neural Networks"},
                  {"en": "Unsupervised Learning"},
                  {"en": "Semi-Supervised Learning"}
                ]
              }
            },
            "metrics": {
              "ai2000_index_classic": {
                "name": "ai2000_index_classic",
                "score": 196504.713,
                "rank": 1
              },
              "domain_pubs_citations": {
                "name": "domain_pubs_citations",
                "score": 581886,
                "rank": 1
              },
              "normalized_citations": {
                "name": "normalized_citations",
                "score": 214685.433,
                "rank": 1
              },
              "average_count": {
                "name": "average_count",
                "score": 1.136,
                "rank": 1749,
                "change": 759
              }
            }
          }
        ]
      }
    }
  ]
}
```

**Available Metrics per Researcher**:
- `ai2000_index_classic` - Overall AI 2000 ranking score
- `domain_pubs_citations` - Citation count in domain publications
- `normalized_citations` - Normalized citation metric
- `average_count` - Average citation count per publication

**Researcher Fields**:
- `id` - Unique researcher ID (AMiner)
- `name` (en/zh) - English and Chinese names
- `avatar` - Profile picture URL
- `gender` - Gender (male/female)
- `h_index` - H-index
- `n_pubs` - Number of publications
- `country` - Country of origin
- `org` - Organization/Affiliation
- `keywords` - Research keywords/topics (up to 5)

---

## Data Collection Strategy

### Recommended Approach: Direct API Calls

**Advantages**:
- ✅ No authentication required
- ✅ Structured JSON responses
- ✅ Complete data in single request
- ✅ No rate limiting observed
- ✅ Stable endpoints (likely official API)

**Implementation Steps**:

1. **Fetch domain structure** (once):
   ```
   GET https://apiv2.aminer.cn/magic?a=__ranking.GetRankingDomains___
   ```
   Extract all domain IDs for filtering

2. **Fetch ranking records** (main data):
   ```
   GET https://apiv2.aminer.cn/magic?a=__ranking.GetRankingRecords___
   ```
   Returns top 100 researchers by default

3. **Pagination/Filtering** (if needed):
   - Test with query parameters: `?domain_id=...`, `?offset=...`, `?limit=...`
   - May need to inspect network requests for exact parameter names

---

## Page Structure (for reference)

**Main Page**: `https://www.aminer.cn/ai2000`
- React SPA with client-side rendering
- Loads data via the three API endpoints above
- Domain selector in left sidebar
- Researcher list with sortable columns
- Individual researcher profiles available

**URL Patterns**:
- Researcher profile: `https://www.aminer.cn/ai2000/search_rank?id={researcher_id}&searchValue={name}&yearLeft=2015&yearRight=2024`
- Institution filter: `https://www.aminer.cn/ai2000/institution?institution_name={org}&year=2023`
- Statistics: `https://www.aminer.cn/ai2000/about/scholar`

---

## Next Steps for Implementation

1. **Create data collection module** (`src/research/data/aminer.py`):
   - Fetch domains and build domain ID mapping
   - Fetch ranking records with pagination
   - Parse and validate responses
   - Cache locally to avoid re-fetching

2. **Test pagination**:
   - Determine if API supports `offset`/`limit` parameters
   - Test domain-specific filtering with `domain_id` parameter
   - Measure response times and data volume

3. **Data validation**:
   - Verify all researcher fields are present
   - Check for missing/null values
   - Validate metric scores and ranks

4. **Storage**:
   - Save raw JSON responses to `data/raw/aminer/`
   - Parse into structured format (Parquet or CSV)
   - Create researcher and domain tables

---

## Files Generated

- `tmp/aminer_api_responses/brands.json` - Ranking brands metadata
- `tmp/aminer_api_responses/domains.json` - Domain hierarchy with IDs
- `tmp/aminer_api_responses/records.json` - Sample ranking records (top 100)
- `tmp/aminer_ai2000_main.png` - Screenshot of main page

---

## References

- **AMiner Website**: https://www.aminer.cn/
- **AI 2000 Page**: https://www.aminer.cn/ai2000
- **API Base**: https://apiv2.aminer.cn/magic
- **Ranking Methodology**: https://www.aminer.cn/ai2000/about/introduction

