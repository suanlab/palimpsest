from __future__ import annotations

import logging


def setup_logging(level: str = "INFO") -> None:
    """Configure the root logger for the application.

    Args:
        level: Logging level name (for example, "INFO" or "DEBUG").

    Returns:
        None.
    """

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger by name.

    Args:
        name: Logger name, usually `__name__`.

    Returns:
        Logger instance.
    """

    return logging.getLogger(name)
