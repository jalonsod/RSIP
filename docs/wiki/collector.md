# Collector Module

## Purpose

Continuously collect new property listings matching defined investment criteria from external sources.

## Data Sources

| Source | Type | Status |
|---|---|---|
| Zillow | Web API / Scraper | Planned |
| Realtor.com | Web API / Scraper | Planned |
| LMS | Internal API | Planned |
| Crexy | Web API / Scraper | Planned |

## Collection Criteria

Properties must match configurable filters:
- Price range
- Property type (single-family, multi-family, commercial)
- Location (ZIP code, city, state)
- Square footage range
- Year built range

## Architecture

```
Celery Beat (scheduler)
    └── CollectorTask
          ├── ZillowAdapter
          ├── RealtorAdapter
          ├── LMSAdapter
          └── CrexyAdapter
                └── → PostgreSQL (properties table)
                └── → Redis (dedup cache)
```

## ATDD Scenarios

Feature file: `backend/tests/features/collector.feature`

Key scenarios:
- Collect properties from Zillow matching criteria
- Deduplicate properties already in database
- Handle source unavailability gracefully
- Trigger zone locator for new properties

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/collector/properties` | List collected properties |
| POST | `/api/v1/collector/run` | Trigger manual collection run |
| GET | `/api/v1/collector/criteria` | Get current collection criteria |
| PUT | `/api/v1/collector/criteria` | Update collection criteria |

## Branch

`feature/collector` — cut from `develop`
