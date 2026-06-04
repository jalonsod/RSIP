from fastapi import APIRouter, HTTPException

from app.modules.zone_locator.schemas import ZoneLocatorQuery, ZoneMetrics

router = APIRouter()

# In-memory cache (replace with Redis in production)
_metrics_cache: dict[str, ZoneMetrics] = {}


@router.post("/analyze", response_model=ZoneMetrics)
async def analyze_zone(query: ZoneLocatorQuery):
    from app.config import settings
    from app.modules.zone_locator.service import (
        BLSAdapter,
        CensusAdapter,
        ZillowZoneAdapter,
        ZoneLocatorService,
    )

    adapters = [
        CensusAdapter(api_key=settings.census_api_key),
        BLSAdapter(api_key=settings.bls_api_key),
        ZillowZoneAdapter(api_key=settings.zillow_api_key),
    ]
    service = ZoneLocatorService(adapters=adapters)
    metrics = await service.analyze(query)
    _metrics_cache[query.zip_code] = metrics
    return metrics


@router.get("/metrics/{zip_code}", response_model=ZoneMetrics)
async def get_metrics(zip_code: str):
    if zip_code not in _metrics_cache:
        raise HTTPException(status_code=404, detail=f"No metrics found for zip code {zip_code}")
    return _metrics_cache[zip_code]
