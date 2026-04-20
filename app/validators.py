import re

_PATTERN = re.compile(r"^\d{7}-\d$")
_WEIGHTS = [7, 9, 10, 5, 8, 4, 2]


def is_valid_business_id(value: str) -> bool:
    if not _PATTERN.match(value):
        return False

    digits = [int(c) for c in value[:7]]
    remainder = sum(w * d for w, d in zip(_WEIGHTS, digits)) % 11

    if remainder == 1:
        return False

    expected = 0 if remainder == 0 else 11 - remainder
    return expected == int(value[8])
