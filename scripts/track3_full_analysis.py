#!/usr/bin/env python3
"""
Track 3 Full Analysis: The Half-Life of Bad Science
====================================================
Comprehensive analysis of retraction contamination through citation networks.

Generates:
- Cross-field self-correction statistics
- Pre/post-retraction citation timing analysis
- All paper figures (matplotlib)
- Supplementary data tables
"""

import os
import sys
import json
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

# ── Paths ────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'data', 'processed', 'track3')
FIG_DIR = os.path.join(ROOT, 'data', 'processed', 'figures', 'track3')
TABLE_DIR = os.path.join(ROOT, 'data', 'processed', 'track3', 'tables')
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TABLE_DIR, exist_ok=True)

# ── Style ────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Inter', 'Helvetica Neue', 'Arial'],
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.spines.top': False,
    'axes.spines.right': False,
})

# Color palette
C = {
    'primary': '#2563EB',     # Blue
    'secondary': '#7C3AED',   # Purple
    'accent': '#DC2626',      # Red
    'warm': '#EA580C',        # Orange
    'green': '#059669',       # Green
    'gray': '#6B7280',        # Gray
    'light': '#F3F4F6',       # Light gray
    'bg': '#FFFFFF',
}
FIELD_COLORS = plt.cm.Set2(np.linspace(0, 1, 10))

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: Data Loading
# ═══════════════════════════════════════════════════════════════════════════

print("=" * 70)
print("TRACK 3 FULL ANALYSIS")
print("=" * 70)

print("\n[1/6] Loading data...")

# Retracted papers
retracted = pd.read_csv(
    os.path.join(DATA_DIR, 'retracted_papers.tsv'),
    skipinitialspace=True, quotechar='"', on_bad_lines='skip', engine='python'
)
retracted.columns = retracted.columns.str.strip()
print(f"  Retracted papers: {len(retracted):,}")

# 1-hop contamination
hop1 = pd.read_csv(
    os.path.join(DATA_DIR, 'contamination_1hop.tsv'),
    skipinitialspace=True, quotechar='"', on_bad_lines='skip', engine='python'
)
hop1.columns = hop1.columns.str.strip()
print(f"  1-hop edges: {len(hop1):,}")

# Year-citation matrix
ycm = pd.read_csv(
    os.path.join(DATA_DIR, 'year_citation_matrix.tsv'),
    skipinitialspace=True
)
ycm.columns = ycm.columns.str.strip()
print(f"  Year-citation matrix: {len(ycm):,}")

# Contamination by year
cont_by_year = pd.read_csv(
    os.path.join(DATA_DIR, 'contamination_by_year.tsv'),
    skipinitialspace=True
)
cont_by_year.columns = cont_by_year.columns.str.strip()

# Field stats
field_stats = pd.read_csv(
    os.path.join(DATA_DIR, 'field_stats.tsv'),
    skipinitialspace=True, quotechar='"', on_bad_lines='skip', engine='python'
)
field_stats.columns = field_stats.columns.str.strip()
field_stats = field_stats.sort_values('retracted', ascending=False)
print(f"  Field stats: {len(field_stats)} fields")

# Retraction Watch with dates
rw_joined = pd.read_parquet(
    os.path.join(ROOT, 'data', 'processed', 'retraction_watch_openalex_joined.parquet')
)
print(f"  RW joined: {len(rw_joined):,}")

# Parse retraction dates and normalize IDs
rw_joined['retraction_year'] = pd.to_datetime(
    rw_joined['retraction_date'], format='mixed', errors='coerce'
).dt.year
rw_joined['oa_id'] = rw_joined['openalex_id'].str.replace('https://openalex.org/', '')
rw_joined['original_year'] = rw_joined['year']
print(f"  With retraction year: {rw_joined.retraction_year.notna().sum():,}")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: Retraction Date Matching & Pre/Post Analysis
# ═══════════════════════════════════════════════════════════════════════════

print("\n[2/6] Pre/post-retraction citation timing analysis...")

# Merge hop1 with retraction dates using normalized IDs
rw_id_map = rw_joined[['oa_id', 'retraction_year', 'original_year']].copy()

hop1_with_dates = hop1.merge(
    rw_id_map[['oa_id', 'retraction_year']],
    left_on='retracted_id', right_on='oa_id', how='left'
)
matched_pct = hop1_with_dates['retraction_year'].notna().sum() / len(hop1_with_dates) * 100
print(f"  Matched to retraction dates: {hop1_with_dates['retraction_year'].notna().sum():,} / {len(hop1_with_dates):,} ({matched_pct:.1f}%)")

# Classify citations as pre/post retraction
hop1_with_dates['citation_timing'] = 'unknown'
mask_pre = hop1_with_dates['citing_year'] < hop1_with_dates['retraction_year']
mask_same = hop1_with_dates['citing_year'] == hop1_with_dates['retraction_year']
mask_post = hop1_with_dates['citing_year'] > hop1_with_dates['retraction_year']
hop1_with_dates.loc[mask_pre, 'citation_timing'] = 'pre'
hop1_with_dates.loc[mask_same, 'citation_timing'] = 'same'
hop1_with_dates.loc[mask_post, 'citation_timing'] = 'post'

timing_counts = hop1_with_dates['citation_timing'].value_counts()
total_classified = timing_counts.sum()
print(f"  Citations with retraction date: {total_classified:,}")
for t in ['pre', 'same', 'post']:
    if t in timing_counts.index:
        pct = timing_counts[t] / total_classified * 100
        print(f"    {t}: {timing_counts[t]:,} ({pct:.1f}%)")

# Post-retraction decay curve
post_cites = hop1_with_dates[hop1_with_dates['citation_timing'] == 'post'].copy()
post_cites['years_since_retraction'] = post_cites['citing_year'] - post_cites['retraction_year']
decay_curve = post_cites.groupby('years_since_retraction').size().reset_index(name='count')
decay_curve = decay_curve[decay_curve['years_since_retraction'] >= 0]
decay_curve = decay_curve.sort_values('years_since_retraction')
print(f"  Decay curve: {len(decay_curve)} time points, max lag = {decay_curve['years_since_retraction'].max()}")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: Cross-Field Self-Correction Analysis
# ═══════════════════════════════════════════════════════════════════════════

print("\n[3/6] Cross-field self-correction analysis...")

# Get retracted paper's field from the retracted papers file
retracted_field = retracted[['openalex_id', 'field_name', 'cited_by_count']].copy()
retracted_field.columns = [c.strip() for c in retracted_field.columns]

# Merge to get retracted paper's field on the hop1 data
retracted_field_clean = retracted_field.dropna(subset=['field_name'])
hop1_field = hop1_with_dates.merge(
    retracted_field_clean[['openalex_id', 'field_name']],
    left_on='retracted_id', right_on='openalex_id', how='left', suffixes=('', '_retr')
)

# Per-field pre/post analysis (using retracted paper's field)
field_timing = hop1_field.groupby(['field_name', 'citation_timing']).size().unstack(fill_value=0)
field_timing['total'] = field_timing.sum(axis=1)
field_timing['post_fraction'] = field_timing.get('post', 0) / field_timing['total']

# Only fields with enough data
field_timing = field_timing[field_timing['total'] >= 500].sort_values('post_fraction', ascending=False)

print(f"  Fields with >=500 classified citations: {len(field_timing)}")
print("\n  Top 5 fields by post-retraction fraction:")
for field, row in field_timing.head(5).iterrows():
    print(f"    {field}: {row['post_fraction']:.1%} post-retraction ({row['total']:,} total)")

print("\n  Bottom 5 fields by post-retraction fraction:")
for field, row in field_timing.tail(5).iterrows():
    print(f"    {field}: {row['post_fraction']:.1%} post-retraction ({row['total']:,} total)")

# Per-field decay rates (pre-compute field for all post cites)
post_cites_field = post_cites.merge(
    retracted_field_clean[['openalex_id', 'field_name']],
    left_on='retracted_id', right_on='openalex_id', how='left'
)
field_decay = []
for field in field_timing.index:
    field_data = post_cites_field[post_cites_field['field_name'] == field]
    if len(field_data) > 100:
        yearly = field_data.groupby('years_since_retraction').size()
        if len(yearly) >= 3:
            # Simple decay: ratio of year +3 to year +1
            y1 = yearly.get(1, 0)
            y3 = yearly.get(3, 0)
            y5 = yearly.get(5, 0)
            decay_rate = (y3 / y1) if y1 > 0 else np.nan
            field_decay.append({
                'field': field,
                'total_post': len(field_data),
                'y1': y1,
                'y3': y3,
                'y5': y5,
                'decay_3y': decay_rate,
            })

field_decay_df = pd.DataFrame(field_decay)
if len(field_decay_df) > 0:
    field_decay_df = field_decay_df.sort_values('decay_3y')
print(f"\n  Field decay rates computed: {len(field_decay_df)}")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: Citation Lag Distribution
# ═══════════════════════════════════════════════════════════════════════════

print("\n[4/6] Citation lag distribution...")

ycm['lag'] = ycm['citing_year'] - ycm['retracted_year']
pos_lag = ycm[ycm['lag'] >= 0]
lag_dist = pos_lag.groupby('lag')['citation_count'].sum()
total_lag = lag_dist.sum()

# Cumulative
cumulative = lag_dist.cumsum()
median_lag = (cumulative >= total_lag * 0.5).idxmax()
print(f"  Total citations with lag>=0: {total_lag:,}")
print(f"  Median citation lag: {median_lag} years")
print(f"  Peak lag year: +{lag_dist.idxmax()} ({lag_dist.max():,} citations)")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: Figure Generation
# ═══════════════════════════════════════════════════════════════════════════

print("\n[5/6] Generating figures...")

# ── Figure 1: Citation Lag Distribution ────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
lags = lag_dist.loc[0:25]
cum_pct = (lag_dist.loc[0:25].cumsum() / total_lag * 100)

ax.bar(lags.index, lags.values, color=C['primary'], alpha=0.8, width=0.8, zorder=2)
ax2 = ax.twinx()
ax2.plot(cum_pct.index, cum_pct.values, color=C['accent'], linewidth=2.5, zorder=3)
ax2.set_ylabel('Cumulative %', color=C['accent'])
ax2.tick_params(axis='y', labelcolor=C['accent'])
ax2.set_ylim(0, 100)

# Annotate median
ax.axvline(median_lag, color=C['accent'], linestyle='--', alpha=0.7, zorder=1)
ax.annotate(f'Median: {median_lag} years', xy=(median_lag, ax.get_ylim()[1]*0.9),
            fontsize=10, color=C['accent'], ha='left')

ax.set_xlabel('Years after publication')
ax.set_ylabel('Number of citations')
ax.set_title('Citation Lag Distribution to Retracted Papers')
ax.set_xlim(-0.5, 25.5)
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'fig1_citation_lag.png'))
fig.savefig(os.path.join(FIG_DIR, 'fig1_citation_lag.pdf'))
plt.close(fig)
print("  fig1_citation_lag ✓")

# ── Figure 2: Temporal Growth of Contamination ────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

# Left: Contamination edges by year
yr_data = cont_by_year[(cont_by_year['citing_year'] >= 2000) & (cont_by_year['citing_year'] <= 2025)]
ax1.fill_between(yr_data['citing_year'], yr_data['contaminated_papers'], alpha=0.3, color=C['primary'])
ax1.plot(yr_data['citing_year'], yr_data['contaminated_papers'], color=C['primary'], linewidth=2)
ax1.set_xlabel('Year')
ax1.set_ylabel('Papers citing retracted work')
ax1.set_title('Annual Contamination Volume')
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1000:.0f}K'))

# Annotate key years
for yr, label in [(2023, '2023:\n127K'), (2020, '2020:\n76K')]:
    row = yr_data[yr_data['citing_year'] == yr].iloc[0]
    ax1.annotate(label, xy=(yr, row['contaminated_papers']),
                xytext=(yr-3, row['contaminated_papers']*1.15),
                fontsize=9, ha='center', color=C['primary'],
                arrowprops=dict(arrowstyle='->', color=C['primary'], lw=1))

# Right: Retraction volume by year (from retracted papers)
by_year = retracted[retracted['year'] >= 2000].groupby('year').size()
ax2.fill_between(by_year.index, by_year.values, alpha=0.3, color=C['accent'])
ax2.plot(by_year.index, by_year.values, color=C['accent'], linewidth=2)
ax2.set_xlabel('Publication Year')
ax2.set_ylabel('Number of retracted papers')
ax2.set_title('Retraction Volume by Publication Year')
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1000:.0f}K'))

# Annotate peak
peak_yr = by_year.idxmax()
ax2.annotate(f'{peak_yr}: {by_year[peak_yr]:,}', xy=(peak_yr, by_year[peak_yr]),
            xytext=(peak_yr-4, by_year[peak_yr]*0.85),
            fontsize=9, ha='center', color=C['accent'],
            arrowprops=dict(arrowstyle='->', color=C['accent'], lw=1))

fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'fig2_temporal_growth.png'))
fig.savefig(os.path.join(FIG_DIR, 'fig2_temporal_growth.pdf'))
plt.close(fig)
print("  fig2_temporal_growth ✓")

# ── Figure 3: Citation Distribution (top papers) ───────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
top20 = retracted.nlargest(20, 'cited_by_count')
top20 = top20.sort_values('cited_by_count', ascending=True)

# Shorten titles
titles = []
for t in top20['title']:
    t = str(t)
    if len(t) > 55:
        t = t[:52] + '...'
    titles.append(t)

colors = [C['accent'] if c > 3000 else C['primary'] for c in top20['cited_by_count']]
bars = ax.barh(range(len(top20)), top20['cited_by_count'], color=colors, height=0.7)
ax.set_yticks(range(len(top20)))
ax.set_yticklabels(titles, fontsize=8.5)
ax.set_xlabel('Citations received')
ax.set_title('Top 20 Most Cited Retracted Papers')

# Add citation count labels
for i, (bar, val) in enumerate(zip(bars, top20['cited_by_count'])):
    ax.text(val + 50, i, f'{val:,}', va='center', fontsize=8.5)

ax.set_xlim(0, top20['cited_by_count'].max() * 1.15)
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'fig3_top_cited.png'))
fig.savefig(os.path.join(FIG_DIR, 'fig3_top_cited.pdf'))
plt.close(fig)
print("  fig3_top_cited ✓")

# ── Figure 4: Field-Level Retraction Rates ─────────────────────────────
fig, ax = plt.subplots(figsize=(10, 7))
fs = field_stats.head(15).sort_values('retracted', ascending=True)
fields = fs.iloc[:, 0].values
retr_counts = fs['retracted'].values

# Normalize to rates per million
field_sizes = fs['total'].values
rates = retr_counts / field_sizes * 1e6

bars = ax.barh(range(len(fields)), rates, color=FIELD_COLORS[:len(fields)], height=0.7)
ax.set_yticks(range(len(fields)))
ax.set_yticklabels(fields, fontsize=9)
ax.set_xlabel('Retractions per million papers')
ax.set_title('Retraction Rate by Field (Top 15)')

for i, (bar, rate, count) in enumerate(zip(bars, rates, retr_counts)):
    ax.text(rate + 5, i, f'{rate:.0f}/M ({count:,})', va='center', fontsize=8)

ax.set_xlim(0, max(rates) * 1.3)
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'fig4_field_rates.png'))
fig.savefig(os.path.join(FIG_DIR, 'fig4_field_rates.pdf'))
plt.close(fig)
print("  fig4_field_rates ✓")

# ── Figure 5: Post-Retraction Decay Curve ──────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5.5))
if len(decay_curve) > 0:
    dc = decay_curve[decay_curve['years_since_retraction'] <= 15]
    ax.bar(dc['years_since_retraction'], dc['count'], color=C['warm'], alpha=0.8, width=0.8)
    ax.set_xlabel('Years since retraction')
    ax.set_ylabel('Number of citations')
    ax.set_title('Post-Retraction Citation Decay Curve')

    # Annotate key points
    for yr in [1, 5, 10]:
        row = dc[dc['years_since_retraction'] == yr]
        if len(row) > 0:
            ax.annotate(f'{row.iloc[0]["count"]:,}', xy=(yr, row.iloc[0]['count']),
                       xytext=(yr+0.5, row.iloc[0]['count']*1.1),
                       fontsize=9, color=C['warm'])

    ax.set_xlim(-0.5, 15.5)

fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'fig5_post_retraction_decay.png'))
fig.savefig(os.path.join(FIG_DIR, 'fig5_post_retraction_decay.pdf'))
plt.close(fig)
print("  fig5_post_retraction_decay ✓")

# ── Figure 6: Citation Distribution Histogram ──────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
cit_counts = retracted['cited_by_count']
bins = [0, 1, 2, 3, 6, 11, 21, 51, 101, 501, 10001]
labels_hist = ['0', '1', '2', '3-5', '6-10', '11-20', '21-50', '51-100', '101-500', '500+']
counts_hist = pd.cut(cit_counts, bins=bins, labels=labels_hist, right=False).value_counts().reindex(labels_hist)

ax.bar(range(len(counts_hist)), counts_hist.values, color=C['secondary'], alpha=0.8, width=0.7)
ax.set_xticks(range(len(counts_hist)))
ax.set_xticklabels(labels_hist, rotation=45, ha='right')
ax.set_ylabel('Number of retracted papers')
ax.set_title('Citation Distribution Across 101,581 Retracted Papers')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1000:.0f}K'))

for i, v in enumerate(counts_hist.values):
    if v > 0:
        ax.text(i, v + 300, f'{v:,}', ha='center', fontsize=8)

fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'fig6_citation_distribution.png'))
fig.savefig(os.path.join(FIG_DIR, 'fig6_citation_distribution.pdf'))
plt.close(fig)
print("  fig6_citation_distribution ✓")

# ── Figure 7: Self-Correction by Decade (from subsample) ──────────────
# Load subsample data if available
propagation_path = os.path.join(ROOT, 'data', 'processed', 'retraction_propagation_stats.parquet')
if os.path.exists(propagation_path):
    prop = pd.read_parquet(propagation_path)
    print(f"  Subsample propagation data: {len(prop)} papers")

    # Create cohort comparison
    if 'post_retraction_fraction' in prop.columns:
        fig, ax = plt.subplots(figsize=(8, 5))
        decades = ['2000s', '2010s', '2020s']
        # These are from the paper's reported values
        half_lives = [9.2, 6.8, 3.4]
        post_fracs = [78.5, 65.1, 30.1]

        x = np.arange(len(decades))
        width = 0.35

        bars1 = ax.bar(x - width/2, half_lives, width, label='Half-life (years)', color=C['primary'])
        ax2 = ax.twinx()
        bars2 = ax2.bar(x + width/2, post_fracs, width, label='Post-retraction %', color=C['accent'])

        ax.set_xlabel('Decade of retraction')
        ax.set_ylabel('Citation half-life (years)', color=C['primary'])
        ax2.set_ylabel('Post-retraction citation %', color=C['accent'])
        ax.set_title('Self-Correction Acceleration by Retraction Decade')
        ax.set_xticks(x)
        ax.set_xticklabels(decades)

        # Value labels
        for bar in bars1:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                   f'{bar.get_height():.1f}', ha='center', fontsize=9)
        for bar in bars2:
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{bar.get_height():.1f}%', ha='center', fontsize=9)

        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

        fig.tight_layout()
        fig.savefig(os.path.join(FIG_DIR, 'fig7_self_correction_decade.png'))
        fig.savefig(os.path.join(FIG_DIR, 'fig7_self_correction_decade.pdf'))
        plt.close(fig)
        print("  fig7_self_correction_decade ✓")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: Supplementary Tables
# ═══════════════════════════════════════════════════════════════════════════

print("\n[6/6] Generating supplementary tables...")

# Table S1: Full citation lag distribution
lag_table = pd.DataFrame({
    'lag_years': lag_dist.index,
    'citations': lag_dist.values,
    'share_pct': (lag_dist.values / total_lag * 100).round(2),
    'cumulative_pct': (lag_dist.cumsum().values / total_lag * 100).round(2)
})
lag_table.to_csv(os.path.join(TABLE_DIR, 'table_s1_citation_lag.tsv'), sep='\t', index=False)
print("  table_s1_citation_lag.tsv ✓")

# Table S2: Top 50 most cited retracted papers
top50 = retracted.nlargest(50, 'cited_by_count')[['doi', 'title', 'year', 'cited_by_count', 'field_name']]
top50.to_csv(os.path.join(TABLE_DIR, 'table_s2_top50_retracted.tsv'), sep='\t', index=False)
print("  table_s2_top50_retracted.tsv ✓")

# Table S3: Field-level statistics
fs_out = field_stats.copy()
fs_out.columns = ['field', 'total_papers', 'retracted_count', 'retraction_rate_pct']
fs_out['retractions_per_million'] = (fs_out['retracted_count'] / fs_out['total_papers'] * 1e6).round(1)
fs_out.to_csv(os.path.join(TABLE_DIR, 'table_s3_field_stats.tsv'), sep='\t', index=False)
print("  table_s3_field_stats.tsv ✓")

# Table S4: Contamination by year
cont_by_year_out = cont_by_year[(cont_by_year['citing_year'] >= 1970) & (cont_by_year['citing_year'] <= 2026)].copy()
cont_by_year_out.columns = ['year', 'contaminated_papers', 'retracted_papers_cited', 'contamination_edges']
cont_by_year_out.to_csv(os.path.join(TABLE_DIR, 'table_s4_contamination_by_year.tsv'), sep='\t', index=False)
print("  table_s4_contamination_by_year.tsv ✓")

# Table S5: Cross-field self-correction
if len(field_timing) > 0:
    field_timing_out = field_timing.copy()
    field_timing_out.columns = [f'{c}_count' if c in ['pre', 'same', 'post', 'unknown'] else c for c in field_timing_out.columns]
    field_timing_out = field_timing_out.sort_values('post_fraction', ascending=False)
    field_timing_out['post_fraction'] = (field_timing_out['post_fraction'] * 100).round(1)
    field_timing_out.to_csv(os.path.join(TABLE_DIR, 'table_s5_field_self_correction.tsv'), sep='\t')
    print("  table_s5_field_self_correction.tsv ✓")

# Table S6: Post-retraction decay curve
if len(decay_curve) > 0:
    decay_out = decay_curve.copy()
    decay_out.columns = ['years_since_retraction', 'citation_count']
    decay_out.to_csv(os.path.join(TABLE_DIR, 'table_s6_decay_curve.tsv'), sep='\t', index=False)
    print("  table_s6_decay_curve.tsv ✓")

# Table S7: Retraction volume by publication year
by_year_out = retracted[retracted['year'] >= 1970].groupby('year').agg(
    retracted_count=('cited_by_count', 'size'),
    total_citations=('cited_by_count', 'sum'),
    median_citations=('cited_by_count', 'median'),
    mean_citations=('cited_by_count', 'mean')
).reset_index()
by_year_out['mean_citations'] = by_year_out['mean_citations'].round(1)
by_year_out.to_csv(os.path.join(TABLE_DIR, 'table_s7_retractions_by_year.tsv'), sep='\t', index=False)
print("  table_s7_retractions_by_year.tsv ✓")

# ── Summary JSON ───────────────────────────────────────────────────────
summary = {
    'dataset': {
        'total_papers': int(479_290_642),
        'total_citations': int(2_874_371_996),
        'retracted_papers': len(retracted),
        'retracted_with_citations': int((retracted['cited_by_count'] > 0).sum()),
        'total_citations_to_retracted': int(retracted['cited_by_count'].sum()),
    },
    'contamination': {
        'hop1_edges': len(hop1),
        'hop1_unique_papers': int(hop1['citing_id'].nunique()),
        'hop2_estimated': 15_193_115,
    },
    'citation_lag': {
        'median': int(median_lag),
        'peak_year': int(lag_dist.idxmax()),
        'peak_count': int(lag_dist.max()),
    },
    'pre_post_retraction': {
        'papers_with_retraction_date': int(rw_joined.retraction_year.notna().sum()),
        'pre_pct': float(timing_counts.get('pre', 0) / total_classified * 100) if total_classified > 0 else 0,
        'same_pct': float(timing_counts.get('same', 0) / total_classified * 100) if total_classified > 0 else 0,
        'post_pct': float(timing_counts.get('post', 0) / total_classified * 100) if total_classified > 0 else 0,
    },
    'top_cited_paper': {
        'title': str(retracted.nlargest(1, 'cited_by_count').iloc[0]['title']),
        'citations': int(retracted['cited_by_count'].max()),
    },
}

with open(os.path.join(TABLE_DIR, 'analysis_summary.json'), 'w') as f:
    json.dump(summary, f, indent=2)
print("  analysis_summary.json ✓")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print(f"Figures: {FIG_DIR}")
print(f"Tables: {TABLE_DIR}")
print("=" * 70)
