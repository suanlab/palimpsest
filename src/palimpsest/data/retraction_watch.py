from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
import pandas as pd

from palimpsest.utils.config import settings
from palimpsest.utils.exceptions import APIError

if TYPE_CHECKING:
    from palimpsest.data.openalex import OpenAlexClient

logger = logging.getLogger(__name__)


class RetractionWatchLoader:
    """Loader for Retraction Watch CSV data."""

    CSV_URL = (
        "https://gitlab.com/crossref/retraction-watch-data/-/raw/main/"
        "retraction_watch.csv"
    )

    def __init__(self, cache_dir: Path | None = None) -> None:
        """Initialize the loader.

        Args:
            cache_dir: Directory for cached CSV file.
        """

        self.cache_dir = cache_dir or settings.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path = self.cache_dir / "retraction_watch.csv"
        self._data: pd.DataFrame | None = None

    def load(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load Retraction Watch data from cache or remote source.

        Args:
            force_refresh: If True, always re-download the CSV.

        Returns:
            DataFrame containing Retraction Watch records.

        Raises:
            APIError: If download or CSV parsing fails.
        """

        if self._data is not None and not force_refresh:
            return self._data

        if self.csv_path.exists() and not force_refresh:
            try:
                self._data = pd.read_csv(self.csv_path)
                return self._data
            except (OSError, pd.errors.ParserError) as exc:
                logger.warning(
                    "Failed to read cached Retraction Watch CSV",
                    extra={"path": str(self.csv_path), "error": str(exc)},
                )

        try:
            response = httpx.get(self.CSV_URL, timeout=60.0)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise APIError(
                "Retraction Watch download failed",
                status_code=exc.response.status_code,
                url=str(exc.request.url),
                details={"error": str(exc)},
            ) from exc
        except httpx.RequestError as exc:
            raise APIError(
                "Retraction Watch network request failed",
                url=str(exc.request.url) if exc.request else self.CSV_URL,
                details={"error": str(exc)},
            ) from exc

        try:
            self.csv_path.write_bytes(response.content)
            self._data = pd.read_csv(self.csv_path)
        except (OSError, pd.errors.ParserError) as exc:
            raise APIError(
                "Failed to parse Retraction Watch CSV",
                details={"path": str(self.csv_path), "error": str(exc)},
            ) from exc

        return self._data

    def get_retracted_dois(self) -> set[str]:
        """Extract unique retracted DOIs.

        Returns:
            Set of normalized DOI strings.
        """

        data = self.load()
        if "OriginalPaperDOI" not in data.columns:
            return set()

        series = data["OriginalPaperDOI"].dropna().astype(str).str.strip().str.lower()
        return {doi for doi in series if doi}

    def get_retracted_pmids(self) -> set[str]:
        """Extract unique retracted PubMed IDs.

        Returns:
            Set of PubMed ID strings.
        """

        data = self.load()
        if "OriginalPaperPubMedID" not in data.columns:
            return set()

        series = data["OriginalPaperPubMedID"].dropna().astype(str).str.strip()
        return {pmid for pmid in series if pmid}

    def map_to_openalex_ids(
        self,
        client: OpenAlexClient,
        dois: set[str] | None = None,
    ) -> dict[str, str]:
        """Map DOI strings to OpenAlex work IDs.

        Args:
            client: OpenAlex API client.
            dois: Optional DOI subset. Uses all retracted DOIs when omitted.

        Returns:
            Mapping from DOI to OpenAlex work ID.
        """

        target_dois = dois or self.get_retracted_dois()
        mapping: dict[str, str] = {}

        for doi in target_dois:
            candidates = [doi]
            if not doi.startswith("https://doi.org/"):
                candidates.append(f"https://doi.org/{doi}")

            openalex_id: str | None = None
            for candidate in candidates:
                try:
                    work = client.get_work(candidate)
                except APIError:
                    continue
                identifier = work.get("id") if isinstance(work, dict) else None
                if isinstance(identifier, str) and identifier:
                    openalex_id = identifier
                    break

            if openalex_id:
                mapping[doi] = openalex_id

        return mapping
