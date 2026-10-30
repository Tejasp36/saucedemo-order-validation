import re
from decimal import Decimal

PRICE_PATTERN = re.compile(r"\d[\d,]*(?:\.\d+)?")


def parse_price(text: str) -> Decimal:
    match = PRICE_PATTERN.search(text)
    if match is None:
        raise ValueError(f"No price found in text: {text!r}")
    return Decimal(match.group().replace(",", ""))