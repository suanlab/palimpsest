from __future__ import annotations

from typing import Any

import networkx as nx
import pandas as pd
import pytest


@pytest.fixture
def sample_works() -> list[dict[str, Any]]:
    """Provide a small OpenAlex-like work list for tests."""
    w1 = {
        "id": "https://openalex.org/W1",
        "title": "Foundations of network science",
        "publication_year": 2019,
        "cited_by_count": 12,
        "doi": "https://doi.org/10.1000/w1",
        "referenced_works": [],
        "primary_topic": {
            "id": "T1000",
            "subfield": {"id": "https://openalex.org/subfields/1101"},
        },
        "topics": [{"id": "https://openalex.org/topics/T1000"}],
        "authorships": [
            {
                "author": {
                    "id": "https://openalex.org/A1",
                    "display_name": "Author One",
                },
                "institutions": [
                    {
                        "id": "https://openalex.org/I1",
                        "display_name": "Institute One",
                    },
                ],
            },
        ],
    }
    w2 = {
        "id": "https://openalex.org/W2",
        "title": "Follow-up statistical analysis",
        "publication_year": 2020,
        "cited_by_count": 8,
        "doi": "https://doi.org/10.1000/w2",
        "referenced_works": ["https://openalex.org/W1"],
        "primary_topic": {
            "id": "T1001",
            "subfield": {"id": "https://openalex.org/subfields/1102"},
        },
        "topics": [{"id": "https://openalex.org/topics/T1001"}],
        "authorships": [
            {
                "author": {
                    "id": "https://openalex.org/A2",
                    "display_name": "Author Two",
                },
                "institutions": [
                    {
                        "id": "https://openalex.org/I2",
                        "display_name": "Institute Two",
                    },
                ],
            },
        ],
    }
    w3 = {
        "id": "https://openalex.org/W3",
        "title": "Comparative benchmark study",
        "publication_year": 2021,
        "cited_by_count": 6,
        "doi": "https://doi.org/10.1000/w3",
        "referenced_works": ["https://openalex.org/W1", "https://openalex.org/W2"],
        "primary_topic": {
            "id": "T1002",
            "subfield": {"id": "https://openalex.org/subfields/1103"},
        },
        "topics": [{"id": "https://openalex.org/topics/T1002"}],
        "authorships": [
            {
                "author": {
                    "id": "https://openalex.org/A3",
                    "display_name": "Author Three",
                },
                "institutions": [
                    {
                        "id": "https://openalex.org/I3",
                        "display_name": "Institute Three",
                    },
                ],
            },
        ],
    }
    w4 = {
        "id": "https://openalex.org/W4",
        "title": "Expanded empirical replication",
        "publication_year": 2022,
        "cited_by_count": 4,
        "doi": "https://doi.org/10.1000/w4",
        "referenced_works": ["https://openalex.org/W2", "https://openalex.org/W3"],
        "primary_topic": {
            "id": "T1003",
            "subfield": {"id": "https://openalex.org/subfields/1104"},
        },
        "topics": [{"id": "https://openalex.org/topics/T1003"}],
        "authorships": [
            {
                "author": {
                    "id": "https://openalex.org/A4",
                    "display_name": "Author Four",
                },
                "institutions": [
                    {
                        "id": "https://openalex.org/I4",
                        "display_name": "Institute Four",
                    },
                ],
            },
        ],
    }
    w5 = {
        "id": "https://openalex.org/W5",
        "title": "Applied extension in field setting",
        "publication_year": 2023,
        "cited_by_count": 2,
        "doi": "https://doi.org/10.1000/w5",
        "referenced_works": ["https://openalex.org/W1"],
        "primary_topic": {
            "id": "T1004",
            "subfield": {"id": "https://openalex.org/subfields/1105"},
        },
        "topics": [{"id": "https://openalex.org/topics/T1004"}],
        "authorships": [
            {
                "author": {
                    "id": "https://openalex.org/A5",
                    "display_name": "Author Five",
                },
                "institutions": [
                    {
                        "id": "https://openalex.org/I5",
                        "display_name": "Institute Five",
                    },
                ],
            },
        ],
    }
    return [w1, w2, w3, w4, w5]


@pytest.fixture
def sample_citation_graph(sample_works: list[dict[str, Any]]) -> nx.DiGraph[str]:
    """Construct a citation graph from sample works."""
    graph = nx.DiGraph()
    for work in sample_works:
        work_id = work["id"]
        graph.add_node(work_id)
        referenced = work["referenced_works"]
        if not isinstance(referenced, list):
            continue
        for referenced_id in referenced:
            if isinstance(referenced_id, str):
                graph.add_edge(str(work_id), referenced_id)
    return graph


@pytest.fixture
def sample_retraction_watch_df() -> pd.DataFrame:
    """Provide minimal retraction metadata frame for tests."""
    return pd.DataFrame(
        [
            {
                "Record ID": 1,
                "Title": "Retraction of Clinical Trial A",
                "OriginalPaperDOI": "10.1000/ret-a",
                "OriginalPaperPubMedID": "10001",
                "RetractionDate": "2021-06-01",
                "RetractionNature": "Retraction",
                "Reason": "Data fabrication",
            },
            {
                "Record ID": 2,
                "Title": "Retraction of Genomics Study B",
                "OriginalPaperDOI": "10.1000/ret-b",
                "OriginalPaperPubMedID": "10002",
                "RetractionDate": "2022-02-14",
                "RetractionNature": "Retraction",
                "Reason": "Image manipulation",
            },
            {
                "Record ID": 3,
                "Title": "Retraction of Materials Study C",
                "OriginalPaperDOI": "10.1000/ret-c",
                "OriginalPaperPubMedID": "10003",
                "RetractionDate": "2023-09-08",
                "RetractionNature": "Retraction",
                "Reason": "Plagiarism",
            },
        ],
    )
