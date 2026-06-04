from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.modules.portfolio.schemas import (
    FinancialTransaction,
    FinancialTransactionCreate,
    MaintenanceRecord,
    MaintenanceRecordCreate,
    PortfolioProperty,
    PortfolioPropertyCreate,
    PortfolioPropertyUpdate,
    PortfolioSummary,
    PropertyFinancialSummary,
    RentalRecord,
    RentalRecordCreate,
)
from app.modules.portfolio.service import PortfolioService

router = APIRouter()

_service = PortfolioService()


# --- Properties ---


@router.post("/properties", response_model=PortfolioProperty, status_code=201)
async def create_property(data: PortfolioPropertyCreate) -> PortfolioProperty:
    return _service.add_property(data)


@router.get("/properties", response_model=list[PortfolioProperty])
async def list_properties() -> list[PortfolioProperty]:
    return _service.list_properties()


@router.get("/properties/{property_id}", response_model=PortfolioProperty)
async def get_property(property_id: uuid.UUID) -> PortfolioProperty:
    prop = _service.get_property(property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.patch("/properties/{property_id}", response_model=PortfolioProperty)
async def update_property(
    property_id: uuid.UUID, data: PortfolioPropertyUpdate
) -> PortfolioProperty:
    prop = _service.update_property(property_id, data)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.delete("/properties/{property_id}", status_code=204)
async def delete_property(property_id: uuid.UUID) -> None:
    if not _service.delete_property(property_id):
        raise HTTPException(status_code=404, detail="Property not found")


# --- Rentals ---


@router.post("/rentals", response_model=RentalRecord, status_code=201)
async def create_rental(data: RentalRecordCreate) -> RentalRecord:
    if not _service.get_property(data.property_id):
        raise HTTPException(status_code=404, detail="Property not found")
    return _service.add_rental(data)


@router.get("/rentals", response_model=list[RentalRecord])
async def list_rentals(property_id: Optional[uuid.UUID] = None) -> list[RentalRecord]:
    return _service.list_rentals(property_id)


# --- Maintenance ---


@router.post("/maintenance", response_model=MaintenanceRecord, status_code=201)
async def create_maintenance(data: MaintenanceRecordCreate) -> MaintenanceRecord:
    if not _service.get_property(data.property_id):
        raise HTTPException(status_code=404, detail="Property not found")
    return _service.add_maintenance(data)


@router.get("/maintenance", response_model=list[MaintenanceRecord])
async def list_maintenance(property_id: Optional[uuid.UUID] = None) -> list[MaintenanceRecord]:
    return _service.list_maintenance(property_id)


# --- Transactions ---


@router.post("/transactions", response_model=FinancialTransaction, status_code=201)
async def create_transaction(data: FinancialTransactionCreate) -> FinancialTransaction:
    if not _service.get_property(data.property_id):
        raise HTTPException(status_code=404, detail="Property not found")
    return _service.add_transaction(data)


@router.get("/transactions", response_model=list[FinancialTransaction])
async def list_transactions(
    property_id: Optional[uuid.UUID] = None,
) -> list[FinancialTransaction]:
    return _service.list_transactions(property_id)


# --- Analysis ---


@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary() -> PortfolioSummary:
    return _service.portfolio_summary()


@router.get("/properties/{property_id}/analysis", response_model=PropertyFinancialSummary)
async def analyze_property(property_id: uuid.UUID) -> PropertyFinancialSummary:
    analysis = _service.analyze_property(property_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Property not found")
    return analysis
