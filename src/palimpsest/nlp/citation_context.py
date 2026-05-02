from __future__ import annotations

from enum import StrEnum
from typing import Any

from palimpsest.data.semantic_scholar import SemanticScholarClient


class CitationIntent(StrEnum):
    """Enumeration of citation intents."""

    SUPPORTING = "supporting"
    CONTRASTING = "contrasting"
    METHODOLOGICAL = "methodological"
    BACKGROUND = "background"
    PERFUNCTORY = "perfunctory"
    UNKNOWN = "unknown"


class CitationContextClassifier:
    """Classify citation context intent using API metadata and heuristics."""

    def __init__(self, client: SemanticScholarClient | None = None) -> None:
        """Initialize the classifier.

        Args:
            client: Optional Semantic Scholar client.
        """
        self.client = client

    def classify_from_semantic_scholar(self, paper_id: str) -> list[dict[str, Any]]:
        """Fetch and normalize citation intents from Semantic Scholar.

        Args:
            paper_id: Identifier of the focal paper.

        Returns:
            List of dictionaries with keys:
            citing_paper_id, intents, contexts.
        """
        if self.client is None:
            return []

        raw_citations = self.client.get_citations_with_context(paper_id)
        normalized: list[dict[str, Any]] = []

        for citation in raw_citations:
            citing_paper_id_raw = citation.get("citing_paper_id")
            if not isinstance(citing_paper_id_raw, str) or not citing_paper_id_raw:
                continue

            raw_intents = citation.get("intents", [])
            intents: list[CitationIntent] = []
            if isinstance(raw_intents, list):
                intents = [_to_citation_intent(intent) for intent in raw_intents]

            raw_contexts = citation.get("contexts", [])
            contexts = [text for text in raw_contexts if isinstance(text, str)]

            normalized.append(
                {
                    "citing_paper_id": citing_paper_id_raw,
                    "intents": intents,
                    "contexts": contexts,
                },
            )

        return normalized

    def classify_context(self, context_text: str) -> CitationIntent:
        """Classify citation intent from a context string.

        Args:
            context_text: Raw citation context text.

        Returns:
            Predicted citation intent.
        """
        normalized_text = context_text.lower()

        contrasting_keywords = ["however", "contradict", "unlike", "challenge"]
        if any(keyword in normalized_text for keyword in contrasting_keywords):
            return CitationIntent.CONTRASTING

        methodological_keywords = ["we use", "we adopt", "following", "based on"]
        if any(keyword in normalized_text for keyword in methodological_keywords):
            return CitationIntent.METHODOLOGICAL

        supporting_keywords = ["consistent with", "confirms", "supports"]
        if any(keyword in normalized_text for keyword in supporting_keywords):
            return CitationIntent.SUPPORTING

        return CitationIntent.BACKGROUND

    def batch_classify(self, contexts: list[str]) -> list[CitationIntent]:
        """Classify a batch of citation contexts.

        Args:
            contexts: Citation context texts.

        Returns:
            Predicted intent list in input order.
        """
        return [self.classify_context(context) for context in contexts]


def compute_context_weighted_citations(
    citations: list[dict[str, Any]],
) -> dict[str, float]:
    """Compute citation weights based on intent labels.

    Args:
        citations: Citation records with keys `citing_paper_id` and `intents`.

    Returns:
        Mapping of citing paper ID to weighted citation score.
    """
    weights = {
        CitationIntent.SUPPORTING: 1.0,
        CitationIntent.METHODOLOGICAL: 0.8,
        CitationIntent.BACKGROUND: 0.3,
        CitationIntent.PERFUNCTORY: 0.1,
        CitationIntent.CONTRASTING: -0.5,
        CitationIntent.UNKNOWN: 0.5,
    }

    weighted_scores: dict[str, float] = {}
    for citation in citations:
        citing_paper_id = citation.get("citing_paper_id")
        if not isinstance(citing_paper_id, str) or not citing_paper_id:
            continue

        raw_intents = citation.get("intents", [])
        intents = (
            [_to_citation_intent(intent) for intent in raw_intents]
            if isinstance(raw_intents, list)
            else [CitationIntent.UNKNOWN]
        )
        if not intents:
            intents = [CitationIntent.UNKNOWN]

        entry_score = sum(weights[intent] for intent in intents) / len(intents)
        weighted_scores[citing_paper_id] = (
            weighted_scores.get(citing_paper_id, 0.0) + entry_score
        )

    return weighted_scores


def _to_citation_intent(intent: Any) -> CitationIntent:
    """Convert free-form intent value to CitationIntent."""
    if isinstance(intent, CitationIntent):
        return intent
    if isinstance(intent, str):
        try:
            return CitationIntent(intent.lower())
        except ValueError:
            return CitationIntent.UNKNOWN
    return CitationIntent.UNKNOWN
