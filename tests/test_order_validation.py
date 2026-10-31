from decimal import Decimal

from config import config_reader
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from pages.order_complete_page import OrderCompletePage
from utils.pdf_reader import read_receipt
from utils.price_parser import to_cents

EXPECTED_CONFIRMATION = "Thank you for your order!"


def test_order_validation(driver, download_dir):
    # Step 1: log in with the demo credentials from config.ini
    login_page = LoginPage(driver)
    login_page.open()
    login_page.login(
        config_reader.get_str("credentials", "username"),
        config_reader.get_str("credentials", "password"),
    )

    inventory_page = InventoryPage(driver)
    assert inventory_page.is_loaded(), "Inventory page did not load after login"

    # Step 2: read every product's name and price, then pick the highest and lowest at runtime. Nothing is hardcoded. On a price tie, the first match wins.
    products = inventory_page.get_products()
    highest = max(products, key=lambda product: product.price)
    lowest = min(products, key=lambda product: product.price)
    assert highest.price > lowest.price, "Highest and lowest price should differ"

    # Step 3: add both products. The cart badge must show 2.
    inventory_page.add_to_cart(highest)
    inventory_page.add_to_cart(lowest)
    assert inventory_page.get_cart_count() == 2, "Cart badge should show 2 items"

    # Step 4 (criterion 1): the cart must hold exactly the two selected products, and the sum of its prices must equal highest + lowest from the inventory page.
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

    # Step 5: fill the checkout form with dummy data from config.ini
    cart_page.proceed_to_checkout()
    checkout_page = CheckoutPage(driver)
    checkout_page.fill_information(
        config_reader.get_str("checkout", "first_name"),
        config_reader.get_str("checkout", "last_name"),
        config_reader.get_str("checkout", "postal_code"),
    )

    # The overview page must show the same items and item total as the cart.
    overview_items = checkout_page.get_overview_items()
    assert set(overview_items) == set(cart_items), \
        "Overview items do not match the cart items"

    item_total = checkout_page.get_item_total()
    assert item_total == cart_total, \
        f"Overview item total {item_total} does not equal cart total {cart_total}"

    # Tax and total are computed from the item total and the tax rate in config.ini, then compared with what the page shows.
    tax_rate = Decimal(config_reader.get_str("checkout", "tax_rate"))
    expected_tax = to_cents(item_total * tax_rate)
    assert checkout_page.get_tax() == expected_tax, \
        f"Tax {checkout_page.get_tax()} does not equal expected {expected_tax}"

    expected_bill = item_total + expected_tax
    assert checkout_page.get_total() == expected_bill, \
        f"Total {checkout_page.get_total()} does not equal expected {expected_bill}"


     # Step 6 (criterion 2): finish the order and check the confirmation message
    checkout_page.finish_order()
    order_complete_page = OrderCompletePage(driver)
    assert order_complete_page.get_confirmation_text() == EXPECTED_CONFIRMATION, \
        "Order completion message not shown after checkout"

    # Step 7 (criterion 3): download the PDF receipt and parse it
    pdf_path = order_complete_page.download_pdf(download_dir)
    assert pdf_path.suffix == ".pdf", f"Downloaded file is not a PDF: {pdf_path.name}"

     # The PDF is checked against values taken from earlier pages, not from the PDF itself.
    receipt = read_receipt(pdf_path)
    assert set(receipt.items) == {highest, lowest}, \
        f"PDF items {receipt.items} do not match selected products {[highest, lowest]}"
    assert receipt.item_total == item_total, \
        f"PDF item total {receipt.item_total} does not equal {item_total}"
    assert receipt.tax == expected_tax, \
        f"PDF tax {receipt.tax} does not equal {expected_tax}"
    assert receipt.total == expected_bill, \
        f"PDF bill amount {receipt.total} does not equal {expected_bill}"

    # Ship-to details in the PDF must match what was typed into the checkout form
    ship_to_name = (
        f"{config_reader.get_str('checkout', 'first_name')} "
        f"{config_reader.get_str('checkout', 'last_name')}"
    )
    assert ship_to_name in receipt.text, f"Ship-to name {ship_to_name!r} not found in PDF"
    assert config_reader.get_str("checkout", "postal_code") in receipt.text, \
    "Ship-to postal code not found in PDF"