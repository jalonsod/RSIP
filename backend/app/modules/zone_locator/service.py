from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import List

import httpx

from app.modules.zone_locator.schemas import ZoneLocatorQuery, ZoneMetrics

logger = logging.getLogger(__name__)


class BaseZoneAdapter(ABC):
    source_name: str

    @abstractmethod
    async def fetch(self, query: ZoneLocatorQuery) -> dict:
        """Return a partial dict of ZoneMetrics fields."""
        ...


class CensusAdapter(BaseZoneAdapter):
    """Fetches population data from US Census ACS API."""

    source_name = "census"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch(self, query: ZoneLocatorQuery) -> dict:
        logger.info("CensusAdapter.fetch called (stub) for zip=%s", query.zip_code)
        # TODO: GET https://api.census.gov/data/2022/acs/acs5?get=B01003_001E,B01003_001MA&for=zip+code+tabulation+area:{zip}&key={api_key}
        return {
            "population": None,
            "population_growth_pct": None,
        }

    async def close(self):
        await self.client.aclose()


class BLSAdapter(BaseZoneAdapter):
    """Fetches employment data from BLS Public Data API."""

    source_name = "bls"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch(self, query: ZoneLocatorQuery) -> dict:
        logger.info("BLSAdapter.fetch called (stub) for zip=%s", query.zip_code)
        # TODO: POST https://api.bls.gov/publicAPI/v2/timeseries/data/ with series ID for MSA employment
        return {
            "jobs_by_radius": None,
            "unemployment_rate_pct": None,
        }

    async def close(self):
        await self.client.aclose()


class ZillowZoneAdapter(BaseZoneAdapter):
    """Fetches rental/sale market data from Zillow via RapidAPI."""

    source_name = "zillow"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch(self, query: ZoneLocatorQuery) -> dict:
        logger.info("ZillowZoneAdapter.fetch called (stub) for zip=%s", query.zip_code)
        # TODO: GET https://zillow-com1.p.rapidapi.com/marketTrends?zipcode={zip} with X-RapidAPI-Key header
        return {
            "rental_availability_count": None,
            "avg_rental_price": None,
            "days_to_rent": None,
            "sale_availability_count": None,
            "avg_sale_price": None,
            "days_to_sell": None,
        }

    async def close(self):
        await self.client.aclose()


class ZoneLocatorService:
    """Merges zone metrics from all configured adapters."""

    def __init__(self, adapters: List[BaseZoneAdapter]):
        self.adapters = adapters

    async def analyze(self, query: ZoneLocatorQuery) -> ZoneMetrics:
        merged: dict = {"zip_code": query.zip_code, "data_sources": [], "errors": []}

        for adapter in self.adapters:
            try:
                partial = await adapter.fetch(query)
                merged.update({k: v for k, v in partial.items() if v is not None})
                merged["data_sources"].append(adapter.source_name)
            except Exception as e:
                logger.exception("Error fetching from %s for zip %s", adapter.source_name, query.zip_code)
                merged["errors"].append(f"{adapter.source_name}: {e}")

        return ZoneMetrics(**merged)
