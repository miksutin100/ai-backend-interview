import json

from google import genai
from google.genai import types
from google.genai.errors import ServerError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.schemas import ExtractedMetrics

# Reads GEMINI_API_KEY from the environment automatically
_client = genai.Client()

# 5xx responses from Gemini are transient and worth retrying
_TRANSIENT = (ServerError,)

_PROMPT = """\
Extract financial and sustainability metrics from the text below.
Return a single JSON object with exactly these fields (null for any value not explicitly stated):

{{
  "revenue": <float >= 0 or null>,
  "currency": <3-letter uppercase ISO 4217 code or null>,
  "co2_emissions": <float >= 0 or null>,
  "water_usage": <float >= 0 or null>,
  "net_income": <float or null>,
  "year": <integer or null>,
  "company_name": <string or null>
}}

Strict rules:
1. Convert magnitude suffixes to raw floats using these EXACT multipliers — no rounding:
   K = 1000 | M = 1000000 | B or bn = 1000000000 | T = 1000000000000
   Example: "12.5M" → 12500000.0 | "1.2B" → 1200000000.0 | "500K" → 500000.0
2. Only extract values that are explicitly stated in the text. Never infer, estimate, or approximate.
3. Use null — never 0 — for any field not explicitly mentioned.
4. Currency must be exactly 3 uppercase letters. If ambiguous or absent, use null.
5. Return only the JSON object. No markdown, no code fences, no explanation.

Text:
{text}
"""


@retry(
    retry=retry_if_exception_type(_TRANSIENT),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
async def extract_metrics(text: str) -> ExtractedMetrics:
    """Call Gemini to extract structured financial metrics from free-form text.

    Retries up to 3 times with exponential back-off on transient server errors.

    Args:
        text: Unstructured financial text to extract metrics from.

    Returns:
        ExtractedMetrics with validated fields; missing values are None.

    Raises:
        google.genai.errors.ServerError: If Gemini returns a 5xx error after all retries.
        google.genai.errors.ClientError: If the request is malformed or unauthorized.
        json.JSONDecodeError: If Gemini returns malformed JSON.
        pydantic.ValidationError: If extracted data fails schema constraints.
    """
    response = await _client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=_PROMPT.format(text=text),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0,
        ),
    )
    raw = json.loads(response.text)
    return ExtractedMetrics.model_validate(raw)
