"""
ATDD step definitions for Collector feature.
Uses pytest-bdd with Gherkin scenarios defined in features/collector.feature.
"""

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from app.modules.collector.schemas import (
    CollectionCriteria,
    CollectionRunResult,
    DataSource,
    PropertyListing,
    PropertyType,
)
from app.modules.collector.service import BaseSourceAdapter, CollectorService


# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------


def make_listing(source: DataSource, idx: int) -> PropertyListing:
    return PropertyListing(
        external_id=f"prop-{source}-{idx}",
        source=source,
        address=f"{idx} Main St",
        city="Testville",
        state="TX",
        zip_code="78701",
        price=250_000 + idx * 10_000,
        property_type=PropertyType.single_family,
    )


class StubAdapter(BaseSourceAdapter):
    def __init__(self, source: DataSource, listings: list[PropertyListing], raise_error: bool = False):
        self.source = source
        self._listings = listings
        self._raise_error = raise_error

    async def fetch(self, criteria: CollectionCriteria) -> list[PropertyListing]:
        if self._raise_error:
            raise RuntimeError("Simulated adapter failure")
        return self._listings


# ---------------------------------------------------------------------------
# Scenario: Collect properties from a source adapter
# ---------------------------------------------------------------------------


@scenario("../features/collector.feature", "Collect properties from a source adapter")
def test_collect_from_adapter():
    pass


@scenario("../features/collector.feature", "Deduplicate already-seen properties")
def test_deduplicate():
    pass


@scenario("../features/collector.feature", "Handle source adapter failure gracefully")
def test_handle_failure():
    pass


@scenario("../features/collector.feature", "Run collection across multiple sources")
def test_multi_source():
    pass


# ---------------------------------------------------------------------------
# Shared Given Steps
# ---------------------------------------------------------------------------


@pytest.fixture
def context():
    return {}


@given(parsers.parse("collection criteria with min price {min_price:d} and max price {max_price:d}"))
def set_criteria(context, min_price, max_price):
    context["criteria"] = CollectionCriteria(min_price=min_price, max_price=max_price)


@given(parsers.parse("a source adapter that returns {count:d} properties"))
def stub_adapter_with_listings(context, count):
    listings = [make_listing(DataSource.zillow, i) for i in range(count)]
    context["adapters"] = [StubAdapter(DataSource.zillow, listings)]


@given(parsers.parse("{already_seen:d} of those properties was already seen"))
def mark_already_seen(context, already_seen):
    # Put the first N listing keys in the "seen" set
    adapters = context["adapters"]
    seen_ids = set()
    for adapter in adapters:
        for listing in adapter._listings[:already_seen]:
            seen_ids.add(f"{listing.source}:{listing.external_id}")
    context["seen_ids"] = seen_ids


@given("a source adapter that raises an error")
def stub_failing_adapter(context):
    context["adapters"] = [StubAdapter(DataSource.zillow, [], raise_error=True)]


@given(parsers.parse("a Zillow adapter returning {count:d} properties"))
def zillow_adapter(context, count):
    listings = [make_listing(DataSource.zillow, i) for i in range(count)]
    context.setdefault("adapters", []).append(StubAdapter(DataSource.zillow, listings))


@given(parsers.parse("a Realtor adapter returning {count:d} property"))
def realtor_adapter(context, count):
    listings = [make_listing(DataSource.realtor, i) for i in range(count)]
    context.setdefault("adapters", []).append(StubAdapter(DataSource.realtor, listings))


# ---------------------------------------------------------------------------
# When Steps
# ---------------------------------------------------------------------------


@when("I run the collector")
@pytest.mark.asyncio
async def run_collector(context):
    service = CollectorService(
        adapters=context["adapters"],
        seen_ids=context.get("seen_ids"),
    )
    context["results"] = await service.run(context["criteria"])


# ---------------------------------------------------------------------------
# Then Steps
# ---------------------------------------------------------------------------


@then(parsers.parse("the result shows {count:d} properties found"))
def assert_found(context, count):
    result: CollectionRunResult = context["results"][0]
    assert result.properties_found == count, f"Expected {count} found, got {result.properties_found}"


@then(parsers.parse("the result shows {count:d} new properties"))
def assert_new(context, count):
    result: CollectionRunResult = context["results"][0]
    assert result.properties_new == count, f"Expected {count} new, got {result.properties_new}"


@then(parsers.parse("the result shows {count:d} skipped properties"))
def assert_skipped(context, count):
    result: CollectionRunResult = context["results"][0]
    assert result.properties_skipped == count, f"Expected {count} skipped, got {result.properties_skipped}"


@then("the result contains an error message")
def assert_error(context):
    result: CollectionRunResult = context["results"][0]
    assert len(result.errors) > 0, "Expected at least one error"


@then(parsers.parse("the collection result has {count:d} source results"))
def assert_source_count(context, count):
    assert len(context["results"]) == count


@then(parsers.parse("the total new properties across all sources is {count:d}"))
def assert_total_new(context, count):
    total = sum(r.properties_new for r in context["results"])
    assert total == count, f"Expected {count} total new, got {total}"
