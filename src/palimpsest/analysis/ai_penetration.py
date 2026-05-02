from __future__ import annotations

from typing import Any, Protocol

import pandas as pd


class OpenAlexClient(Protocol):
    """Protocol for OpenAlex client operations used by this analyzer."""

    def get_works(self, **filters: Any) -> list[dict[str, Any]]:
        """Fetch works using OpenAlex-compatible filters."""
        ...


AI_SUBFIELD_ID = "https://openalex.org/subfields/1702"
AI_TOPIC_IDS: list[str] = [
    "https://openalex.org/topics/T12072",
    "https://openalex.org/topics/T10320",
    "https://openalex.org/topics/T10181",
    "https://openalex.org/topics/T13904",
    "https://openalex.org/topics/T12026",
    "https://openalex.org/topics/T11273",
    "https://openalex.org/topics/T10462",
]
AI_KEYWORDS: list[str] = [
    "machine learning",
    "deep learning",
    "neural network",
    "artificial intelligence",
    "natural language processing",
    "computer vision",
    "reinforcement learning",
    "transformer model",
    "convolutional neural",
    "generative adversarial",
    "large language model",
]


class AIPenetrationAnalyzer:
    """Analyze AI/ML adoption trends across scientific fields."""

    def __init__(self, client: OpenAlexClient) -> None:
        """Initialize the analyzer.

        Args:
            client: OpenAlex client used to fetch works.
        """
        self.client = client

    def classify_work_as_ai(self, work: dict[str, Any]) -> bool:
        """Classify whether a work is AI-related.

        A work is considered AI-related if one of these conditions is true:
        1) `primary_topic.subfield.id` equals the AI subfield,
        2) any topic ID appears in the configured AI topic list,
        3) title contains one of the configured AI keywords.

        Args:
            work: OpenAlex work record.

        Returns:
            True when classified as AI-related, otherwise False.
        """
        primary_topic = work.get("primary_topic")
        if isinstance(primary_topic, dict):
            subfield = primary_topic.get("subfield")
            if isinstance(subfield, dict):
                subfield_id = subfield.get("id")
                if isinstance(subfield_id, str) and subfield_id == AI_SUBFIELD_ID:
                    return True

        topics = work.get("topics", [])
        if isinstance(topics, list):
            for topic in topics:
                if not isinstance(topic, dict):
                    continue
                topic_id = topic.get("id")
                if isinstance(topic_id, str) and topic_id in AI_TOPIC_IDS:
                    return True

        title_raw = work.get("title")
        title = title_raw.lower() if isinstance(title_raw, str) else ""
        return any(keyword in title for keyword in AI_KEYWORDS)

    def compute_field_ai_adoption(
        self,
        field_id: str,
        year_range: tuple[int, int],
    ) -> pd.DataFrame:
        """Compute yearly AI adoption for a single field.

        Args:
            field_id: OpenAlex field identifier.
            year_range: Inclusive start and end year.

        Returns:
            DataFrame with columns: year, total_works, ai_works, ai_fraction.
        """
        start_year, end_year = year_range
        if start_year > end_year:
            raise ValueError("year_range start must be <= end")

        rows: list[dict[str, float | int]] = []
        for year in range(start_year, end_year + 1):
            works = self.client.get_works(
                filters={
                    "primary_topic.field.id": field_id,
                    "publication_year": year,
                },
            )
            total_works = len(works)
            ai_works = sum(1 for work in works if self.classify_work_as_ai(work))
            ai_fraction = (ai_works / total_works) if total_works > 0 else 0.0
            rows.append(
                {
                    "year": year,
                    "total_works": total_works,
                    "ai_works": ai_works,
                    "ai_fraction": ai_fraction,
                },
            )

        return pd.DataFrame(rows)

    def compute_adoption_timeline(
        self,
        field_ids: list[str],
        year_range: tuple[int, int],
    ) -> pd.DataFrame:
        """Compute AI adoption timeline across multiple fields.

        Args:
            field_ids: Field identifiers to evaluate.
            year_range: Inclusive start and end year.

        Returns:
            DataFrame with columns:
            field_id, year, total_works, ai_works, ai_fraction.
        """
        frames: list[pd.DataFrame] = []
        for field_id in field_ids:
            field_df = self.compute_field_ai_adoption(field_id, year_range).copy()
            field_df.insert(0, "field_id", field_id)
            frames.append(field_df)

        if not frames:
            return pd.DataFrame(
                {
                    "field_id": [],
                    "year": [],
                    "total_works": [],
                    "ai_works": [],
                    "ai_fraction": [],
                },
            )

        return pd.concat(frames, ignore_index=True)
