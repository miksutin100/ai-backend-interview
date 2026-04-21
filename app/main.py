import httpx
from fastapi import FastAPI, HTTPException

from app.client import fetch_company
from app.schemas import CompanyProfile
from app.service import map_company
from app.validators import is_valid_business_id

app = FastAPI()


@app.get("/health")
async def health():
    """Check service liveness.

    Returns:
        dict: A status payload with key ``status`` set to ``"ok"``.
    """
    return {"status": "ok"}


@app.get("/company/{business_id}", response_model=CompanyProfile)
async def get_company(business_id: str):
    """Fetch a Finnish company profile by Business ID (Y-tunnus).

    Validates the format locally before hitting the upstream API to avoid
    unnecessary external calls for malformed inputs.

    Args:
        business_id: Finnish Business ID (Y-tunnus), e.g. "1234567-8"

    Returns:
        CompanyProfile with normalized company data.

    Raises:
        HTTPException 422: If business_id format is invalid.
        HTTPException 502: If upstream API returns an error response.
        HTTPException 503: If upstream service is unreachable or times out.
        HTTPException 404: If no company found with given ID.
    """
    if not is_valid_business_id(business_id):
        raise HTTPException(status_code=422, detail=f"'{business_id}' is not a valid Finnish Business ID")
    try:
        raw = await fetch_company(business_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail="Upstream API error") from exc
    except (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError) as exc:
        raise HTTPException(status_code=503, detail="Upstream service unavailable") from exc

    profile = map_company(raw)

    if profile is None:
        raise HTTPException(status_code=404, detail=f"Company '{business_id}' not found")

    return profile
