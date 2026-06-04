"""ATDD step definitions for Portfolio Management feature."""

import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenario, then, when

from app.modules.portfolio.schemas import (
    FinancialTransactionCreate,
    MaintenanceRecordCreate,
    PortfolioPropertyCreate,
    RentalRecordCreate,
    RentalStatus,
    TransactionType,
)
from app.modules.portfolio.service import PortfolioService


# ---------------------------------------------------------------------------
# Scenario registrations
# ---------------------------------------------------------------------------


@scenario("../features/portfolio.feature", "Add property to portfolio")
def test_add_property():
    pass


@scenario("../features/portfolio.feature", "Record rental income")
def test_record_rental():
    pass


@scenario("../features/portfolio.feature", "Calculate NOI")
def test_calculate_noi():
    pass


@scenario("../features/portfolio.feature", "Portfolio summary")
def test_portfolio_summary():
    pass


@scenario("../features/portfolio.feature", "Get portfolio summary via API")
def test_api_summary():
    pass


@scenario("../features/portfolio.feature", "Create property via API")
def test_api_create_property():
    pass


@scenario("../features/portfolio.feature", "Get property analysis via API")
def test_api_analysis():
    pass


@scenario("../features/portfolio.feature", "Request analysis for unknown property via API")
def test_api_analysis_not_found():
    pass


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def context():
    return {"service": PortfolioService()}


@pytest.fixture
def api_client():
    from app.main import app

    return TestClient(app)


@pytest.fixture
def api_response():
    return {}


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------


@given(
    parsers.parse(
        "a portfolio property purchased for {price:d} currently valued at {value:d}"
    )
)
def given_property(context, price, value):
    data = PortfolioPropertyCreate(
        address="100 Test Ave",
        city="Austin",
        state="TX",
        zip_code="78701",
        purchase_price=float(price),
        purchase_date=date(2024, 1, 1),
        current_value=float(value),
        mortgage_balance=0.0,
    )
    context["property"] = context["service"].add_property(data)


@given(
    parsers.parse(
        "a portfolio property purchased for {price:d} currently valued at {value:d} with mortgage {mortgage:d}"
    )
)
def given_property_with_mortgage(context, price, value, mortgage):
    data = PortfolioPropertyCreate(
        address="100 Test Ave",
        city="Austin",
        state="TX",
        zip_code="78701",
        purchase_price=float(price),
        purchase_date=date(2024, 1, 1),
        current_value=float(value),
        mortgage_balance=float(mortgage),
    )
    context["property"] = context["service"].add_property(data)


@given(parsers.parse("an active rental with monthly rent {rent:d}"))
def given_rental(context, rent):
    data = RentalRecordCreate(
        property_id=context["property"].id,
        tenant="Test Tenant",
        lease_start=date(2024, 1, 1),
        lease_end=date(2025, 1, 1),
        monthly_rent=float(rent),
        status=RentalStatus.active,
    )
    context["service"].add_rental(data)


@given(parsers.parse("a maintenance expense of {amount:d} for the year"))
def given_maintenance_expense(context, amount):
    context["service"].add_maintenance(
        MaintenanceRecordCreate(
            property_id=context["property"].id,
            description="Annual maintenance",
            cost=float(amount),
            date=date(2024, 6, 1),
            status="complete",
        )
    )
    context["service"].add_transaction(
        FinancialTransactionCreate(
            property_id=context["property"].id,
            type=TransactionType.expense,
            amount=float(amount),
            date=date(2024, 6, 1),
            description="Annual maintenance",
        )
    )


@given(
    parsers.parse(
        "a second portfolio property purchased for {price:d} currently valued at {value:d} with mortgage {mortgage:d}"
    )
)
def given_second_property(context, price, value, mortgage):
    data = PortfolioPropertyCreate(
        address="200 Second St",
        city="Austin",
        state="TX",
        zip_code="78702",
        purchase_price=float(price),
        purchase_date=date(2024, 1, 1),
        current_value=float(value),
        mortgage_balance=float(mortgage),
    )
    context["property2"] = context["service"].add_property(data)


@given(parsers.parse("an active rental on the second property with monthly rent {rent:d}"))
def given_rental_second_property(context, rent):
    data = RentalRecordCreate(
        property_id=context["property2"].id,
        tenant="Tenant 2",
        lease_start=date(2024, 1, 1),
        lease_end=date(2025, 1, 1),
        monthly_rent=float(rent),
        status=RentalStatus.active,
    )
    context["service"].add_rental(data)


@given("the API is running")
def api_running(api_client, api_response):
    pass


@given("a property exists in the API")
def api_property_exists(api_client, api_response):
    resp = api_client.post(
        "/api/v1/portfolio/properties",
        json={
            "address": "99 Sample Rd",
            "city": "Austin",
            "state": "TX",
            "zip_code": "78701",
            "purchase_price": 300000,
            "purchase_date": "2024-01-01",
            "current_value": 320000,
            "mortgage_balance": 200000,
        },
    )
    api_response["created_id"] = resp.json()["id"]


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------


@when(
    parsers.parse(
        'I add a property with address "{address}" in "{city}" "{state}" "{zip_code}" '
        "purchased for {price:d} on \"{purchase_date}\" currently valued at {value:d} "
        "with mortgage {mortgage:d}"
    )
)
def add_property(context, address, city, state, zip_code, price, purchase_date, value, mortgage):
    data = PortfolioPropertyCreate(
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        purchase_price=float(price),
        purchase_date=date.fromisoformat(purchase_date),
        current_value=float(value),
        mortgage_balance=float(mortgage),
    )
    context["property"] = context["service"].add_property(data)


@when(parsers.parse("I add an active rental with monthly rent {rent:d}"))
def add_rental(context, rent):
    data = RentalRecordCreate(
        property_id=context["property"].id,
        tenant="New Tenant",
        lease_start=date(2024, 3, 1),
        lease_end=date(2025, 3, 1),
        monthly_rent=float(rent),
        status=RentalStatus.active,
    )
    context["rental"] = context["service"].add_rental(data)


@when("I analyze the property financials")
def analyze_financials(context):
    context["analysis"] = context["service"].analyze_property(context["property"].id)


@when("I request the portfolio summary")
def request_summary(context):
    context["summary"] = context["service"].portfolio_summary()


@when("I GET the portfolio summary")
def api_get_summary(api_client, api_response):
    api_response["resp"] = api_client.get("/api/v1/portfolio/summary")


@when("I POST a new property to the portfolio API")
def api_post_property(api_client, api_response):
    api_response["resp"] = api_client.post(
        "/api/v1/portfolio/properties",
        json={
            "address": "42 Oak Lane",
            "city": "Houston",
            "state": "TX",
            "zip_code": "77001",
            "purchase_price": 250000,
            "purchase_date": "2024-06-01",
            "current_value": 265000,
            "mortgage_balance": 180000,
        },
    )


@when("I GET the property analysis")
def api_get_analysis(api_client, api_response):
    prop_id = api_response["created_id"]
    api_response["resp"] = api_client.get(f"/api/v1/portfolio/properties/{prop_id}/analysis")


@when("I GET analysis for a nonexistent property id")
def api_get_analysis_not_found(api_client, api_response):
    api_response["resp"] = api_client.get(f"/api/v1/portfolio/properties/{uuid.uuid4()}/analysis")


# ---------------------------------------------------------------------------
# Then steps
# ---------------------------------------------------------------------------


@then(parsers.parse("the portfolio has {count:d} property"))
def assert_portfolio_count(context, count):
    assert len(context["service"].list_properties()) == count


@then(parsers.parse('the property address is "{address}"'))
def assert_property_address(context, address):
    assert context["property"].address == address


@then(parsers.parse("the property current value is {value:d}"))
def assert_property_value(context, value):
    assert context["property"].current_value == float(value)


@then(parsers.parse("the property has {count:d} active rental"))
def assert_active_rentals(context, count):
    rentals = context["service"].list_rentals(context["property"].id)
    active = [r for r in rentals if r.status == RentalStatus.active]
    assert len(active) == count


@then(parsers.parse("the total monthly income for the property is {amount}"))
def assert_monthly_income(context, amount):
    analysis = context["service"].analyze_property(context["property"].id)
    assert analysis is not None
    assert analysis.monthly_income == float(amount)


@then(parsers.parse("the monthly income is {amount}"))
def assert_monthly_income_analysis(context, amount):
    assert context["analysis"].monthly_income == float(amount)


@then("the annual NOI is greater than 0")
def assert_noi_positive(context):
    assert context["analysis"].noi > 0


@then("the cap rate is greater than 0")
def assert_cap_rate_positive(context):
    assert context["analysis"].cap_rate > 0


@then("the cash on cash return is greater than 0")
def assert_cash_on_cash_positive(context):
    assert context["analysis"].cash_on_cash_return > 0


@then(parsers.parse("the summary shows {count:d} total properties"))
def assert_summary_total_properties(context, count):
    assert context["summary"].total_properties == count


@then(parsers.parse("the total portfolio value is {value}"))
def assert_summary_total_value(context, value):
    assert context["summary"].total_value == float(value)


@then("the total NOI is greater than 0")
def assert_summary_noi_positive(context):
    assert context["summary"].total_noi > 0


@then(parsers.parse("the response status is {status:d}"))
def assert_response_status(api_response, status):
    assert api_response["resp"].status_code == status


@then("the response contains total_properties")
def assert_response_has_total_properties(api_response):
    body = api_response["resp"].json()
    assert "total_properties" in body


@then("the response contains a property id")
def assert_response_has_property_id(api_response):
    body = api_response["resp"].json()
    assert "id" in body


@then("the response contains monthly_income")
def assert_response_has_monthly_income(api_response):
    body = api_response["resp"].json()
    assert "monthly_income" in body
