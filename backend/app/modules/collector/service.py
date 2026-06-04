import logging
from abc import ABC, abstractmethod

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.modules.collector.schemas import (
    CollectionCriteria,
    CollectionRunResult,
    DataSource,
    PropertyListing,
)
from app.models.property_listing import PropertyListingModel

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
        self.client = httpx.AsyncClient(base_url=api_url, timeout=30.0, headers={"X-API-Key": api_key})

    def _matches_criteria(self, listing: PropertyListing, criteria: CollectionCriteria) -> bool:
        if listing.price < criteria.min_price or listing.price > criteria.max_price:
            return False
        if criteria.property_types and listing.property_type not in criteria.property_types:
            return False
        if criteria.zip_codes and listing.zip_code not in criteria.zip_codes:
            return False
        if criteria.min_sqft is not None and listing.sqft is not None and listing.sqft < criteria.min_sqft:
            return False
        if criteria.max_sqft is not None and listing.sqft is not None and listing.sqft > criteria.max_sqft:
            return False
        if criteria.min_year_built is not None and listing.year_built is not None and listing.year_built < criteria.min_year_built:
            return False
        return True

    async def fetch(self, criteria: CollectionCriteria) -> list[PropertyListing]:
        if not self.api_url or not self.api_key:
            logger.warning("LMS API credentials not configured, skipping LMS collection")
            return []
        
        try:
            response = await self.client.get("/properties")
            response.raise_for_status()
            data = response.json()
            
            listings = []
            for item in data.get("properties", []):
                listing = PropertyListing(
                    external_id=str(item.get("id", "")),
                    source=DataSource.lms,
                    address=item.get("address", ""),
                    city=item.get("city", ""),
                    state=item.get("state", ""),
                    zip_code=item.get("zip_code", ""),
                    price=float(item.get("price", 0)),
                    bedrooms=item.get("bedrooms"),
                    bathrooms=item.get("bathrooms"),
                    sqft=item.get("sqft"),
                    year_built=item.get("year_built"),
                    property_type=PropertyType(item["property_type"]) if item.get("property_type") in [p.value for p in PropertyType] else None,
                    listing_url=item.get("url"),
                )
                if self._matches_criteria(listing, criteria):
                    listings.append(listing)
            
            logger.info(f"LMSAdapter.fetch returned {len(listings)} properties")
            return listings
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch from LMS API: {e}")
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

    def __init__(
        self,
        adapters: list[BaseSourceAdapter],
        session: AsyncSession | None = None,
        seen_ids: set[str] | None = None,
    ):
        self.adapters = adapters
        self._session = session
        self._seen_ids: set[str] = seen_ids or set()

    def _make_dedup_key(self, listing: PropertyListing) -> str:
        return f"{listing.source}:{listing.external_id}"

    def _is_duplicate(self, listing: PropertyListing) -> bool:
        return self._make_dedup_key(listing) in self._seen_ids

    def _mark_seen(self, listing: PropertyListing) -> None:
        self._seen_ids.add(self._make_dedup_key(listing))

    async def _persist_listing(self, listing: PropertyListing) -> bool:
        if self._session is None:
            return False
        try:
            stmt = insert(PropertyListingModel).values(
                external_id=listing.external_id,
                source=listing.source.value,
                address=listing.address,
                city=listing.city,
                state=listing.state,
                zip_code=listing.zip_code,
                price=listing.price,
                bedrooms=listing.bedrooms,
                bathrooms=listing.bathrooms,
                sqft=listing.sqft,
                year_built=listing.year_built,
                property_type=listing.property_type.value if listing.property_type else None,
                listing_url=listing.listing_url,
                collected_at=listing.collected_at,
            ).on_conflict_do_nothing(
                index_elements=["source", "external_id"]
            ).returning(PropertyListingModel.id)
            
            result = await self._session.execute(stmt)
            return result.fetchone() is not None
        except Exception:
            logger.exception("Failed to persist listing %s", listing.external_id)
            return False

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
                        await self._persist_listing(listing)
            except Exception as e:
                logger.exception("Error collecting from %s", adapter.source)
                result.errors.append(str(e))
            results.append(result)
        
        if self._session is not None:
            await self._session.commit()
        
        return results
