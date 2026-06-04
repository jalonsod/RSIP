from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ZoneLocatorQuery(BaseModel):
    zip_code: str = Field(pattern=r"^\d{5}$")
    radius_miles: float = Field(default=10.0, gt=0, le=100)


class ZoneMetrics(BaseModel):
    zip_code: str
    # Population & growth
    population: Optional[int] = None
    population_growth_pct: Optional[float] = None  # year-over-year %
    # Employment
    jobs_by_radius: Optional[int] = None
    unemployment_rate_pct: Optional[float] = None
    # Rental market
    rental_availability_count: Optional[int] = None
    avg_rental_price: Optional[float] = None
    days_to_rent: Optional[float] = None
    # Sale market
    sale_availability_count: Optional[int] = None
    avg_sale_price: Optional[float] = None
    days_to_sell: Optional[float] = None
    # Metadata
    data_sources: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
