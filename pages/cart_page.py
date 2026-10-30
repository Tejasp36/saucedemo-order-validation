from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.price_parser import parse_price
from utils.product import Product


class CartPage(BasePage):
    CHECKOUT_BUTTON = (By.CSS_SELECTOR, "[data-test='checkout']")
    CART_ITEMS = (By.CSS_SELECTOR, "[data-test='inventory-item']")
    ITEM_NAME = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    ITEM_PRICE = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")

    def get_items(self) -> list[Product]:
        self.find(self.CHECKOUT_BUTTON)
        items = [
            Product(
                name=row.find_element(*self.ITEM_NAME).text,
                price=parse_price(row.find_element(*self.ITEM_PRICE).text),
            )
            for row in self.find_all(self.CART_ITEMS)
        ]
        self.log.info("Cart contains %d items: %s", len(items), items)
        return items