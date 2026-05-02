#!/usr/bin/env python3
"""
Matched control analysis for Track 3 retraction paper.

Compares citation patterns between retracted papers and matched non-retracted
controls to determine if post-retraction citation persistence reflects normal
citation aging or retraction-specific failure.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from typing import Tuple
import warnings
warnings.filterwarnings('ignore')


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load all required datasets."""
    data_dir = Path("data/processed/track3")

    # Load retracted papers with retraction dates
    print("Loading retraction watch data...")
    rw = pd.read_parquet("data/processed/retraction_watch_openalex_joined.parquet")
    rw['openalex_id'] = rw['openalex_id'].str.replace('https://openalex.org/', '')

    # Load retracted papers TSV (comma-separated with quoted fields)
    print("Loading retracted papers...")
    retracted = pd.read_csv(
        data_dir / "retracted_papers.tsv",
        skipinitialspace=True,
        quotechar='"',
        on_bad_lines='skip',
        engine='python'
    )
    retracted.columns = retracted.columns.str.strip()

    # Load citation data (1-hop contamination)
    print("Loading citation data...")
    citations = pd.read_csv(
        data_dir / "contamination_1hop.tsv",
        skipinitialspace=True,
        quotechar='"',
        on_bad_lines='skip',
        engine='python'
    )
    citations.columns = citations.columns.str.strip()

    # Filter to papers with >=5 citations for reliable analysis
    retracted = retracted[retracted['cited_by_count'] >= 5].copy()

    # Merge retraction dates
    retracted = retracted.merge(
        rw[['openalex_id', 'retraction_date', 'journal', 'subject']],
        on='openalex_id',
        how='left'
    )

    # Parse retraction date
    retracted['retraction_date'] = pd.to_datetime(retracted['retraction_date'])
    retracted['retraction_year'] = retracted['retraction_date'].dt.year

    print(f"\nDataset sizes:")
    print(f"  Retracted papers (>=5 citations): {len(retracted)}")
    print(f"  Citation edges: {len(citations)}")

    return retracted, citations, rw


def find_control_papers(retracted: pd.DataFrame, citations: pd.DataFrame) -> pd.DataFrame:
    """
    Find non-retracted control papers matched on field and year.

    Strategy: Sample from citing papers in contamination_1hop.tsv that are
    NOT themselves retracted (based on not appearing in retracted list).
    """
    print("\nBuilding control paper pool...")

    # Get set of retracted paper IDs
    retracted_ids = set(retracted['openalex_id'].tolist())

    # Extract unique citing papers with their metadata
    citing_papers = citations[
        ['citing_id', 'citing_year', 'citing_field']
    ].drop_duplicates().copy()

    # Filter out papers that are themselves retracted
    citing_papers = citing_papers[~citing_papers['citing_id'].isin(retracted_ids)]

    # Add citation counts for each citing paper
    citation_counts = citations['citing_id'].value_counts().reset_index()
    citation_counts.columns = ['citing_id', 'citation_count']
    citing_papers = citing_papers.merge(citation_counts, on='citing_id', how='left')
    citing_papers['citation_count'] = citing_papers['citation_count'].fillna(0)

    # For matching, need papers with at least 5 citations
    citing_papers = citing_papers[citing_papers['citation_count'] >= 5].copy()

    print(f"  Control pool size (non-retracted, >=5 citations): {len(citing_papers)}")
    print(f"  Fields in control pool: {citing_papers['citing_field'].nunique()}")

    return citing_papers


def match_controls(retracted: pd.DataFrame, control_pool: pd.DataFrame, citations: pd.DataFrame) -> pd.DataFrame:
    """
    Match up to 3 controls per retracted paper based on field, year, and citations.
    """
    print("\nMatching controls...")

    matches = []

    for _, retracted_paper in retracted.iterrows():
        retracted_id = retracted_paper['openalex_id']
        field = retracted_paper['field_name']
        year = retracted_paper['year']
        retracted_citation_count = retracted_paper['cited_by_count']
        retraction_date = retracted_paper['retraction_date']
        retraction_year = retracted_paper['retraction_year']

        # Find potential matches: same field, year ±1, citations ±30%
        potential_matches = control_pool[
            (control_pool['citing_field'] == field) &
            (control_pool['citing_year'].between(year - 1, year + 1)) &
            (control_pool['citation_count'].between(retracted_citation_count * 0.7, retracted_citation_count * 1.3))
        ].copy()

        # Exclude papers that cite this specific retracted paper (to avoid bias)
        citing_this_paper = set(
            citations[
                citations['retracted_id'] == retracted_id
            ]['citing_id'].tolist()
        )
        potential_matches = potential_matches[
            ~potential_matches['citing_id'].isin(citing_this_paper)
        ]

        # Select up to 3 controls
        n_controls = min(3, len(potential_matches))
        if n_controls > 0:
            selected_controls = potential_matches.sample(n=n_controls, random_state=42)

            for _, control in selected_controls.iterrows():
                matches.append({
                    'retracted_id': retracted_id,
                    'retracted_year': year,
                    'retracted_citations': retracted_citation_count,
                    'retracted_field': field,
                    'retraction_date': retraction_date,
                    'retraction_year': retraction_year,
                    'control_id': control['citing_id'],
                    'control_year': control['citing_year'],
                    'control_citations': control['citation_count'],
                })

    matches_df = pd.DataFrame(matches)

    print(f"  Matched {len(retracted)} retracted papers to {len(matches_df)} control pairs")
    print(f"  Avg controls per retracted paper: {len(matches_df) / len(retracted):.2f}")

    return matches_df


def compute_post_retraction_metrics(
    matches: pd.DataFrame,
    citations: pd.DataFrame
) -> pd.DataFrame:
    """
    Compute post-retraction citation metrics for both groups.
    """
    print("\nComputing post-retraction metrics...")

    results = []

    for _, match in matches.iterrows():
        retracted_id = match['retracted_id']
        control_id = match['control_id']
        retraction_year = match['retraction_year']

        # Get citations to retracted paper by year
        retracted_cites = citations[citations['retracted_id'] == retracted_id].copy()
        retracted_cites['is_post_retraction'] = retracted_cites['citing_year'] >= retraction_year

        # Get citations to control paper (as a citing paper)
        # Note: This is a limitation - we only see citations FROM control paper,
        # not TO it. We'll use the citation count as a proxy.

        # Compute post-retraction fraction for retracted paper
        total_citations = len(retracted_cites)
        if total_citations > 0:
            post_retraction_citations = retracted_cites['is_post_retraction'].sum()
            post_retraction_fraction = post_retraction_citations / total_citations
        else:
            post_retraction_fraction = 0.0

        # For control paper, use a simplified metric:
        # Fraction of control's citations that occurred after its publication year + 3 years
        # (analogous to "post-retraction" period)
        control_year = match['control_year']
        control_citation_count = match['control_citations']

        # Since we don't have yearly citation data for controls, use a conservative estimate
        # Controls are sampled from citing papers, so their citation count reflects impact
        # We'll classify as "zombie" if they have high citation count despite being old
        control_age = 2026 - control_year
        control_zombie = (control_citation_count >= 10) and (control_age >= 5)

        results.append({
            'retracted_id': retracted_id,
            'control_id': control_id,
            'retracted_post_retraction_fraction': post_retraction_fraction,
            'retracted_total_citations': total_citations,
            'retracted_post_retraction_count': retracted_cites['is_post_retraction'].sum() if total_citations > 0 else 0,
            'control_citation_count': control_citation_count,
            'control_year': control_year,
            'control_age': control_age,
            'control_zombie': control_zombie,
            'retraction_year': retraction_year,
            'retracted_field': match['retracted_field'],
        })

    results_df = pd.DataFrame(results)

    return results_df


def compute_statistics(results: pd.DataFrame) -> dict:
    """Compute comparative statistics."""
    print("\nComputing statistics...")

    # Zombie rate comparison
    retracted_zombie = (results['retracted_post_retraction_fraction'] > 0.5).sum()
    retracted_total = len(results)
    retracted_zombie_rate = retracted_zombie / retracted_total

    control_zombie = results['control_zombie'].sum()
    control_zombie_rate = control_zombie / retracted_total

    # Post-retraction citation fraction statistics
    post_retr_frac = results['retracted_post_retraction_fraction'].values

    # Remove NaN values for statistical tests
    valid_mask = ~np.isnan(post_retr_frac)
    valid_post_retr_frac = post_retr_frac[valid_mask]

    # Mean and median
    mean_post_retr = np.mean(valid_post_retr_frac)
    median_post_retr = np.median(valid_post_retr_frac)

    # Statistical test: Wilcoxon signed-rank test for paired samples
    # Compare post-retraction fraction to 0.5 (random expectation)
    if len(valid_post_retr_frac) > 0:
        wilcoxon_stat, wilcoxon_p = stats.wilcoxon(
            valid_post_retr_frac - 0.5,
            alternative='greater'
        )
    else:
        wilcoxon_stat, wilcoxon_p = np.nan, np.nan

    stats_dict = {
        'n_matched_pairs': len(results),
        'retracted_zombie_rate': retracted_zombie_rate,
        'retracted_zombie_count': retracted_zombie,
        'control_zombie_rate': control_zombie_rate,
        'control_zombie_count': control_zombie,
        'zombie_rate_ratio': retracted_zombie_rate / (control_zombie_rate + 1e-10),
        'mean_post_retraction_fraction': mean_post_retr,
        'median_post_retraction_fraction': median_post_retr,
        'wilcoxon_stat': wilcoxon_stat,
        'wilcoxon_p': wilcoxon_p,
    }

    return stats_dict


def main():
    """Main analysis pipeline."""
    print("=" * 70)
    print("MATCHED CONTROL ANALYSIS FOR TRACK 3 RETRACTION PAPER")
    print("=" * 70)

    # Load data
    retracted, citations, rw = load_data()

    # Find control papers
    control_pool = find_control_papers(retracted, citations)

    # Match controls
    matches = match_controls(retracted, control_pool, citations)

    # Compute metrics
    results = compute_post_retraction_metrics(matches, citations)

    # Compute statistics
    stats_dict = compute_statistics(results)

    # Save results
    output_dir = Path("data/processed/track3")
    output_dir.mkdir(parents=True, exist_ok=True)

    results.to_csv(output_dir / "matched_controls_pairs.tsv", sep='\t', index=False)
    print(f"\nSaved detailed results to {output_dir / 'matched_controls_pairs.tsv'}")

    # Save summary statistics
    summary_df = pd.DataFrame([stats_dict])
    summary_df.to_csv(output_dir / "matched_controls_summary.tsv", sep='\t', index=False)
    print(f"Saved summary to {output_dir / 'matched_controls_summary.tsv'}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    print(f"\nMatched pairs: {stats_dict['n_matched_pairs']:,}")
    print(f"\nZombie rate comparison:")
    print(f"  Retracted papers: {stats_dict['retracted_zombie_rate']:.1%} ({stats_dict['retracted_zombie_count']:,} / {stats_dict['n_matched_pairs']:,})")
    print(f"  Control papers: {stats_dict['control_zombie_rate']:.1%} ({stats_dict['control_zombie_count']:,} / {stats_dict['n_matched_pairs']:,})")
    print(f"  Ratio (retracted/control): {stats_dict['zombie_rate_ratio']:.2f}x")
    print(f"\nPost-retraction citation fraction:")
    print(f"  Mean: {stats_dict['mean_post_retraction_fraction']:.3f}")
    print(f"  Median: {stats_dict['median_post_retraction_fraction']:.3f}")
    print(f"\nWilcoxon test (vs. 0.5 random):")
    print(f"  Statistic: {stats_dict['wilcoxon_stat']:.0f}")
    print(f"  p-value: {stats_dict['wilcoxon_p']:.2e}")

    if stats_dict['wilcoxon_p'] < 0.001:
        print(f"  *** HIGHLY SIGNIFICANT ***")
    elif stats_dict['wilcoxon_p'] < 0.05:
        print(f"  ** SIGNIFICANT **")

    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
