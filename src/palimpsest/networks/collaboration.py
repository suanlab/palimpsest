from __future__ import annotations

import logging
from itertools import combinations
from typing import TypedDict, cast

import networkx as nx

logger = logging.getLogger(__name__)


class InstitutionRecord(TypedDict, total=False):
    id: str
    display_name: str


class AuthorRecord(TypedDict, total=False):
    id: str
    display_name: str


class AuthorshipRecord(TypedDict, total=False):
    author: AuthorRecord
    institutions: list[InstitutionRecord]


class WorkRecord(TypedDict, total=False):
    authorships: list[AuthorshipRecord]


class CollaborationNetwork:
    """Build and query undirected co-authorship networks."""

    def __init__(self) -> None:
        """Initialize an empty collaboration graph."""
        self._graph: nx.Graph[str] = nx.Graph()

    @property
    def graph(self) -> nx.Graph[str]:
        """Return the underlying collaboration graph.

        Returns:
            The internal undirected co-authorship graph.
        """
        return self._graph

    @property
    def node_count(self) -> int:
        """Return the total number of author nodes.

        Returns:
            Number of author nodes.
        """
        return int(self._graph.number_of_nodes())

    @property
    def edge_count(self) -> int:
        """Return the total number of collaboration edges.

        Returns:
            Number of collaboration edges.
        """
        return int(self._graph.number_of_edges())

    def build_from_works(self, works: list[WorkRecord]) -> nx.Graph[str]:
        """Build a collaboration graph from work records.

        This method replaces the current internal graph.

        Args:
            works: Work records with OpenAlex-like authorship structure.

        Returns:
            The built undirected collaboration graph.
        """
        self._graph = nx.Graph()

        for work in works:
            authorships = work.get("authorships", [])

            author_ids: list[str] = []
            for authorship in authorships:
                author = authorship.get("author", {})
                author_id = author.get("id")
                if author_id is None or not author_id:
                    continue

                institutions = authorship.get("institutions", [])
                institution_name: str | None = None
                if institutions:
                    first_inst = institutions[0]
                    inst_name_raw = first_inst.get("display_name")
                    if inst_name_raw is not None:
                        institution_name = inst_name_raw

                self._graph.add_node(
                    author_id,
                    display_name=author.get("display_name"),
                    institution=institution_name,
                )
                author_ids.append(author_id)

            unique_authors = list(dict.fromkeys(author_ids))
            for author_a, author_b in combinations(unique_authors, 2):
                if self._graph.has_edge(author_a, author_b):
                    edge_data = cast(
                        dict[str, object],
                        self._graph.get_edge_data(author_a, author_b, default={}),
                    )
                    current_weight_raw = edge_data.get("weight", 0)
                    current_weight = (
                        current_weight_raw if isinstance(current_weight_raw, int) else 0
                    )
                    self._graph[author_a][author_b]["weight"] = current_weight + 1
                else:
                    _ = self._graph.add_edge(author_a, author_b, weight=1)

        return self._graph

    def get_collaborators(self, author_id: str) -> set[str]:
        """Get direct collaborators of an author.

        Args:
            author_id: Author identifier.

        Returns:
            Set of neighboring author IDs.
        """
        if author_id not in self._graph:
            return set()
        return {str(node_id) for node_id in self._graph.neighbors(author_id)}

    def get_collaboration_strength(self, author_a: str, author_b: str) -> int:
        """Get collaboration strength between two authors.

        Args:
            author_a: First author identifier.
            author_b: Second author identifier.

        Returns:
            Number of co-authored papers represented by edge weight.
        """
        if not self._graph.has_edge(author_a, author_b):
            return 0
        edge_data = cast(
            dict[str, object],
            self._graph.get_edge_data(author_a, author_b, default={}),
        )
        weight_raw = edge_data.get("weight", 0)
        return weight_raw if isinstance(weight_raw, int) else 0
