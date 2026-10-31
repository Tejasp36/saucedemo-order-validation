from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.price_parser import parse_price
from utils.product import Product


class InventoryPage(BasePage):
    CART_LINK = (By.CSS_SELECTOR, "[data-test='shopping-cart-link']")
    CART_BADGE = (By.CSS_SELECTOR, "[data-test='shopping-cart-badge']")
    ITEM_CARDS = (By.CSS_SELECTOR, "[data-test='inventory-item']")
    ITEM_NAME = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    ITEM_PRICE = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")
    ADD_TO_CART_BUTTON = (By.CSS_SELECTOR, "button[data-test^='add-to-cart']")

    def is_loaded(self) -> bool:
        return self.is_displayed(self.CART_LINK)

    def get_products(self) -> list[Product]:
        products = []
        for card in self.find_all(self.ITEM_CARDS):
            name = card.find_element(*self.ITEM_NAME).text
            price_text = card.find_element(*self.ITEM_PRICE).text
            products.append(Product(name=name, price=parse_price(price_text)))
        self.log.info("Found %d products: %s", len(products), products)
        return products

    def add_to_cart(self, product: Product) -> None:
        self.log.info("Add to cart: %s (%s)", product.name, product.price)
        for card in self.find_all(self.ITEM_CARDS):
            if card.find_element(*self.ITEM_NAME).text == product.name:
                card.find_element(*self.ADD_TO_CART_BUTTON).click()
                return
        raise ValueError(f"Product not found on inventory page: {product.name}")

    def get_cart_count(self) -> int:
        return int(self.get_text(self.CART_BADGE))

    def open_cart(self) -> None:
        self.click(self.CART_LINK)