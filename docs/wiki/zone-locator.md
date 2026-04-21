# Zone Locator Module

## Purpose

Collect and analyze demographic and market data per geographic region to support investment decisions.

## Data Points

### Population & Growth
- Current population
- Year-over-year growth rate
- 5-year trend

### Employment
- Jobs within 3, 5, 10, 20 mile radius
- Major employers
- Employment sector breakdown

### Market Availability
- Rental listings count
- Sales listings count
- Days on market (average)

### Pricing
- Average rental price (by bedroom count)
- Average sale price (by property type)
- Median price per sq ft

### Market Velocity
- Average time to rent
- Average time to sell

## Data Sources

- US Census Bureau API
- Bureau of Labor Statistics API
- Zillow Market Data API
- Realtor.com Market Trends

## Architecture

```
ZoneLocatorService
    ├── CensusAdapter
    ├── BLSAdapter
    ├── ZillowMarketAdapter
    └── → PostgreSQL (zones, zone_snapshots tables)
```

## Branch

`feature/zone-locator` — cut from `develop`
