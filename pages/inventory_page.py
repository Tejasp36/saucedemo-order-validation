from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class InventoryPage(BasePage):
    CART_LINK = (By.CSS_SELECTOR, "[data-test='shopping-cart-link']")

    def is_loaded(self) -> bool:
        return self.is_displayed(self.CART_LINK)