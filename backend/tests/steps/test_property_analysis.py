"""BDD step definitions for Property Investment Analysis (ATDD)."""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.modules.property_analysis.schemas import PropertyAnalysis, PropertyAnalysisQuery
from app.modules.property_analysis.service import (
    BasePropertyAdapter,
    PropertyAnalysisService,
)

scenarios("../features/property_analysis.feature")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def query():
    return PropertyAnalysisQuery(zpid="12345678")


@pytest.fixture
def adapters():
    return []


@pytest.fixture
def analysis_result():
    return {}


@pytest.fixture
def api_client():
    from app.main import app
    return TestClient(app)


@pytest.fixture
def api_response():
    return {}


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------


@given(parsers.parse('a property with zpid "{zpid}"'), target_fixture="query")
def given_property_zpid(zpid):
    return PropertyAnalysisQuery(zpid=zpid)


# ---------------------------------------------------------------------------
# Adapter setup steps
# ---------------------------------------------------------------------------


class StubPropertyAdapter(BasePropertyAdapter):
    source_name = "zillow_property"

    def __init__(self, data: dict):
        self._data = data

    async def fetch(self, query):
        return self._data


class StubRentEstimateAdapter(BasePropertyAdapter):
    source_name = "zillow_rent_estimate"

    def __init__(self, data: dict):
        self._data = data

    async def fetch(self, query):
        return self._data


class StubComparablesAdapter(BasePropertyAdapter):
    source_name = "comparables"

    def __init__(self, data: dict):
        self._data = data

    async def fetch(self, query):
        return self._data


class FailingAdapter(BasePropertyAdapter):
    def __init__(self, name: str):
        self.source_name = name

    async def fetch(self, query):
        raise RuntimeError(f"Simulated failure from {self.source_name}")


@given(
    parsers.parse(
        "a Zillow property adapter returning price {price:d} sqft {sqft:d} beds {beds:d} baths {baths:d}"
    ),
    target_fixture="adapters",
)
def given_property_adapter(price, sqft, beds, baths):
    return [
        StubPropertyAdapter(
            {"price": float(price), "sqft": float(sqft), "beds": beds, "baths": float(baths)}
        )
    ]


@given(
    parsers.parse("a Zillow rental estimate adapter returning expected rent {rent:d}"),
    target_fixture="adapters",
)
def given_rent_estimate_adapter(adapters, rent):
    adapters.append(StubRentEstimateAdapter({"expected_rent": float(rent)}))
    return adapters


@given(
    parsers.parse(
        "a comparables adapter returning {count:d} neighbors with avg price {avg_price:d}"
    ),
    target_fixture="adapters",
)
def given_comparables_adapter(adapters, count, avg_price):
    adapters.append(
        StubComparablesAdapter({"neighbor_count": count, "avg_neighbor_price": float(avg_price)})
    )
    return adapters


@given("a failing Zillow property adapter", target_fixture="adapters")
def given_failing_property_adapter():
    return [FailingAdapter("zillow_property")]


@given("a failing Zillow rental estimate adapter", target_fixture="adapters")
def given_failing_rent_adapter(adapters):
    adapters.append(FailingAdapter("zillow_rent_estimate"))
    return adapters


@given("a failing comparables adapter", target_fixture="adapters")
def given_failing_comparables_adapter(adapters):
    adapters.append(FailingAdapter("comparables"))
    return adapters


@given("a failing Zillow zone adapter", target_fixture="adapters")
def given_failing_zone_adapter(adapters):
    adapters.append(FailingAdapter("zillow_zone"))
    return adapters


# ---------------------------------------------------------------------------
# Action
# ---------------------------------------------------------------------------


@when("I analyze the property", target_fixture="analysis_result")
def when_analyze(query, adapters):
    import asyncio
    service = PropertyAnalysisService(adapters=adapters)
    return asyncio.get_event_loop().run_until_complete(service.analyze(query))


# ---------------------------------------------------------------------------
# Assertions — service-level
# ---------------------------------------------------------------------------


@then(parsers.parse('the analysis zpid is "{zpid}"'))
def then_zpid(analysis_result, zpid):
    assert analysis_result.zpid == zpid


@then(parsers.parse("the analysis price is {price:d}"))
def then_price(analysis_result, price):
    assert analysis_result.price == float(price)


@then(parsers.parse("the analysis expected rent is {rent:f}"))
def then_expected_rent(analysis_result, rent):
    assert analysis_result.expected_rent == rent


@then("the analysis expected rent is None")
def then_expected_rent_none(analysis_result):
    assert analysis_result.expected_rent is None


@then(parsers.parse("the analysis price per sqft is {ppsf:f}"))
def then_price_per_sqft(analysis_result, ppsf):
    assert abs(analysis_result.price_per_sqft - ppsf) < 0.01


@then(parsers.parse("the analysis price vs neighbors delta is {delta:d}"))
def then_price_vs_neighbors(analysis_result, delta):
    assert analysis_result.price_vs_neighbors_delta == float(delta)


@then(parsers.parse('the analysis data sources include "{source}"'))
def then_data_source(analysis_result, source):
    assert source in analysis_result.data_sources


@then("the analysis has no errors")
def then_no_errors(analysis_result):
    assert analysis_result.errors == []


@then(parsers.parse('the analysis contains an error from "{source}"'))
def then_error_from(analysis_result, source):
    assert any(source in e for e in analysis_result.errors)


@then(parsers.parse("the analysis has {count:d} errors"))
def then_error_count(analysis_result, count):
    assert len(analysis_result.errors) == count


# ---------------------------------------------------------------------------
# API-level steps
# ---------------------------------------------------------------------------


@given("the API is running", target_fixture="api_client")
def given_api_running():
    from app.main import app
    return TestClient(app)


@given(
    parsers.parse('property analysis for zpid "{zpid}" is cached'),
    target_fixture="cached_zpid",
)
def given_analysis_cached(api_client, zpid):
    resp = api_client.post("/api/v1/properties/analyze", json={"zpid": zpid})
    assert resp.status_code == 200
    return zpid


@when(
    parsers.parse('I GET analysis for zpid "{zpid}"'),
    target_fixture="api_response",
)
def when_get_analysis(api_client, zpid):
    return api_client.get(f"/api/v1/properties/analysis/{zpid}")


@when(
    parsers.parse('I POST analyze for zpid "{zpid}"'),
    target_fixture="api_response",
)
def when_post_analyze(api_client, zpid):
    return api_client.post("/api/v1/properties/analyze", json={"zpid": zpid})


@then(parsers.parse("the response status is {status:d}"))
def then_status(api_response, status):
    assert api_response.status_code == status


@then(parsers.parse('the response zpid is "{zpid}"'))
def then_response_zpid(api_response, zpid):
    assert api_response.json()["zpid"] == zpid
