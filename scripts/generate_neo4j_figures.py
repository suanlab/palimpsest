#!/usr/bin/env python3
"""Generate publication-quality figures for Neo4j 26-field AI adoption analysis."""

from __future__ import annotations

import json
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
PANEL_PATH = DATA_DIR / "neo4j_field_panel.parquet"
RETRACTION_PATH = DATA_DIR / "neo4j_retraction_by_field_year.parquet"
ANALYSIS_PATH = DATA_DIR / "neo4j_field_analysis.json"
OUTPUT_DIR = DATA_DIR / "figures" / "neo4j"

START_YEAR = 2000
END_YEAR = 2024
RECENT_PERIOD = (2015, 2024)

METHOD_SPECS = {
    "title": {"fraction_column": "ai_title_fraction", "label": "Title-based AI"},
    "concept": {
        "fraction_column": "ai_concept_fraction",
        "label": "Concept-based AI",
    },
}

TOP_COLORS = ["#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F"]
NEUTRAL_GRAY = "#B3B3B3"
TYPE_COLORS = {"A": "#1B9E77", "B": "#7570B3", "C": "#D95F02", "D": "#666666"}


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
        },
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


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing analysis file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    if not PANEL_PATH.exists():
        raise FileNotFoundError(f"Missing panel data file: {PANEL_PATH}")
    if not RETRACTION_PATH.exists():
        raise FileNotFoundError(f"Missing retraction data file: {RETRACTION_PATH}")

    panel_df = pd.read_parquet(PANEL_PATH)
    retraction_df = pd.read_parquet(RETRACTION_PATH)
    analysis = _load_json(ANALYSIS_PATH)

    _require_columns(
        panel_df,
        {
            "field_id",
            "field_name",
            "year",
            "total_count",
            "ai_title_fraction",
            "ai_concept_fraction",
        },
        "neo4j_field_panel",
    )
    _require_columns(
        retraction_df,
        {"field_id", "field_name", "year", "retracted_count"},
        "neo4j_retraction_by_field_year",
    )

    panel_df = panel_df.copy()
    panel_df["year"] = pd.to_numeric(panel_df["year"], errors="coerce").astype("Int64")
    panel_df = panel_df.dropna(subset=["year"]).copy()
    panel_df["year"] = panel_df["year"].astype(int)

    retraction_df = retraction_df.copy()
    retraction_df["year"] = pd.to_numeric(
        retraction_df["year"], errors="coerce"
    ).astype("Int64")
    retraction_df = retraction_df.dropna(subset=["year"]).copy()
    retraction_df["year"] = retraction_df["year"].astype(int)

    return panel_df, retraction_df, analysis


def generate_figure_1_timeline(panel_df: pd.DataFrame, output_dir: Path) -> list[str]:
    df = panel_df[panel_df["year"].between(START_YEAR, END_YEAR)].copy()
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.6), sharey=True)

    for ax, method_key in zip(axes, ["title", "concept"], strict=False):
        spec = METHOD_SPECS[method_key]
        fraction_col = str(spec["fraction_column"])
        latest = (
            df[df["year"] == END_YEAR][["field_name", fraction_col]]
            .sort_values(fraction_col, ascending=False)
            .head(5)
        )
        top_fields = latest["field_name"].tolist()
        color_map = dict(zip(top_fields, TOP_COLORS, strict=False))

        for field_name, group in df.groupby("field_name", sort=True):
            ordered = group.sort_values("year")
            is_top = field_name in top_fields
            ax.plot(
                ordered["year"],
                ordered[fraction_col] * 100,
                color=color_map.get(field_name, NEUTRAL_GRAY),
                linewidth=1.6 if is_top else 0.8,
                alpha=1.0 if is_top else 0.6,
                label=field_name if is_top else None,
                zorder=3 if is_top else 1,
            )

        ax.set_title(f"({'a' if method_key == 'title' else 'b'}) {spec['label']}")
        ax.set_xlabel("Year")
        ax.set_xlim(START_YEAR, END_YEAR)
        _style_axis(ax)

    axes[0].set_ylabel("AI publication fraction (%)")
    axes[1].legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), frameon=False)
    fig.suptitle("Figure 1. AI Adoption Timeline Across 26 Fields", y=1.02)
    fig.tight_layout()
    return _save_figure(fig, "figure_1_ai_adoption_timeline_26_fields", output_dir)


def generate_figure_2_heatmap(panel_df: pd.DataFrame, output_dir: Path) -> list[str]:
    df = panel_df[panel_df["year"].between(START_YEAR, END_YEAR)].copy()
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 6.0), sharey=True)

    for ax, method_key in zip(axes, ["title", "concept"], strict=False):
        spec = METHOD_SPECS[method_key]
        fraction_col = str(spec["fraction_column"])
        ordering = (
            df[df["year"].between(RECENT_PERIOD[0], RECENT_PERIOD[1])]
            .groupby("field_name")[fraction_col]
            .mean()
            .sort_values(ascending=False)
            .index.tolist()
        )
        heat = (
            df.pivot_table(index="field_name", columns="year", values=fraction_col)
            .reindex(ordering)
            .mul(100)
        )
        sns.heatmap(
            heat,
            ax=ax,
            cmap="YlOrRd",
            linewidths=0.1,
            linecolor="white",
            cbar_kws={"label": "AI fraction (%)", "shrink": 0.75},
        )
        ax.set_title(spec["label"])
        ax.set_xlabel("Year")
        if method_key == "title":
            ax.set_ylabel("Field")
        else:
            ax.set_ylabel("")
        ax.tick_params(axis="x", labelrotation=45)

    fig.suptitle("Figure 2. AI Adoption Heatmap (26 Fields x 25 Years)", y=1.02)
    fig.tight_layout()
    return _save_figure(fig, "figure_2_ai_adoption_heatmap_26_fields", output_dir)


def generate_figure_3_field_comparison(
    panel_df: pd.DataFrame, output_dir: Path
) -> list[str]:
    period_df = panel_df[
        panel_df["year"].between(RECENT_PERIOD[0], RECENT_PERIOD[1])
    ].copy()
    summary = (
        period_df.groupby("field_name", as_index=False)
        .agg(
            title_fraction=("ai_title_fraction", "mean"),
            concept_fraction=("ai_concept_fraction", "mean"),
        )
        .sort_values("concept_fraction", ascending=True)
    )
    summary["title_pct"] = summary["title_fraction"] * 100
    summary["concept_pct"] = summary["concept_fraction"] * 100

    fig, ax = plt.subplots(figsize=(7.0, 6.6))
    y_pos = np.arange(len(summary))
    bar_h = 0.38
    ax.barh(
        y_pos - bar_h / 2,
        summary["title_pct"],
        height=bar_h,
        color="#4E79A7",
        label="Title-based",
    )
    ax.barh(
        y_pos + bar_h / 2,
        summary["concept_pct"],
        height=bar_h,
        color="#F28E2B",
        label="Concept-based",
    )
    ax.set_yticks(y_pos)
    ax.set_yticklabels(summary["field_name"])
    ax.set_xlabel("Mean AI fraction, 2015-2024 (%)")
    ax.set_ylabel("Field")
    ax.set_title("Figure 3. Field-Level AI Fraction: Title vs Concept")
    ax.legend(loc="lower right")
    _style_axis(ax, horizontal_grid=True)
    fig.tight_layout()
    return _save_figure(fig, "figure_3_field_comparison_bars", output_dir)


def generate_figure_4_scurve_parameters(
    panel_df: pd.DataFrame,
    analysis: dict[str, Any],
    output_dir: Path,
) -> list[str]:
    latest = panel_df[panel_df["year"] == END_YEAR][
        ["field_name", "ai_title_fraction", "ai_concept_fraction"]
    ].set_index("field_name")

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.4), sharex=False, sharey=False)
    for ax, method_key in zip(axes, ["title", "concept"], strict=False):
        method_data = analysis["methods"][method_key]
        scurve = pd.DataFrame(
            method_data["analysis_1_s_curve_fitting"]["field_results"]
        )
        fraction_col = str(METHOD_SPECS[method_key]["fraction_column"])

        scurve["current_fraction"] = (
            scurve["field_name"].map(latest[fraction_col]).fillna(0.0)
        )
        scurve = scurve.dropna(subset=["K", "r", "adoption_type"])
        scurve["size"] = 35 + (scurve["current_fraction"] * 420)

        for adoption_type, group in scurve.groupby("adoption_type", sort=True):
            ax.scatter(
                group["K"],
                group["r"],
                s=group["size"],
                color=TYPE_COLORS.get(str(adoption_type), "#666666"),
                alpha=0.85,
                edgecolor="white",
                linewidth=0.5,
                label=f"Type {adoption_type}",
            )

        ax.set_title(METHOD_SPECS[method_key]["label"])
        ax.set_xlabel("Carrying capacity K")
        ax.set_ylabel("Growth rate r")
        _style_axis(ax)

    handles, labels = axes[1].get_legend_handles_labels()
    dedup = dict(zip(labels, handles, strict=False))
    axes[1].legend(dedup.values(), dedup.keys(), loc="lower right")
    fig.suptitle("Figure 4. S-curve Parameters by Adoption Type", y=1.02)
    fig.tight_layout()
    return _save_figure(fig, "figure_4_scurve_parameters", output_dir)


def generate_figure_5_correlation_matrix(
    analysis: dict[str, Any], output_dir: Path
) -> list[str]:
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.8), sharex=False, sharey=False)

    for ax, method_key in zip(axes, ["title", "concept"], strict=False):
        corr_raw = analysis["methods"][method_key][
            "analysis_3_cross_field_correlation"
        ]["correlation_matrix"]
        corr = pd.DataFrame(corr_raw).sort_index().sort_index(axis=1)
        mask = np.triu(np.ones_like(corr, dtype=bool), k=0)
        sns.heatmap(
            corr,
            mask=mask,
            cmap="RdBu_r",
            vmin=-1,
            vmax=1,
            center=0,
            square=True,
            ax=ax,
            cbar_kws={"shrink": 0.65},
        )

        for i in range(corr.shape[0]):
            for j in range(corr.shape[1]):
                if i <= j:
                    continue
                value = float(np.asarray(corr.iloc[i, j], dtype=float).item())
                if abs(value) >= 0.70:
                    ax.text(
                        j + 0.5,
                        i + 0.5,
                        f"{value:.2f}",
                        ha="center",
                        va="center",
                        fontsize=5.5,
                        color="black",
                    )

        ax.set_title(METHOD_SPECS[method_key]["label"])
        ax.tick_params(axis="x", labelrotation=90, labelsize=6)
        ax.tick_params(axis="y", labelsize=6)

    fig.suptitle("Figure 5. Cross-Field Correlation Matrix", y=1.02)
    fig.tight_layout()
    return _save_figure(fig, "figure_5_correlation_matrix", output_dir)


def generate_figure_6_retraction_rates(
    analysis: dict[str, Any], output_dir: Path
) -> list[str]:
    field_summary = pd.DataFrame(
        analysis["methods"]["concept"]["analysis_5_retraction_rate"]["field_summary"]
    )
    ranked = field_summary.sort_values("retraction_per_million", ascending=True)

    fig, ax = plt.subplots(figsize=(7.0, 6.2))
    ax.barh(
        ranked["field_name"],
        ranked["retraction_per_million"],
        color="#E15759",
        alpha=0.85,
    )
    ax.set_title("Figure 6. Retraction Rates by Field")
    ax.set_xlabel("Retractions per million papers")
    ax.set_ylabel("Field")
    _style_axis(ax, horizontal_grid=True)
    fig.tight_layout()
    return _save_figure(fig, "figure_6_retraction_rates_by_field", output_dir)


def generate_figure_7_retraction_timeline(
    panel_df: pd.DataFrame,
    retraction_df: pd.DataFrame,
    output_dir: Path,
) -> list[str]:
    merged = panel_df[["field_id", "field_name", "year"]].merge(
        retraction_df[["field_id", "year", "retracted_count"]],
        on=["field_id", "year"],
        how="left",
    )
    merged["retracted_count"] = pd.to_numeric(
        merged["retracted_count"],
        errors="coerce",
    ).fillna(0.0)
    merged = merged[merged["year"].between(START_YEAR, END_YEAR)].copy()

    top_fields_df = (
        merged.groupby("field_name", as_index=False)
        .agg(retracted_count=("retracted_count", "sum"))
        .sort_values(by="retracted_count", ascending=False)
        .head(6)
    )
    top_fields = top_fields_df["field_name"].tolist()
    merged["stack_field"] = np.where(
        merged["field_name"].isin(top_fields),
        merged["field_name"],
        "Other fields",
    )

    timeline = (
        merged.groupby(["year", "stack_field"], as_index=False)["retracted_count"]
        .sum()
        .pivot_table(
            index="year", columns="stack_field", values="retracted_count", fill_value=0
        )
        .sort_index()
    )
    ordered_cols = [field for field in top_fields if field in timeline.columns]
    if "Other fields" in timeline.columns:
        ordered_cols.append("Other fields")
    timeline = timeline[ordered_cols]

    palette = sns.color_palette("tab10", len(timeline.columns)).as_hex()
    fig, ax = plt.subplots(figsize=(7.0, 3.9))
    ax.stackplot(
        timeline.index,
        timeline.T.values,
        labels=timeline.columns,
        colors=palette,
        alpha=0.85,
    )
    ax.set_title("Figure 7. Retraction Timeline by Field")
    ax.set_xlabel("Year")
    ax.set_ylabel("Retracted papers")
    ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
    _style_axis(ax)
    fig.tight_layout()
    return _save_figure(fig, "figure_7_retraction_timeline_stacked", output_dir)


def main() -> None:
    setup_publication_style()
    panel_df, retraction_df, analysis = load_inputs()
    panel_main = panel_df[panel_df["year"].between(START_YEAR, END_YEAR)].copy()

    generated: list[str] = []
    generated.extend(generate_figure_1_timeline(panel_main, OUTPUT_DIR))
    generated.extend(generate_figure_2_heatmap(panel_main, OUTPUT_DIR))
    generated.extend(generate_figure_3_field_comparison(panel_main, OUTPUT_DIR))
    generated.extend(
        generate_figure_4_scurve_parameters(panel_main, analysis, OUTPUT_DIR)
    )
    generated.extend(generate_figure_5_correlation_matrix(analysis, OUTPUT_DIR))
    generated.extend(generate_figure_6_retraction_rates(analysis, OUTPUT_DIR))
    generated.extend(
        generate_figure_7_retraction_timeline(panel_main, retraction_df, OUTPUT_DIR)
    )

    print("Generated Neo4j publication figures:")
    for path in generated:
        print(f"- {path}")
    print(f"Total files generated: {len(generated)}")


if __name__ == "__main__":
    main()
