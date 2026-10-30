from decimal import ROUND_HALF_UP, Decimal

from config import config_reader
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.price_parser import to_cents


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
    cart_page = CartPage(driver)
    cart_items = cart_page.get_items()
    assert len(cart_items) == 2, "Cart should contain exactly 2 items"
    assert {item.name for item in cart_items} == {highest.name, lowest.name}, \
        "Cart items do not match the selected products"

    cart_total = sum(item.price for item in cart_items)
    expected_total = highest.price + lowest.price
    assert cart_total == expected_total, \
        f"Cart total {cart_total} does not equal highest + lowest price {expected_total}"

    cart_page.proceed_to_checkout()
    checkout_page = CheckoutPage(driver)
    checkout_page.fill_information(
        config_reader.get_str("checkout", "first_name"),
        config_reader.get_str("checkout", "last_name"),
        config_reader.get_str("checkout", "postal_code"),
    )

    overview_items = checkout_page.get_overview_items()
    assert set(overview_items) == set(cart_items), \
        "Overview items do not match the cart items"

    item_total = checkout_page.get_item_total()
    assert item_total == cart_total, \
        f"Overview item total {item_total} does not equal cart total {cart_total}"

    tax_rate = Decimal(config_reader.get_str("checkout", "tax_rate"))
    expected_tax = to_cents(item_total * tax_rate)
    assert checkout_page.get_tax() == expected_tax, \
        f"Tax {checkout_page.get_tax()} does not equal expected {expected_tax}"

    expected_bill = item_total + expected_tax
    assert checkout_page.get_total() == expected_bill, \
        f"Total {checkout_page.get_total()} does not equal expected {expected_bill}"