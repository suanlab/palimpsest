from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded

from palimpsest.api.dependencies import (
    check_neo4j_connectivity,
    create_neo4j_driver,
    get_neo4j_driver,
    limiter,
)
from palimpsest.api.routes.export import router as export_router
from palimpsest.api.routes.graph import router as graph_router
from palimpsest.api.routes.search import router as search_router
from palimpsest.utils.config import settings

FRONTEND_DIST = Path(__file__).resolve().parents[3] / "frontend" / "dist"
STATIC_PREFIXES = ("/assets/", "/favicon")

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage startup and shutdown resources for API lifecycle.

    Args:
        app: FastAPI application.

    Yields:
        None.
    """

    driver = create_neo4j_driver()
    app.state.neo4j_driver = driver
    try:
        yield
    finally:
        driver.close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application.
    """

    app = FastAPI(
        title="SuanAI SciGraph API",
        description="REST API for bibliographic graph exploration.",
        version="0.1.0",
        lifespan=lifespan,
    )

    origins = [o.strip() for o in settings.cors_origins.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["X-API-Key", "Content-Type", "Accept"],
        expose_headers=["Content-Disposition"],
        max_age=3600,
    )

    app.state.limiter = limiter

    @app.exception_handler(RateLimitExceeded)
    async def _rate_limit_handler(
        request: Request,
        exc: RateLimitExceeded,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={"detail": f"Rate limit exceeded: {exc.detail}"},
        )

    _ = _rate_limit_handler

    @app.middleware("http")
    async def auth_and_timing(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Enforce API key auth on /api routes and log request timing.

        Args:
            request: Incoming request.
            call_next: Next ASGI middleware/application callable.

        Returns:
            HTTP response from downstream stack.
        """
        path = request.url.path

        if (
            settings.api_key
            and path.startswith("/api")
            and path != "/api/health"
            and not any(path.startswith(p) for p in STATIC_PREFIXES)
        ):
            key = request.headers.get("X-API-Key", "")
            if key != settings.api_key:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or missing API key"},
                )

        started = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - started) * 1000.0

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": path,
                "status_code": response.status_code,
                "elapsed_ms": round(elapsed_ms, 2),
            },
        )
        return response

    _ = auth_and_timing

    @app.get("/api/health")
    def health(request: Request) -> dict[str, str]:
        """Return API and Neo4j health status.

        Args:
            request: FastAPI request object.

        Returns:
            Status payload with Neo4j connectivity.
        """

        driver = get_neo4j_driver(request)
        neo4j_status = "connected" if check_neo4j_connectivity(driver) else "error"
        return {"status": "ok", "neo4j": neo4j_status}

    _ = health

    app.include_router(graph_router, prefix="/api")
    app.include_router(search_router, prefix="/api")
    app.include_router(export_router, prefix="/api")

    if FRONTEND_DIST.is_dir():
        app.mount(
            "/assets",
            StaticFiles(directory=FRONTEND_DIST / "assets"),
            name="static-assets",
        )

        @app.get("/{path:path}")
        async def spa_fallback(path: str) -> FileResponse:
            file_path = FRONTEND_DIST / path
            if file_path.is_file():
                return FileResponse(file_path)
            return FileResponse(FRONTEND_DIST / "index.html")

        _ = spa_fallback

    return app


app = create_app()
