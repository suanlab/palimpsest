#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.colors as mcolors

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

DATA_DIR = Path("data/processed")
OUTPUT_DIR = DATA_DIR / "figures" / "pub"

FAST_FIELDS = {"Computer Science", "Biology"}
MODERATE_FIELDS = {
    "Geology",
    "Environmental Science",
    "Materials Science",
    "Geography",
    "Engineering",
}

HIGHLIGHT_RED = "#E64B35"
HIGHLIGHT_BLUE = "#4DBBD5"
HIGHLIGHT_GREEN = "#00A087"
HIGHLIGHT_NAVY = "#3C5488"


def setup_publication_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "axes.linewidth": 0.5,
            "lines.linewidth": 1.2,
            "grid.color": "#D9D9D9",
            "grid.alpha": 0.3,
            "grid.linewidth": 0.5,
            "legend.frameon": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    sns.set_palette("colorblind")


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = required - set(df.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"{name} missing required columns: {missing_text}")


def _save_figure(fig: Figure, stem: str, output_dir: Path) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / f"{stem}.png"
    pdf_path = output_dir / f"{stem}.pdf"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    return [str(png_path), str(pdf_path)]


def _style_axis(ax: Axes, horizontal_grid: bool = False) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if horizontal_grid:
        ax.grid(axis="y", linestyle="-", alpha=0.3)
    else:
        ax.grid(False)


def _short_label(text: str, max_len: int = 44) -> str:
    clean = (text or "Unknown").strip()
    if len(clean) <= max_len:
        return clean
    return f"{clean[: max_len - 3]}..."


def _field_group(field_name: str) -> str:
    if field_name in FAST_FIELDS:
        return "fast"
    if field_name in MODERATE_FIELDS:
        return "moderate"
    return "slow"


def _safe_kde(ax: Axes, values: pd.Series, color: str) -> None:
    series = values.dropna()
    if series.nunique() < 2:
        return
    try:
        sns.kdeplot(x=series.to_numpy(dtype=float), ax=ax, color=color, linewidth=1.2)
    except Exception:
        return


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing analysis file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _prepare_retraction_summary(
    retracted_df: pd.DataFrame,
    citers_df: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        retracted_df,
        {"doi", "title", "publication_year", "cited_by_count"},
        "retracted_papers",
    )
    _require_columns(
        citers_df,
        {
            "retracted_doi",
            "retracted_title",
            "retracted_year",
            "citing_year",
            "citing_cited_by_count",
        },
        "retraction_citers",
    )

    per_paper = (
        citers_df.groupby("retracted_doi", as_index=False)
        .agg(
            direct_citers_count=("citing_year", "size"),
            avg_citer_citations=("citing_cited_by_count", "mean"),
            two_hop_reach_estimate=("citing_cited_by_count", "sum"),
            retracted_year=("retracted_year", "median"),
            retracted_title=("retracted_title", "first"),
        )
        .rename(columns={"retracted_doi": "doi"})
    )
    merged = per_paper.merge(
        retracted_df[["doi", "title", "publication_year", "cited_by_count"]],
        on="doi",
        how="left",
    )
    merged["title"] = (
        merged["title"].fillna(merged["retracted_title"]).fillna("Unknown")
    )
    merged["severity"] = merged["direct_citers_count"] * merged[
        "avg_citer_citations"
    ].fillna(0)
    merged["estimated_retraction_year"] = (
        merged["retracted_year"].fillna(merged["publication_year"]) + 5
    )
    return merged


def generate_figure_1_ai_timeline(
    ai_df: pd.DataFrame,
    output_dir: Path,
) -> list[str]:
    _require_columns(
        ai_df,
        {"field_name", "year", "ai_fraction"},
        "ai_adoption_by_field",
    )
    df = ai_df[ai_df["year"].between(2000, 2024)].copy()
    fields = sorted(df["field_name"].unique())
    palette = dict(
        zip(fields, sns.color_palette("tab20", len(fields)).as_hex(), strict=False)
    )
    palette["Computer Science"] = HIGHLIGHT_BLUE
    palette["Biology"] = HIGHLIGHT_GREEN

    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    for field in fields:
        series = df[df["field_name"] == field].sort_values("year")
        group = _field_group(field)
        linestyle = "-" if group == "fast" else "--" if group == "moderate" else ":"
        linewidth = 1.5 if group == "fast" else 1.1 if group == "moderate" else 0.9
        alpha = 1.0 if field in {"Computer Science", "Biology"} else 0.85
        ax.plot(
            series["year"],
            series["ai_fraction"] * 100,
            color=palette[field],
            linestyle=linestyle,
            linewidth=linewidth,
            alpha=alpha,
            label=field,
        )

    biology = df[df["field_name"] == "Biology"].set_index("year")["ai_fraction"]
    if 2020 in biology.index:
        y_2020 = biology.loc[2020] * 100
        ax.annotate(
            "AlphaFold (2020)",
            xy=(2020, y_2020),
            xytext=(2012.5, y_2020 + 2.5),
            fontsize=7,
            arrowprops={"arrowstyle": "->", "linewidth": 0.8, "color": HIGHLIGHT_NAVY},
            color=HIGHLIGHT_NAVY,
        )

    latest = (
        df[df["year"] == 2024][["field_name", "ai_fraction"]]
        .sort_values("ai_fraction", ascending=False)
        .head(5)
    )
    inset = inset_axes(ax, width="34%", height="42%", loc="upper left", borderpad=1.0)
    for field in latest["field_name"]:
        s = df[df["field_name"] == field].sort_values("year")
        inset.plot(
            s["year"], s["ai_fraction"] * 100, color=palette[field], linewidth=1.2
        )
    inset.set_title("Top 5 fields", fontsize=8)
    inset.tick_params(labelsize=7)
    inset.spines["top"].set_visible(False)
    inset.spines["right"].set_visible(False)

    ax.set_title("Figure 1. AI Adoption Timeline by Scientific Field")
    ax.set_xlabel("Year")
    ax.set_ylabel("AI/ML Publication Fraction (%)")
    ax.set_xlim(2000, 2024)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.18), frameon=False)
    _style_axis(ax)
    fig.subplots_adjust(left=0.09, right=0.99, top=0.92, bottom=0.28)
    return _save_figure(fig, "figure_1_ai_adoption_timeline", output_dir)


def generate_figure_2_ai_heatmap(ai_df: pd.DataFrame, output_dir: Path) -> list[str]:
    _require_columns(
        ai_df,
        {"field_name", "year", "ai_fraction"},
        "ai_adoption_by_field",
    )
    df = ai_df[ai_df["year"].between(2000, 2024)].copy()
    ordered = (
        df[df["year"] == 2024]
        .sort_values("ai_fraction", ascending=False)["field_name"]
        .tolist()
    )
    heat = (
        df.pivot_table(index="field_name", columns="year", values="ai_fraction")
        .reindex(ordered)
        .mul(100)
    )

    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    hm = sns.heatmap(
        heat,
        cmap="YlOrRd",
        ax=ax,
        cbar_kws={"label": "AI Fraction (%)", "shrink": 0.9},
        linewidths=0.1,
        linecolor="white",
    )

    annotate_years = {2000, 2010, 2020, 2024}
    for row_idx, field in enumerate(heat.index):
        for col_idx, year in enumerate(heat.columns):
            if year in annotate_years and pd.notna(heat.loc[field, year]):
                val = float(np.asarray(heat.loc[field, year], dtype=float).item())
                ax.text(
                    col_idx + 0.5,
                    row_idx + 0.5,
                    f"{val:.1f}",
                    ha="center",
                    va="center",
                    fontsize=6.5,
                    color="black" if val < 18 else "white",
                )

    colorbar = hm.collections[0].colorbar
    if colorbar is not None:
        colorbar.ax.tick_params(labelsize=8)
    ax.set_title("Figure 2. AI Adoption Intensity Heatmap")
    ax.set_xlabel("Year")
    ax.set_ylabel("Field")
    fig.tight_layout()
    return _save_figure(fig, "figure_2_ai_adoption_heatmap", output_dir)


def generate_figure_3_adoption_acceleration(
    ai_df: pd.DataFrame,
    output_dir: Path,
) -> list[str]:
    _require_columns(
        ai_df,
        {"field_name", "year", "ai_fraction"},
        "ai_adoption_by_field",
    )
    early = (
        ai_df[ai_df["year"].between(2005, 2014)]
        .groupby("field_name")["ai_fraction"]
        .mean()
    )
    recent = (
        ai_df[ai_df["year"].between(2015, 2024)]
        .groupby("field_name")["ai_fraction"]
        .mean()
    )
    acceleration = ((recent - early) * 100).dropna().sort_values(ascending=False)
    acc_df = acceleration.rename("acceleration").reset_index()
    acc_df["adoption_type"] = acc_df["field_name"].map(_field_group)

    color_map = {"fast": HIGHLIGHT_RED, "moderate": "#F39B7F", "slow": HIGHLIGHT_BLUE}

    fig, ax = plt.subplots(figsize=(4.7, 5.0))
    ax.barh(
        acc_df["field_name"],
        acc_df["acceleration"],
        color=acc_df["adoption_type"].map(color_map),
        edgecolor="none",
    )
    ax.invert_yaxis()
    ax.set_title("Figure 3. AI Adoption Acceleration (2015-2024 vs 2005-2014)")
    ax.set_xlabel("Change in AI Fraction (percentage points)")
    ax.set_ylabel("Field")
    _style_axis(ax, horizontal_grid=True)
    fig.tight_layout()
    return _save_figure(fig, "figure_3_adoption_acceleration", output_dir)


def generate_figure_4_growth_summary(
    ai_df: pd.DataFrame, output_dir: Path
) -> list[str]:
    _require_columns(
        ai_df,
        {"field_name", "year", "total_count", "ai_count", "ai_fraction"},
        "ai_adoption_by_field",
    )
    df = ai_df[ai_df["year"].between(2000, 2024)].copy()
    latest_fields = (
        df[df["year"] == 2024]
        .sort_values("ai_count", ascending=False)["field_name"]
        .head(5)
        .tolist()
    )

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.5))
    ax_a, ax_b, ax_c, ax_d = axes.flatten()

    area = (
        df[df["field_name"].isin(latest_fields)]
        .pivot_table(
            index="year", columns="field_name", values="ai_count", fill_value=0
        )
        .sort_index()
    )
    ax_a.stackplot(area.index, area.T.values, labels=area.columns, alpha=0.85)
    ax_a.set_title("Absolute AI counts (top 5 fields)")
    ax_a.set_xlabel("Year")
    ax_a.set_ylabel("AI papers")
    ax_a.legend(loc="upper left", fontsize=7, frameon=False)

    cagr_fields = ["Biology", "Computer Science", "Medicine"]
    for field, color in zip(
        cagr_fields, [HIGHLIGHT_GREEN, HIGHLIGHT_BLUE, HIGHLIGHT_RED], strict=False
    ):
        s = (
            df[df["field_name"] == field]
            .set_index("year")
            .sort_index()["ai_count"]
            .replace(0, np.nan)
        )
        cagr = (s / s.shift(3)).pow(1 / 3) - 1
        ax_b.plot(cagr.index, cagr * 100, label=field, color=color)
    ax_b.axhline(0, color="#6e6e6e", linewidth=0.8)
    ax_b.set_title("Rolling 3-year CAGR")
    ax_b.set_xlabel("Year")
    ax_b.set_ylabel("CAGR (%)")
    ax_b.legend(frameon=False, fontsize=7)

    size_2024 = (
        df[df["year"] == 2024][["field_name", "total_count"]]
        .sort_values("total_count", ascending=False)
        .head(10)
    )
    pos = np.arange(len(size_2024))
    ax_c.bar(
        pos,
        size_2024["total_count"] / 1_000,
        color=HIGHLIGHT_NAVY,
        alpha=0.85,
    )
    ax_c.set_title("Field size context (2024)")
    ax_c.set_ylabel("Total papers (thousands)")
    ax_c.set_xticks(pos)
    ax_c.set_xticklabels(size_2024["field_name"], rotation=60, ha="right", fontsize=7)
    _style_axis(ax_c, horizontal_grid=True)

    p_2010 = (
        df[df["year"] == 2010][["field_name", "ai_fraction"]]
        .set_index("field_name")
        .rename(columns={"ai_fraction": "f2010"})
    )
    p_2024 = (
        df[df["year"] == 2024][["field_name", "ai_fraction"]]
        .set_index("field_name")
        .rename(columns={"ai_fraction": "f2024"})
    )
    scatter_df = p_2010.join(p_2024, how="inner").mul(100)
    ax_d.scatter(scatter_df["f2010"], scatter_df["f2024"], color=HIGHLIGHT_BLUE, s=26)
    lim_max = max(scatter_df.max()) * 1.05
    ax_d.plot(
        [0, lim_max], [0, lim_max], linestyle="--", color="#8c8c8c", linewidth=0.8
    )
    for field, row in scatter_df.iterrows():
        ax_d.text(row["f2010"] + 0.1, row["f2024"] + 0.1, field, fontsize=6.5)
    ax_d.set_title("AI fraction: 2024 vs 2010")
    ax_d.set_xlabel("2010 AI fraction (%)")
    ax_d.set_ylabel("2024 AI fraction (%)")

    for panel_label, axis in zip(
        ["A", "B", "C", "D"], [ax_a, ax_b, ax_c, ax_d], strict=False
    ):
        axis.text(
            -0.13,
            1.05,
            panel_label,
            transform=axis.transAxes,
            fontsize=10,
            fontweight="bold",
            va="top",
        )
        _style_axis(axis)

    fig.tight_layout()
    return _save_figure(fig, "figure_4_growth_summary_panels", output_dir)


def generate_figure_5_correlation_matrix(
    ai_df: pd.DataFrame,
    ai_analysis: dict[str, Any],
    output_dir: Path,
) -> list[str]:
    _require_columns(
        ai_df,
        {"field_name", "year", "ai_fraction"},
        "ai_adoption_by_field",
    )
    pivot = (
        ai_df[ai_df["year"].between(2000, 2024)]
        .pivot_table(index="year", columns="field_name", values="ai_fraction")
        .sort_index(axis=1)
    )
    corr = pivot.corr()
    fields = corr.index.tolist()

    p_matrix_raw = ai_analysis.get("analysis_3_cross_field_diffusion", {}).get(
        "p_value_matrix", {}
    )
    p_matrix = pd.DataFrame(p_matrix_raw).reindex(index=fields, columns=fields)

    mask = np.triu(np.ones_like(corr, dtype=bool), k=0)
    fig, ax = plt.subplots(figsize=(3.5, 3.5))
    sns.heatmap(
        corr,
        mask=mask,
        cmap="RdBu_r",
        vmin=-1,
        vmax=1,
        center=0,
        square=True,
        cbar_kws={"shrink": 0.7},
        ax=ax,
    )

    for i, field_i in enumerate(fields):
        for j, field_j in enumerate(fields):
            if i <= j:
                continue
            p_val_raw = p_matrix.loc[field_i, field_j]
            p_val = float(np.asarray(p_val_raw, dtype=float).item())
            if not np.isnan(p_val) and p_val < 0.05:
                ax.text(j + 0.5, i + 0.5, "*", ha="center", va="center", fontsize=7)

    ax.set_title("Figure 5. Cross-Field Correlation Matrix")
    ax.tick_params(axis="x", labelrotation=90, labelsize=6)
    ax.tick_params(axis="y", labelsize=6)
    fig.tight_layout()
    return _save_figure(fig, "figure_5_correlation_matrix", output_dir)


def generate_figure_6_did_event_study(
    ai_df: pd.DataFrame,
    ai_analysis: dict[str, Any],
    output_dir: Path,
) -> list[str]:
    did = ai_analysis.get("analysis_4_did_framework", {})
    treatment_fields = did.get("treatment_fields", ["Computer Science", "Engineering"])
    control_fields = did.get("control_fields", ["Medicine", "Psychology"])
    cutoff = 2015

    t = (
        ai_df[ai_df["field_name"].isin(treatment_fields)]
        .groupby("year")["ai_fraction"]
        .mean()
        .mul(100)
    )
    c = (
        ai_df[ai_df["field_name"].isin(control_fields)]
        .groupby("year")["ai_fraction"]
        .mean()
        .mul(100)
    )

    fig, ax = plt.subplots(figsize=(4.7, 3.5))
    ax.axvspan(2000, cutoff - 0.5, color="#D6EAF8", alpha=0.4, zorder=0)
    ax.axvspan(cutoff - 0.5, 2024.5, color="#FADBD8", alpha=0.35, zorder=0)
    ax.plot(
        t.index.to_numpy(dtype=float),
        t.to_numpy(dtype=float),
        color=HIGHLIGHT_RED,
        label="Treatment",
        linewidth=1.4,
    )
    ax.plot(
        c.index.to_numpy(dtype=float),
        c.to_numpy(dtype=float),
        color=HIGHLIGHT_BLUE,
        label="Control",
        linewidth=1.4,
    )
    ax.axvline(cutoff, color=HIGHLIGHT_NAVY, linestyle="--", linewidth=1.0)

    att_pp = did.get("att_pct_points", np.nan)
    p_value = did.get("welch_t_test_on_field_level_changes", {}).get("p_value", np.nan)
    if pd.notna(att_pp):
        p_text = f"{p_value:.3f}" if pd.notna(p_value) else "NA"
        ax.text(
            2001,
            float(np.nanmax(t.to_numpy(dtype=float))) * 0.9,
            f"ATT = {att_pp:.2f} pp\np = {p_text}",
            fontsize=7,
            bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "alpha": 0.8},
        )

    ax.set_title("Figure 6. DID Event Study: AI Adoption")
    ax.set_xlabel("Year")
    ax.set_ylabel("AI Fraction (%)")
    ax.legend(frameon=False)
    _style_axis(ax)
    fig.tight_layout()
    return _save_figure(fig, "figure_6_did_event_study", output_dir)


def generate_figure_7_field_characteristics(
    ai_df: pd.DataFrame,
    output_dir: Path,
) -> list[str]:
    _require_columns(
        ai_df,
        {"field_name", "year", "ai_fraction", "total_count"},
        "ai_adoption_by_field",
    )
    early = (
        ai_df[ai_df["year"].between(2000, 2004)]
        .groupby("field_name")["ai_fraction"]
        .mean()
        .rename("math_intensity")
    )
    latest = (
        ai_df[ai_df["year"] == 2024]
        .set_index("field_name")[["ai_fraction", "total_count"]]
        .rename(columns={"ai_fraction": "ai_fraction_2024"})
    )
    plot_df = early.to_frame().join(latest, how="inner").dropna()
    plot_df["x"] = plot_df["math_intensity"] * 100
    plot_df["y"] = plot_df["ai_fraction_2024"] * 100
    size_scale = np.sqrt(plot_df["total_count"].to_numpy())
    plot_df["size"] = 30 + (size_scale / np.nanmax(size_scale)) * 160

    x = plot_df["x"].to_numpy()
    y = plot_df["y"].to_numpy()
    slope, intercept = np.polyfit(x, y, deg=1)
    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan

    fig, ax = plt.subplots(figsize=(3.5, 3.5))
    ax.scatter(
        x, y, s=plot_df["size"], color=HIGHLIGHT_BLUE, alpha=0.75, edgecolor="white"
    )
    x_line = np.linspace(np.nanmin(x), np.nanmax(x), 100)
    ax.plot(x_line, slope * x_line + intercept, color=HIGHLIGHT_RED, linewidth=1.2)

    for field, row in plot_df.iterrows():
        ax.text(row["x"] + 0.05, row["y"] + 0.05, str(field), fontsize=6.5)

    ax.text(
        0.03,
        0.95,
        f"$R^2$ = {r2:.2f}",
        transform=ax.transAxes,
        fontsize=7,
        va="top",
    )
    ax.set_title("Figure 7. Field Characteristics vs AI Adoption")
    ax.set_xlabel("Math intensity proxy (% AI in 2000-2004)")
    ax.set_ylabel("2024 AI fraction (%)")
    _style_axis(ax)
    fig.tight_layout()
    return _save_figure(fig, "figure_7_field_characteristics", output_dir)


def generate_figure_8_contamination_scale(
    retraction_summary: pd.DataFrame,
    output_dir: Path,
) -> list[str]:
    values = retraction_summary["direct_citers_count"].dropna()
    if values.empty:
        raise ValueError("No direct citer counts available for Figure 8")

    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.hist(values, bins=18, color=HIGHLIGHT_BLUE, alpha=0.75, edgecolor="white")
    _safe_kde(ax, values, HIGHLIGHT_RED)
    ax.set_yscale("log")

    mean_val = values.mean()
    median_val = values.median()
    total_reach = retraction_summary["two_hop_reach_estimate"].sum()
    ax.axvline(mean_val, color=HIGHLIGHT_RED, linestyle="--", linewidth=1.1)
    ax.text(
        0.98,
        0.95,
        f"mean={mean_val:.1f}\nmedian={median_val:.1f}\ntotal reach={total_reach:,.0f}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=7,
        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "alpha": 0.9},
    )

    ax.set_title("Figure 8. Contamination Scale Overview")
    ax.set_xlabel("Direct citers per retracted paper")
    ax.set_ylabel("Number of retracted papers (log scale)")
    _style_axis(ax)
    fig.tight_layout()
    return _save_figure(fig, "figure_8_contamination_scale", output_dir)


def generate_figure_9_temporal_trajectory(
    citers_df: pd.DataFrame,
    retraction_summary: pd.DataFrame,
    output_dir: Path,
) -> list[str]:
    _require_columns(
        citers_df,
        {"retracted_doi", "citing_year"},
        "retraction_citers",
    )

    merged = citers_df.merge(
        retraction_summary[["doi", "estimated_retraction_year"]],
        left_on="retracted_doi",
        right_on="doi",
        how="left",
    )
    merged["rel_year"] = (
        (merged["citing_year"] - merged["estimated_retraction_year"])
        .round()
        .astype("Int64")
    )
    merged = merged[merged["rel_year"].between(-10, 15)]
    if merged.empty:
        raise ValueError("No relative-year citations available for Figure 9")

    all_years = np.arange(-10, 16)
    counts = (
        merged.groupby(["retracted_doi", "rel_year"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=all_years, fill_value=0)
        .astype(float)
    )
    mean_series = counts.mean(axis=0)
    sem_series = counts.sem(axis=0)
    ci = 1.96 * sem_series
    mean_vals = mean_series.to_numpy(dtype=float)
    ci_vals = ci.to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.plot(all_years, mean_vals, color=HIGHLIGHT_NAVY, linewidth=1.3)
    ax.fill_between(
        all_years,
        mean_vals - ci_vals,
        mean_vals + ci_vals,
        color=HIGHLIGHT_BLUE,
        alpha=0.25,
        linewidth=0,
    )
    ax.axvline(0, color=HIGHLIGHT_RED, linestyle="--", linewidth=1.0)
    ax.set_title("Figure 9. Temporal Citation Trajectory Around Retraction")
    ax.set_xlabel("Years relative to estimated retraction (t = 0)")
    ax.set_ylabel("Average citing papers per retracted paper")
    _style_axis(ax)
    fig.tight_layout()
    return _save_figure(fig, "figure_9_temporal_trajectory", output_dir)


def _compute_half_life_distribution(
    retracted_df: pd.DataFrame,
    citers_df: pd.DataFrame,
) -> pd.Series:
    merged = citers_df.merge(
        retracted_df[["doi", "publication_year"]],
        left_on="retracted_doi",
        right_on="doi",
        how="left",
    )
    merged["age"] = merged["citing_year"] - merged["publication_year"]
    merged = merged[merged["age"] >= 0]

    half_life: dict[str, float] = {}
    for doi, group in merged.groupby("retracted_doi"):
        counts = group.groupby("age").size().sort_index()
        if counts.empty:
            continue
        cum_frac = counts.cumsum() / counts.sum()
        year_idx = cum_frac[cum_frac >= 0.5].index
        if len(year_idx):
            half_life[str(doi)] = float(year_idx[0])
    return pd.Series(half_life, name="half_life_years")


def generate_figure_10_half_life_distribution(
    half_life: pd.Series,
    output_dir: Path,
) -> list[str]:
    values = half_life.dropna()
    if values.empty:
        raise ValueError("No half-life values available for Figure 10")

    fig, ax = plt.subplots(figsize=(4.7, 3.5))
    bins = np.arange(values.min(), values.max() + 2) - 0.5
    ax.hist(values, bins=bins, color=HIGHLIGHT_GREEN, alpha=0.75, edgecolor="white")
    _safe_kde(ax, values, HIGHLIGHT_RED)
    mean_val = values.mean()
    median_val = values.median()
    ax.axvline(mean_val, color=HIGHLIGHT_RED, linestyle="--", linewidth=1.0)
    ax.text(
        0.97,
        0.95,
        f"mean={mean_val:.2f}\nmedian={median_val:.1f}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=7,
    )
    ax.set_title("Figure 10. Contamination Half-Life Distribution")
    ax.set_xlabel("Half-life (years)")
    ax.set_ylabel("Count")
    _style_axis(ax)
    fig.tight_layout()
    return _save_figure(fig, "figure_10_half_life_distribution", output_dir)


def generate_figure_11_top_contaminating(
    retraction_summary: pd.DataFrame,
    output_dir: Path,
) -> list[str]:
    top20 = retraction_summary.sort_values("severity", ascending=False).head(20).copy()
    top20 = top20.sort_values("severity", ascending=True)
    if top20.empty:
        raise ValueError("No contamination summary available for Figure 11")

    norm = mcolors.Normalize(top20["severity"].min(), top20["severity"].max())
    cmap = plt.get_cmap("YlOrRd")
    colors = cmap(norm(top20["severity"].to_numpy()))

    labels = [_short_label(str(x), 50) for x in top20["title"]]

    fig, ax = plt.subplots(figsize=(7.2, 6.0))
    bars = ax.barh(labels, top20["severity"], color=colors, edgecolor="none")
    for bar, two_hop in zip(bars, top20["two_hop_reach_estimate"], strict=False):
        ax.text(
            bar.get_width() + top20["severity"].max() * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"2-hop: {int(two_hop):,}",
            va="center",
            fontsize=6.8,
        )

    ax.set_title("Figure 11. Top 20 Most Contaminating Retracted Papers")
    ax.set_xlabel("Severity score (direct citers x avg citer citations)")
    ax.set_ylabel("Retracted paper (truncated title)")
    _style_axis(ax)
    fig.tight_layout()
    return _save_figure(fig, "figure_11_top20_contaminating", output_dir)


def _citation_velocity_curves(
    retracted_df: pd.DataFrame,
    citers_df: pd.DataFrame,
) -> dict[str, pd.Series]:
    merged = citers_df.merge(
        retracted_df[["doi", "publication_year"]],
        left_on="retracted_doi",
        right_on="doi",
        how="left",
    )
    merged["age"] = merged["citing_year"] - merged["publication_year"]
    merged = merged[merged["age"] >= 0]
    curves: dict[str, pd.Series] = {}
    for doi, group in merged.groupby("retracted_doi"):
        counts = group.groupby("age").size().sort_index()
        if counts.sum() == 0:
            continue
        cumulative_fraction = counts.cumsum() / counts.sum()
        curves[str(doi)] = cumulative_fraction
    return curves


def generate_figure_12_velocity_curves(
    curves: dict[str, pd.Series],
    output_dir: Path,
) -> list[str]:
    if not curves:
        raise ValueError("No citation velocity curves available for Figure 12")
    max_age = int(max(float(series.index.max()) for series in curves.values()))
    max_age = min(max_age, 30)
    ages = np.arange(0, max_age + 1)

    matrix = []
    for series in curves.values():
        y = np.interp(
            ages,
            series.index.to_numpy(dtype=float),
            series.to_numpy(dtype=float),
            left=0,
            right=1,
        )
        matrix.append(y)
    mat = np.vstack(matrix)
    median_curve = np.median(mat, axis=0)

    t50 = int(ages[np.argmax(median_curve >= 0.5)])
    t90 = int(ages[np.argmax(median_curve >= 0.9)])

    fig, ax = plt.subplots(figsize=(4.7, 3.5))
    for row in mat:
        ax.plot(ages, row, color="#BEBEBE", alpha=0.12, linewidth=0.8)
    ax.plot(ages, median_curve, color=HIGHLIGHT_RED, linewidth=1.6, label="Median")
    ax.axhline(0.5, color="#999999", linestyle="--", linewidth=0.8)
    ax.axhline(0.9, color="#999999", linestyle=":", linewidth=0.8)
    ax.text(t50 + 0.2, 0.52, f"t50={t50}y", fontsize=7)
    ax.text(t90 + 0.2, 0.92, f"t90={t90}y", fontsize=7)

    ax.set_title("Figure 12. Citation Velocity Curves")
    ax.set_xlabel("Years since publication")
    ax.set_ylabel("Cumulative citation fraction")
    ax.set_ylim(0, 1.02)
    ax.legend(frameon=False)
    _style_axis(ax)
    fig.tight_layout()
    return _save_figure(fig, "figure_12_citation_velocity", output_dir)


def generate_figure_13_track3_summary(
    retracted_df: pd.DataFrame,
    citers_df: pd.DataFrame,
    retraction_summary: pd.DataFrame,
    half_life: pd.Series,
    output_dir: Path,
) -> list[str]:
    rel_data = citers_df.merge(
        retraction_summary[["doi", "estimated_retraction_year", "direct_citers_count"]],
        left_on="retracted_doi",
        right_on="doi",
        how="left",
    )
    rel_data["rel_year"] = (
        (rel_data["citing_year"] - rel_data["estimated_retraction_year"])
        .round()
        .astype("Int64")
    )

    post_fraction = (
        rel_data.assign(post=lambda x: (x["rel_year"] >= 0).astype(int))
        .groupby("retracted_doi")["post"]
        .mean()
        .dropna()
    )

    merged_hl = retraction_summary.set_index("doi").join(
        half_life.to_frame(), how="inner"
    )

    pre_post_counts = (
        rel_data.assign(period=np.where(rel_data["rel_year"] < 0, "pre", "post"))
        .groupby(["retracted_doi", "period"])
        .size()
        .unstack(fill_value=0)
    )
    pre_post_counts["total"] = pre_post_counts.sum(axis=1)
    pre_post_top = (
        pre_post_counts.sort_values("total", ascending=False)
        .head(10)
        .join(retraction_summary.set_index("doi")["title"], how="left")
    )

    amplification = (
        retraction_summary["two_hop_reach_estimate"]
        / retraction_summary["direct_citers_count"].replace(0, np.nan)
    ).dropna()

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.5))
    ax_a, ax_b, ax_c, ax_d = axes.flatten()

    ax_a.hist(
        post_fraction, bins=12, color=HIGHLIGHT_BLUE, alpha=0.75, edgecolor="white"
    )
    _safe_kde(ax_a, post_fraction, HIGHLIGHT_RED)
    ax_a.set_title("Post-retraction citation fraction")
    ax_a.set_xlabel("Fraction of citations after estimated retraction")
    ax_a.set_ylabel("Count")

    ax_b.scatter(
        merged_hl["publication_year"],
        merged_hl["half_life_years"],
        s=28,
        color=HIGHLIGHT_GREEN,
        alpha=0.8,
    )
    if len(merged_hl) >= 2:
        coef = np.polyfit(
            merged_hl["publication_year"], merged_hl["half_life_years"], deg=1
        )
        x_line = np.linspace(
            merged_hl["publication_year"].min(),
            merged_hl["publication_year"].max(),
            100,
        )
        ax_b.plot(
            x_line, coef[0] * x_line + coef[1], color=HIGHLIGHT_NAVY, linewidth=1.2
        )
    ax_b.set_title("Half-life vs publication year")
    ax_b.set_xlabel("Publication year")
    ax_b.set_ylabel("Half-life (years)")

    indices = np.arange(len(pre_post_top))
    width = 0.38
    ax_c.bar(
        indices - width / 2,
        pre_post_top.get("pre", 0),
        width,
        color=HIGHLIGHT_NAVY,
        label="Pre",
    )
    ax_c.bar(
        indices + width / 2,
        pre_post_top.get("post", 0),
        width,
        color=HIGHLIGHT_RED,
        label="Post",
    )
    ax_c.set_xticks(indices)
    ax_c.set_xticklabels(
        [_short_label(str(v), 16) for v in pre_post_top["title"]],
        rotation=55,
        ha="right",
    )
    ax_c.set_title("Pre vs post citations (top 10 papers)")
    ax_c.set_ylabel("Citation count")
    ax_c.legend(frameon=False)

    ax_d.hist(amplification, bins=12, color="#7E6148", alpha=0.8, edgecolor="white")
    _safe_kde(ax_d, amplification, HIGHLIGHT_RED)
    ax_d.set_title("2-hop amplification factor")
    ax_d.set_xlabel("2-hop reach / direct citers")
    ax_d.set_ylabel("Count")

    for panel_label, axis in zip(
        ["A", "B", "C", "D"], [ax_a, ax_b, ax_c, ax_d], strict=False
    ):
        axis.text(
            -0.13,
            1.05,
            panel_label,
            transform=axis.transAxes,
            fontsize=10,
            fontweight="bold",
            va="top",
        )
        _style_axis(axis)

    fig.tight_layout()
    return _save_figure(fig, "figure_13_track3_summary_panels", output_dir)


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    ai_path = DATA_DIR / "ai_adoption_by_field.parquet"
    retracted_path = DATA_DIR / "retracted_papers.parquet"
    citers_path = DATA_DIR / "retraction_citers.parquet"

    for required_path in [ai_path, retracted_path, citers_path]:
        if not required_path.exists():
            raise FileNotFoundError(f"Missing required data file: {required_path}")

    ai_df = pd.read_parquet(ai_path)
    retracted_df = pd.read_parquet(retracted_path)
    citers_df = pd.read_parquet(citers_path)

    ai_analysis = _load_json(DATA_DIR / "ai_adoption_analysis.json")
    return ai_df, retracted_df, citers_df, ai_analysis


def main() -> None:
    setup_publication_style()

    ai_df, retracted_df, citers_df, ai_analysis = load_inputs()
    retraction_summary = _prepare_retraction_summary(retracted_df, citers_df)
    half_life = _compute_half_life_distribution(retracted_df, citers_df)
    curves = _citation_velocity_curves(retracted_df, citers_df)

    generated: list[str] = []
    generated.extend(generate_figure_1_ai_timeline(ai_df, OUTPUT_DIR))
    generated.extend(generate_figure_2_ai_heatmap(ai_df, OUTPUT_DIR))
    generated.extend(generate_figure_3_adoption_acceleration(ai_df, OUTPUT_DIR))
    generated.extend(generate_figure_4_growth_summary(ai_df, OUTPUT_DIR))
    generated.extend(
        generate_figure_5_correlation_matrix(ai_df, ai_analysis, OUTPUT_DIR)
    )
    generated.extend(generate_figure_6_did_event_study(ai_df, ai_analysis, OUTPUT_DIR))
    generated.extend(generate_figure_7_field_characteristics(ai_df, OUTPUT_DIR))

    generated.extend(
        generate_figure_8_contamination_scale(retraction_summary, OUTPUT_DIR)
    )
    generated.extend(
        generate_figure_9_temporal_trajectory(citers_df, retraction_summary, OUTPUT_DIR)
    )
    generated.extend(generate_figure_10_half_life_distribution(half_life, OUTPUT_DIR))
    generated.extend(
        generate_figure_11_top_contaminating(retraction_summary, OUTPUT_DIR)
    )
    generated.extend(generate_figure_12_velocity_curves(curves, OUTPUT_DIR))
    generated.extend(
        generate_figure_13_track3_summary(
            retracted_df,
            citers_df,
            retraction_summary,
            half_life,
            OUTPUT_DIR,
        )
    )

    print("Generated publication figures:")
    for path in generated:
        print(f"- {path}")
    print(f"Total files generated: {len(generated)}")


if __name__ == "__main__":
    main()
