from __future__ import annotations

from typing import Any

from palimpsest.analysis.ai_penetration import AIPenetrationAnalyzer


class DummyOpenAlexClient:
    def get_works(self, **filters: Any) -> list[dict[str, Any]]:
        _ = filters
        return []


def test_classify_work_as_ai_by_topic() -> None:
    analyzer = AIPenetrationAnalyzer(DummyOpenAlexClient())
    work = {
        "title": "An empirical study",
        "primary_topic": {
            "subfield": {"id": "https://openalex.org/subfields/9999"},
        },
        "topics": [{"id": "https://openalex.org/topics/T12072"}],
    }

    assert analyzer.classify_work_as_ai(work) is True


def test_classify_work_as_ai_by_keyword() -> None:
    analyzer = AIPenetrationAnalyzer(DummyOpenAlexClient())
    work = {
        "title": "A deep learning approach for microscopy",
        "primary_topic": {
            "subfield": {"id": "https://openalex.org/subfields/9999"},
        },
        "topics": [{"id": "https://openalex.org/topics/T99999"}],
    }

    assert analyzer.classify_work_as_ai(work) is True


def test_classify_work_as_non_ai() -> None:
    analyzer = AIPenetrationAnalyzer(DummyOpenAlexClient())
    work = {
        "title": "Ecological dynamics in wetlands",
        "primary_topic": {
            "subfield": {"id": "https://openalex.org/subfields/1108"},
        },
        "topics": [{"id": "https://openalex.org/topics/T55555"}],
    }

    assert analyzer.classify_work_as_ai(work) is False
