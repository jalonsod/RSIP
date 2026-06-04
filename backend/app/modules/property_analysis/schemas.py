from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class PropertyAnalysisQuery(BaseModel):
    zpid: str = Field(min_length=1, description="Zillow property ID")


class PropertyAnalysis(BaseModel):
    zpid: str
    # Property details
    price: Optional[float] = None
    sqft: Optional[float] = None
    beds: Optional[int] = None
    baths: Optional[float] = None
    # Investment metrics
    expected_rent: Optional[float] = None
    price_per_sqft: Optional[float] = None
    # Neighborhood comparison
    neighbor_count: Optional[int] = None
    avg_neighbor_price: Optional[float] = None
    price_vs_neighbors_delta: Optional[float] = None  # positive = above market
    # Metadata
    data_sources: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
