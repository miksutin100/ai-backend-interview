from typing import Optional
from app.schemas import CompanyProfile

LANG = ("1", "3", "2")  # fi=1, en=3, sv=2; priority: fi → en → sv


def _by_language(items: list, value_key: str) -> Optional[str]:
    """Return the value for the highest-priority language from a list of localised items.

    Iterates through items in Finnish, English, Swedish priority order
    and returns the first non-empty value found.

    Args:
        items: List of dicts, each expected to have 'languageCode' and the given value_key.
        value_key: The dict key whose value should be returned, e.g. 'description' or 'city'.

    Returns:
        The value for the highest-priority language, or None if no match found.
    """
    indexed = {item.get("languageCode"): item.get(value_key) for item in items or []}
    for code in LANG:
        if indexed.get(code):
            return indexed[code]
    return None


def map_company(raw: dict) -> Optional[CompanyProfile]:
    """Map a raw PRH API response to a CompanyProfile.

    Extracts the first company from the response and picks the current
    official name, earliest Trade Register entry, and localised fields
    using Finnish → English → Swedish priority.

    Args:
        raw: Raw response dict from the PRH API.

    Returns:
        CompanyProfile with normalised company data,
        or None if the response contains no companies.
    """
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
