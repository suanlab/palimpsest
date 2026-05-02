from __future__ import annotations

from typing import Any


class ResearchError(Exception):
    """Base exception for research toolkit errors."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the base research error.

        Args:
            message: Human-readable error message.
            details: Optional structured context for debugging.
        """

        super().__init__(message or self.__class__.__name__)
        self.message = message or self.__class__.__name__
        self.details = details or {}

    def __str__(self) -> str:
        """Render error message with optional details.

        Returns:
            String representation of the error.
        """

        if not self.details:
            return self.message
        return f"{self.message} | details={self.details}"


class APIError(ResearchError):
    """Raised when an external API call fails."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
        status_code: int | None = None,
        url: str | None = None,
    ) -> None:
        """Initialize an API error.

        Args:
            message: Human-readable error message.
            details: Optional structured context for debugging.
            status_code: HTTP status code when available.
            url: Request URL when available.
        """

        merged_details = dict(details or {})
        if status_code is not None:
            merged_details["status_code"] = status_code
        if url is not None:
            merged_details["url"] = url
        super().__init__(message=message, details=merged_details)
        self.status_code = status_code
        self.url = url


class DataValidationError(ResearchError):
    """Raised when data fails validation checks."""


class RateLimitError(APIError):
    """Raised when an API rate limit is exceeded."""
