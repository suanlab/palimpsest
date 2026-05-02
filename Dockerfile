# SciGraph FastAPI backend — containerised for GHCR deployment
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

# System deps for scientific Python wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copy project manifest first for better layer caching
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# Install dependencies into system site-packages (no venv in container)
RUN uv sync --frozen --no-dev --no-editable

# Copy runtime scripts
COPY scripts/run_api.py scripts/

# Runtime config defaults
ENV RESEARCH_API_HOST=0.0.0.0 \
    RESEARCH_API_PORT=8300 \
    RESEARCH_NEO4J_URI=bolt://neo4j:7687 \
    RESEARCH_NEO4J_USER=neo4j

EXPOSE 8300

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8300/api/health || exit 1

# Ensure Neo4j indexes exist on startup (idempotent — IF NOT EXISTS), then run API
COPY scripts/ensure_neo4j_indexes.py scripts/
CMD ["sh", "-c", "uv run python scripts/ensure_neo4j_indexes.py || true; exec uv run python scripts/run_api.py --host 0.0.0.0 --port 8300"]
