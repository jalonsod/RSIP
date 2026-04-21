# RSIP — Real State Investment Portal Wiki

Welcome to the RSIP development wiki. This portal helps investors collect, analyze, and manage real estate investments.

## Modules

| Module | Status | Branch | Docs |
|---|---|---|---|
| [Collector](./collector.md) | In Progress | `feature/collector` | [→](./collector.md) |
| [Zone Locator](./zone-locator.md) | Planned | `feature/zone-locator` | [→](./zone-locator.md) |
| [Property Analysis](./property-analysis.md) | Planned | `feature/property-analysis` | [→](./property-analysis.md) |
| [Portfolio Management](./portfolio-management.md) | Planned | `feature/portfolio-management` | [→](./portfolio-management.md) |

## Architecture

- **ADR-001**: [Tech Stack Selection](../adr/001-tech-stack.md)
- 3-tier: Next.js Frontend → FastAPI Backend → PostgreSQL Database
- Background jobs via Celery + Redis
- Full ATDD with pytest-bdd (Gherkin) + Playwright

## Development Setup

See [README.md](../../README.md) for local dev setup instructions.

## GitFlow

```
main          ←── production releases
  └── develop ←── integration branch
        ├── feature/collector
        ├── feature/zone-locator
        ├── feature/property-analysis
        └── feature/portfolio-management
```

## API Reference

- Local: `http://localhost:8000/docs` (Swagger UI)
- ReDoc: `http://localhost:8000/redoc`

## Test Coverage

Coverage reports generated per module on every CI run:
- Backend: `htmlcov/` (pytest + coverage.py)
- Frontend: `coverage/` (Jest)
