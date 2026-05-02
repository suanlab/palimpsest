from __future__ import annotations

import math

import pytest

from palimpsest.bibliometrics.indicators import (
    disruption_index,
    g_index,
    h_index,
    i10_index,
)


def test_h_index_basic() -> None:
    assert h_index([10, 8, 5, 4, 3]) == 4


def test_h_index_empty() -> None:
    assert h_index([]) == 0


def test_h_index_single() -> None:
    assert h_index([100]) == 1


def test_i10_index() -> None:
    assert i10_index([15, 12, 10, 8, 3]) == 3


def test_g_index() -> None:
    assert g_index([25, 8, 5, 3, 3]) == 5


def test_disruption_index_pure_disruptive() -> None:
    reference_map = {
        "focal": {"R1", "R2"},
        "C1": {"X1", "X2"},
        "C2": {"X3"},
        "C3": set(),
    }

    def get_references_fn(paper_id: str) -> set[str]:
        return reference_map.get(paper_id, set())

    score = disruption_index("focal", ["C1", "C2", "C3"], get_references_fn)
    assert score == pytest.approx(1.0)


def test_disruption_index_pure_consolidating() -> None:
    reference_map = {
        "focal": {"R1", "R2"},
        "C1": {"R1", "Y1"},
        "C2": {"R2", "Y2"},
        "C3": {"R1", "R2"},
    }

    def get_references_fn(paper_id: str) -> set[str]:
        return reference_map.get(paper_id, set())

    score = disruption_index("focal", ["C1", "C2", "C3"], get_references_fn)
    assert score == pytest.approx(-1.0)


def test_disruption_index_no_citations() -> None:
    def get_references_fn(_: str) -> set[str]:
        return set()

    score = disruption_index("focal", [], get_references_fn)
    assert math.isnan(score)
