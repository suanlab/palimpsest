#!/usr/bin/env python3
"""Generate supplementary publication-quality figures for Track 1 and Track 3.

This script produces six supplementary figures and saves each as PNG and PDF
at 300 DPI in ``data/processed/figures/supplementary``.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.figure import Figure

DATA_DIR = Path("data/processed")
OUTPUT_DIR = DATA_DIR / "figures" / "supplementary"

PANEL_PATH = DATA_DIR / "neo4j_field_panel.parquet"
SUMMARY_PATH = DATA_DIR / "neo4j_field_summary.parquet"
ANALYSIS_PATH = DATA_DIR / "neo4j_field_analysis.json"
RETRACTION_ANALYSIS_PATH = (
    DATA_DIR / "retraction_analysis" / "retraction_citation_analysis.json"
)
RETRACTION_CITERS_PATH = DATA_DIR / "retraction_citers.parquet"

LOGGER = logging.getLogger(__name__)
JsonDict = dict[str, Any]

SOCIAL_FIELDS = {
    "Arts and Humanities",
    "Business, Management and Accounting",
    "Decision Sciences",
    "Economics, Econometrics and Finance",
    "Psychology",
    "Social Sciences",
}

HEALTH_FIELDS = {
    "Dentistry",
    "Health Professions",
    "Immunology and Microbiology",
    "Medicine",
    "Neuroscience",
    "Nursing",
    "Pharmacology, Toxicology and Pharmaceutics",
}

DOMAIN_COLORS = {
    "STEM": "#4E79A7",
    "Social Sciences": "#F28E2B",
    "Health": "#59A14F",
}


def setup_style() -> None:
    """Configure plotting style for publication-quality white-background figures."""
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "axes.titlesize": 12,
            "axes.labelsize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
            "axes.linewidth": 0.7,
            "lines.linewidth": 1.5,
            "grid.color": "#D9D9D9",
            "grid.alpha": 0.35,
            "grid.linewidth": 0.6,
            "legend.frameon": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    sns.set_style("whitegrid")
    sns.set_palette("colorblind")


def _style_axis(ax: Axes, horizontal_grid: bool = False) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if horizontal_grid:
        ax.grid(axis="y")
    else:
        ax.grid(False)


def _save_figure(fig: Figure, stem: str) -> list[Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    png_path = OUTPUT_DIR / f"{stem}.png"
    pdf_path = OUTPUT_DIR / f"{stem}.pdf"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    return [png_path, pdf_path]


def _load_json(path: Path) -> JsonDict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _classify_domain(field_name: str) -> str:
    if field_name in HEALTH_FIELDS:
        return "Health"
    if field_name in SOCIAL_FIELDS:
        return "Social Sciences"
    return "STEM"


def _pearson_with_permutation_p(
    x: np.ndarray,
    y: np.ndarray,
    n_permutations: int = 10000,
    seed: int = 42,
) -> tuple[float, float]:
    """Compute Pearson r and two-sided permutation p-value.

    Args:
        x: First variable.
        y: Second variable.
        n_permutations: Number of random permutations for p-value.
        seed: RNG seed.

    Returns:
        Tuple of (r, p_value).
    """
    if x.size != y.size or x.size < 3:
        raise ValueError("x and y must have equal size >= 3")

    observed_r = float(np.corrcoef(x, y)[0, 1])
    rng = np.random.default_rng(seed)
    extreme = 0
    for _ in range(n_permutations):
        permuted = rng.permutation(y)
        perm_r = float(np.corrcoef(x, permuted)[0, 1])
        if abs(perm_r) >= abs(observed_r):
            extreme += 1
    p_value = (extreme + 1) / (n_permutations + 1)
    return observed_r, p_value


def _bootstrap_regression_ci(
    x: np.ndarray,
    y: np.ndarray,
    x_grid: np.ndarray,
    n_bootstrap: int = 2000,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fit linear regression and bootstrap confidence intervals."""
    rng = np.random.default_rng(seed)
    slope, intercept = np.polyfit(x, y, deg=1)
    y_fit = slope * x_grid + intercept

    n = x.size
    boot_lines = np.empty((n_bootstrap, x_grid.size), dtype=float)
    for i in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        b_slope, b_intercept = np.polyfit(x[idx], y[idx], deg=1)
        boot_lines[i, :] = b_slope * x_grid + b_intercept

    lower = np.percentile(boot_lines, 2.5, axis=0)
    upper = np.percentile(boot_lines, 97.5, axis=0)
    return y_fit, lower, upper


def _compute_gini(values: np.ndarray) -> float:
    """Compute Gini coefficient for non-negative values."""
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return np.nan
    arr = np.clip(arr, a_min=0.0, a_max=None)
    total = float(arr.sum())
    if total <= 0:
        return 0.0
    sorted_arr = np.sort(arr)
    n = sorted_arr.size
    index = np.arange(1, n + 1, dtype=float)
    gini = float((2 * np.sum(index * sorted_arr)) / (n * total) - (n + 1) / n)
    return gini


def load_inputs() -> tuple[
    pd.DataFrame, pd.DataFrame, JsonDict, JsonDict, pd.DataFrame
]:
    """Load panel, summary, and retraction analysis data files."""
    required_paths = [
        PANEL_PATH,
        SUMMARY_PATH,
        ANALYSIS_PATH,
        RETRACTION_ANALYSIS_PATH,
        RETRACTION_CITERS_PATH,
    ]
    for path in required_paths:
        if not path.exists():
            raise FileNotFoundError(f"Missing required file: {path}")

    panel_df = pd.read_parquet(PANEL_PATH)
    summary_df = pd.read_parquet(SUMMARY_PATH)
    neo_analysis = _load_json(ANALYSIS_PATH)
    retraction_analysis = _load_json(RETRACTION_ANALYSIS_PATH)
    retraction_citers_df = pd.read_parquet(RETRACTION_CITERS_PATH)
    return panel_df, summary_df, neo_analysis, retraction_analysis, retraction_citers_df


def generate_figure_s1(
    panel_df: pd.DataFrame,
    neo_analysis: JsonDict,
) -> list[Path]:
    """Generate Figure S1: AI adoption vs retraction-rate scatter."""
    ai_recent = (
        panel_df[panel_df["year"].between(2015, 2024)]
        .groupby("field_name")["ai_concept_fraction"]
        .mean()
        .reset_index(name="ai_adoption_rate")
    )

    retraction_field = pd.DataFrame(
        neo_analysis["methods"]["concept"]["analysis_5_retraction_rate"][
            "field_summary"
        ]
    )[["field_name", "retraction_per_million"]]

    plot_df = ai_recent.merge(retraction_field, on="field_name", how="inner")
    plot_df["domain"] = plot_df["field_name"].map(_classify_domain)

    x = plot_df["ai_adoption_rate"].to_numpy(dtype=float) * 100
    y = plot_df["retraction_per_million"].to_numpy(dtype=float)
    x_grid = np.linspace(x.min() * 0.95, x.max() * 1.05, 200)
    y_fit, y_low, y_high = _bootstrap_regression_ci(x=x, y=y, x_grid=x_grid)
    r_val, p_val = _pearson_with_permutation_p(x=x, y=y)

    fig, ax = plt.subplots(figsize=(8.0, 6.0))

    for domain, domain_df in plot_df.groupby("domain", sort=False):
        domain_name = str(domain)
        ax.scatter(
            domain_df["ai_adoption_rate"] * 100,
            domain_df["retraction_per_million"],
            s=52,
            color=DOMAIN_COLORS[domain_name],
            alpha=0.9,
            label=domain_name,
            edgecolor="white",
            linewidth=0.5,
        )

    ax.plot(x_grid, y_fit, color="#2F2F2F", linewidth=1.6)
    ax.fill_between(x_grid, y_low, y_high, color="#BDBDBD", alpha=0.35)

    for _, row in plot_df.iterrows():
        ax.text(
            row["ai_adoption_rate"] * 100 + 0.05,
            row["retraction_per_million"] + 5,
            str(row["field_name"]),
            fontsize=7,
            alpha=0.9,
        )

    ax.text(
        0.02,
        0.98,
        f"Pearson r = {r_val:.2f}\nPermutation p = {p_val:.4f}",
        transform=ax.transAxes,
        va="top",
        fontsize=10,
        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "alpha": 0.85},
    )

    ax.set_title("Figure S1. AI Adoption Rate vs Retraction Rate Across 26 Fields")
    ax.set_xlabel("AI adoption rate (concept-based, 2015-2024 mean, %)")
    ax.set_ylabel("Retraction rate per million papers")
    ax.legend(loc="upper right")
    _style_axis(ax)
    fig.tight_layout()
    return _save_figure(fig, "figure_s1_ai_vs_retraction_scatter")


def generate_figure_s2(panel_df: pd.DataFrame) -> list[Path]:
    """Generate Figure S2: AI adoption acceleration panel for representative fields."""
    field_map = {
        "Computer Science": "Computer Science",
        "Biology": "Agricultural and Biological Sciences",
        "Medicine": "Medicine",
        "Psychology": "Psychology",
        "Social Sciences": "Social Sciences",
        "Engineering": "Engineering",
    }
    periods = [
        ("2000-2009", 2000, 2009),
        ("2010-2017", 2010, 2017),
        ("2018-2024", 2018, 2024),
    ]

    records: list[dict[str, float | str]] = []
    for display_name, actual_name in field_map.items():
        field_df = panel_df[panel_df["field_name"] == actual_name]
        for period_label, start, end in periods:
            mean_rate = float(
                field_df[field_df["year"].between(start, end)][
                    "ai_concept_fraction"
                ].mean()
            )
            records.append(
                {
                    "field": display_name,
                    "period": period_label,
                    "ai_rate_pct": mean_rate * 100,
                }
            )

    plot_df = pd.DataFrame(records)
    y_max = float(plot_df["ai_rate_pct"].max()) * 1.2

    fig, axes = plt.subplots(3, 2, figsize=(10.5, 10.0), sharey=True)
    flat_axes = axes.flatten()
    bar_colors = ["#A0CBE8", "#4E79A7", "#1F4E79"]

    for ax, field_name in zip(flat_axes, field_map.keys(), strict=False):
        data = plot_df[plot_df["field"] == field_name]
        bars = ax.bar(
            data["period"],
            data["ai_rate_pct"],
            color=bar_colors,
            edgecolor="none",
        )
        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                f"{bar.get_height():.1f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )
        ax.set_title(field_name)
        ax.set_ylim(0, y_max)
        ax.tick_params(axis="x", rotation=20)
        _style_axis(ax, horizontal_grid=True)

    fig.suptitle(
        "Figure S2. AI Adoption Growth Acceleration by Field (Concept-based)",
        y=1.01,
    )
    fig.supxlabel("Period")
    fig.supylabel("AI adoption rate (%)")
    fig.tight_layout()
    return _save_figure(fig, "figure_s2_ai_growth_acceleration_panel")


def generate_figure_s3(retraction_citers_df: pd.DataFrame) -> list[Path]:
    """Generate Figure S3: citation persistence curve around retraction."""
    df = retraction_citers_df.copy()
    df["relative_year"] = df["citing_year"] - df["retracted_year"]
    window = np.arange(-5, 21)

    counts = (
        df[df["relative_year"].between(-5, 20)]
        .groupby("relative_year")
        .size()
        .reindex(window, fill_value=0)
    )
    if counts.sum() == 0:
        raise ValueError("No relative-year citation counts available in [-5, 20]")

    cumulative_pct = counts.cumsum() / counts.sum() * 100
    peak_year = int(counts.idxmax())
    peak_value = int(counts.max())

    fig, ax = plt.subplots(figsize=(9.0, 5.8))
    pre_mask = window < 0
    post_mask = window >= 0

    ax.axvspan(-5, -0.01, color="#E8F1FA", alpha=0.75)
    ax.axvspan(0, 20, color="#FDEBEA", alpha=0.6)

    ax.plot(window[pre_mask], counts.to_numpy()[pre_mask], color="#4E79A7", label="Pre")
    ax.plot(
        window[post_mask],
        counts.to_numpy()[post_mask],
        color="#E15759",
        label="Post",
    )
    ax.axvline(0, color="#2F2F2F", linestyle="--", linewidth=1.0)

    ax.annotate(
        f"Peak: year {peak_year} ({peak_value:,})",
        xy=(peak_year, peak_value),
        xytext=(peak_year + 2, peak_value * 1.08),
        arrowprops={"arrowstyle": "->", "linewidth": 1.0, "color": "#2F2F2F"},
        fontsize=10,
    )

    ax2 = ax.twinx()
    ax2.plot(
        window, cumulative_pct.to_numpy(), color="#59A14F", linestyle=":", linewidth=1.8
    )
    ax2.set_ylabel("Cumulative citations (%)")
    ax2.set_ylim(0, 100)
    ax2.spines["top"].set_visible(False)

    ax.set_title("Figure S3. Citation Persistence Around Retraction")
    ax.set_xlabel("Years relative to retraction")
    ax.set_ylabel("Number of citations")
    ax.set_xlim(-5, 20)
    ax.legend(loc="upper right")
    _style_axis(ax)
    fig.tight_layout()
    return _save_figure(fig, "figure_s3_citation_persistence_curve")


def generate_figure_s4(retraction_analysis: JsonDict) -> list[Path]:
    """Generate Figure S4: post-retraction citation survival by field.

    Note:
        Field-level pre-retraction counts are estimated by scaling each field's
        post-retraction count using the global pre/post ratio from the analysis.
    """
    field_df = pd.DataFrame(retraction_analysis["field_patterns"])
    global_stats = retraction_analysis["pre_post_distribution"]

    pre_ratio = float(global_stats["pre_retraction"]) / float(
        global_stats["post_retraction"]
    )
    field_df["pre_retraction_estimated"] = (
        field_df["post_retraction_citations"] * pre_ratio
    )
    field_df["post_pct"] = (
        field_df["post_retraction_citations"]
        / (field_df["post_retraction_citations"] + field_df["pre_retraction_estimated"])
        * 100
    )

    top10 = field_df.nlargest(10, "post_retraction_citations").sort_values(
        "post_retraction_citations", ascending=True
    )

    fig, ax = plt.subplots(figsize=(10.0, 6.8))
    y = np.arange(len(top10))
    h = 0.38

    ax.barh(
        y - h / 2,
        top10["pre_retraction_estimated"],
        height=h,
        color="#A0CBE8",
        label="Estimated pre-retraction citations",
    )
    ax.barh(
        y + h / 2,
        top10["post_retraction_citations"],
        height=h,
        color="#E15759",
        label="Post-retraction citations",
    )

    ax2 = ax.twiny()
    ax2.plot(top10["post_pct"], y, color="#59A14F", marker="o", linewidth=1.4)
    ax2.set_xlabel("Post-retraction share (%)")
    ax2.set_xlim(top10["post_pct"].min() * 0.995, top10["post_pct"].max() * 1.005)
    ax2.spines["top"].set_visible(False)

    ax.set_yticks(y)
    ax.set_yticklabels(top10["field"])
    ax.set_xlabel("Citation count")
    ax.set_ylabel("Field")
    ax.set_title("Figure S4. Post-Retraction Citation Survival by Field (Top 10)")
    ax.legend(loc="lower right")
    _style_axis(ax, horizontal_grid=True)
    fig.tight_layout()
    return _save_figure(fig, "figure_s4_post_retraction_survival_by_field")


def generate_figure_s5(
    panel_df: pd.DataFrame,
) -> list[Path]:
    """Generate Figure S5: title-based vs concept-based AI detection comparison."""
    df = (
        panel_df[panel_df["year"].between(2015, 2024)]
        .groupby("field_name", as_index=False)
        .agg(
            title_fraction=("ai_title_fraction", "mean"),
            concept_fraction=("ai_concept_fraction", "mean"),
        )
    )
    df["title_pct"] = df["title_fraction"] * 100
    df["concept_pct"] = df["concept_fraction"] * 100
    df["gap"] = df["concept_fraction"] - df["title_fraction"]

    eps = 1e-12
    df["log_ratio_abs"] = np.abs(
        np.log2((df["concept_fraction"] + eps) / (df["title_fraction"] + eps))
    )
    outliers = df.nlargest(8, "log_ratio_abs")

    max_lim = float(max(df["title_pct"].max(), df["concept_pct"].max()) * 1.08)
    fig, ax = plt.subplots(figsize=(8.0, 6.2))

    ax.scatter(
        df["title_pct"],
        df["concept_pct"],
        s=50,
        color="#4E79A7",
        alpha=0.85,
        edgecolor="white",
        linewidth=0.5,
    )
    ax.plot([0, max_lim], [0, max_lim], color="#2F2F2F", linestyle="--", linewidth=1.0)

    for _, row in outliers.iterrows():
        ax.text(
            row["title_pct"] + 0.08,
            row["concept_pct"] + 0.08,
            str(row["field_name"]),
            fontsize=8,
        )

    share_above_identity = (df["concept_fraction"] > df["title_fraction"]).mean() * 100
    ax.text(
        0.03,
        0.97,
        f"Fields above y=x: {share_above_identity:.1f}%",
        transform=ax.transAxes,
        va="top",
        fontsize=10,
        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "alpha": 0.85},
    )

    ax.set_xlim(0, max_lim)
    ax.set_ylim(0, max_lim)
    ax.set_title("Figure S5. Title-based vs Concept-based AI Detection")
    ax.set_xlabel("Title-based AI fraction (2015-2024 mean, %)")
    ax.set_ylabel("Concept-based AI fraction (2015-2024 mean, %)")
    _style_axis(ax)
    fig.tight_layout()
    return _save_figure(fig, "figure_s5_title_vs_concept_comparison")


def generate_figure_s6(panel_df: pd.DataFrame) -> list[Path]:
    """Generate Figure S6: Gini coefficient of AI adoption over time."""
    years = np.arange(2000, 2025)
    rows: list[dict[str, float | int | str]] = []

    for year in years:
        year_df = panel_df[panel_df["year"] == year]
        gini_title = _compute_gini(year_df["ai_title_fraction"].to_numpy(dtype=float))
        gini_concept = _compute_gini(
            year_df["ai_concept_fraction"].to_numpy(dtype=float)
        )
        rows.append({"year": int(year), "method": "Title-based", "gini": gini_title})
        rows.append(
            {"year": int(year), "method": "Concept-based", "gini": gini_concept}
        )

    gini_df = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    for method, color in [("Title-based", "#4E79A7"), ("Concept-based", "#E15759")]:
        subset = gini_df[gini_df["method"] == method]
        ax.plot(
            subset["year"],
            subset["gini"],
            marker="o",
            markersize=3.5,
            color=color,
            label=method,
        )

    ax.set_title("Figure S6. AI Adoption Inequality Across Fields (Gini, 2000-2024)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Gini coefficient")
    ax.set_xlim(2000, 2024)
    ax.set_ylim(0, min(1.0, float(gini_df["gini"].max() * 1.1)))
    ax.legend(loc="best")
    _style_axis(ax)
    fig.tight_layout()
    return _save_figure(fig, "figure_s6_ai_adoption_gini_over_time")


def main() -> None:
    """Run supplementary figure generation pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    setup_style()

    panel_df, summary_df, neo_analysis, retraction_analysis, retraction_citers_df = (
        load_inputs()
    )

    LOGGER.info("Loaded panel rows=%s, summary rows=%s", len(panel_df), len(summary_df))

    panel_df = panel_df.copy()
    panel_df["year"] = pd.to_numeric(panel_df["year"], errors="coerce")
    panel_df = panel_df.dropna(subset=["year"])
    panel_df["year"] = panel_df["year"].astype(int)

    generated: list[Path] = []
    generated.extend(generate_figure_s1(panel_df=panel_df, neo_analysis=neo_analysis))
    generated.extend(generate_figure_s2(panel_df=panel_df))
    generated.extend(generate_figure_s3(retraction_citers_df=retraction_citers_df))
    generated.extend(generate_figure_s4(retraction_analysis=retraction_analysis))
    generated.extend(generate_figure_s5(panel_df=panel_df))
    generated.extend(generate_figure_s6(panel_df=panel_df))

    LOGGER.info("Generated %s supplementary figure files", len(generated))
    for path in generated:
        LOGGER.info("Saved %s", path)


if __name__ == "__main__":
    main()
