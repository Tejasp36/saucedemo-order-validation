from selenium.webdriver.common.by import By

from config import config_reader
from pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME_INPUT = (By.CSS_SELECTOR, "[data-test='username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "[data-test='password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "[data-test='login-button']")

    def open(self) -> None:
        self.log.info("Open login page")
        self.driver.get(config_reader.get_str("app", "base_url"))

    def login(self, username: str, password: str) -> None:
        self.log.info("Login as %s", username)
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)