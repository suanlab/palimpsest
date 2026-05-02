#!/usr/bin/env python3
"""Generate research figures from collected data."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid", palette="husl")

FIGURES_DIR = Path("data/processed/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = Path("data/processed")


def save_figure(filename: str) -> None:
    plt.savefig(FIGURES_DIR / filename, dpi=150, bbox_inches="tight")
    plt.close()


def generate_ai_figures(ai_df: pd.DataFrame) -> list[str]:
    generated: list[str] = []

    _, ax = plt.subplots(figsize=(14, 8), dpi=150)
    for field_name, group in ai_df.groupby("field_name"):
        sorted_group = group.sort_values("year")
        ax.plot(
            sorted_group["year"],
            sorted_group["ai_fraction"] * 100,
            linewidth=2,
            label=field_name,
        )
    ax.set_title("AI Adoption Timeline by Scientific Field")
    ax.set_xlabel("Year")
    ax.set_ylabel("AI Fraction (%)")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", title="Field")
    save_figure("ai_adoption_timeline.png")
    generated.append("ai_adoption_timeline.png")

    heatmap_data = ai_df.pivot_table(
        index="field_name",
        columns="year",
        values="ai_fraction",
    )
    _, ax = plt.subplots(figsize=(14, 8), dpi=150)
    sns.heatmap(heatmap_data * 100, cmap="YlOrRd", ax=ax)
    ax.set_title("AI Adoption Heatmap by Field and Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Field")
    save_figure("ai_adoption_heatmap.png")
    generated.append("ai_adoption_heatmap.png")

    recent_avg = (
        ai_df[ai_df["year"].between(2020, 2024)]
        .groupby("field_name")["ai_fraction"]
        .mean()
    )
    early_avg = (
        ai_df[ai_df["year"].between(2010, 2014)]
        .groupby("field_name")["ai_fraction"]
        .mean()
    )
    acceleration = (
        (recent_avg - early_avg).dropna().astype(float).sort_values(ascending=True)
    )
    acceleration_pct = acceleration.mul(100.0)
    _, ax = plt.subplots(figsize=(14, 8), dpi=150)
    ax.barh(acceleration_pct.index.tolist(), acceleration_pct.to_numpy())
    ax.set_title("AI Adoption Acceleration by Field")
    ax.set_xlabel("Change in AI Fraction (2020-2024 avg vs 2010-2014 avg, pp)")
    ax.set_ylabel("Field")
    save_figure("ai_adoption_acceleration.png")
    generated.append("ai_adoption_acceleration.png")

    area_data = ai_df.pivot_table(
        index="year", columns="field_name", values="ai_count", fill_value=0
    ).sort_index()
    _, ax = plt.subplots(figsize=(14, 8), dpi=150)
    ax.stackplot(
        area_data.index,
        area_data.T.values,
        labels=area_data.columns,
        alpha=0.8,
    )
    ax.set_title("Absolute AI Works Growth by Field")
    ax.set_xlabel("Year")
    ax.set_ylabel("AI Works (count)")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", title="Field")
    save_figure("ai_absolute_growth.png")
    generated.append("ai_absolute_growth.png")

    return generated


def generate_retraction_figures(
    retracted_df: pd.DataFrame,
    citers_df: pd.DataFrame,
) -> list[str]:
    generated: list[str] = []

    _, ax = plt.subplots(figsize=(14, 8), dpi=150)
    ax.hist(
        retracted_df["cited_by_count"].dropna(), bins=50, edgecolor="black", alpha=0.7
    )
    ax.set_yscale("log")
    ax.set_title("Citation Count Distribution of Retracted Papers")
    ax.set_xlabel("Cited By Count")
    ax.set_ylabel("Number of Retracted Papers (log scale)")
    save_figure("retraction_citation_dist.png")
    generated.append("retraction_citation_dist.png")

    citers_per_paper = (
        citers_df.groupby("retracted_doi").size().reset_index(name="num_citers")
    )
    top20 = (
        citers_per_paper.merge(
            retracted_df[["doi", "title", "cited_by_count"]],
            left_on="retracted_doi",
            right_on="doi",
            how="left",
        )
        .sort_values("num_citers", ascending=False)
        .head(20)
        .sort_values("num_citers", ascending=True)
    )
    labels = [
        f"{str(title)[:65]}{'...' if len(str(title)) > 65 else ''}"
        for title in top20["title"].fillna("Unknown title")
    ]
    _, ax = plt.subplots(figsize=(14, 8), dpi=150)
    ax.barh(labels, top20["num_citers"], alpha=0.85)
    ax.set_title("Top 20 Most-Cited Retracted Papers (by Captured Citers)")
    ax.set_xlabel("Number of Citing Papers")
    ax.set_ylabel("Retracted Paper Title")
    save_figure("retraction_top20_cited.png")
    generated.append("retraction_top20_cited.png")

    merged = citers_df.merge(
        retracted_df[["doi", "publication_year"]],
        left_on="retracted_doi",
        right_on="doi",
        how="left",
    )
    merged["years_after_publication"] = (
        merged["citing_year"] - merged["publication_year"]
    )
    _, ax = plt.subplots(figsize=(14, 8), dpi=150)
    ax.hist(
        merged["years_after_publication"].dropna(),
        bins=40,
        edgecolor="black",
        alpha=0.7,
    )
    ax.axvline(0, color="red", linestyle="--", label="Publication year")
    ax.set_title("Temporal Lag of Citations to Retracted Papers")
    ax.set_xlabel("Years After Publication")
    ax.set_ylabel("Number of Citing Papers")
    ax.legend()
    save_figure("retraction_temporal.png")
    generated.append("retraction_temporal.png")

    return generated


def main() -> None:
    ai_df = pd.read_parquet(DATA_DIR / "ai_adoption_by_field.parquet")
    retracted_df = pd.read_parquet(DATA_DIR / "retracted_papers.parquet")
    citers_df = pd.read_parquet(DATA_DIR / "retraction_citers.parquet")

    generated: list[str] = []
    generated.extend(generate_ai_figures(ai_df))
    generated.extend(generate_retraction_figures(retracted_df, citers_df))

    print("Generated figures:")
    for filename in generated:
        print(f"- {FIGURES_DIR / filename}")


if __name__ == "__main__":
    main()
