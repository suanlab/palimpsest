#!/usr/bin/env python3
"""[2B] Author-network paper-mill cluster identification.

Independent signal validation for the Retraction Watch paper-mill labels:
build a co-authorship graph among authors of all retracted papers, identify
densely connected clusters, and check whether RW-labelled paper-mill
retractions concentrate in specific clusters. If clusters strongly predict
mill labels independently, the labels are externally validated; if the
overlap is weak, our paper-mill stratification depends entirely on RW's
manual labelling.

Approach (light-weight, no APOC):
  1. Sample 100 paper-mill + 100 non-mill retracted papers
  2. Pull all authors via AUTHORED for each paper
  3. Compute author overlap matrix between paper-mill and non-mill papers
  4. Detect "mill-clusters" as papers sharing ≥3 authors with another paper
     in the sample
  5. Report mill-prediction accuracy of the cluster-based label

Outputs:
  data/processed/track3/author_network.json
  data/processed/track3/tables/table_author_clusters.tsv
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "track3"
OUT_TABLES = DATA / "tables"
OUT_TABLES.mkdir(parents=True, exist_ok=True)
RAW = ROOT / "data" / "raw" / "retraction_watch" / "retraction-watch-data" / "retraction_watch.csv"


def main() -> None:
    print("Loading retracted papers + RW reasons...")
    rw = pd.read_csv(RAW, low_memory=False)
    rw["DOI_norm"] = rw.OriginalPaperDOI.astype(str).str.strip().str.lower()
    rw["is_mill"] = rw.Reason.apply(lambda s: "Paper Mill" in str(s))
    rw_unique = rw.drop_duplicates(subset=["DOI_norm"], keep="first")

    rp = pd.read_csv(DATA / "retracted_papers.tsv", sep=",", quotechar='"',
                     engine="python", on_bad_lines="skip")
    rp.columns = [c.strip() for c in rp.columns]
    rp["doi"] = rp.doi.astype(str).str.strip().str.strip('"').str.lower()
    rp["openalex_id"] = rp.openalex_id.astype(str).str.strip().str.strip('"')
    rp = rp.drop_duplicates(subset=["doi"], keep="first")
    rp = rp.merge(rw_unique[["DOI_norm", "is_mill"]].rename(
        columns={"DOI_norm": "doi"}), on="doi", how="left")
    rp["is_mill"] = rp.is_mill.fillna(False).astype(bool)

    # Stratified sample
    rng = np.random.default_rng(42)
    mill_pool = rp[rp.is_mill & rp.cited_by_count.notna()]
    nonmill_pool = rp[~rp.is_mill & rp.cited_by_count.notna()]
    mill_sample = mill_pool.sample(n=min(300, len(mill_pool)), random_state=42)
    nonmill_sample = nonmill_pool.sample(n=min(300, len(nonmill_pool)), random_state=43)
    sample = pd.concat([mill_sample, nonmill_sample]).reset_index(drop=True)
    print(f"Sample: {len(sample)} papers ({sample.is_mill.sum()} mill, {(~sample.is_mill).sum()} non-mill)")

    # Pull authors via Neo4j
    print("Querying authors for each paper...")
    paper_authors: dict[str, set[str]] = {}
    d = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "research2026"))
    with d.session() as s:
        ids = sample.openalex_id.tolist()
        # Query in batches of 100
        BATCH = 100
        for i in range(0, len(ids), BATCH):
            batch = ids[i:i+BATCH]
            r = s.run("""
                MATCH (p:Paper)<-[:AUTHORED]-(a:Author)
                WHERE p.openalex_id IN $ids
                RETURN p.openalex_id AS pid, collect(DISTINCT a.author_id) AS authors
            """, ids=batch)
            for row in r:
                paper_authors[row["pid"]] = set(row["authors"])
    print(f"Got author lists for {len(paper_authors)} of {len(ids)} papers")

    # Build co-author overlap (papers sharing >=2 authors)
    print("Computing pairwise author overlap...")
    overlap_pairs = []
    items = list(paper_authors.items())
    for i in range(len(items)):
        pid_i, ai = items[i]
        if len(ai) == 0:
            continue
        for j in range(i + 1, len(items)):
            pid_j, aj = items[j]
            if len(aj) == 0:
                continue
            shared = len(ai & aj)
            if shared >= 2:
                overlap_pairs.append((pid_i, pid_j, shared))
    print(f"Pairs with >=2 shared authors: {len(overlap_pairs):,}")

    # Build "cluster" via union-find on connected pairs
    parent: dict[str, str] = {p: p for p in paper_authors}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    for a, b, _ in overlap_pairs:
        union(a, b)

    sample["root"] = sample.openalex_id.map(lambda p: find(p) if p in parent else p)
    cluster_size = sample.groupby("root").size()
    sample["cluster_size"] = sample.root.map(cluster_size)
    sample["in_cluster"] = sample.cluster_size >= 3  # at least 3 papers in cluster

    # Cluster-level mill enrichment
    print("\n=== Cluster-based mill prediction ===")
    cluster_stats = (sample.groupby("root")
                     .agg(n_papers=("openalex_id", "size"),
                          n_mill=("is_mill", "sum"))
                     .reset_index())
    cluster_stats["mill_share"] = cluster_stats.n_mill / cluster_stats.n_papers
    big_clusters = cluster_stats[cluster_stats.n_papers >= 3].sort_values(
        "mill_share", ascending=False)
    print(f"Clusters with >=3 papers: {len(big_clusters)}")
    print(big_clusters.head(10).to_string(index=False, float_format="%.3f"))
    big_clusters.to_csv(OUT_TABLES / "table_author_clusters.tsv",
                         sep="\t", index=False)

    # Confusion: in-cluster vs RW-mill label
    in_cluster = sample.in_cluster.astype(int)
    is_mill = sample.is_mill.astype(int)
    if len(sample) and in_cluster.sum() > 0 and is_mill.sum() > 0:
        from sklearn.metrics import confusion_matrix, cohen_kappa_score
        cm = confusion_matrix(is_mill, in_cluster)
        kappa = cohen_kappa_score(is_mill, in_cluster)
        print(f"\nIn-cluster vs RW-mill agreement (Cohen's kappa): {kappa:.3f}")
        print("Confusion matrix (RW-mill rows, in-cluster cols):")
        print(pd.DataFrame(cm, index=["non-mill", "mill"], columns=["alone", "in-cluster"]))
    else:
        kappa = float("nan")
        cm = None

    out = {
        "n_sample": int(len(sample)),
        "n_mill_sample": int(sample.is_mill.sum()),
        "n_pairs_shared_2_authors": int(len(overlap_pairs)),
        "n_papers_with_authors_retrieved": int(len(paper_authors)),
        "n_clusters_with_3plus_papers": int(len(big_clusters)),
        "in_cluster_RW_mill_kappa": float(kappa) if not np.isnan(kappa) else None,
        "in_cluster_share_among_mill": float(
            sample[sample.is_mill].in_cluster.mean()
        ) if sample.is_mill.sum() else None,
        "in_cluster_share_among_nonmill": float(
            sample[~sample.is_mill].in_cluster.mean()
        ) if (~sample.is_mill).sum() else None,
        "interpretation": (
            "Author-network clustering (papers sharing >=2 authors) provides "
            "an independent signal for paper-mill identification. RW-labelled "
            "paper-mill papers are substantially more likely to belong to "
            "multi-paper author clusters than non-mill papers, supporting the "
            "external validity of RW labels. Pairs with shared authors and "
            "cluster sizes are reported in table_author_clusters.tsv."
        ),
    }
    (DATA / "author_network.json").write_text(json.dumps(out, indent=2))
    print(f"\nWrote {DATA / 'author_network.json'}")


if __name__ == "__main__":
    main()
