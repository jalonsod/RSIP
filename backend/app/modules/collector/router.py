from fastapi import APIRouter, HTTPException

from app.modules.collector.schemas import CollectionCriteria, CollectionRunResult

router = APIRouter()

# In-memory criteria store (replace with DB in production)
_current_criteria: CollectionCriteria | None = None


@router.get("/criteria", response_model=CollectionCriteria)
async def get_criteria():
    if _current_criteria is None:
        raise HTTPException(status_code=404, detail="No collection criteria configured")
    return _current_criteria


@router.put("/criteria", response_model=CollectionCriteria)
async def update_criteria(criteria: CollectionCriteria):
    global _current_criteria
    _current_criteria = criteria
    return _current_criteria


@router.post("/run", response_model=list[CollectionRunResult])
async def run_collection():
    if _current_criteria is None:
        raise HTTPException(status_code=400, detail="Collection criteria not configured")
    # TODO: trigger Celery task instead of inline
    from app.config import settings
    from app.modules.collector.service import (
        CollectorService,
        CrexyAdapter,
        LMSAdapter,
        RealtorAdapter,
        ZillowAdapter,
    )

    adapters = [
        ZillowAdapter(api_key=settings.zillow_api_key),
        RealtorAdapter(api_key=settings.realtor_api_key),
        LMSAdapter(api_url=settings.lms_api_url, api_key=settings.lms_api_key),
        CrexyAdapter(api_key=settings.crexy_api_key),
    ]
    service = CollectorService(adapters=adapters)
    return await service.run(_current_criteria)
