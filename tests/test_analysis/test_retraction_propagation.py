from __future__ import annotations

import pytest

from palimpsest.analysis.retraction_propagation import (
    RetractionPropagationAnalyzer,
    compute_time_weighted_score,
)
from palimpsest.networks.citation import CitationNetwork


@pytest.fixture
def retraction_network() -> CitationNetwork:
    """Build a citation network with a retracted paper and cascading citers.

    Graph structure (edges = citing → cited):
        W_retracted (2015, retracted)
        ├── W_d1a (2016, cites retracted, cited_by_count=50)
        │   ├── W_d2a (2018, cites W_d1a, cited_by_count=20)
        │   │   └── W_d3a (2020, cites W_d2a, cited_by_count=5)
        │   └── W_d2b (2022, cites W_d1a, cited_by_count=10)
        └── W_d1b (2014, cites retracted, cited_by_count=30)
    """
    cn = CitationNetwork()
    cn.add_works(
        [
            {
                "id": "W_retracted",
                "title": "Retracted paper",
                "publication_year": 2015,
                "cited_by_count": 100,
                "doi": "10.1000/retracted",
                "referenced_works": [],
            },
            {
                "id": "W_d1a",
                "title": "Direct citer A",
                "publication_year": 2016,
                "cited_by_count": 50,
                "doi": "10.1000/d1a",
                "referenced_works": ["W_retracted"],
            },
            {
                "id": "W_d1b",
                "title": "Direct citer B (pre-retraction)",
                "publication_year": 2014,
                "cited_by_count": 30,
                "doi": "10.1000/d1b",
                "referenced_works": ["W_retracted"],
            },
            {
                "id": "W_d2a",
                "title": "Second-order citer A",
                "publication_year": 2018,
                "cited_by_count": 20,
                "doi": "10.1000/d2a",
                "referenced_works": ["W_d1a"],
            },
            {
                "id": "W_d2b",
                "title": "Second-order citer B",
                "publication_year": 2022,
                "cited_by_count": 10,
                "doi": "10.1000/d2b",
                "referenced_works": ["W_d1a"],
            },
            {
                "id": "W_d3a",
                "title": "Third-order citer",
                "publication_year": 2020,
                "cited_by_count": 5,
                "doi": "10.1000/d3a",
                "referenced_works": ["W_d2a"],
            },
        ],
    )
    return cn


class TestComputeTimeWeightedScore:
    def test_depth_decay(self) -> None:
        score_d1 = compute_time_weighted_score(
            depth=1, years_after_retraction=None, cited_by_count=0
        )
        score_d2 = compute_time_weighted_score(
            depth=2, years_after_retraction=None, cited_by_count=0
        )
        score_d3 = compute_time_weighted_score(
            depth=3, years_after_retraction=None, cited_by_count=0
        )
        assert score_d1 > score_d2 > score_d3 > 0

    def test_post_retraction_penalty(self) -> None:
        score_before = compute_time_weighted_score(
            depth=1, years_after_retraction=-2, cited_by_count=0
        )
        score_at = compute_time_weighted_score(
            depth=1, years_after_retraction=0, cited_by_count=0
        )
        score_after = compute_time_weighted_score(
            depth=1, years_after_retraction=5, cited_by_count=0
        )
        assert score_before == score_at
        assert score_after > score_at

    def test_amplification_increases_with_citations(self) -> None:
        score_low = compute_time_weighted_score(
            depth=1, years_after_retraction=None, cited_by_count=1
        )
        score_high = compute_time_weighted_score(
            depth=1, years_after_retraction=None, cited_by_count=1000
        )
        assert score_high > score_low

    def test_zero_depth_uses_minimum(self) -> None:
        score = compute_time_weighted_score(
            depth=0, years_after_retraction=None, cited_by_count=0
        )
        assert score > 0

    def test_negative_years_no_penalty(self) -> None:
        score = compute_time_weighted_score(
            depth=1, years_after_retraction=-10, cited_by_count=0
        )
        baseline = compute_time_weighted_score(
            depth=1, years_after_retraction=None, cited_by_count=0
        )
        assert score == baseline


class TestBuildContaminationEdges:
    def test_basic_traversal(self, retraction_network: CitationNetwork) -> None:
        analyzer = RetractionPropagationAnalyzer(retraction_network)
        edges = analyzer.build_contamination_edges(
            "W_retracted", retraction_year=2016, max_depth=3
        )
        target_ids = {e.target_id for e in edges}
        assert "W_d1a" in target_ids
        assert "W_d1b" in target_ids
        assert "W_d2a" in target_ids
        assert "W_d2b" in target_ids
        assert "W_d3a" in target_ids
        assert "W_retracted" not in target_ids

    def test_depth_assignment(self, retraction_network: CitationNetwork) -> None:
        analyzer = RetractionPropagationAnalyzer(retraction_network)
        edges = analyzer.build_contamination_edges(
            "W_retracted", retraction_year=2016, max_depth=3
        )
        depth_map = {e.target_id: e.depth for e in edges}
        assert depth_map["W_d1a"] == 1
        assert depth_map["W_d1b"] == 1
        assert depth_map["W_d2a"] == 2
        assert depth_map["W_d2b"] == 2
        assert depth_map["W_d3a"] == 3

    def test_max_depth_limits_traversal(
        self, retraction_network: CitationNetwork
    ) -> None:
        analyzer = RetractionPropagationAnalyzer(retraction_network)
        edges = analyzer.build_contamination_edges(
            "W_retracted", retraction_year=2016, max_depth=1
        )
        target_ids = {e.target_id for e in edges}
        assert "W_d1a" in target_ids
        assert "W_d1b" in target_ids
        assert "W_d2a" not in target_ids

    def test_years_after_retraction_computed(
        self, retraction_network: CitationNetwork
    ) -> None:
        analyzer = RetractionPropagationAnalyzer(retraction_network)
        edges = analyzer.build_contamination_edges(
            "W_retracted", retraction_year=2016, max_depth=3
        )
        years_map = {e.target_id: e.years_after_retraction for e in edges}
        assert years_map["W_d1a"] == 0
        assert years_map["W_d1b"] == -2
        assert years_map["W_d2a"] == 2
        assert years_map["W_d2b"] == 6
        assert years_map["W_d3a"] == 4

    def test_scores_decrease_with_depth(
        self, retraction_network: CitationNetwork
    ) -> None:
        analyzer = RetractionPropagationAnalyzer(retraction_network)
        edges = analyzer.build_contamination_edges(
            "W_retracted", retraction_year=2016, max_depth=3
        )
        score_map = {e.target_id: e.contamination_score for e in edges}
        assert all(s > 0 for s in score_map.values())

    def test_empty_for_unknown_paper(self, retraction_network: CitationNetwork) -> None:
        analyzer = RetractionPropagationAnalyzer(retraction_network)
        edges = analyzer.build_contamination_edges(
            "W_unknown", retraction_year=2016, max_depth=3
        )
        assert edges == []

    def test_to_dataframe(self, retraction_network: CitationNetwork) -> None:
        analyzer = RetractionPropagationAnalyzer(retraction_network)
        edges = analyzer.build_contamination_edges(
            "W_retracted", retraction_year=2016, max_depth=3
        )
        df = analyzer.contamination_edges_to_dataframe(edges)
        assert len(df) == 5
        assert set(df.columns) == {
            "source_id",
            "target_id",
            "depth",
            "citation_year",
            "retraction_year",
            "years_after_retraction",
            "target_cited_by_count",
            "contamination_score",
        }

    def test_empty_dataframe(self, retraction_network: CitationNetwork) -> None:
        analyzer = RetractionPropagationAnalyzer(retraction_network)
        df = analyzer.contamination_edges_to_dataframe([])
        assert len(df) == 0
        assert "contamination_score" in df.columns
