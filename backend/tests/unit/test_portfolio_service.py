"""Unit tests for PortfolioService and portfolio router."""

import uuid
from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient

from app.modules.portfolio.schemas import (
    FinancialTransactionCreate,
    MaintenanceRecordCreate,
    PortfolioPropertyCreate,
    PortfolioPropertyUpdate,
    RentalRecordCreate,
    RentalStatus,
    TransactionType,
)
from app.modules.portfolio.service import PortfolioService


def make_property_data(**kwargs) -> PortfolioPropertyCreate:
    defaults = dict(
        address="1 Test St",
        city="Austin",
        state="TX",
        zip_code="78701",
        purchase_price=300_000,
        purchase_date=date(2024, 1, 1),
        current_value=320_000,
        mortgage_balance=200_000,
    )
    defaults.update(kwargs)
    return PortfolioPropertyCreate(**defaults)


# ---------------------------------------------------------------------------
# PortfolioService — CRUD paths
# ---------------------------------------------------------------------------


def test_get_nonexistent_property():
    service = PortfolioService()
    assert service.get_property(uuid.uuid4()) is None


def test_update_property():
    service = PortfolioService()
    prop = service.add_property(make_property_data())
    updated = service.update_property(prop.id, PortfolioPropertyUpdate(current_value=350_000))
    assert updated is not None
    assert updated.current_value == 350_000


def test_update_nonexistent_property():
    service = PortfolioService()
    result = service.update_property(uuid.uuid4(), PortfolioPropertyUpdate(current_value=1))
    assert result is None


def test_delete_property():
    service = PortfolioService()
    prop = service.add_property(make_property_data())
    assert service.delete_property(prop.id) is True
    assert service.get_property(prop.id) is None


def test_delete_nonexistent_property():
    service = PortfolioService()
    assert service.delete_property(uuid.uuid4()) is False


def test_get_rental():
    service = PortfolioService()
    prop = service.add_property(make_property_data())
    rental = service.add_rental(
        RentalRecordCreate(
            property_id=prop.id,
            tenant="Alice",
            lease_start=date(2024, 1, 1),
            lease_end=date(2025, 1, 1),
            monthly_rent=1500,
        )
    )
    assert service.get_rental(rental.id) == rental
    assert service.get_rental(uuid.uuid4()) is None


def test_list_rentals_by_property():
    service = PortfolioService()
    p1 = service.add_property(make_property_data(address="A"))
    p2 = service.add_property(make_property_data(address="B"))
    service.add_rental(
        RentalRecordCreate(property_id=p1.id, tenant="T1", lease_start=date(2024, 1, 1),
                           lease_end=date(2025, 1, 1), monthly_rent=1000)
    )
    service.add_rental(
        RentalRecordCreate(property_id=p2.id, tenant="T2", lease_start=date(2024, 1, 1),
                           lease_end=date(2025, 1, 1), monthly_rent=2000)
    )
    assert len(service.list_rentals(p1.id)) == 1
    assert len(service.list_rentals(p2.id)) == 1
    assert len(service.list_rentals()) == 2


def test_get_maintenance():
    service = PortfolioService()
    prop = service.add_property(make_property_data())
    rec = service.add_maintenance(
        MaintenanceRecordCreate(
            property_id=prop.id, description="HVAC", cost=500, date=date(2024, 3, 1)
        )
    )
    assert service.get_maintenance(rec.id) == rec
    assert service.get_maintenance(uuid.uuid4()) is None


def test_list_maintenance_by_property():
    service = PortfolioService()
    p1 = service.add_property(make_property_data(address="A"))
    p2 = service.add_property(make_property_data(address="B"))
    service.add_maintenance(
        MaintenanceRecordCreate(property_id=p1.id, description="Fix", cost=100, date=date(2024, 1, 1))
    )
    assert len(service.list_maintenance(p1.id)) == 1
    assert len(service.list_maintenance(p2.id)) == 0
    assert len(service.list_maintenance()) == 1


def test_get_transaction():
    service = PortfolioService()
    prop = service.add_property(make_property_data())
    txn = service.add_transaction(
        FinancialTransactionCreate(
            property_id=prop.id, type=TransactionType.rent, amount=2000, date=date(2024, 1, 1)
        )
    )
    assert service.get_transaction(txn.id) == txn
    assert service.get_transaction(uuid.uuid4()) is None


def test_list_transactions_by_property():
    service = PortfolioService()
    p1 = service.add_property(make_property_data(address="A"))
    p2 = service.add_property(make_property_data(address="B"))
    service.add_transaction(
        FinancialTransactionCreate(property_id=p1.id, type=TransactionType.expense,
                                   amount=300, date=date(2024, 1, 1))
    )
    assert len(service.list_transactions(p1.id)) == 1
    assert len(service.list_transactions(p2.id)) == 0
    assert len(service.list_transactions()) == 1


def test_analyze_nonexistent_property():
    service = PortfolioService()
    assert service.analyze_property(uuid.uuid4()) is None


def test_empty_portfolio_summary():
    service = PortfolioService()
    summary = service.portfolio_summary()
    assert summary.total_properties == 0
    assert summary.total_value == 0.0
    assert summary.total_noi == 0.0


def test_portfolio_zero_equity():
    """Property with zero equity should not cause division by zero."""
    service = PortfolioService()
    prop = service.add_property(
        make_property_data(current_value=300_000, mortgage_balance=300_000)
    )
    service.add_rental(
        RentalRecordCreate(property_id=prop.id, tenant="T", lease_start=date(2024, 1, 1),
                           lease_end=date(2025, 1, 1), monthly_rent=2000)
    )
    analysis = service.analyze_property(prop.id)
    assert analysis is not None
    assert analysis.cash_on_cash_return == 0.0


# ---------------------------------------------------------------------------
# Router — missing 404 paths
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    from app.main import app

    return TestClient(app)


def test_router_get_nonexistent_property(client):
    resp = client.get(f"/api/v1/portfolio/properties/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_router_update_nonexistent_property(client):
    resp = client.patch(
        f"/api/v1/portfolio/properties/{uuid.uuid4()}",
        json={"current_value": 400000},
    )
    assert resp.status_code == 404


def test_router_delete_nonexistent_property(client):
    resp = client.delete(f"/api/v1/portfolio/properties/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_router_rental_for_missing_property(client):
    resp = client.post(
        "/api/v1/portfolio/rentals",
        json={
            "property_id": str(uuid.uuid4()),
            "tenant": "T",
            "lease_start": "2024-01-01",
            "lease_end": "2025-01-01",
            "monthly_rent": 1000,
        },
    )
    assert resp.status_code == 404


def test_router_maintenance_for_missing_property(client):
    resp = client.post(
        "/api/v1/portfolio/maintenance",
        json={
            "property_id": str(uuid.uuid4()),
            "description": "Fix roof",
            "cost": 500,
            "date": "2024-06-01",
        },
    )
    assert resp.status_code == 404


def test_router_transaction_for_missing_property(client):
    resp = client.post(
        "/api/v1/portfolio/transactions",
        json={
            "property_id": str(uuid.uuid4()),
            "type": "expense",
            "amount": 200,
            "date": "2024-06-01",
        },
    )
    assert resp.status_code == 404


def test_router_list_maintenance(client):
    resp = client.get("/api/v1/portfolio/maintenance")
    assert resp.status_code == 200


def test_router_list_transactions(client):
    resp = client.get("/api/v1/portfolio/transactions")
    assert resp.status_code == 200


def test_router_delete_property(client):
    create = client.post(
        "/api/v1/portfolio/properties",
        json={
            "address": "Delete Me",
            "city": "Houston",
            "state": "TX",
            "zip_code": "77001",
            "purchase_price": 200000,
            "purchase_date": "2024-01-01",
            "current_value": 210000,
            "mortgage_balance": 0,
        },
    )
    prop_id = create.json()["id"]
    resp = client.delete(f"/api/v1/portfolio/properties/{prop_id}")
    assert resp.status_code == 204
