import logging
from abc import ABC, abstractmethod

import httpx

from app.modules.property_analysis.schemas import PropertyAnalysis, PropertyAnalysisQuery

logger = logging.getLogger(__name__)


class BasePropertyAdapter(ABC):
    source_name: str

    @abstractmethod
    async def fetch(self, query: PropertyAnalysisQuery) -> dict:
        """Return a partial dict of PropertyAnalysis fields."""
        ...


class ZillowPropertyAdapter(BasePropertyAdapter):
    """Fetches property details (price, sqft, beds, baths) from Zillow."""

    source_name = "zillow_property"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch(self, query: PropertyAnalysisQuery) -> dict:
        logger.info("ZillowPropertyAdapter.fetch called (stub) for zpid=%s", query.zpid)
        # TODO: GET https://zillow-com1.p.rapidapi.com/property?zpid={zpid} with X-RapidAPI-Key header
        return {
            "price": None,
            "sqft": None,
            "beds": None,
            "baths": None,
        }

    async def close(self):
        await self.client.aclose()


class ZillowRentEstimateAdapter(BasePropertyAdapter):
    """Fetches expected rent from Zillow Rent Zestimate."""

    source_name = "zillow_rent_estimate"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch(self, query: PropertyAnalysisQuery) -> dict:
        logger.info("ZillowRentEstimateAdapter.fetch called (stub) for zpid=%s", query.zpid)
        # TODO: GET https://zillow-com1.p.rapidapi.com/rentEstimate?zpid={zpid} with X-RapidAPI-Key header
        return {
            "expected_rent": None,
        }

    async def close(self):
        await self.client.aclose()


class ComparablesAdapter(BasePropertyAdapter):
    """Fetches comparable sales (comps) from Zillow."""

    source_name = "comparables"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch(self, query: PropertyAnalysisQuery) -> dict:
        logger.info("ComparablesAdapter.fetch called (stub) for zpid=%s", query.zpid)
        # TODO: GET https://zillow-com1.p.rapidapi.com/propertyComps?zpid={zpid} with X-RapidAPI-Key header
        return {
            "neighbor_count": None,
            "avg_neighbor_price": None,
        }

    async def close(self):
        await self.client.aclose()


class PropertyAnalysisService:
    """Aggregates property investment data from all configured adapters."""

    def __init__(self, adapters: list[BasePropertyAdapter]):
        self.adapters = adapters

    async def analyze(self, query: PropertyAnalysisQuery) -> PropertyAnalysis:
        merged: dict = {"zpid": query.zpid, "data_sources": [], "errors": []}

        for adapter in self.adapters:
            try:
                partial = await adapter.fetch(query)
                merged.update({k: v for k, v in partial.items() if v is not None})
                merged["data_sources"].append(adapter.source_name)
            except Exception as e:
                logger.exception("Error fetching from %s for zpid %s", adapter.source_name, query.zpid)
                merged["errors"].append(f"{adapter.source_name}: {e}")

        # Derived metrics
        price = merged.get("price")
        sqft = merged.get("sqft")
        if price is not None and sqft is not None and sqft > 0:
            merged["price_per_sqft"] = round(price / sqft, 2)

        avg_neighbor = merged.get("avg_neighbor_price")
        if price is not None and avg_neighbor is not None:
            merged["price_vs_neighbors_delta"] = round(price - avg_neighbor, 2)

        return PropertyAnalysis(**merged)
