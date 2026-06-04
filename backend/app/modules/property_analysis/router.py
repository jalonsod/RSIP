from fastapi import APIRouter, HTTPException

from app.modules.property_analysis.schemas import PropertyAnalysis, PropertyAnalysisQuery

router = APIRouter()

# In-memory cache (replace with Redis in production)
_analysis_cache: dict[str, PropertyAnalysis] = {}


@router.post("/analyze", response_model=PropertyAnalysis)
async def analyze_property(query: PropertyAnalysisQuery):
    from app.config import settings
    from app.modules.property_analysis.service import (
        ComparablesAdapter,
        PropertyAnalysisService,
        ZillowPropertyAdapter,
        ZillowRentEstimateAdapter,
    )

    adapters = [
        ZillowPropertyAdapter(api_key=settings.zillow_api_key),
        ZillowRentEstimateAdapter(api_key=settings.zillow_api_key),
        ComparablesAdapter(api_key=settings.zillow_api_key),
    ]
    service = PropertyAnalysisService(adapters=adapters)
    analysis = await service.analyze(query)
    _analysis_cache[query.zpid] = analysis
    return analysis


@router.get("/analysis/{zpid}", response_model=PropertyAnalysis)
async def get_analysis(zpid: str):
    if zpid not in _analysis_cache:
        raise HTTPException(status_code=404, detail=f"No analysis found for zpid {zpid}")
    return _analysis_cache[zpid]
