from typing import Optional
from app.schemas import CompanyProfile

LANG = ("1", "3", "2")  # fi → en → sv


def _by_language(items: list, value_key: str) -> Optional[str]:
    indexed = {item.get("languageCode"): item.get(value_key) for item in items or []}
    for code in LANG:
        if indexed.get(code):
            return indexed[code]
    return None


def map_company(raw: dict) -> Optional[CompanyProfile]:
    companies = raw.get("companies") or []
    if not companies:
        return None

    c = companies[0]

    business_id = (c.get("businessId") or {}).get("value", "")

    # Current official name: type "1", no endDate
    name = None
    for n in c.get("names") or []:
        if n.get("type") == "1" and not n.get("endDate"):
            name = n.get("name")
            break

    # Earliest Trade Register entry (register "1")
    registration_date = None
    for entry in c.get("registeredEntries") or []:
        if entry.get("register") == "1":
            registration_date = entry.get("registrationDate")
            break

    # Company form: fi → en → sv
    company_form = None
    forms = c.get("companyForms") or []
    if forms:
        company_form = _by_language(forms[0].get("descriptions") or [], "description")

    # City: fi → en → sv, from first address
    city = None
    for addr in c.get("addresses") or []:
        city = _by_language(addr.get("postOffices") or [], "city")
        if city:
            break

    return CompanyProfile(
        business_id=business_id,
        name=name,
        registration_date=registration_date,
        company_form=company_form,
        website=None,
        city=city,
        last_modified=c.get("lastModified"),
    )
