# ADR-001: RSIP Tech Stack Selection

**Date:** 2026-04-20  
**Status:** Accepted  
**Deciders:** CTO

---

## Context

The Real State Investment Portal (RSIP) requires a robust, scalable architecture to:
- Collect and scrape property data from multiple external sources (Zillow, Realtor, LMS, Crexy)
- Store and process large volumes of real estate data
- Perform investment analysis and portfolio management
- Serve a responsive web UI for investors

Key constraints:
- Development methodology: ATDD (Acceptance Test-Driven Development)
- 3-tier architecture: Frontend + API + Database
- GitFlow branching model
- Board-reviewed PRs before merge

---

## Decision

### Backend: Python 3.12 + FastAPI

**Rationale:**
- Python excels at data scraping (BeautifulSoup, Playwright, Scrapy), numeric analysis (pandas, numpy), and ML integration
- FastAPI provides async I/O, automatic OpenAPI docs, and Pydantic v2 validation — ideal for data-heavy APIs
- Celery + Redis for background scraping jobs and scheduled collection

**Alternatives rejected:**
- Node.js/Express: weaker data science ecosystem
- Django: heavier ORM overhead, less composable for microservice-style modules

### Frontend: Next.js 14 (TypeScript)

**Rationale:**
- Server-side rendering for SEO and initial load performance
- App Router enables per-module code splitting
- React ecosystem for rich UI components (charts, maps for zone data)
- TypeScript enforces API contract consistency

**Alternatives rejected:**
- Vue.js: smaller ecosystem for financial/real-estate UI components
- Plain React SPA: loses SSR performance benefits

### Database: PostgreSQL 16

**Rationale:**
- Relational model fits property, portfolio, and financial data
- PostGIS extension for geospatial zone queries
- Full-text search for property filtering
- Strong ACID guarantees for financial calculations

**Alternatives rejected:**
- MongoDB: schema flexibility not needed; financial integrity requires ACID
- MySQL: PostGIS support inferior; weaker window functions

### Task Queue: Celery + Redis

**Rationale:**
- Property collection from external sources is async by nature
- Celery supports cron-based scheduled scraping
- Redis doubles as API cache layer for expensive zone analysis queries

### Testing Framework (ATDD)

**Backend:** pytest + pytest-bdd (Gherkin `.feature` files)
- Acceptance criteria written as Gherkin scenarios
- Steps implemented in pytest-bdd step definitions

**Frontend:** Playwright (E2E acceptance tests) + Jest (unit/component)

### Containerization & CI/CD

- **Docker + Docker Compose** for local development and staging
- **GitHub Actions** for CI (lint, test, coverage) and CD (build + deploy)

---

## Consequences

- All modules share a Python backend codebase under `backend/app/modules/`
- Each module has its own Gherkin feature file in `backend/tests/features/`
- Frontend pages map to modules under `frontend/app/(modules)/`
- Database migrations managed with Alembic
- API versioned under `/api/v1/`

---

## Module Branch Strategy (GitFlow)

| Module | Branch |
|---|---|
| Collector | `feature/collector` |
| Zone Locator | `feature/zone-locator` |
| Property Analysis | `feature/property-analysis` |
| Portfolio Management | `feature/portfolio-management` |

All feature branches cut from `develop`. PRs merge back to `develop` after board review. `develop` merges to `main` on release.
