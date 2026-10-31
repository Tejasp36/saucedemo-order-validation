import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from pypdf import PdfReader

from utils.price_parser import parse_price
from utils.product import Product

AMOUNT_LINE = re.compile(r"^(?P<label>.+?)\s*\$(?P<amount>[\d,]+(?:\.\d+)?)$")
ITEM_TOTAL_LABEL = "Item total"
TAX_LABEL = "Tax"
TOTAL_LABEL = "Total"
SUMMARY_LABELS = frozenset({ITEM_TOTAL_LABEL, TAX_LABEL, TOTAL_LABEL})


@dataclass()
class Receipt:
    text: str
    items: list[Product]
    item_total: Decimal
    tax: Decimal
    total: Decimal


def read_receipt(pdf_path: Path) -> Receipt:
    text = "\n".join(page.extract_text() for page in PdfReader(pdf_path).pages)

    items: list[Product] = []
    summary: dict[str, Decimal] = {}
    for line in text.splitlines():
        match = AMOUNT_LINE.match(line.strip())
        if match is None:
            continue
        label = match["label"]
        amount = parse_price(match["amount"])
        if label in SUMMARY_LABELS:
            summary[label] = amount
        else:
            items.append(Product(name=label, price=amount))

    missing = SUMMARY_LABELS - summary.keys()
    if missing:
        raise ValueError(f"Receipt {pdf_path.name} is missing amounts: {sorted(missing)}")

    return Receipt(
        text=text,
        items=items,
        item_total=summary[ITEM_TOTAL_LABEL],
        tax=summary[TAX_LABEL],
        total=summary[TOTAL_LABEL],
    )