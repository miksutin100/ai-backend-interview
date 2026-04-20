import os

import httpx
from dotenv import load_dotenv
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

load_dotenv()

BASE_URL = os.environ["PRH_BASE_URL"]

_TRANSIENT = (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError)


@retry(
    retry=retry_if_exception_type(_TRANSIENT),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
async def fetch_company(business_id: str) -> dict:
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
        resp = await client.get(
            f"{BASE_URL}/companies",
            params={"businessId": business_id},
        )
        resp.raise_for_status()
        return resp.json()
