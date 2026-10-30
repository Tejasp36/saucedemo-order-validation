import re
from decimal import ROUND_HALF_UP, Decimal

PRICE_PATTERN = re.compile(r"\d[\d,]*(?:\.\d+)?")
CENT = Decimal("0.01")


def parse_price(text: str) -> Decimal:
    match = PRICE_PATTERN.search(text)
    if match is None:
        raise ValueError(f"No price found in text: {text!r}")
    return Decimal(match.group().replace(",", ""))


def to_cents(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)