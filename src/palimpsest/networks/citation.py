from __future__ import annotations

import logging
from collections import deque
from typing import TypedDict, cast

import networkx as nx

logger = logging.getLogger(__name__)


class WorkRecord(TypedDict, total=False):
    id: str
    title: str
    publication_year: int
    cited_by_count: int
    doi: str
    referenced_works: list[str]


class CitationNetwork:
    """Build and query directed citation networks.

    Nodes represent papers and directed edges represent citation direction
    (citing paper -> cited paper).
    """

    def __init__(self) -> None:
        """Initialize an empty citation graph."""
        self._graph: nx.DiGraph[str] = nx.DiGraph()

    @property
    def graph(self) -> nx.DiGraph[str]:
        """Return the underlying directed citation graph.

        Returns:
            The internal citation graph.
        """
        return self._graph

    @property
    def node_count(self) -> int:
        """Return the total number of nodes in the graph.

        Returns:
            Number of nodes.
        """
        return int(self._graph.number_of_nodes())

    @property
    def edge_count(self) -> int:
        """Return the total number of edges in the graph.

        Returns:
            Number of edges.
        """
        return int(self._graph.number_of_edges())

    def build_from_works(self, works: list[WorkRecord]) -> nx.DiGraph[str]:
        """Build a citation graph from a list of works.

        This method replaces the current internal graph.

        Args:
            works: Work records containing OpenAlex-like fields.

        Returns:
            The built citation graph.
        """
        self._graph = nx.DiGraph()
        self.add_works(works)
        return self._graph

    def add_works(self, works: list[WorkRecord]) -> None:
        """Add works incrementally to the existing citation graph.

        Args:
            works: Work records containing identifiers and references.
        """
        for work in works:
            work_id_raw = work.get("id")
            if work_id_raw is None or not work_id_raw:
                logger.warning("Skipping work without valid id", extra={"work": work})
                continue

            work_id = work_id_raw
            self._graph.add_node(
                work_id,
                id=work_id,
                title=work.get("title"),
                publication_year=work.get("publication_year"),
                cited_by_count=work.get("cited_by_count"),
                doi=work.get("doi"),
            )

            referenced_works = work.get("referenced_works", [])
            for referenced_id in referenced_works:
                if referenced_id:
                    _ = self._graph.add_edge(work_id, referenced_id)

    def get_citing_papers(self, work_id: str) -> set[str]:
        """Get papers that cite a given work.

        Args:
            work_id: Identifier of the focal work.

        Returns:
            Set of citing paper IDs.
        """
        if work_id not in self._graph:
            return set()
        return {str(node_id) for node_id in self._graph.predecessors(work_id)}

    def get_references(self, work_id: str) -> set[str]:
        """Get papers referenced by a given work.

        Args:
            work_id: Identifier of the focal work.

        Returns:
            Set of referenced paper IDs.
        """
        if work_id not in self._graph:
            return set()
        return {str(node_id) for node_id in self._graph.successors(work_id)}

    def get_subgraph(self, work_ids: set[str], depth: int = 1) -> nx.DiGraph[str]:
        """Extract an induced subgraph around seed papers.

        Expansion uses breadth-first traversal in both citation directions up
        to the requested hop depth.

        Args:
            work_ids: Seed paper IDs.
            depth: Maximum BFS depth in hops.

        Returns:
            Directed subgraph induced by reached nodes.
        """
        if depth < 0:
            raise ValueError("depth must be >= 0")

        seeds = {work_id for work_id in work_ids if work_id in self._graph}
        if not seeds:
            return nx.DiGraph()

        visited: set[str] = set(seeds)
        queue: deque[tuple[str, int]] = deque((seed, 0) for seed in seeds)

        while queue:
            current, current_depth = queue.popleft()
            if current_depth >= depth:
                continue

            neighbors = set(self._graph.predecessors(current)) | set(
                self._graph.successors(current),
            )
            for neighbor in neighbors:
                neighbor_id = neighbor
                if neighbor_id in visited:
                    continue
                visited.add(neighbor_id)
                queue.append((neighbor_id, current_depth + 1))

        return cast("nx.DiGraph[str]", self._graph.subgraph(visited).copy())
