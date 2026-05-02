#!/usr/bin/env python3
"""[2C] Citation-context expansion: stratify Semantic Scholar intent tags
by retraction reason and publisher, on a larger sample.

Pulls citation contexts for 100 paper-mill + 100 non-mill retracted papers
(20 citations each → ~4,000 citation rows) via Semantic Scholar batch API.
Computes:
  - influential-citation rate per reason category
  - influential-citation rate per publisher (Hindawi vs others)
  - intent-tag distribution (background, methodology, result) by stratum

Outputs:
  data/processed/track3/citation_context_v2.json
  data/processed/track3/citation_context_v2_sample.tsv
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import httpx
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "track3"
RAW = ROOT / "data" / "raw" / "retraction_watch" / "retraction-watch-data" / "retraction_watch.csv"
S2 = "https://api.semanticscholar.org/graph/v1"
N_PER_GROUP = 50      # 50 mill + 50 non-mill = 100 papers
N_CITATIONS = 20       # 20 citations each → 2,000 citation rows
RATE_DELAY = 1.1


def fetch_citations(doi: str, client: httpx.Client) -> list[dict]:
    url = f"{S2}/paper/DOI:{doi}/citations"
    params = {"fields": "intents,contexts,isInfluential", "limit": N_CITATIONS}
    for attempt in range(3):
        try:
            r = client.get(url, params=params, timeout=30.0)
            if r.status_code == 200:
                return r.json().get("data", [])
            if r.status_code == 429:
                time.sleep(15)
                continue
            if r.status_code == 404:
                return []
        except httpx.HTTPError:
            time.sleep(5)
    return []


def main() -> None:
    print("Loading...")
    rw = pd.read_csv(RAW, low_memory=False)
    rw["DOI_norm"] = rw.OriginalPaperDOI.astype(str).str.strip().str.lower()
    rw["is_mill"] = rw.Reason.apply(lambda s: "Paper Mill" in str(s))
    rw["publisher_norm"] = rw.Publisher.fillna("Unknown").str.strip()
    rw_unique = rw.drop_duplicates(subset=["DOI_norm"], keep="first")

    rp = pd.read_csv(DATA / "retracted_papers.tsv", sep=",", quotechar='"',
                     engine="python", on_bad_lines="skip")
    rp.columns = [c.strip() for c in rp.columns]
    rp["doi"] = rp.doi.astype(str).str.strip().str.strip('"').str.lower()
    rp["openalex_id"] = rp.openalex_id.astype(str).str.strip().str.strip('"')
    rp["cited_by_count"] = pd.to_numeric(rp.cited_by_count, errors="coerce")
    rp = rp.drop_duplicates(subset=["doi"], keep="first")
    rp = rp.merge(rw_unique[["DOI_norm", "is_mill", "publisher_norm"]].rename(
        columns={"DOI_norm": "doi"}), on="doi", how="left")
    rp["is_mill"] = rp.is_mill.fillna(False).astype(bool)
    rp["publisher_norm"] = rp.publisher_norm.fillna("Unknown")

    # Sample: top-cited mill + non-mill papers (likely to have S2 records)
    rp_cited = rp[rp.cited_by_count.fillna(0) >= 5].copy()
    rng = np.random.default_rng(42)
    mill = rp_cited[rp_cited.is_mill].sample(
        n=min(N_PER_GROUP, len(rp_cited[rp_cited.is_mill])), random_state=42)
    nonmill = rp_cited[~rp_cited.is_mill].sample(
        n=min(N_PER_GROUP, len(rp_cited[~rp_cited.is_mill])), random_state=43)
    sample = pd.concat([mill, nonmill]).reset_index(drop=True)
    print(f"Sample: {len(sample)} papers (mill={sample.is_mill.sum()}, "
          f"non-mill={(~sample.is_mill).sum()})")

    # Fetch citations
    rows = []
    with httpx.Client(headers={"User-Agent": "research-track3/2.0"}) as client:
        for i, r in sample.iterrows():
            doi = r.doi
            if not doi or doi == "nan":
                continue
            print(f"[{i+1}/{len(sample)}] DOI: {doi[:60]}")
            cits = fetch_citations(doi, client)
            for c in cits:
                rows.append({
                    "retracted_doi": doi,
                    "is_mill": bool(r.is_mill),
                    "publisher": r.publisher_norm,
                    "is_influential": c.get("isInfluential", False),
                    "intents": "|".join(c.get("intents") or []),
                    "n_contexts": len(c.get("contexts") or []),
                })
            time.sleep(RATE_DELAY)

    df = pd.DataFrame(rows)
    df.to_csv(DATA / "citation_context_v2_sample.tsv", sep="\t", index=False)
    print(f"\nFetched {len(df):,} citation rows")
    if len(df) == 0:
        print("No citations retrieved.")
        return

    # Aggregate
    print("\n=== Influential rate by stratum ===")
    by_mill = df.groupby("is_mill").agg(
        n=("is_influential", "size"),
        influential=("is_influential", "sum"),
        with_intent=("intents", lambda s: (s.str.len() > 0).sum()),
        with_context=("n_contexts", lambda s: (s > 0).sum()),
    ).reset_index()
    by_mill["pct_influential"] = by_mill.influential / by_mill.n
    by_mill["pct_intent"] = by_mill.with_intent / by_mill.n
    print(by_mill.to_string(index=False, float_format="%.4f"))

    print("\n=== Influential rate Hindawi vs other ===")
    df["is_hindawi"] = df.publisher == "Hindawi"
    by_pub = df.groupby("is_hindawi").agg(
        n=("is_influential", "size"),
        influential=("is_influential", "sum"),
    ).reset_index()
    by_pub["pct_influential"] = by_pub.influential / by_pub.n
    print(by_pub.to_string(index=False, float_format="%.4f"))

    out = {
        "n_papers_sampled": int(len(sample)),
        "n_citation_rows": int(len(df)),
        "by_mill": by_mill.to_dict("records"),
        "by_publisher_hindawi_vs_other": by_pub.to_dict("records"),
        "interpretation": (
            "Citation-context analysis stratified by mill label and publisher. "
            "If paper-mill content semantically contaminates downstream papers "
            "more than other retractions do, mill-paper citations should show "
            "higher influential-citation rates. The data report the influential "
            "rate per stratum directly; differences quantify the semantic "
            "contamination component beyond the structural citation count."
        ),
    }
    (DATA / "citation_context_v2.json").write_text(json.dumps(out, indent=2))
    print(f"\nWrote {DATA / 'citation_context_v2.json'}")


if __name__ == "__main__":
    main()
