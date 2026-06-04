from __future__ import annotations

import uuid
from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RentalStatus(str, Enum):
    active = "active"
    vacant = "vacant"
    pending = "pending"


class MaintenanceStatus(str, Enum):
    pending = "pending"
    complete = "complete"


class TransactionType(str, Enum):
    rent = "rent"
    expense = "expense"
    mortgage = "mortgage"


# --- PortfolioProperty ---


class PortfolioPropertyCreate(BaseModel):
    address: str
    city: str
    state: str
    zip_code: str
    purchase_price: float = Field(gt=0)
    purchase_date: date
    current_value: float = Field(gt=0)
    mortgage_balance: float = Field(default=0.0, ge=0)


class PortfolioPropertyUpdate(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    current_value: Optional[float] = Field(default=None, gt=0)
    mortgage_balance: Optional[float] = Field(default=None, ge=0)


class PortfolioProperty(PortfolioPropertyCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- RentalRecord ---


class RentalRecordCreate(BaseModel):
    property_id: uuid.UUID
    tenant: str
    lease_start: date
    lease_end: date
    monthly_rent: float = Field(gt=0)
    status: RentalStatus = RentalStatus.active


class RentalRecord(RentalRecordCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- MaintenanceRecord ---


class MaintenanceRecordCreate(BaseModel):
    property_id: uuid.UUID
    description: str
    cost: float = Field(ge=0)
    date: date
    status: MaintenanceStatus = MaintenanceStatus.pending


class MaintenanceRecord(MaintenanceRecordCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- FinancialTransaction ---


class FinancialTransactionCreate(BaseModel):
    property_id: uuid.UUID
    type: TransactionType
    amount: float
    date: date
    description: str = ""


class FinancialTransaction(FinancialTransactionCreate):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Analysis ---


class PropertyFinancialSummary(BaseModel):
    property_id: uuid.UUID
    monthly_income: float
    monthly_expenses: float
    noi: float
    cap_rate: float
    cash_on_cash_return: float


class PortfolioSummary(BaseModel):
    total_properties: int
    total_value: float
    total_noi: float
    avg_cap_rate: float
    avg_cash_on_cash_return: float
