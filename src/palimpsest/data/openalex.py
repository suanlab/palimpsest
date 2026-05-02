from __future__ import annotations

import importlib
import logging
from itertools import chain
from types import SimpleNamespace
from typing import Any, NoReturn

from palimpsest.utils.cache import ResponseCache
from palimpsest.utils.config import settings
from palimpsest.utils.exceptions import APIError, RateLimitError

logger = logging.getLogger(__name__)

_pyalex_module = importlib.import_module("pyalex")
pyalex = SimpleNamespace(
    config=SimpleNamespace(
        email=getattr(_pyalex_module.config, "email", None),
        api_key=getattr(_pyalex_module.config, "api_key", None),
    ),
    Works=_pyalex_module.Works,
    Authors=_pyalex_module.Authors,
    Institutions=_pyalex_module.Institutions,
    Topics=_pyalex_module.Topics,
)
_OPENALEX_ENTITIES: tuple[Any, ...] = (
    pyalex.Authors,
    pyalex.Institutions,
    pyalex.Topics,
)


class OpenAlexClient:
    """OpenAlex API client wrapper based on `pyalex`.

    Args:
        email: Contact email used for OpenAlex polite pool requests.
        api_key: Optional OpenAlex API key.
    """

    def __init__(self, email: str | None = None, api_key: str | None = None) -> None:
        """Initialize OpenAlex client.

        Args:
            email: Contact email used for OpenAlex polite pool requests.
            api_key: Optional OpenAlex API key.
        """

        self.email = email or settings.openalex_email
        self.api_key = api_key or settings.openalex_api_key
        self.cache = ResponseCache()

        if self.email:
            pyalex.config.email = self.email
            _pyalex_module.config.email = self.email
        if self.api_key:
            pyalex.config.api_key = self.api_key
            _pyalex_module.config.api_key = self.api_key

    def get_works(
        self,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        per_page: int = 200,
        max_results: int | None = None,
        **legacy_filters: Any,
    ) -> list[dict[str, Any]]:
        """Fetch works with cursor pagination.

        Args:
            filters: OpenAlex filter key-value pairs.
            search: Full-text search query.
            per_page: Number of records per page.
            max_results: Maximum total records to return.
            **legacy_filters: Additional filter arguments for compatibility.

        Returns:
            List of OpenAlex work records.

        Raises:
            APIError: If the OpenAlex request fails.
            RateLimitError: If OpenAlex rate limiting occurs.
        """

        try:
            query = pyalex.Works()
            combined_filters = dict(filters or {})
            combined_filters.update(legacy_filters)
            if combined_filters:
                query = query.filter(**combined_filters)
            if search:
                query = query.search(search)

            if max_results is None:
                pages = query.paginate(per_page=per_page)
            else:
                pages = query.paginate(per_page=per_page, n_max=max_results)
            return list(chain.from_iterable(pages))
        except Exception as exc:
            self._raise_openalex_error(exc)

    def get_work(self, work_id: str) -> dict[str, Any]:
        """Fetch a single work by OpenAlex ID or DOI.

        Args:
            work_id: OpenAlex ID or DOI.

        Returns:
            OpenAlex work record.

        Raises:
            APIError: If the OpenAlex request fails.
            RateLimitError: If OpenAlex rate limiting occurs.
        """

        cache_key = f"openalex:work:{work_id}"
        cached_work = self.cache.get(cache_key)
        if isinstance(cached_work, dict):
            return cached_work

        try:
            result = pyalex.Works()[work_id]
        except Exception as exc:
            self._raise_openalex_error(exc)

        work = result[0] if isinstance(result, tuple) and result else result

        if not isinstance(work, dict):
            raise APIError(
                "Unexpected OpenAlex work response format",
                details={"work_id": work_id},
            )

        self.cache.set(cache_key, work)
        return work

    def get_authors(
        self,
        filters: dict[str, Any] | None = None,
        max_results: int | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch authors with cursor pagination.

        Args:
            filters: OpenAlex filter key-value pairs for authors.
            max_results: Maximum total records to return.

        Returns:
            List of OpenAlex author records.

        Raises:
            APIError: If the OpenAlex request fails.
            RateLimitError: If OpenAlex rate limiting occurs.
        """

        try:
            query = pyalex.Authors()
            if filters:
                query = query.filter(**filters)

            if max_results is None:
                pages = query.paginate(per_page=200)
            else:
                pages = query.paginate(per_page=200, n_max=max_results)
            return list(chain.from_iterable(pages))
        except Exception as exc:
            self._raise_openalex_error(exc)

    def get_cited_by(
        self,
        work_id: str,
        max_results: int | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch works that cite the target work.

        Args:
            work_id: OpenAlex ID or DOI for the target work.
            max_results: Maximum total records to return.

        Returns:
            List of citing works.

        Raises:
            APIError: If the OpenAlex request fails.
            RateLimitError: If OpenAlex rate limiting occurs.
        """

        try:
            query = pyalex.Works().filter(cites=work_id)
            if max_results is None:
                pages = query.paginate(per_page=200)
            else:
                pages = query.paginate(per_page=200, n_max=max_results)
            return list(chain.from_iterable(pages))
        except Exception as exc:
            self._raise_openalex_error(exc)

    def get_references(self, work_id: str) -> list[dict[str, Any]]:
        """Fetch works referenced by the target work.

        Args:
            work_id: OpenAlex ID or DOI for the target work.

        Returns:
            List of referenced work records.

        Raises:
            APIError: If loading the target work fails.
            RateLimitError: If OpenAlex rate limiting occurs.
        """

        work = self.get_work(work_id)
        referenced_works = work.get("referenced_works")
        if not isinstance(referenced_works, list):
            return []

        references: list[dict[str, Any]] = []
        for referenced_id in referenced_works:
            if not isinstance(referenced_id, str) or not referenced_id:
                continue
            try:
                references.append(self.get_work(referenced_id))
            except APIError:
                logger.warning(
                    "Failed to fetch referenced work",
                    extra={"work_id": work_id, "referenced_id": referenced_id},
                )
        return references

    def _raise_openalex_error(self, exc: Exception) -> NoReturn:
        """Normalize pyalex exceptions to project-specific exceptions.

        Args:
            exc: Exception raised by pyalex.

        Raises:
            APIError: For non-rate-limit API failures.
            RateLimitError: For rate-limit failures.
        """

        message = str(exc)
        message_lower = message.lower()
        if "429" in message or "rate limit" in message_lower:
            raise RateLimitError(
                "OpenAlex rate limit exceeded",
                details={"error": message},
            ) from exc

        raise APIError(
            "OpenAlex request failed",
            details={"error": message},
        ) from exc
