# Palimpsest — Science of Science Research Platform

[![CI](https://github.com/suanlab/palimpsest/actions/workflows/ci.yml/badge.svg)](https://github.com/suanlab/palimpsest/actions/workflows/ci.yml)
[![Deploy Pages](https://github.com/suanlab/palimpsest/actions/workflows/pages.yml/badge.svg)](https://github.com/suanlab/palimpsest/actions/workflows/pages.yml)
[![Docker Image](https://github.com/suanlab/palimpsest/actions/workflows/docker-image.yml/badge.svg)](https://github.com/suanlab/palimpsest/actions/workflows/docker-image.yml)

Python research toolkit + React frontend + Neo4j graph database for analyzing scholarly metadata, citation networks, collaboration patterns, retraction dynamics, and AI adoption across 479M+ papers.

**Live services:**
- Frontend (static): GitHub Pages — `https://scigraph.suanlab.com/`
- API: `https://scigraph.suanlab.com/` (FastAPI + Neo4j)
- Interactive exploration: `https://scigraph.suanlab.com/` (queries live API)

Active research outputs:
- Track 3 (PNAS): "Citation Palimpsests" — `docs/submissions/track3_pnas/`
- Track 1 (NHB): "AI Adoption in Science Is a Late-Adopter Diffusion Story" (AI adoption across fields) — `docs/submissions/track1_nhb/`
- Track 2 (note): AI-retraction correlation null result — `docs/submissions/track2_note/`

---

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) - Modern Python package manager
- Docker & Docker Compose (for Neo4j graph database)
- Neo4j (optional - can run via Docker, see below)

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd research

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your API keys (see Configuration section)

# 3. Install dependencies (creates .venv automatically)
uv sync

# 4. Install dev dependencies (for testing/linting)
uv pip install pytest mypy ruff pandas-stubs

# 5. Run tests to verify installation
uv run pytest tests/ -v
```

### Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Required for API access
RESEARCH_OPENALEX_EMAIL=your@email.com
RESEARCH_OPENALEX_API_KEY=your_key_here

# Required for Neo4j graph database
RESEARCH_NEO4J_URI=bolt://localhost:7687
RESEARCH_NEO4J_USER=neo4j
RESEARCH_NEO4J_PASSWORD=your_password
```

**Get API Keys:**
- OpenAlex: https://openalex.org/users/me (free, recommended for higher rate limits)
- Semantic Scholar: https://www.semanticscholar.org/product/api (optional)

## Development

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_data/test_openalex.py -v

# Run with coverage
uv run pytest tests/ --cov=src/research
```

### Linting & Type Checking

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check . --fix

# Type checking
uv run mypy src/

# Full check (run before committing)
uv run ruff check . --fix && uv run ruff format . && uv run mypy src/ && uv run pytest
```

### Running the API Server

```bash
# Development server with auto-reload
uv run python scripts/run_api.py --reload

# Production server
uv run python scripts/run_api.py --host 0.0.0.0 --port 8300
```

API will be available at http://localhost:8300

### Neo4j Graph Database (Optional)

For graph-based analysis and API features:

```bash
# Start Neo4j with Docker
docker-compose up -d neo4j

# Check status
docker-compose ps

# Access Neo4j Browser: http://localhost:7474
# Default login: neo4j / research2026
```

See [docs/NEO4J.md](docs/NEO4J.md) for detailed setup and data import instructions.

## Project Structure

```
research/
├── src/research/           # Main Python package
│   ├── data/              # API clients (OpenAlex, Semantic Scholar)
│   ├── networks/          # Graph construction (citation, collaboration)
│   ├── bibliometrics/     # Publication metrics (h-index, disruption)
│   ├── analysis/          # Research domain logic
│   ├── api/               # FastAPI REST server
│   ├── nlp/               # Text mining & embeddings
│   └── utils/             # Config, cache, logging
├── tests/                 # Test suite
├── scripts/               # CLI utilities & pipelines
├── notebooks/             # Jupyter notebooks for exploration
├── data/                  # Local data cache
│   ├── raw/              # Downloaded API data
│   ├── processed/        # Cleaned/analyzed data
│   └── cache/            # API response cache
└── pyproject.toml        # Project configuration
```

## Data Sources

- **OpenAlex** - Open scholarly data (works, authors, institutions)
- **Semantic Scholar** - Academic paper corpus with citation contexts
- **Retraction Watch** - Retracted papers database
- **PubMed** - Biomedical literature
- **arXiv** - Preprint repository
- **DBLP** - Computer science bibliography

## Reproducibility

This project uses:

- **uv** for deterministic dependency resolution (`uv.lock`)
- **pydantic-settings** for environment-based configuration
- **diskcache** for API response caching
- **pytest** for testing

All dependencies are pinned in `uv.lock`. To reproduce the environment:

```bash
uv sync  # Installs exact versions from lockfile
```

## Documentation

- See `AGENTS.md` for detailed development guidelines
- See `src/research/AGENTS.md` for package architecture
- See module-level `AGENTS.md` files for specific conventions

## Production Deployment

### One-command bootstrap (new server)

```bash
curl -fsSL https://raw.githubusercontent.com/suanlab/palimpsest/main/deploy/bootstrap.sh | bash
```

### Manual Docker deployment

```bash
# Pull pre-built image from GHCR and start full stack
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

# Verify
curl http://127.0.0.1:8300/api/health
```

### Production CORS configuration

When the frontend is served from GitHub Pages while the API runs on a separate origin (e.g. `scigraph.suanlab.com`), the API must explicitly list the Pages origin in `RESEARCH_CORS_ORIGINS`. The default `"*"` does **not** work because the API uses `allow_credentials=True`. Example:

```bash
RESEARCH_CORS_ORIGINS=https://scigraph.suanlab.com,http://localhost:3000
```

Multiple origins are comma-separated. Restart the API after changing.

### GitHub Actions CI/CD

Workflows in `.github/workflows/`:
- `ci.yml` — run pytest + ruff + mypy on every push/PR, build frontend artifact
- `docker-image.yml` — build and push `palimpsest-api` container image to GHCR (ghcr.io/<owner>/<repo>/palimpsest-api)
- `pages.yml` — build Vite frontend and deploy to GitHub Pages
- `deploy-api.yml` — on main-branch push, SSH to production server and restart API container

Required GitHub secrets for `deploy-api.yml`:

| Secret | Description |
|---|---|
| `DEPLOY_HOST` | Production server hostname/IP |
| `DEPLOY_USER` | SSH username (e.g., `suanlab`) |
| `DEPLOY_SSH_KEY` | Private SSH key authorised for the deploy user |
| `DEPLOY_PORT` | Optional SSH port (default 22) |
| `DEPLOY_PATH` | Absolute path to deployed repo (e.g., `/opt/scigraph`) |

Required GitHub variable (not secret):

| Variable | Description |
|---|---|
| `PUBLIC_API_BASE_URL` | Public API URL used by Pages frontend (default `https://scigraph.suanlab.com`) |

---

## License

Code: MIT. Data outputs: subject to upstream licenses (Retraction Watch, OpenAlex, Semantic Scholar).

## Citation

If you use this toolkit in your research, please cite:

```
Lee, S. (2026). Paper mills breed zombie citations: reason-stratified evidence
that industrial-scale fraud evades retraction. Manuscript under review at
Proc. Natl. Acad. Sci. U.S.A.
```

Corresponding author: Suan Lee, Semyung University, suanlee@semyung.ac.kr
