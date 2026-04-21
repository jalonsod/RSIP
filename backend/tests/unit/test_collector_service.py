"""Unit tests for CollectorService."""

import pytest

from app.modules.collector.schemas import (
    CollectionCriteria,
    DataSource,
    PropertyListing,
    PropertyType,
)
from app.modules.collector.service import BaseSourceAdapter, CollectorService


def make_listing(source: DataSource = DataSource.zillow, idx: int = 0) -> PropertyListing:
    return PropertyListing(
        external_id=f"prop-{idx}",
        source=source,
        address=f"{idx} Oak Ave",
        city="Austin",
        state="TX",
        zip_code="78701",
        price=300_000,
        property_type=PropertyType.single_family,
    )


class MockAdapter(BaseSourceAdapter):
    def __init__(self, source: DataSource, listings: list[PropertyListing], fail: bool = False):
        self.source = source
        self._listings = listings
        self._fail = fail

    async def fetch(self, criteria: CollectionCriteria) -> list[PropertyListing]:
        if self._fail:
            raise RuntimeError("Network error")
        return self._listings


CRITERIA = CollectionCriteria(min_price=100_000, max_price=600_000)


@pytest.mark.asyncio
async def test_no_adapters_returns_empty():
    service = CollectorService(adapters=[])
    results = await service.run(CRITERIA)
    assert results == []


@pytest.mark.asyncio
async def test_single_adapter_all_new():
    listings = [make_listing(idx=i) for i in range(3)]
    adapter = MockAdapter(DataSource.zillow, listings)
    service = CollectorService(adapters=[adapter])
    results = await service.run(CRITERIA)
    assert len(results) == 1
    assert results[0].properties_found == 3
    assert results[0].properties_new == 3
    assert results[0].properties_skipped == 0
    assert results[0].errors == []


@pytest.mark.asyncio
async def test_deduplication():
    listing = make_listing(idx=0)
    adapter = MockAdapter(DataSource.zillow, [listing])
    seen = {f"{listing.source}:{listing.external_id}"}
    service = CollectorService(adapters=[adapter], seen_ids=seen)
    results = await service.run(CRITERIA)
    assert results[0].properties_found == 1
    assert results[0].properties_new == 0
    assert results[0].properties_skipped == 1


@pytest.mark.asyncio
async def test_adapter_error_captured():
    adapter = MockAdapter(DataSource.zillow, [], fail=True)
    service = CollectorService(adapters=[adapter])
    results = await service.run(CRITERIA)
    assert results[0].properties_found == 0
    assert len(results[0].errors) == 1
    assert "Network error" in results[0].errors[0]


@pytest.mark.asyncio
async def test_multi_source_independent_dedup():
    z_listing = make_listing(DataSource.zillow, idx=1)
    r_listing = make_listing(DataSource.realtor, idx=1)
    adapters = [
        MockAdapter(DataSource.zillow, [z_listing]),
        MockAdapter(DataSource.realtor, [r_listing]),
    ]
    service = CollectorService(adapters=adapters)
    results = await service.run(CRITERIA)
    assert len(results) == 2
    assert sum(r.properties_new for r in results) == 2


@pytest.mark.asyncio
async def test_second_run_deduplicates():
    listings = [make_listing(idx=i) for i in range(2)]
    adapter = MockAdapter(DataSource.zillow, listings)
    service = CollectorService(adapters=[adapter])
    await service.run(CRITERIA)
    results = await service.run(CRITERIA)
    assert results[0].properties_new == 0
    assert results[0].properties_skipped == 2
