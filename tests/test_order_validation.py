from config import config_reader
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from pages.cart_page import CartPage


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

    inventory_page.open_cart()
    cart_items = CartPage(driver).get_items()
    assert len(cart_items) == 2, "Cart should contain exactly 2 items"
    assert {item.name for item in cart_items} == {highest.name, lowest.name}, \
        "Cart items do not match the selected products"

    cart_total = sum(item.price for item in cart_items)
    expected_total = highest.price + lowest.price
    assert cart_total == expected_total, \
        f"Cart total {cart_total} does not equal highest + lowest price {expected_total}"