from typing import Optional
from pydantic import BaseModel, Field


class CompanyProfile(BaseModel):
    business_id: str
    name: Optional[str] = None
    registration_date: Optional[str] = None
    company_form: Optional[str] = None
    website: Optional[str] = None
    city: Optional[str] = None
    last_modified: Optional[str] = None


class ExtractRequest(BaseModel):
    text: str


class ExtractedMetrics(BaseModel):
    revenue: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, pattern=r"^[A-Z]{3}$")
    co2_emissions: Optional[float] = Field(None, ge=0)
    water_usage: Optional[float] = Field(None, ge=0)
    net_income: Optional[float] = None
    year: Optional[int] = None
    company_name: Optional[str] = None
