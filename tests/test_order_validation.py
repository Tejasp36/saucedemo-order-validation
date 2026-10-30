from config import config_reader
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


def test_order_validation(driver):
    login_page = LoginPage(driver)
    login_page.open()
    login_page.login(
        config_reader.get_str("credentials", "username"),
        config_reader.get_str("credentials", "password"),
    )

    inventory_page = InventoryPage(driver)
    assert inventory_page.is_loaded(), "Inventory page did not load after login"

    products = inventory_page.get_products()
    highest = max(products, key=lambda product: product.price)
    lowest = min(products, key=lambda product: product.price)
    assert highest.price > lowest.price, "Highest and lowest price should differ"

    inventory_page.add_to_cart(highest)
    inventory_page.add_to_cart(lowest)
    assert inventory_page.get_cart_count() == 2, "Cart badge should show 2 items"