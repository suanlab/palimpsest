from __future__ import annotations

from unittest.mock import MagicMock, patch

from palimpsest.data.openalex import OpenAlexClient


def test_client_initialization() -> None:
    with patch("palimpsest.data.openalex.pyalex.config") as mock_config:
        OpenAlexClient(email="research@example.org", api_key="test-key")
        assert mock_config.email == "research@example.org"
        assert mock_config.api_key == "test-key"


def test_get_works_empty_result() -> None:
    with patch("palimpsest.data.openalex.pyalex.Works") as mock_works:
        works_instance = MagicMock()
        filtered_instance = MagicMock()
        filtered_instance.paginate.return_value = iter([])
        works_instance.filter.return_value = filtered_instance
        mock_works.return_value = works_instance

        client = OpenAlexClient()
        result = client.get_works(publication_year=2024)

        assert result == []
        works_instance.filter.assert_called_once_with(publication_year=2024)
