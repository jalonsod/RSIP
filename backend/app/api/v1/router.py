from fastapi import APIRouter

from app.modules.collector.router import router as collector_router
from app.modules.zone_locator.router import router as zone_locator_router
from app.modules.property_analysis.router import router as property_analysis_router

router = APIRouter()

router.include_router(collector_router, prefix="/collector", tags=["Collector"])
router.include_router(zone_locator_router, prefix="/zone-locator", tags=["Zone Locator"])
router.include_router(property_analysis_router, prefix="/properties", tags=["Property Analysis"])

# Future modules:
# router.include_router(portfolio_router, prefix="/portfolio", tags=["Portfolio Management"])
