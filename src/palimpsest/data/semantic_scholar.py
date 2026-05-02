from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from palimpsest.utils.config import settings
from palimpsest.utils.exceptions import APIError, DataValidationError, RateLimitError

logger = logging.getLogger(__name__)


class SemanticScholarClient:
    """Client for Semantic Scholar Graph API."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize the Semantic Scholar API client.

        Args:
            api_key: Optional API key. Falls back to settings value.
        """

        self.api_key = api_key or settings.semantic_scholar_api_key
        headers: dict[str, str] = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers=headers,
            timeout=30.0,
        )

    def get_paper(
        self,
        paper_id: str,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Fetch a single paper from Semantic Scholar.

        Args:
            paper_id: Semantic Scholar paper ID, DOI, PMID, or ArXiv ID.
            fields: Optional list of fields to request.

        Returns:
            Paper payload as a dictionary.

        Raises:
            APIError: If the API request fails.
            DataValidationError: If the API payload is invalid.
            RateLimitError: If API rate limit is exceeded.
        """

        params = {"fields": ",".join(fields)} if fields else None
        payload = self._request("GET", f"/paper/{paper_id}", params=params)
        if not isinstance(payload, dict):
            raise DataValidationError(
                "Unexpected Semantic Scholar paper payload",
                details={"paper_id": paper_id},
            )
        return payload

    def get_citations_with_context(self, paper_id: str) -> list[dict[str, Any]]:
        """Fetch citations with intents and context strings.

        Args:
            paper_id: Semantic Scholar paper ID, DOI, PMID, or ArXiv ID.

        Returns:
            List of citation dictionaries with `intents` and `contexts` fields.

        Raises:
            APIError: If the API request fails.
            DataValidationError: If the API payload is invalid.
            RateLimitError: If API rate limit is exceeded.
        """

        paper = self.get_paper(
            paper_id,
            fields=["citations.contexts", "citations.intents"],
        )
        citations = paper.get("citations")
        if not isinstance(citations, list):
            return []

        normalized: list[dict[str, Any]] = []
        for citation in citations:
            if not isinstance(citation, dict):
                continue
            citation_copy = dict(citation)

            intents = citation_copy.get("intents")
            citation_copy["intents"] = intents if isinstance(intents, list) else []

            contexts_value = citation_copy.get("contexts")
            if not isinstance(contexts_value, list):
                citation_context = citation_copy.get("citationContext")
                if isinstance(citation_context, str) and citation_context:
                    contexts_value = [citation_context]
                else:
                    contexts_value = []
            citation_copy["contexts"] = contexts_value

            normalized.append(citation_copy)

        return normalized

    def batch_get_papers(
        self,
        paper_ids: list[str],
        fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch papers in batches using Semantic Scholar batch endpoint.

        Args:
            paper_ids: List of paper IDs to retrieve.
            fields: Optional list of fields to request.

        Returns:
            List of paper payload dictionaries.

        Raises:
            APIError: If the API request fails.
            DataValidationError: If the API payload is invalid.
            RateLimitError: If API rate limit is exceeded.
        """

        if not paper_ids:
            return []

        all_papers: list[dict[str, Any]] = []
        params = {"fields": ",".join(fields)} if fields else None

        for start_index in range(0, len(paper_ids), 500):
            batch_ids = paper_ids[start_index : start_index + 500]
            payload = self._request(
                "POST",
                "/paper/batch",
                params=params,
                json={"ids": batch_ids},
            )
            if not isinstance(payload, list):
                raise DataValidationError(
                    "Unexpected Semantic Scholar batch payload",
                    details={"batch_start": start_index},
                )

            for item in payload:
                if isinstance(item, dict):
                    all_papers.append(item)

        return all_papers

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        """Perform HTTP requests with retry and backoff.

        Args:
            method: HTTP method.
            path: API path.
            params: Optional query parameters.
            json: Optional JSON body.

        Returns:
            Parsed JSON payload.

        Raises:
            APIError: If retries are exhausted or request fails.
            RateLimitError: If rate limit retries are exhausted.
        """

        delay_seconds = 1.0
        max_attempts = 5
        last_error: Exception | None = None

        for attempt in range(max_attempts):
            try:
                response = self._client.request(
                    method,
                    path,
                    params=params,
                    json=json,
                )
            except httpx.RequestError as exc:
                last_error = exc
                if attempt == max_attempts - 1:
                    request_url = str(exc.request.url) if exc.request else path
                    raise APIError(
                        "Semantic Scholar request failed",
                        url=request_url,
                        details={"error": str(exc)},
                    ) from exc
                time.sleep(delay_seconds)
                delay_seconds *= 2
                continue

            if response.status_code == 429:
                last_error = RateLimitError(
                    "Semantic Scholar rate limit exceeded",
                    status_code=429,
                    url=str(response.request.url),
                )
                if attempt == max_attempts - 1:
                    raise last_error

                retry_after = response.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    delay_seconds = max(delay_seconds, float(retry_after))
                time.sleep(delay_seconds)
                delay_seconds *= 2
                continue

            if response.is_error:
                raise APIError(
                    "Semantic Scholar API error",
                    status_code=response.status_code,
                    url=str(response.request.url),
                    details={"body": response.text},
                )

            try:
                return response.json()
            except ValueError as exc:
                raise APIError(
                    "Semantic Scholar returned invalid JSON",
                    status_code=response.status_code,
                    url=str(response.request.url),
                ) from exc

        raise APIError(
            "Semantic Scholar request exhausted retries",
            details={"error": str(last_error) if last_error else "unknown"},
        )
