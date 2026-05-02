"""Phase 1B: Right-Censoring Correction via Survival Analysis.

Addresses the reviewer concern: "Self-correction acceleration" may be an artifact
of right-censoring — papers retracted recently haven't had enough time to accumulate
post-retraction citations, making decay appear faster than it is.

Uses Kaplan-Meier survival analysis with Cox proportional hazards regression.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "processed" / "track3"
OUTPUT_DIR = DATA_DIR
RW_PATH = ROOT / "data" / "processed" / "retraction_watch_openalex_joined.parquet"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load hop1 edges and retraction dates."""
    hop1 = pd.read_csv(
        DATA_DIR / "contamination_1hop.tsv",
        skipinitialspace=True, quotechar='"', on_bad_lines="skip", engine="python",
    )
    hop1.columns = hop1.columns.str.strip()

    rw = pd.read_parquet(RW_PATH)
    rw["retraction_year"] = pd.to_datetime(
        rw["retraction_date"], format="mixed", errors="coerce"
    ).dt.year
    rw["oa_id"] = rw["openalex_id"].str.replace("https://openalex.org/", "", regex=False)

    return hop1, rw


def build_paper_time_series(
    hop1: pd.DataFrame, rw: pd.DataFrame
) -> pd.DataFrame:
    """Build per-paper citation time series with retraction dates."""
    # Merge with retraction dates
    rw_map = rw[["oa_id", "retraction_year"]].dropna(subset=["retraction_year"])
    rw_map["retraction_year"] = rw_map["retraction_year"].astype(int)

    merged = hop1.merge(
        rw_map, left_on="retracted_id", right_on="oa_id", how="inner"
    )
    logger.info("Merged edges with retraction dates: %d", len(merged))

    # Classify timing
    merged["timing"] = "unknown"
    merged.loc[merged["citing_year"] < merged["retraction_year"], "timing"] = "pre"
    merged.loc[merged["citing_year"] == merged["retraction_year"], "timing"] = "same"
    merged.loc[merged["citing_year"] > merged["retraction_year"], "timing"] = "post"

    # Per-paper: year-level citation counts
    paper_year = merged.groupby(
        ["retracted_id", "retraction_year", "retracted_year", "citing_year", "timing"]
    ).size().reset_index(name="n_citations")

    return paper_year


def prepare_survival_data(paper_year: pd.DataFrame) -> pd.DataFrame:
    """Prepare survival analysis input: one row per retracted paper.

    Event: post-retraction citations drop below 50% of peak pre-retraction annual rate.
    Time: years since retraction.
    Censored: paper hasn't reached the threshold by 2025.
    """
    records = []

    for retracted_id, grp in paper_year.groupby("retracted_id"):
        retr_year = grp["retraction_year"].iloc[0]
        pub_year = grp["retracted_year"].iloc[0]

        pre = grp[grp["timing"] == "pre"]
        post = grp[grp["timing"] == "post"]

        pre_total = pre["n_citations"].sum()
        post_total = post["n_citations"].sum()

        if pre_total < 5:
            continue  # need enough pre-retraction citations to define a baseline

        # Peak pre-retraction annual citation rate
        pre_peak = pre["n_citations"].max() if len(pre) > 0 else 0
        threshold = pre_peak * 0.5

        # Find when post-retraction citations first drop below threshold
        post_sorted = post.sort_values("citing_year")
        event_time = None
        event_occurred = False

        for _, row in post_sorted.iterrows():
            if row["n_citations"] < threshold and threshold > 0:
                event_time = row["citing_year"] - retr_year
                event_occurred = True
                break

        # Observation time (max years since retraction we can observe)
        obs_time = 2025 - retr_year

        if event_occurred and event_time is not None:
            records.append({
                "retracted_id": retracted_id,
                "retraction_year": retr_year,
                "pub_year": pub_year,
                "pre_total": pre_total,
                "post_total": post_total,
                "pre_peak": pre_peak,
                "threshold": threshold,
                "time": event_time,
                "event": 1,
                "obs_time": obs_time,
                "decade": "2000s" if retr_year < 2010 else ("2010s" if retr_year < 2020 else "2020s"),
            })
        else:
            # Censored: event hasn't occurred yet
            records.append({
                "retracted_id": retracted_id,
                "retraction_year": retr_year,
                "pub_year": pub_year,
                "pre_total": pre_total,
                "post_total": post_total,
                "pre_peak": pre_peak,
                "threshold": threshold,
                "time": obs_time,
                "event": 0,
                "obs_time": obs_time,
                "decade": "2000s" if retr_year < 2010 else ("2010s" if retr_year < 2020 else "2020s"),
            })

    df = pd.DataFrame(records)
    logger.info("Survival data: %d papers (%d events, %d censored)",
                len(df), df["event"].sum(), (df["event"] == 0).sum())
    return df


def run_survival_analysis(surv_df: pd.DataFrame) -> dict:
    """Run Kaplan-Meier and Cox regression."""
    results = {}

    # Try lifelines first
    try:
        from lifelines import KaplanMeierFitter, CoxPHFitter
        from lifelines.statistics import logrank_test
    except ImportError:
        logger.info("Installing lifelines...")
        import subprocess
        subprocess.run(["uv", "pip", "install", "lifelines"], check=True)
        from lifelines import KaplanMeierFitter, CoxPHFitter
        from lifelines.statistics import logrank_test

    # Overall KM
    kmf = KaplanMeierFitter()
    kmf.fit(surv_df["time"], surv_df["event"])
    results["km_median"] = kmf.median_survival_time_
    results["km_confidence_interval"] = kmf.confidence_interval_.to_dict() if hasattr(kmf, 'confidence_interval_') else None

    # Per-decade KM
    decade_results = {}
    for decade in ["2000s", "2010s", "2020s"]:
        subset = surv_df[surv_df["decade"] == decade]
        if len(subset) < 10:
            continue
        kmf_d = KaplanMeierFitter()
        kmf_d.fit(subset["time"], subset["event"])
        decade_results[decade] = {
            "n": len(subset),
            "events": int(subset["event"].sum()),
            "censored": int((subset["event"] == 0).sum()),
            "median_survival": float(kmf_d.median_survival_time_) if not np.isnan(kmf_d.median_survival_time_) else None,
            "survival_at_5yr": float(kmf_d.predict(5)) if 5 in kmf_d.survival_function_.index or kmf_d.survival_function_.index.max() >= 5 else None,
        }
    results["decade_km"] = decade_results

    # Log-rank tests (pairwise between decades)
    logrank_results = {}
    decades = ["2000s", "2010s", "2020s"]
    for i in range(len(decades)):
        for j in range(i + 1, len(decades)):
            d1 = surv_df[surv_df["decade"] == decades[i]]
            d2 = surv_df[surv_df["decade"] == decades[j]]
            if len(d1) < 10 or len(d2) < 10:
                continue
            lr = logrank_test(d1["time"], d2["time"], d1["event"], d2["event"])
            logrank_results[f"{decades[i]}_vs_{decades[j]}"] = {
                "test_statistic": float(lr.test_statistic),
                "p_value": float(lr.p_value),
            }
    results["logrank"] = logrank_results

    # Cox regression (retraction_year only, obs_time is collinear with censoring)
    cox_df = surv_df[["time", "event", "retraction_year"]].copy()
    cox_df.columns = ["duration", "event", "retraction_year"]
    try:
        cph = CoxPHFitter(penalizer=0.1)
        cph.fit(cox_df, duration_col="duration", event_col="event")
        results["cox"] = {
            "hazard_ratio_retraction_year": float(np.exp(cph.params_["retraction_year"])),
            "coef": float(cph.params_["retraction_year"]),
            "p_value": float(cph.summary.loc["retraction_year", "p"]),
            "ci_lower": float(cph.confidence_intervals_.loc["retraction_year", "95% lower-bound"]),
            "ci_upper": float(cph.confidence_intervals_.loc["retraction_year", "95% upper-bound"]),
            "concordance": float(cph.concordance_index_),
        }
    except Exception as e:
        results["cox_error"] = str(e)

    # Censoring fraction by decade
    censoring = {}
    for decade in decades:
        subset = surv_df[surv_df["decade"] == decade]
        if len(subset) > 0:
            censoring[decade] = {
                "censored_pct": float((subset["event"] == 0).mean() * 100),
                "mean_obs_time": float(subset["obs_time"].mean()),
            }
    results["censoring_by_decade"] = censoring

    return results


def main() -> None:
    logger.info("Loading data...")
    hop1, rw = load_data()

    logger.info("Building paper time series...")
    paper_year = build_paper_time_series(hop1, rw)

    logger.info("Preparing survival data...")
    surv_df = prepare_survival_data(paper_year)

    # Save survival data
    surv_path = OUTPUT_DIR / "survival_analysis.tsv"
    surv_df.to_csv(surv_path, sep="\t", index=False)
    logger.info("Survival data saved to %s", surv_path)

    logger.info("Running survival analysis...")
    results = run_survival_analysis(surv_df)

    # Save results
    results_path = OUTPUT_DIR / "survival_results.json"
    results_path.write_text(json.dumps(results, indent=2, default=str))
    logger.info("Results saved to %s", results_path)

    # Print summary
    print("\n" + "=" * 60)
    print("RIGHT-CENSORING CORRECTION: SURVIVAL ANALYSIS")
    print("=" * 60)
    print(f"\nPapers analyzed: {len(surv_df):,}")
    print(f"  Events (citation drop <50% peak): {int(surv_df['event'].sum()):,}")
    print(f"  Censored: {int((surv_df['event'] == 0).sum()):,}")
    print(f"  Overall median survival: {results.get('km_median', 'N/A')}")

    print("\nPer-decade Kaplan-Meier:")
    for decade, stats in results.get("decade_km", {}).items():
        med = stats.get("median_survival", "N/A")
        med_str = f"{med:.1f} yrs" if med else "not reached"
        print(f"  {decade}: N={stats['n']:,}, events={stats['events']:,}, "
              f"censored={stats['censored']:,} ({stats['censored']/stats['n']*100:.1f}%), "
              f"median={med_str}")

    print("\nLog-rank tests:")
    for pair, stats in results.get("logrank", {}).items():
        sig = "***" if stats["p_value"] < 0.001 else ("**" if stats["p_value"] < 0.01 else ("*" if stats["p_value"] < 0.05 else ""))
        print(f"  {pair}: χ²={stats['test_statistic']:.2f}, p={stats['p_value']:.4f} {sig}")

    if "cox" in results:
        cox = results["cox"]
        print(f"\nCox regression:")
        print(f"  HR per year = {cox['hazard_ratio_retraction_year']:.4f}")
        print(f"  β = {cox['coef']:.4f}, p = {cox['p_value']:.4f}")
        print(f"  95% CI: [{cox['ci_lower']:.4f}, {cox['ci_upper']:.4f}]")
        print(f"  Concordance = {cox['concordance']:.3f}")
        print(f"\n  → HR > 1 means later retractions have HIGHER hazard of citation drop")
        print(f"  → HR < 1 means later retractions have LOWER hazard (self-correction decelerating)")

    print("\nCensoring by decade:")
    for decade, stats in results.get("censoring_by_decade", {}).items():
        print(f"  {decade}: {stats['censored_pct']:.1f}% censored, mean obs = {stats['mean_obs_time']:.1f} yrs")


if __name__ == "__main__":
    main()
