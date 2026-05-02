# AMiner AI 2000 Data Collection - Quick Start Guide

## TL;DR

The AMiner AI 2000 ranking is accessible via **3 public JSON APIs** with no authentication required.

```python
import httpx
import json

# Fetch all ranking data
client = httpx.Client()

# 1. Get domain structure
domains = client.get("https://apiv2.aminer.cn/magic?a=__ranking.GetRankingDomains___").json()

# 2. Get ranking records (top 100 researchers)
records = client.get("https://apiv2.aminer.cn/magic?a=__ranking.GetRankingRecords___").json()

# 3. Extract researcher data
researchers = records['data'][0]['data']['records']
for researcher in researchers:
    person = researcher['content']['person']
    metrics = researcher['metrics']
    print(f"{person['name']['en']}: {metrics['ai2000_index_classic']['score']}")
```

---

## API Endpoints

| Endpoint | Purpose | Returns |
|----------|---------|---------|
| `__ranking.GetRankingBrands___` | Ranking systems metadata | 6 brands (AI 2000, Conference Rank, etc.) |
| `__ranking.GetRankingDomains___` | Domain hierarchy | 66 subfields with IDs and annual stats |
| `__ranking.GetRankingRecords___` | Ranking data | Top 100 researchers with metrics |

**Base URL**: `https://apiv2.aminer.cn/magic?a=`

---

## Data Structure

### Researcher Record
```python
{
    "brand": "ai_2000_scholar",
    "id": "681ae3151d209b27150e2b61",
    "entity_id": "53f431badabfaee02ac9803b",
    "content": {
        "person": {
            "id": "53f431badabfaee02ac9803b",
            "name": {"en": "Kaiming He", "zh": "何恺明"},
            "avatar": "https://...",
            "gender": "male",
            "h_index": 74,
            "n_pubs": 105,
            "country": {"name": {"en": "USA", "zh": "美国"}},
            "org": {"name": {"en": "MIT", "zh": "麻省理工学院"}},
            "keywords": [
                {"en": "Object Detection"},
                {"en": "Representation Learning"},
                ...
            ]
        }
    },
    "metrics": {
        "ai2000_index_classic": {"score": 196504.713, "rank": 1},
        "domain_pubs_citations": {"score": 581886, "rank": 1},
        "normalized_citations": {"score": 214685.433, "rank": 1},
        "average_count": {"score": 1.136, "rank": 1749, "change": 759}
    }
}
```

### Domain Record
```python
{
    "id": "5dc122672ebaa6faa962c006",
    "name": "Machine Learning",
    "description": {"en": "...", "zh": "..."},
    "annual_detail": [
        {"year": 2019, "pubs": 108181, "scholars": 210763},
        {"year": 2020, "pubs": 137228, "scholars": 150642},
        ...
    ],
    "children": [
        {
            "id": "5ed9089828bfc96d9199fa01",
            "name": "NeurIPS",
            ...
        }
    ]
}
```

---

## Key Findings

### Subfields (66 total)

**AI (13 subfields)**:
- AAAI/IJCAI (IJCAI, AAAI)
- Machine Learning (NeurIPS, ICML, ICLR)
- Computer Vision (CVPR, ICCV, ECCV)
- NLP (ACL, NAACL, EMNLP)
- Robotics (IROS, ICRA)
- Knowledge Engineering (ISWC, KR)
- Speech Recognition (ICASSP)
- Data Mining (KDD, WSDM)
- IR and Recommendation (RecSys, SIGIR, WWW)
- HCI (CHI, CSCW)
- Multimedia (MM)

**Computer Science (13 subfields)**:
- Database (VLDB, SIGMOD)
- Computer Graphics (SIGGRAPH, TOG)
- Visualization (TVCG, IEEE VIS)
- Security and Privacy (USS, S&P, CCS)
- Computer Networking (SIGCOMM, MobiCom)
- Computer Systems (SOSP, OSDI)
- Theory (STOC, FOCS)
- Chip Technology (FPGA, ISSCC, DAC)
- Internet of Things (TWC, IoT-J)

### Metrics Available

Per researcher:
- **ai2000_index_classic** - Overall ranking score
- **domain_pubs_citations** - Citation count in domain
- **normalized_citations** - Normalized citation metric
- **average_count** - Average citations per publication

Each metric includes: `score`, `rank`, and optionally `change` (year-over-year)

### Researcher Fields

- Name (English + Chinese)
- Avatar URL
- Gender
- H-index
- Publication count
- Country
- Organization
- Research keywords (up to 5)

---

## Implementation Checklist

- [ ] Test API endpoints with httpx
- [ ] Parse domain hierarchy and extract IDs
- [ ] Fetch ranking records (test pagination with offset/limit)
- [ ] Create Pydantic models for validation
- [ ] Cache responses locally (data/raw/aminer/)
- [ ] Parse into structured format (Parquet)
- [ ] Create researcher and domain tables
- [ ] Add unit tests with sample data
- [ ] Document any query parameters discovered

---

## Potential Query Parameters to Test

```python
# Test these parameters for filtering/pagination
params = {
    "domain_id": "5dc122672ebaa6faa962c006",  # Machine Learning
    "offset": 0,
    "limit": 100,
    "sort_by": "domain_pubs_citations",
    "year": 2024,
}

response = client.get(
    "https://apiv2.aminer.cn/magic?a=__ranking.GetRankingRecords___",
    params=params
)
```

---

## Files to Create

```
src/research/data/
├── aminer.py              # Main AMiner client
├── models/
│   └── aminer.py          # Pydantic models
└── __init__.py

tests/test_data/
├── test_aminer.py         # Unit tests
└── fixtures/
    ├── domains.json       # Sample domain response
    └── records.json       # Sample records response

data/raw/aminer/
├── domains.json           # Cached domain structure
├── records_*.json         # Cached ranking records
└── metadata.json          # Collection metadata
```

---

## Example: Complete Data Collection Script

```python
# src/research/data/aminer.py
import httpx
import json
from pathlib import Path
from typing import Any
from pydantic import BaseModel

class AMinerClient:
    BASE_URL = "https://apiv2.aminer.cn/magic"
    
    def __init__(self, cache_dir: Path = Path("data/raw/aminer")):
        self.client = httpx.Client(timeout=30.0)
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_domains(self, use_cache: bool = True) -> dict[str, Any]:
        """Fetch domain hierarchy."""
        cache_file = self.cache_dir / "domains.json"
        
        if use_cache and cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        
        response = self.client.get(
            self.BASE_URL,
            params={"a": "__ranking.GetRankingDomains___"}
        )
        response.raise_for_status()
        data = response.json()
        
        # Cache
        with open(cache_file, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return data
    
    def fetch_records(
        self,
        domain_id: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Fetch ranking records."""
        params = {"a": "__ranking.GetRankingRecords___"}
        
        if domain_id:
            params["domain_id"] = domain_id
        if offset:
            params["offset"] = offset
        if limit:
            params["limit"] = limit
        
        response = self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    
    def close(self):
        self.client.close()

# Usage
if __name__ == "__main__":
    client = AMinerClient()
    
    # Fetch domains
    domains = client.fetch_domains()
    print(f"Fetched {len(domains['data'][0]['data'])} domain trees")
    
    # Fetch records
    records = client.fetch_records(limit=100)
    researchers = records['data'][0]['data']['records']
    print(f"Fetched {len(researchers)} researchers")
    
    # Print top researcher
    top = researchers[0]
    person = top['content']['person']
    metrics = top['metrics']
    print(f"\nTop researcher: {person['name']['en']}")
    print(f"  H-index: {person['h_index']}")
    print(f"  Score: {metrics['ai2000_index_classic']['score']}")
    
    client.close()
```

---

## Status

✅ **Investigation Complete**
- API endpoints identified and tested
- Response structures documented
- Domain hierarchy extracted (66 subfields)
- Sample data collected and validated
- Ready for implementation

**Next**: Create `src/research/data/aminer.py` with full client implementation
