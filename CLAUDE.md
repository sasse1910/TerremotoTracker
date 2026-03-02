# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Full stack (Docker)
```bash
docker-compose up --build          # start all services
docker-compose down                # stop all services
```

### Backend (local dev — requires PostgreSQL + Redis running)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Apply migrations
alembic upgrade head

# Create a new migration (always write manually — do NOT use --autogenerate)
alembic revision -m "describe_change"

# Run server
uvicorn app.main:app --reload
```

### Backend — Lint & Test
```bash
cd backend

# Lint + format check
ruff check app tests
ruff format --check app tests

# Auto-fix lint issues
ruff check --fix app tests
ruff format app tests

# Run all tests with coverage
pytest --cov=app --cov-report=term-missing

# Run a single test file
pytest tests/test_health.py -v

# Run only unit tests (no I/O)
pytest -m unit

# Run only integration tests (requires real DB + Redis)
pytest -m integration
```

### Frontend (local dev)
```bash
cd frontend
npm install
npm run dev          # starts Vite dev server on :5173
npm run build        # tsc + vite build
npm run type-check   # tsc --noEmit only
npm run lint         # eslint, zero warnings policy
```

## Architecture

### Request flow
Browser → FastAPI `/api/v1` → `CacheService` (Redis, TTL 60s) → PostgreSQL → USGS/GVP external APIs.
On cache miss, the service fetches from the external API, upserts into PostgreSQL, then caches the result.
WebSocket (`/ws/live`) receives events from a background USGS poller (every 30 s) and broadcasts to all connected clients.

### Backend structure (`backend/app/`)
| Layer | Path | Role |
|---|---|---|
| Config | `core/config.py` | `Settings` via pydantic-settings; loaded once with `lru_cache` |
| Database | `core/database.py` | Async SQLAlchemy engine; `get_db()` FastAPI dependency |
| Cache | `core/redis.py` | `CacheService` wrapper around `redis.asyncio`; `get_redis()` singleton |
| Logging | `core/logging.py` | structlog — JSON in prod, colored in dev |
| Models | `models/` | SQLAlchemy 2.0 `mapped_column` style (`Earthquake`, `Volcano`, `Alert`) |
| Schemas | `schemas/` | Pydantic v2 request/response models |
| Services | `services/` | Business logic + external API clients (httpx async) |
| Endpoints | `api/v1/endpoints/` | Thin FastAPI routers; delegate to services |
| Router | `api/v1/__init__.py` | Aggregates all routers under `/api/v1` |

### Frontend structure (`frontend/src/`)
| Path | Role |
|---|---|
| `components/` | React components (map, charts, filters, alert banner) |
| `hooks/` | Custom hooks (`useWebSocket`, etc.) |
| `services/` | Axios HTTP client + WebSocket client |
| `store/` | Zustand global state |

### Key conventions
- **Everything async**: asyncpg driver, async SQLAlchemy, httpx for outbound HTTP — never use sync I/O in endpoint handlers.
- **Migrations are hand-written**: do not use `alembic revision --autogenerate`. Write SQL explicitly for full control.
- **`alembic/env.py` imports `app.models`**: ensures all models register on `Base.metadata` before migrations run.
- **Ruff** replaces flake8 + isort + black. Config in `backend/ruff.toml`. Line length: 100. Target: Python 3.12.
- **Test fixtures** live in `backend/tests/conftest.py`. Unit tests use SQLite in-memory; the `client` fixture overrides `get_db` via `app.dependency_overrides`. Mark tests with `@pytest.mark.unit` or `@pytest.mark.integration`.
- **Cache keys**: `"earthquakes:24h"`, `"earthquakes:7d"`, `"volcanoes:all"` — earthquake TTL 60 s, volcano TTL 3600 s.
- **CI gate**: lint must pass before tests run; coverage must be ≥ 80% (`--cov-fail-under=80`).

### External APIs (no key required)
- USGS: `https://earthquake.usgs.gov/fdsnws/event/1` (query) and feed URL in `settings.USGS_FEED_URL`
- Smithsonian GVP: `https://volcano.si.edu/api`

### Service ports
| Service | Port |
|---|---|
| Frontend (Vite) | 5173 |
| API (FastAPI) | 8000 |
| PostgreSQL | 5432 |
| Redis | 6379 |
| pgAdmin | 5050 |
