from __future__ import annotations

import logging
from typing import cast

import networkx as nx

logger = logging.getLogger(__name__)

type GraphLike = nx.Graph[str] | nx.DiGraph[str]


def degree_centrality(graph: GraphLike) -> dict[str, float]:
    """Compute degree centrality for all nodes.

    Args:
        graph: Input graph.

    Returns:
        Mapping from node ID to degree centrality score.
    """
    return {str(node): score for node, score in nx.degree_centrality(graph).items()}


def betweenness_centrality(
    graph: GraphLike,
    k: int | None = None,
) -> dict[str, float]:
    """Compute betweenness centrality for all nodes.

    Args:
        graph: Input graph.
        k: Number of nodes to sample for approximation on large graphs.

    Returns:
        Mapping from node ID to betweenness centrality score.
    """
    return {
        str(node): score
        for node, score in nx.betweenness_centrality(graph, k=k).items()
    }


def pagerank(graph: nx.DiGraph[str], alpha: float = 0.85) -> dict[str, float]:
    """Compute PageRank scores for a directed graph.

    Args:
        graph: Directed citation graph.
        alpha: Damping parameter.

    Returns:
        Mapping from node ID to PageRank score.
    """
    return {str(node): score for node, score in nx.pagerank(graph, alpha=alpha).items()}


def detect_communities(graph: nx.Graph[str], resolution: float = 1.0) -> dict[str, int]:
    """Detect communities using Louvain optimization.

    Args:
        graph: Input graph.
        resolution: Community resolution parameter.

    Returns:
        Mapping from node ID to integer community ID.
    """
    communities = cast(
        list[set[str]],
        nx.community.louvain_communities(graph, resolution=resolution),
    )
    assignments: dict[str, int] = {}
    for community_id, community_nodes in enumerate(communities):
        for node in community_nodes:
            assignments[node] = community_id
    return assignments


def network_summary(graph: GraphLike) -> dict[str, object]:
    """Generate a compact summary of graph-level properties.

    Args:
        graph: Input graph (directed or undirected).

    Returns:
        Dictionary with node and edge counts, density, average clustering,
        component count, and directedness.
    """
    is_directed = graph.is_directed()
    if graph.is_directed():
        directed_graph = cast("nx.DiGraph[str]", graph)
        connected_components = nx.number_weakly_connected_components(directed_graph)
    else:
        connected_components = nx.number_connected_components(graph)

    node_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()
    if node_count <= 1:
        density = 0.0
    elif graph.is_directed():
        density = edge_count / (node_count * (node_count - 1))
    else:
        density = (2 * edge_count) / (node_count * (node_count - 1))

    return {
        "node_count": node_count,
        "edge_count": edge_count,
        "density": density,
        "avg_clustering": nx.average_clustering(graph),
        "connected_components": connected_components,
        "is_directed": is_directed,
    }
