from decimal import Decimal


def parse_price(text: str) -> Decimal:
    return Decimal(text.replace("$", "").replace(",", "").strip())