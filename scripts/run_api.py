#!/usr/bin/env python3
"""Run the FastAPI application with uvicorn."""

from __future__ import annotations

import argparse
from typing import cast

import uvicorn

from palimpsest.utils.config import settings
from palimpsest.utils.logging import setup_logging


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for API server execution.

    Returns:
        Parsed CLI arguments.
    """

    parser = argparse.ArgumentParser(description="Run Research Graph API server.")
    _ = parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Uvicorn host address.",
    )
    _ = parser.add_argument(
        "--port",
        type=int,
        default=8300,
        help="Uvicorn port number.",
    )
    _ = parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for local development.",
    )
    _ = parser.add_argument(
        "--log-level",
        default=settings.log_level.lower(),
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Uvicorn log level.",
    )
    return parser.parse_args()


def main() -> None:
    """Run uvicorn server for the API module."""

    args = parse_args()
    host = cast(str, args.host)
    port = cast(int, args.port)
    reload_enabled = cast(bool, args.reload)
    log_level = cast(str, args.log_level)
    setup_logging(settings.log_level)
    uvicorn.run(
        "palimpsest.api.app:app",
        host=host,
        port=port,
        reload=reload_enabled,
        log_level=log_level,
    )


if __name__ == "__main__":
    main()
