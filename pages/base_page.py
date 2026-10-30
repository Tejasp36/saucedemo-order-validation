import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import config_reader

Locator = tuple[str, str]

class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config_reader.get_int("browser", "timeout"))
        self.log = logging.getLogger(type(self).__name__)

    def find(self, locator: Locator) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator: Locator) -> list[WebElement]:
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def click(self, locator: Locator) -> None:
        self.log.info("Click %s", locator[1])
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type_text(self, locator: Locator, text: str) -> None:
        self.log.info("Type into %s", locator[1])
        element = self.find(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: Locator) -> str:
        return self.find(locator).text

    def is_displayed(self, locator: Locator) -> bool:
        try:
            self.find(locator)
            return True
        except TimeoutException:
            return False