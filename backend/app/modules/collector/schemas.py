from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PropertyType(str, Enum):
    single_family = "single_family"
    multi_family = "multi_family"
    condo = "condo"
    townhouse = "townhouse"
    commercial = "commercial"


class DataSource(str, Enum):
    zillow = "zillow"
    realtor = "realtor"
    lms = "lms"
    crexy = "crexy"


class CollectionCriteria(BaseModel):
    min_price: float = Field(gt=0)
    max_price: float = Field(gt=0)
    property_types: list[PropertyType] = Field(default_factory=list)
    zip_codes: list[str] = Field(default_factory=list)
    min_sqft: Optional[float] = None
    max_sqft: Optional[float] = None
    min_year_built: Optional[int] = None


class PropertyListing(BaseModel):
    external_id: str
    source: DataSource
    address: str
    city: str
    state: str
    zip_code: str
    price: float
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    sqft: Optional[float] = None
    year_built: Optional[int] = None
    property_type: Optional[PropertyType] = None
    listing_url: Optional[str] = None
    collected_at: datetime = Field(default_factory=datetime.utcnow)


class CollectionRunResult(BaseModel):
    source: DataSource
    properties_found: int
    properties_new: int
    properties_skipped: int
    errors: list[str] = Field(default_factory=list)
