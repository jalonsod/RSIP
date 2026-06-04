from __future__ import annotations

import uuid
from datetime import datetime, date
from typing import Optional

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
    RentalStatus,
    TransactionType,
)


class PortfolioService:
    def __init__(self) -> None:
        self._properties: dict[uuid.UUID, PortfolioProperty] = {}
        self._rentals: dict[uuid.UUID, RentalRecord] = {}
        self._maintenance: dict[uuid.UUID, MaintenanceRecord] = {}
        self._transactions: dict[uuid.UUID, FinancialTransaction] = {}

    # --- Properties ---

    def add_property(self, data: PortfolioPropertyCreate) -> PortfolioProperty:
        now = datetime.utcnow()
        prop = PortfolioProperty(id=uuid.uuid4(), created_at=now, updated_at=now, **data.model_dump())
        self._properties[prop.id] = prop
        return prop

    def get_property(self, property_id: uuid.UUID) -> Optional[PortfolioProperty]:
        return self._properties.get(property_id)

    def list_properties(self) -> list[PortfolioProperty]:
        return list(self._properties.values())

    def update_property(
        self, property_id: uuid.UUID, data: PortfolioPropertyUpdate
    ) -> Optional[PortfolioProperty]:
        prop = self._properties.get(property_id)
        if not prop:
            return None
        updates = {k: v for k, v in data.model_dump(exclude_none=True).items()}
        updated = prop.model_copy(update={**updates, "updated_at": datetime.utcnow()})
        self._properties[property_id] = updated
        return updated

    def delete_property(self, property_id: uuid.UUID) -> bool:
        if property_id not in self._properties:
            return False
        del self._properties[property_id]
        return True

    # --- Rentals ---

    def add_rental(self, data: RentalRecordCreate) -> RentalRecord:
        now = datetime.utcnow()
        rental = RentalRecord(id=uuid.uuid4(), created_at=now, updated_at=now, **data.model_dump())
        self._rentals[rental.id] = rental
        return rental

    def get_rental(self, rental_id: uuid.UUID) -> Optional[RentalRecord]:
        return self._rentals.get(rental_id)

    def list_rentals(self, property_id: Optional[uuid.UUID] = None) -> list[RentalRecord]:
        if property_id:
            return [r for r in self._rentals.values() if r.property_id == property_id]
        return list(self._rentals.values())

    # --- Maintenance ---

    def add_maintenance(self, data: MaintenanceRecordCreate) -> MaintenanceRecord:
        now = datetime.utcnow()
        record = MaintenanceRecord(
            id=uuid.uuid4(), created_at=now, updated_at=now, **data.model_dump()
        )
        self._maintenance[record.id] = record
        return record

    def get_maintenance(self, record_id: uuid.UUID) -> Optional[MaintenanceRecord]:
        return self._maintenance.get(record_id)

    def list_maintenance(
        self, property_id: Optional[uuid.UUID] = None
    ) -> list[MaintenanceRecord]:
        if property_id:
            return [m for m in self._maintenance.values() if m.property_id == property_id]
        return list(self._maintenance.values())

    # --- Transactions ---

    def add_transaction(self, data: FinancialTransactionCreate) -> FinancialTransaction:
        txn = FinancialTransaction(
            id=uuid.uuid4(), created_at=datetime.utcnow(), **data.model_dump()
        )
        self._transactions[txn.id] = txn
        return txn

    def get_transaction(self, txn_id: uuid.UUID) -> Optional[FinancialTransaction]:
        return self._transactions.get(txn_id)

    def list_transactions(
        self, property_id: Optional[uuid.UUID] = None
    ) -> list[FinancialTransaction]:
        if property_id:
            return [t for t in self._transactions.values() if t.property_id == property_id]
        return list(self._transactions.values())

    # --- Analysis ---

    def analyze_property(self, property_id: uuid.UUID) -> Optional[PropertyFinancialSummary]:
        prop = self._properties.get(property_id)
        if not prop:
            return None

        active_rentals = [
            r
            for r in self._rentals.values()
            if r.property_id == property_id and r.status == RentalStatus.active
        ]
        monthly_income = sum(r.monthly_rent for r in active_rentals)

        expense_txns = [
            t
            for t in self._transactions.values()
            if t.property_id == property_id
            and t.type in (TransactionType.expense, TransactionType.mortgage)
        ]
        # Annualize recorded expenses then derive monthly average
        annual_expenses = sum(abs(t.amount) for t in expense_txns)
        monthly_expenses = annual_expenses / 12

        annual_noi = (monthly_income - monthly_expenses) * 12
        cap_rate = (annual_noi / prop.current_value * 100) if prop.current_value > 0 else 0.0
        equity = prop.current_value - prop.mortgage_balance
        cash_on_cash = (annual_noi / equity * 100) if equity > 0 else 0.0

        return PropertyFinancialSummary(
            property_id=property_id,
            monthly_income=round(monthly_income, 2),
            monthly_expenses=round(monthly_expenses, 2),
            noi=round(annual_noi, 2),
            cap_rate=round(cap_rate, 2),
            cash_on_cash_return=round(cash_on_cash, 2),
        )

    def portfolio_summary(self) -> PortfolioSummary:
        if not self._properties:
            return PortfolioSummary(
                total_properties=0,
                total_value=0.0,
                total_noi=0.0,
                avg_cap_rate=0.0,
                avg_cash_on_cash_return=0.0,
            )

        analyses = [a for pid in self._properties if (a := self.analyze_property(pid))]
        total_value = sum(p.current_value for p in self._properties.values())
        total_noi = sum(a.noi for a in analyses)
        avg_cap_rate = sum(a.cap_rate for a in analyses) / len(analyses) if analyses else 0.0
        avg_cash_on_cash = (
            sum(a.cash_on_cash_return for a in analyses) / len(analyses) if analyses else 0.0
        )

        return PortfolioSummary(
            total_properties=len(self._properties),
            total_value=round(total_value, 2),
            total_noi=round(total_noi, 2),
            avg_cap_rate=round(avg_cap_rate, 2),
            avg_cash_on_cash_return=round(avg_cash_on_cash, 2),
        )
