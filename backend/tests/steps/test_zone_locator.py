"""
ATDD step definitions for Zone Locator feature.
Uses pytest-bdd with Gherkin scenarios in features/zone_locator.feature.
"""

import asyncio

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenario, then, when

from app.modules.zone_locator.schemas import ZoneLocatorQuery, ZoneMetrics
from app.modules.zone_locator.service import BaseZoneAdapter, ZoneLocatorService


# ---------------------------------------------------------------------------
# Helpers / Stubs
# ---------------------------------------------------------------------------


class StubCensusAdapter(BaseZoneAdapter):
    source_name = "census"

    def __init__(self, population: int | None = None, growth: float | None = None, fail: bool = False):
        self._population = population
        self._growth = growth
        self._fail = fail

    async def fetch(self, query: ZoneLocatorQuery) -> dict:
        if self._fail:
            raise RuntimeError("Census API unavailable")
        return {"population": self._population, "population_growth_pct": self._growth}


class StubBLSAdapter(BaseZoneAdapter):
    source_name = "bls"

    def __init__(self, jobs: int | None = None, unemployment: float | None = None, fail: bool = False):
        self._jobs = jobs
        self._unemployment = unemployment
        self._fail = fail

    async def fetch(self, query: ZoneLocatorQuery) -> dict:
        if self._fail:
            raise RuntimeError("BLS API unavailable")
        return {"jobs_by_radius": self._jobs, "unemployment_rate_pct": self._unemployment}


class StubZillowZoneAdapter(BaseZoneAdapter):
    source_name = "zillow"

    def __init__(
        self,
        rental_count: int | None = None,
        avg_rental: float | None = None,
        days_to_rent: float | None = None,
        sale_count: int | None = None,
        avg_sale: float | None = None,
        days_to_sell: float | None = None,
        fail: bool = False,
    ):
        self._rental_count = rental_count
        self._avg_rental = avg_rental
        self._days_to_rent = days_to_rent
        self._sale_count = sale_count
        self._avg_sale = avg_sale
        self._days_to_sell = days_to_sell
        self._fail = fail

    async def fetch(self, query: ZoneLocatorQuery) -> dict:
        if self._fail:
            raise RuntimeError("Zillow API unavailable")
        return {
            "rental_availability_count": self._rental_count,
            "avg_rental_price": self._avg_rental,
            "days_to_rent": self._days_to_rent,
            "sale_availability_count": self._sale_count,
            "avg_sale_price": self._avg_sale,
            "days_to_sell": self._days_to_sell,
        }


# ---------------------------------------------------------------------------
# Scenario bindings
# ---------------------------------------------------------------------------


@scenario("../features/zone_locator.feature", "Analyze zone with all adapters returning data")
def test_analyze_all_adapters():
    pass


@scenario("../features/zone_locator.feature", "Analyze zone with partial adapter data")
def test_analyze_partial():
    pass


@scenario("../features/zone_locator.feature", "Analyze zone with all adapters failing")
def test_analyze_all_failing():
    pass


@scenario("../features/zone_locator.feature", "Analyze zone with no adapters")
def test_analyze_no_adapters():
    pass


@scenario("../features/zone_locator.feature", "Retrieve cached metrics via API")
def test_api_cached_metrics():
    pass


@scenario("../features/zone_locator.feature", "Request metrics for unknown zip via API")
def test_api_not_found():
    pass


@scenario("../features/zone_locator.feature", "Analyze zone via POST API endpoint")
def test_api_post_analyze():
    pass


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def context():
    return {}


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------


@given(parsers.parse('a zone locator query for zip code "{zip_code}" with radius {radius:d} miles'))
def set_query(context, zip_code, radius):
    context["query"] = ZoneLocatorQuery(zip_code=zip_code, radius_miles=float(radius))
    context["adapters"] = []


@given(parsers.parse("a Census adapter returning population {population:d} and growth {growth:f}%"))
def census_adapter(context, population, growth):
    context["adapters"].append(StubCensusAdapter(population=population, growth=growth))


@given("a failing Census adapter")
def failing_census_adapter(context):
    context["adapters"].append(StubCensusAdapter(fail=True))


@given(parsers.parse("a BLS adapter returning {jobs:d} jobs and {unemployment:f}% unemployment"))
def bls_adapter(context, jobs, unemployment):
    context["adapters"].append(StubBLSAdapter(jobs=jobs, unemployment=unemployment))


@given("a failing BLS adapter")
def failing_bls_adapter(context):
    context["adapters"].append(StubBLSAdapter(fail=True))


@given(
    parsers.parse(
        "a Zillow zone adapter returning {rental_count:d} rentals avg price {avg_rental:d} days {days_rent:d}"
        " and {sale_count:d} sales avg price {avg_sale:d} days {days_sell:d}"
    )
)
def zillow_zone_adapter(context, rental_count, avg_rental, days_rent, sale_count, avg_sale, days_sell):
    context["adapters"].append(
        StubZillowZoneAdapter(
            rental_count=rental_count,
            avg_rental=float(avg_rental),
            days_to_rent=float(days_rent),
            sale_count=sale_count,
            avg_sale=float(avg_sale),
            days_to_sell=float(days_sell),
        )
    )


@given("a failing Zillow zone adapter")
def failing_zillow_adapter(context):
    context["adapters"].append(StubZillowZoneAdapter(fail=True))


@given("no adapters configured")
def no_adapters(context):
    context["adapters"] = []


@given("the API is running")
def api_client(context):
    from app.main import app
    context["client"] = TestClient(app)


@given(parsers.parse('zone metrics for zip "{zip_code}" are cached'))
def cache_metrics(context, zip_code):
    from app.modules.zone_locator.router import _metrics_cache
    _metrics_cache[zip_code] = ZoneMetrics(zip_code=zip_code, population=1000, data_sources=["census"])


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------


@when("I analyze the zone")
def analyze_zone(context):
    service = ZoneLocatorService(adapters=context["adapters"])
    context["metrics"] = asyncio.run(service.analyze(context["query"]))


@when(parsers.parse('I GET metrics for zip code "{zip_code}"'))
def get_metrics(context, zip_code):
    context["response"] = context["client"].get(f"/api/v1/zone-locator/metrics/{zip_code}")


@when(parsers.parse('I POST analyze for zip code "{zip_code}"'))
def post_analyze(context, zip_code):
    context["response"] = context["client"].post(
        "/api/v1/zone-locator/analyze",
        json={"zip_code": zip_code, "radius_miles": 10.0},
    )


# ---------------------------------------------------------------------------
# Then steps
# ---------------------------------------------------------------------------


@then(parsers.parse('the metrics zip code is "{zip_code}"'))
def assert_zip_code(context, zip_code):
    metrics: ZoneMetrics = context["metrics"]
    assert metrics.zip_code == zip_code


@then(parsers.parse("the metrics population is {population:d}"))
def assert_population(context, population):
    metrics: ZoneMetrics = context["metrics"]
    assert metrics.population == population


@then(parsers.parse("the metrics population growth is {growth:f}"))
def assert_growth(context, growth):
    metrics: ZoneMetrics = context["metrics"]
    assert metrics.population_growth_pct == pytest.approx(growth)


@then(parsers.parse("the metrics jobs by radius is {jobs:d}"))
def assert_jobs(context, jobs):
    metrics: ZoneMetrics = context["metrics"]
    assert metrics.jobs_by_radius == jobs


@then(parsers.parse("the metrics avg rental price is {price:f}"))
def assert_avg_rental(context, price):
    metrics: ZoneMetrics = context["metrics"]
    assert metrics.avg_rental_price == pytest.approx(price)


@then(parsers.parse("the metrics avg sale price is {price:f}"))
def assert_avg_sale(context, price):
    metrics: ZoneMetrics = context["metrics"]
    assert metrics.avg_sale_price == pytest.approx(price)


@then(parsers.parse('the metrics data sources include "{source}"'))
def assert_source(context, source):
    metrics: ZoneMetrics = context["metrics"]
    assert source in metrics.data_sources, f"Expected {source} in {metrics.data_sources}"


@then("the metrics have no errors")
def assert_no_errors(context):
    metrics: ZoneMetrics = context["metrics"]
    assert metrics.errors == [], f"Expected no errors, got: {metrics.errors}"


@then(parsers.parse('the metrics contain an error from "{source}"'))
def assert_error_from(context, source):
    metrics: ZoneMetrics = context["metrics"]
    assert any(source in e for e in metrics.errors), f"Expected error from {source} in {metrics.errors}"


@then(parsers.parse("the metrics have {count:d} errors"))
def assert_error_count(context, count):
    metrics: ZoneMetrics = context["metrics"]
    assert len(metrics.errors) == count, f"Expected {count} errors, got {len(metrics.errors)}: {metrics.errors}"


@then("the metrics data sources list is empty")
def assert_no_sources(context):
    metrics: ZoneMetrics = context["metrics"]
    assert metrics.data_sources == []


@then(parsers.parse("the response status is {status:d}"))
def assert_status(context, status):
    assert context["response"].status_code == status, f"Expected {status}, got {context['response'].status_code}: {context['response'].text}"


@then(parsers.parse('the response zip code is "{zip_code}"'))
def assert_response_zip(context, zip_code):
    data = context["response"].json()
    assert data["zip_code"] == zip_code
