from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from typing import Any

import pandas as pd

from palimpsest.networks.citation import CitationNetwork


@dataclass(frozen=True)
class ContaminationEdge:
    """A single contamination propagation edge with metadata.

    Attributes:
        source_id: Paper that propagated contamination.
        target_id: Paper that received contamination.
        depth: Distance from original retracted paper (1 = direct citer).
        citation_year: Year the citing paper was published.
        retraction_year: Year the source paper was retracted.
        years_after_retraction: Citation year minus retraction year (negative = before).
        target_cited_by_count: How many papers cite the target (amplification factor).
        contamination_score: Composite time-weighted contamination score.
    """

    source_id: str
    target_id: str
    depth: int
    citation_year: int | None
    retraction_year: int | None
    years_after_retraction: int | None
    target_cited_by_count: int
    contamination_score: float


def compute_time_weighted_score(
    depth: int,
    years_after_retraction: int | None,
    cited_by_count: int,
    depth_decay: float = 0.5,
    time_weight_factor: float = 0.1,
    amplification_log_base: float = 10.0,
) -> float:
    """Compute a composite contamination score.

    Score components:
    1. Depth decay: ``depth_decay ** depth`` (deeper = less direct contamination).
    2. Time penalty: citations AFTER retraction get a multiplier > 1.
       ``1 + time_weight_factor * max(0, years_after_retraction)``.
       Citations BEFORE retraction get no time penalty (multiplier = 1).
    3. Amplification: ``1 + log(1 + cited_by_count)`` — high-cited papers
       amplify contamination because more downstream papers are exposed.

    Final score = depth_component * time_component * amplification_component.

    Args:
        depth: Hop distance from retracted paper (>= 1).
        years_after_retraction: How many years after retraction the citation
            occurred. None if unknown. Negative means before retraction.
        cited_by_count: Number of citations the contaminated paper received.
        depth_decay: Exponential decay factor per hop. Default 0.5.
        time_weight_factor: Linear weight per year after retraction. Default 0.1.
        amplification_log_base: Log base for amplification term. Default 10.

    Returns:
        Composite contamination score (>= 0).
    """
    depth_component = depth_decay ** max(depth, 1)

    if years_after_retraction is not None and years_after_retraction > 0:
        time_component = 1.0 + time_weight_factor * years_after_retraction
    else:
        time_component = 1.0

    amplification_component = 1.0 + math.log(
        1.0 + max(cited_by_count, 0),
        amplification_log_base,
    )

    return depth_component * time_component * amplification_component


class RetractionPropagationAnalyzer:
    """Analyze contamination propagation from retracted papers."""

    def __init__(self, citation_network: CitationNetwork) -> None:
        """Initialize the analyzer.

        Args:
            citation_network: Citation network used for propagation tracing.
        """
        self.citation_network = citation_network

    def trace_propagation(
        self, retracted_id: str, max_depth: int = 3
    ) -> dict[int, set[str]]:
        """Trace propagation levels from a retracted paper using BFS.

        Depth 1 includes direct citers of the retracted paper, depth 2 includes
        citers of depth-1 papers, and so on up to `max_depth`.

        Args:
            retracted_id: Identifier of the retracted paper.
            max_depth: Maximum traversal depth.

        Returns:
            Mapping from depth to set of paper IDs at that depth.
        """
        if max_depth < 1:
            return {}

        propagation: dict[int, set[str]] = {}
        visited: set[str] = {retracted_id}
        queue: deque[tuple[str, int]] = deque([(retracted_id, 0)])

        while queue:
            current_id, depth = queue.popleft()
            if depth >= max_depth:
                continue

            citing_papers = self.citation_network.get_citing_papers(current_id)
            next_depth = depth + 1
            for citing_id in citing_papers:
                if citing_id in visited:
                    continue
                visited.add(citing_id)
                propagation.setdefault(next_depth, set()).add(citing_id)
                queue.append((citing_id, next_depth))

        return propagation

    def compute_contamination_score(
        self,
        retracted_id: str,
        max_depth: int = 3,
    ) -> dict[str, float]:
        """Compute depth-decayed contamination scores.

        Args:
            retracted_id: Identifier of the retracted paper.
            max_depth: Maximum propagation depth.

        Returns:
            Per-paper contamination score where score is `1 / depth`.
        """
        propagation = self.trace_propagation(retracted_id, max_depth=max_depth)
        scores: dict[str, float] = {}
        for depth, paper_ids in propagation.items():
            if depth <= 0:
                continue
            score = 1.0 / depth
            for paper_id in paper_ids:
                scores[paper_id] = score
        return scores

    def analyze_self_correction(
        self,
        retracted_id: str,
        retraction_year: int,
        citations_by_year: dict[str, dict[int, int]],
    ) -> pd.DataFrame:
        """Assess whether citing papers reduce citations after retraction.

        Args:
            retracted_id: Identifier of the retracted paper.
            retraction_year: Retraction year threshold.
            citations_by_year: Mapping of citing paper ID to yearly citation counts.

        Returns:
            DataFrame with columns:
            citing_paper_id, pre_retraction_citations,
            post_retraction_citations, correction_ratio.
        """
        _ = retracted_id

        rows: list[dict[str, str | int | float]] = []
        for citing_paper_id, yearly_counts in citations_by_year.items():
            pre_retraction_citations = sum(
                count
                for year, count in yearly_counts.items()
                if year < retraction_year and count > 0
            )
            post_retraction_citations = sum(
                count
                for year, count in yearly_counts.items()
                if year > retraction_year and count > 0
            )

            if pre_retraction_citations > 0:
                correction_ratio = (
                    pre_retraction_citations - post_retraction_citations
                ) / pre_retraction_citations
            else:
                correction_ratio = 0.0

            rows.append(
                {
                    "citing_paper_id": citing_paper_id,
                    "pre_retraction_citations": pre_retraction_citations,
                    "post_retraction_citations": post_retraction_citations,
                    "correction_ratio": correction_ratio,
                },
            )

        return pd.DataFrame(rows)

    def propagation_summary(
        self,
        retracted_id: str,
        max_depth: int = 3,
    ) -> dict[str, Any]:
        """Build a summary of contamination propagation.

        Args:
            retracted_id: Identifier of the retracted paper.
            max_depth: Maximum propagation depth.

        Returns:
            Summary dictionary with totals, depth distribution, and average score.
        """
        propagation = self.trace_propagation(retracted_id, max_depth=max_depth)
        scores = self.compute_contamination_score(retracted_id, max_depth=max_depth)

        papers_by_depth = {
            depth: len(propagation.get(depth, set()))
            for depth in range(1, max_depth + 1)
        }
        total_affected_papers = sum(papers_by_depth.values())
        avg_score = sum(scores.values()) / len(scores) if scores else 0.0

        return {
            "retracted_id": retracted_id,
            "total_affected_papers": total_affected_papers,
            "papers_by_depth": papers_by_depth,
            "avg_contamination_score": avg_score,
        }

    def build_contamination_edges(
        self,
        retracted_id: str,
        retraction_year: int | None = None,
        max_depth: int = 3,
    ) -> list[ContaminationEdge]:
        """Build time-weighted contamination edges from a retracted paper.

        Each edge represents a contamination link: source (closer to retracted)
        cited by target (further from retracted). Edges carry composite scores
        factoring depth decay, post-retraction time penalty, and citation
        amplification.

        Args:
            retracted_id: Identifier of the retracted paper.
            retraction_year: Year the paper was retracted (for time weighting).
            max_depth: Maximum BFS depth.

        Returns:
            List of scored contamination edges.
        """
        graph = self.citation_network.graph

        visited: set[str] = {retracted_id}
        queue: deque[tuple[str, int]] = deque([(retracted_id, 0)])
        edges: list[ContaminationEdge] = []

        while queue:
            current_id, depth = queue.popleft()
            if depth >= max_depth:
                continue

            citing_papers = self.citation_network.get_citing_papers(current_id)
            next_depth = depth + 1

            for citing_id in citing_papers:
                if citing_id in visited:
                    continue
                visited.add(citing_id)
                queue.append((citing_id, next_depth))

                node_data = graph.nodes.get(citing_id, {})
                citation_year = node_data.get("publication_year")
                cited_by_count = node_data.get("cited_by_count", 0) or 0

                years_after: int | None = None
                if retraction_year is not None and isinstance(citation_year, int):
                    years_after = citation_year - retraction_year

                score = compute_time_weighted_score(
                    depth=next_depth,
                    years_after_retraction=years_after,
                    cited_by_count=cited_by_count,
                )

                edges.append(
                    ContaminationEdge(
                        source_id=current_id,
                        target_id=citing_id,
                        depth=next_depth,
                        citation_year=citation_year,
                        retraction_year=retraction_year,
                        years_after_retraction=years_after,
                        target_cited_by_count=cited_by_count,
                        contamination_score=score,
                    ),
                )

        return edges

    def contamination_edges_to_dataframe(
        self,
        edges: list[ContaminationEdge],
    ) -> pd.DataFrame:
        """Convert contamination edges to a DataFrame.

        Args:
            edges: List of contamination edges.

        Returns:
            DataFrame with one row per edge and all edge attributes as columns.
        """
        if not edges:
            return pd.DataFrame(
                columns=[
                    "source_id",
                    "target_id",
                    "depth",
                    "citation_year",
                    "retraction_year",
                    "years_after_retraction",
                    "target_cited_by_count",
                    "contamination_score",
                ],
            )

        rows = [
            {
                "source_id": edge.source_id,
                "target_id": edge.target_id,
                "depth": edge.depth,
                "citation_year": edge.citation_year,
                "retraction_year": edge.retraction_year,
                "years_after_retraction": edge.years_after_retraction,
                "target_cited_by_count": edge.target_cited_by_count,
                "contamination_score": edge.contamination_score,
            }
            for edge in edges
        ]
        return pd.DataFrame(rows)
