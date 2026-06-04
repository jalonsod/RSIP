from fastapi import APIRouter

from app.modules.collector.router import router as collector_router
from app.modules.portfolio.router import router as portfolio_router

router = APIRouter()

router.include_router(collector_router, prefix="/collector", tags=["Collector"])
router.include_router(portfolio_router, prefix="/portfolio", tags=["Portfolio Management"])

# Future modules:
# router.include_router(zone_locator_router, prefix="/zones", tags=["Zone Locator"])
# router.include_router(property_analysis_router, prefix="/properties", tags=["Property Analysis"])
