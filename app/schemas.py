from typing import Optional
from pydantic import BaseModel


class CompanyProfile(BaseModel):
    business_id: str
    name: Optional[str] = None
    registration_date: Optional[str] = None
    company_form: Optional[str] = None
    website: Optional[str] = None
    city: Optional[str] = None
    last_modified: Optional[str] = None
