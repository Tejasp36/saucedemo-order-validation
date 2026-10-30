from decimal import Decimal

from selenium.webdriver.common.by import By

from pages.base_page import BasePage,Locator
from utils.price_parser import parse_price
from utils.product import Product
from utils.price_parser import parse_price, to_cents

class CheckoutPage(BasePage):
    FIRST_NAME_INPUT = (By.CSS_SELECTOR, "[data-test='firstName']")
    LAST_NAME_INPUT = (By.CSS_SELECTOR, "[data-test='lastName']")
    POSTAL_CODE_INPUT = (By.CSS_SELECTOR, "[data-test='postalCode']")
    CONTINUE_BUTTON = (By.CSS_SELECTOR, "[data-test='continue']")
    FINISH_BUTTON = (By.CSS_SELECTOR, "[data-test='finish']")
    OVERVIEW_ITEMS = (By.CSS_SELECTOR, "[data-test='inventory-item']")
    ITEM_NAME = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    ITEM_PRICE = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")
    ITEM_TOTAL_LABEL = (By.CSS_SELECTOR, "[data-test='subtotal-label']")
    TAX_LABEL = (By.CSS_SELECTOR, "[data-test='tax-label']")
    TOTAL_LABEL = (By.CSS_SELECTOR, "[data-test='total-label']")

    def fill_information(self, first_name: str, last_name: str, postal_code: str) -> None:
        self.log.info("Fill checkout information")
        self.type_text(self.FIRST_NAME_INPUT, first_name)
        self.type_text(self.LAST_NAME_INPUT, last_name)
        self.type_text(self.POSTAL_CODE_INPUT, postal_code)
        self.click(self.CONTINUE_BUTTON)

    def get_overview_items(self) -> list[Product]:
        self.find(self.FINISH_BUTTON)
        items = [
            Product(
                name=row.find_element(*self.ITEM_NAME).text,
                price=parse_price(row.find_element(*self.ITEM_PRICE).text),
            )
            for row in self.find_all(self.OVERVIEW_ITEMS)
        ]
        self.log.info("Overview contains %d items: %s", len(items), items)
        return items

    def get_item_total(self) -> Decimal:
        return self._read_amount(self.ITEM_TOTAL_LABEL)

    def get_tax(self) -> Decimal:
        return self._read_amount(self.TAX_LABEL)

    def get_total(self) -> Decimal:
        return self._read_amount(self.TOTAL_LABEL)

    def _read_amount(self, locator: Locator) -> Decimal:
        label_text = self.get_text(locator)
        amount = parse_price(label_text)
        rounded = to_cents(amount)
        if amount != rounded:
            self.log.warning("Label %r is not a 2-decimal amount, using %s", label_text, rounded)
        return rounded