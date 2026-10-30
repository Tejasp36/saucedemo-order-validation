from config import config_reader
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


def test_valid_user_can_login(driver):
    login_page = LoginPage(driver)
    login_page.open()
    login_page.login(
        config_reader.get_str("credentials", "username"),
        config_reader.get_str("credentials", "password"),
    )

    assert InventoryPage(driver).is_loaded(), "Inventory page did not load after login"