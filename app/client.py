import os

import httpx
from dotenv import load_dotenv
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

load_dotenv()

BASE_URL = os.environ["PRH_BASE_URL"]

# Network-level errors worth retrying; excludes HTTP 4xx/5xx (those are handled upstream)
_TRANSIENT = (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError)


@retry(
    retry=retry_if_exception_type(_TRANSIENT),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
async def fetch_company(business_id: str) -> dict:
    """Fetch raw company data from the upstream API.

    Retries up to 3 times with exponential backoff on transient errors.

    Args:
        business_id: Finnish Business ID (Y-tunnus)

    Returns:
        Raw API response as a dict.

    Raises:
        httpx.HTTPStatusError: If upstream returns an error response.
        httpx.ConnectError: If upstream is unreachable.
        httpx.TimeoutException: If upstream times out.
    """
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
        resp = await client.get(
            f"{BASE_URL}/companies",
            params={"businessId": business_id},
        )
        resp.raise_for_status()
        return resp.json()
