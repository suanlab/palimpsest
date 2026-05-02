from __future__ import annotations

from typing import cast

from palimpsest.networks.citation import CitationNetwork, WorkRecord


def test_build_from_works(sample_works: list[dict[str, object]]) -> None:
    network = CitationNetwork()
    network.build_from_works(cast(list[WorkRecord], sample_works))

    assert network.node_count == 5
    assert network.edge_count == 6


def test_get_citing_papers(sample_works: list[dict[str, object]]) -> None:
    network = CitationNetwork()
    network.build_from_works(cast(list[WorkRecord], sample_works))

    citing = network.get_citing_papers("https://openalex.org/W1")
    assert citing == {
        "https://openalex.org/W2",
        "https://openalex.org/W3",
        "https://openalex.org/W5",
    }


def test_get_references(sample_works: list[dict[str, object]]) -> None:
    network = CitationNetwork()
    network.build_from_works(cast(list[WorkRecord], sample_works))

    references = network.get_references("https://openalex.org/W3")
    assert references == {
        "https://openalex.org/W1",
        "https://openalex.org/W2",
    }


def test_get_subgraph(sample_works: list[dict[str, object]]) -> None:
    network = CitationNetwork()
    network.build_from_works(cast(list[WorkRecord], sample_works))

    subgraph = network.get_subgraph({"https://openalex.org/W3"}, depth=1)
    assert {
        "https://openalex.org/W1",
        "https://openalex.org/W2",
        "https://openalex.org/W3",
    }.issubset(set(subgraph.nodes()))
