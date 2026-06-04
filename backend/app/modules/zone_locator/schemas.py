from pydantic import BaseModel, Field


class ZoneLocatorQuery(BaseModel):
    zip_code: str = Field(pattern=r"^\d{5}$")
    radius_miles: float = Field(default=10.0, gt=0, le=100)


class ZoneMetrics(BaseModel):
    zip_code: str
    # Population & growth
    population: int | None = None
    population_growth_pct: float | None = None  # year-over-year %
    # Employment
    jobs_by_radius: int | None = None
    unemployment_rate_pct: float | None = None
    # Rental market
    rental_availability_count: int | None = None
    avg_rental_price: float | None = None
    days_to_rent: float | None = None
    # Sale market
    sale_availability_count: int | None = None
    avg_sale_price: float | None = None
    days_to_sell: float | None = None
    # Metadata
    data_sources: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
