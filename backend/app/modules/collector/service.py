from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Optional

import httpx

from app.modules.collector.schemas import (
    CollectionCriteria,
    CollectionRunResult,
    DataSource,
    PropertyListing,
)

logger = logging.getLogger(__name__)


class BaseSourceAdapter(ABC):
    """Abstract base for all property source adapters."""

    source: DataSource

    @abstractmethod
    async def fetch(self, criteria: CollectionCriteria) -> list[PropertyListing]:
        """Fetch property listings matching the given criteria."""
        ...


class ZillowAdapter(BaseSourceAdapter):
    source = DataSource.zillow

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch(self, criteria: CollectionCriteria) -> list[PropertyListing]:
        # TODO: Implement Zillow RapidAPI integration
        logger.info("ZillowAdapter.fetch called (stub)")
        return []

    async def close(self):
        await self.client.aclose()


class RealtorAdapter(BaseSourceAdapter):
    source = DataSource.realtor

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch(self, criteria: CollectionCriteria) -> list[PropertyListing]:
        # TODO: Implement Realtor.com API integration
        logger.info("RealtorAdapter.fetch called (stub)")
        return []

    async def close(self):
        await self.client.aclose()


class LMSAdapter(BaseSourceAdapter):
    source = DataSource.lms

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(base_url=api_url, timeout=30.0)

    async def fetch(self, criteria: CollectionCriteria) -> list[PropertyListing]:
        # TODO: Implement LMS internal API integration
        logger.info("LMSAdapter.fetch called (stub)")
        return []

    async def close(self):
        await self.client.aclose()


class CrexyAdapter(BaseSourceAdapter):
    source = DataSource.crexy

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch(self, criteria: CollectionCriteria) -> list[PropertyListing]:
        # TODO: Implement Crexy API integration
        logger.info("CrexyAdapter.fetch called (stub)")
        return []

    async def close(self):
        await self.client.aclose()


class CollectorService:
    """Orchestrates property collection from all configured sources."""

    def __init__(self, adapters: list[BaseSourceAdapter], seen_ids: Optional[set[str]] = None):
        self.adapters = adapters
        # In production this would be backed by Redis for dedup
        self._seen_ids: set[str] = seen_ids or set()

    def _make_dedup_key(self, listing: PropertyListing) -> str:
        return f"{listing.source}:{listing.external_id}"

    def _is_duplicate(self, listing: PropertyListing) -> bool:
        return self._make_dedup_key(listing) in self._seen_ids

    def _mark_seen(self, listing: PropertyListing) -> None:
        self._seen_ids.add(self._make_dedup_key(listing))

    async def run(self, criteria: CollectionCriteria) -> list[CollectionRunResult]:
        results = []
        for adapter in self.adapters:
            result = CollectionRunResult(
                source=adapter.source,
                properties_found=0,
                properties_new=0,
                properties_skipped=0,
            )
            try:
                listings = await adapter.fetch(criteria)
                result.properties_found = len(listings)
                for listing in listings:
                    if self._is_duplicate(listing):
                        result.properties_skipped += 1
                    else:
                        self._mark_seen(listing)
                        result.properties_new += 1
                        # TODO: persist to database
            except Exception as e:
                logger.exception("Error collecting from %s", adapter.source)
                result.errors.append(str(e))
            results.append(result)
        return results
