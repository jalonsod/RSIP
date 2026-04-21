# RSIP — Real State Investment Portal

A platform to collect, analyze, and manage real estate investments.

## Architecture

- **Frontend**: Next.js 14 (TypeScript) — `frontend/`
- **Backend API**: FastAPI (Python 3.12) — `backend/`
- **Database**: PostgreSQL 16 + PostGIS
- **Task Queue**: Celery + Redis
- **Methodology**: ATDD with pytest-bdd (Gherkin) + Playwright

See [ADR-001](docs/adr/001-tech-stack.md) for full rationale.

## Modules

| Module | Branch | Status |
|---|---|---|
| Collector | `feature/collector` | In Progress |
| Zone Locator | `feature/zone-locator` | Planned |
| Property Analysis | `feature/property-analysis` | Planned |
| Portfolio Management | `feature/portfolio-management` | Planned |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Node.js 22+

### Run locally

```bash
# Start infrastructure
cd infra/docker && docker compose up -d postgres redis

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs

# Frontend
cd frontend
npm install
npm run dev
# UI: http://localhost:3000
```

### Run tests

```bash
# Backend (ATDD + unit, with coverage)
cd backend && pytest

# Frontend unit tests
cd frontend && npm test

# Frontend E2E
cd frontend && npm run test:e2e
```

## GitFlow

```
main         ← production
  └── develop
        ├── feature/collector
        ├── feature/zone-locator
        ├── feature/property-analysis
        └── feature/portfolio-management
```

PRs must be reviewed and approved by the board before merging.

## Wiki

See [docs/wiki/index.md](docs/wiki/index.md) for full documentation.
