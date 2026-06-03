"""Mock LMS (Lead Management System) API for RSIP development."""
import os
from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

app = FastAPI(title="LMS Mock API", version="1.0.0")

API_KEY = os.getenv("LMS_API_KEY", "lms-dev-mock-key-rsip")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return key


class Property(BaseModel):
    id: str
    address: str
    city: str
    state: str
    zip_code: str
    price: float
    bedrooms: int | None = None
    bathrooms: float | None = None
    sqft: float | None = None
    year_built: int | None = None
    property_type: str | None = None
    url: str | None = None


MOCK_PROPERTIES = [
    Property(
        id="lms-001",
        address="123 Oak Street",
        city="Austin",
        state="TX",
        zip_code="78701",
        price=485000,
        bedrooms=3,
        bathrooms=2.0,
        sqft=1850.0,
        year_built=2005,
        property_type="single_family",
        url="http://lms.internal/listings/lms-001",
    ),
    Property(
        id="lms-002",
        address="456 Maple Avenue",
        city="Austin",
        state="TX",
        zip_code="78702",
        price=620000,
        bedrooms=4,
        bathrooms=2.5,
        sqft=2400.0,
        year_built=2012,
        property_type="single_family",
        url="http://lms.internal/listings/lms-002",
    ),
    Property(
        id="lms-003",
        address="789 Pine Road Unit 4",
        city="Austin",
        state="TX",
        zip_code="78703",
        price=320000,
        bedrooms=2,
        bathrooms=1.0,
        sqft=1100.0,
        year_built=1998,
        property_type="condo",
        url="http://lms.internal/listings/lms-003",
    ),
    Property(
        id="lms-004",
        address="321 Cedar Lane",
        city="Austin",
        state="TX",
        zip_code="78704",
        price=890000,
        bedrooms=5,
        bathrooms=3.0,
        sqft=3200.0,
        year_built=2019,
        property_type="multi_family",
        url="http://lms.internal/listings/lms-004",
    ),
    Property(
        id="lms-005",
        address="654 Elm Drive",
        city="Austin",
        state="TX",
        zip_code="78705",
        price=1250000,
        bedrooms=None,
        bathrooms=None,
        sqft=5500.0,
        year_built=2003,
        property_type="commercial",
        url="http://lms.internal/listings/lms-005",
    ),
]


@app.get("/health")
def health():
    return {"status": "ok", "service": "lms-mock"}


@app.get("/properties")
def get_properties(api_key: str = Security(verify_api_key)):
    return {"properties": [p.model_dump() for p in MOCK_PROPERTIES]}
