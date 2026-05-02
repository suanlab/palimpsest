from __future__ import annotations

import math
from collections.abc import Callable, Iterable


def h_index(citations: list[int]) -> int:
    """Compute Hirsch h-index.

    Args:
        citations: Citation counts per paper.

    Returns:
        Largest h such that at least h papers have >= h citations.
    """
    sorted_citations = sorted(
        (count for count in citations if count >= 0), reverse=True
    )
    h = 0
    for index, citation_count in enumerate(sorted_citations, start=1):
        if citation_count < index:
            break
        h = index
    return h


def i10_index(citations: list[int]) -> int:
    """Compute i10-index.

    Args:
        citations: Citation counts per paper.

    Returns:
        Number of papers with at least 10 citations.
    """
    return sum(1 for citation_count in citations if citation_count >= 10)


def g_index(citations: list[int]) -> int:
    """Compute Egghe g-index.

    Args:
        citations: Citation counts per paper.

    Returns:
        Largest g such that top g papers have at least g^2 total citations.
    """
    sorted_citations = sorted(
        (count for count in citations if count >= 0), reverse=True
    )
    cumulative = 0
    g = 0
    for index, citation_count in enumerate(sorted_citations, start=1):
        cumulative += citation_count
        if cumulative >= index * index:
            g = index
    return g


def disruption_index(
    focal_paper_id: str,
    citing_paper_ids: Iterable[str],
    get_references_fn: Callable[[str], set[str]],
) -> float:
    """Compute a simplified disruption index from citing behavior.

    Args:
        focal_paper_id: Identifier for the focal paper.
        citing_paper_ids: IDs of papers citing the focal paper.
        get_references_fn: Function returning references for a paper ID.

    Returns:
        Disruption score in [-1, 1], or NaN if no citing papers are provided.
    """
    citing_ids = list(citing_paper_ids)
    if not citing_ids:
        return math.nan

    focal_references = get_references_fn(focal_paper_id)
    disruptive_count = 0
    consolidating_count = 0

    for citing_id in citing_ids:
        citing_references = get_references_fn(citing_id)
        if focal_references & citing_references:
            consolidating_count += 1
        else:
            disruptive_count += 1

    total = disruptive_count + consolidating_count
    if total == 0:
        return math.nan
    return (disruptive_count - consolidating_count) / total
