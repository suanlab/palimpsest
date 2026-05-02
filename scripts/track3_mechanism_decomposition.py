#!/usr/bin/env python3
"""[2A] Stepwise mechanism decomposition: how much of the 4.31x paper-mill
zombie effect is attributable to publisher / journal / field / paper content?

Approach: conditional logistic-style stratified analysis with progressively
finer strata. We compute Mantel-Haenszel pooled odds ratios at each level:

  L0  unadjusted (baseline 4.31x)
  L1  + retraction year (5-year bins)
  L2  + retraction year + field
  L3  + retraction year + field + publisher
  L4  + retraction year + field + publisher + journal

The attenuation from L0 to L4 quantifies how much of the apparent paper-mill
effect is mediated through these structural confounders. The residual at L4
is the "true" content-specific paper-mill effect.

Outputs:
  data/processed/track3/mechanism_decomposition.json
  data/processed/track3/tables/table_mechanism_or.tsv
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "retraction_watch" / "retraction-watch-data" / "retraction_watch.csv"
DATA = ROOT / "data" / "processed" / "track3"
OUT_TABLES = DATA / "tables"
OUT_TABLES.mkdir(parents=True, exist_ok=True)


def mh_or(strata: dict[tuple, list[int]]) -> tuple[float, int, int, int]:
    """Mantel-Haenszel pooled OR over strata where each stratum is [a,b,c,d].

    a = mill zombie, b = mill non-zombie
    c = non-mill zombie, d = non-mill non-zombie
    """
    num = 0.0
    den = 0.0
    used = 0
    n_total = 0
    for s in strata.values():
        a, b, c, d = s
        n = a + b + c + d
        if n == 0:
            continue
        # Skip degenerate strata (no variation)
        if (a + b == 0) or (c + d == 0) or (a + c == 0) or (b + d == 0):
            continue
        num += a * d / n
        den += b * c / n
        used += 1
        n_total += n
    or_ = num / den if den > 0 else float("nan")
    return or_, used, n_total


def main() -> None:
    print("Loading...")
    rw = pd.read_csv(RAW, low_memory=False)
    rw["DOI_norm"] = rw.OriginalPaperDOI.astype(str).str.strip().str.lower()
    rw["is_mill"] = rw.Reason.apply(lambda s: "Paper Mill" in str(s))
    rw["publisher_norm"] = rw.Publisher.fillna("Unknown").str.strip()
    rw["journal_norm"] = rw.Journal.fillna("Unknown").str.strip()
    rw["retract_year"] = pd.to_datetime(rw.RetractionDate, errors="coerce").dt.year
    rw_unique = rw.drop_duplicates(subset=["DOI_norm"], keep="first")

    pairs = pd.read_csv(DATA / "matched_controls_pairs.tsv", sep="\t")
    pairs["retracted_id_clean"] = pairs.retracted_id.astype(str).str.strip()
    rp = pd.read_csv(DATA / "retracted_papers.tsv", sep=",", quotechar='"',
                     engine="python", on_bad_lines="skip")
    rp.columns = [c.strip() for c in rp.columns]
    rp["doi"] = rp.doi.astype(str).str.strip().str.strip('"').str.lower()
    rp["openalex_id_clean"] = rp.openalex_id.astype(str).str.strip().str.strip('"')
    rp["field_name"] = rp.field_name.astype(str).str.strip().str.strip('"')
    rp = rp.drop_duplicates(subset=["doi"], keep="first")
    rp = rp.merge(
        rw_unique[["DOI_norm", "publisher_norm", "journal_norm", "is_mill",
                   "retract_year"]].rename(columns={"DOI_norm": "doi"}),
        on="doi", how="left",
    )
    rp = rp.drop_duplicates(subset=["openalex_id_clean"], keep="first")

    pairs = pairs.merge(
        rp[["openalex_id_clean", "publisher_norm", "journal_norm", "is_mill",
            "retract_year", "field_name"]].rename(
            columns={"openalex_id_clean": "retracted_id_clean"}),
        on="retracted_id_clean", how="left",
    )
    pairs["publisher_norm"] = pairs.publisher_norm.fillna("Unknown")
    pairs["journal_norm"] = pairs.journal_norm.fillna("Unknown")
    pairs["field_name"] = pairs.field_name.fillna("Unknown")
    pairs["is_mill"] = pairs.is_mill.fillna(False).astype(bool)
    pairs["retract_year_bin"] = (pairs.retract_year // 5).astype("Int64") * 5
    pairs["retracted_zombie"] = (pairs.retracted_post_retraction_fraction >= 0.5).astype(int)

    # Build 2x2 strata at each level: cells are mill/non-mill x zombie/non-zombie
    def build_strata(group_cols: list[str]) -> dict[tuple, list[int]]:
        out: dict[tuple, list[int]] = {}
        if not group_cols:
            # Single stratum
            mill = pairs[pairs.is_mill]
            nm = pairs[~pairs.is_mill]
            a = int(mill.retracted_zombie.sum()); b = int(len(mill) - a)
            c = int(nm.retracted_zombie.sum()); d = int(len(nm) - c)
            out[("ALL",)] = [a, b, c, d]
            return out
        for key, sub in pairs.groupby(group_cols):
            mill = sub[sub.is_mill]
            nm = sub[~sub.is_mill]
            a = int(mill.retracted_zombie.sum()); b = int(len(mill) - a)
            c = int(nm.retracted_zombie.sum()); d = int(len(nm) - c)
            if isinstance(key, tuple):
                out[key] = [a, b, c, d]
            else:
                out[(key,)] = [a, b, c, d]
        return out

    levels = [
        ("L0_unadjusted", []),
        ("L1_+year", ["retract_year_bin"]),
        ("L2_+year_+field", ["retract_year_bin", "field_name"]),
        ("L3_+year_+field_+publisher", ["retract_year_bin", "field_name", "publisher_norm"]),
        ("L4_+year_+field_+publisher_+journal",
         ["retract_year_bin", "field_name", "publisher_norm", "journal_norm"]),
    ]

    rows = []
    print("\n=== Stepwise Mantel-Haenszel OR ===")
    print(f"{'Level':45s}  {'OR':>6s}  {'strata':>7s}  {'N':>10s}")
    for name, cols in levels:
        strata = build_strata(cols)
        or_, used, n = mh_or(strata)
        print(f"{name:45s}  {or_:>6.3f}  {used:>7,}  {n:>10,}")
        rows.append({
            "level": name,
            "controls": cols,
            "OR_MH": float(or_),
            "n_strata": int(used),
            "n_pairs": int(n),
        })

    pd.DataFrame(rows).to_csv(OUT_TABLES / "table_mechanism_or.tsv", sep="\t", index=False)

    # Also: mill effect on the OUTCOME zombie-vs-not, separately for control papers
    # to verify control-side balance.
    print("\n=== Sanity: control-side zombie rate by mill flag ===")
    for is_mill_label, sub in pairs.groupby("is_mill"):
        cz = sub.control_zombie.mean()
        print(f"  is_mill={is_mill_label}: control zombie rate = {cz:.3f}, n={len(sub):,}")

    # Decomposition: % attenuation explained by each addition
    or_l0 = rows[0]["OR_MH"]
    or_l4 = rows[-1]["OR_MH"]
    if not np.isnan(or_l0) and not np.isnan(or_l4) and or_l0 > 0:
        attenuation_pct = (1 - (or_l4 - 1) / max(or_l0 - 1, 1e-9)) * 100
    else:
        attenuation_pct = float("nan")

    out = {
        "stepwise_OR": rows,
        "L0_to_L4_attenuation_pct": float(attenuation_pct),
        "interpretation": (
            f"The unadjusted paper-mill vs non-mill OR (zombie outcome) is "
            f"{or_l0:.2f}. After controlling for retraction year, field, "
            f"publisher, and journal, the OR attenuates to {or_l4:.2f} "
            f"({attenuation_pct:.0f}% of the original effect attributable to "
            "these structural confounders). The residual OR represents the "
            "content-specific paper-mill effect after holding constant the "
            "publisher/journal/field/year of the retraction. This decomposition "
            "directly addresses the reviewer concern that the headline finding "
            "is mostly a Hindawi-publisher artefact."
        ),
    }
    (DATA / "mechanism_decomposition.json").write_text(json.dumps(out, indent=2))
    print(f"\nWrote {DATA / 'mechanism_decomposition.json'}")


if __name__ == "__main__":
    main()
