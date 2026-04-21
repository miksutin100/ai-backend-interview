import re

_PATTERN = re.compile(r"^\d{7}-\d$")
_WEIGHTS = [7, 9, 10, 5, 8, 4, 2]


def is_valid_business_id(value: str) -> bool:
    """Validate a Finnish Business ID (Y-tunnus) format and checksum.

    Validates both the format (1234567-8) and the official PRH checksum
    algorithm. See https://www.prh.fi/en/kaupparekisteri/yritystunnusneuvonta.html

    Args:
        value: String to validate, expected format '1234567-8'.

    Returns:
        True if the Business ID is valid, False otherwise.
    """
    if not _PATTERN.match(value):
        return False

    digits = [int(c) for c in value[:7]]

    # Multiply each digit by its weight and sum, then take modulo 11
    remainder = sum(w * d for w, d in zip(_WEIGHTS, digits)) % 11

    # Remainder 1 is explicitly invalid per PRH specification
    if remainder == 1:
        return False
    
    # Remainder 0 → check digit is 0, otherwise check digit is 11 - remainder
    expected = 0 if remainder == 0 else 11 - remainder
    return expected == int(value[8])
