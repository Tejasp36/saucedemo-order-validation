# SauceDemo Order Validation

End-to-end UI automation for the [SauceDemo](https://www.saucedemo.com/) purchase flow: log in, find the highest- and lowest-priced products, add them to the cart, check out, confirm the order, then download the PDF receipt and validate its contents.

Built for the Dyad Technologies QA Automation practical assessment (Scenario 1: E-Commerce Order Validation).

## Tech stack

- Python 3.11 or newer (CI runs 3.11)
- Selenium 4 (Selenium Manager downloads the matching ChromeDriver automatically)
- PyTest, with pytest-html for the execution report
- pypdf for reading the downloaded receipt
- Page Object Model, explicit waits only (no `sleep`)

## Prerequisites

- Python 3.11+
- Google Chrome installed
- Git

## Setup

Windows (PowerShell):

```powershell
git clone https://github.com/Tejasp36/saucedemo-order-validation.git
cd saucedemo-order-validation
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS / Linux:

```bash
git clone https://github.com/Tejasp36/saucedemo-order-validation.git
cd saucedemo-order-validation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the tests

Run from the project root:

```bash
pytest
```

Useful variations:

```bash
pytest tests/test_order_validation.py   # only the end-to-end scenario
pytest -k test_order_validation         # one test by name
```

On Windows PowerShell, headless mode for one run:

```powershell
$env:HEADLESS="true"; pytest
```

On macOS / Linux: `HEADLESS=true pytest`.

Always start `pytest` from the project root. Report and log paths are relative to where pytest starts.

## Configuration

All settings are in `config/config.ini`:

| Section | Key | Purpose |
| --- | --- | --- |
| `app` | `base_url` | Site under test |
| `credentials` | `username`, `password` | Public demo login shown on the SauceDemo login page |
| `checkout` | `first_name`, `last_name`, `postal_code` | Dummy checkout data, also asserted in the PDF |
| `checkout` | `tax_rate` | Expected tax rate (0.08), used to compute the expected tax |
| `browser` | `headless` | `false` by default |
| `browser` | `timeout` | Explicit-wait timeout in seconds |

The environment variable `HEADLESS` (`true` or `false`) overrides `browser.headless`. CI uses it.

## Credentials and secrets

The login in `config/config.ini` (`standard_user` / `secret_sauce`) is the public demo account that SauceDemo prints on its own login page, and the assignment asks for the demo site's own test data. These values are not secrets, so I kept them in the config file to keep clone-and-run simple. The checkout data is dummy. No real personal data, card numbers or API keys are committed anywhere in this repository.

On a real project I would not commit credentials:

- Read them from environment variables, or from a git-ignored `.env` file, and commit a `.env.example` that lists only the variable names.
- Store them in GitHub Secrets for CI and pass them to the job as environment variables.
- Keep them out of logs and reports. The password is never logged: page objects log locators and the username only.
- Rotate any secret that reaches git history. Deleting the line is not enough.

## Reports and logs

After a run:

- `reports/report.html`: self-contained HTML report. A failed test includes a browser screenshot.
- `logs/test_run.log`: timestamped log of every step. Also shown live in the console.
- `downloads/`: the receipt PDF downloaded during the run. The folder is emptied at the start of each test.

All three folders are generated and git-ignored.

## Project structure

```
.github/workflows/tests.yml   CI: runs the suite on Python 3.11
config/
  config.ini                  test data and settings
  config_reader.py            typed access to config.ini
pages/                        Page Object Model, one class per page
  base_page.py                explicit-wait helpers shared by all pages
  login_page.py
  inventory_page.py
  cart_page.py
  checkout_page.py
  order_complete_page.py
utils/
  product.py                  Product(name, price) value object
  price_parser.py             text to Decimal, rounding to cents
  pdf_reader.py               parses the receipt PDF into a Receipt object
tests/
  conftest.py                 driver and download fixtures, failure screenshot hook
  test_login.py
  test_order_validation.py    the full scenario
pytest.ini                    pytest, logging and report settings
```

## How the scenario is covered

| Step | What the test does |
| --- | --- |
| 1. Login | Logs in with credentials from config and checks the inventory page loads |
| 2. Fetch prices | Reads name and price from every product card on the inventory page |
| 3. Add products | Picks the highest- and lowest-priced product at runtime and adds each one |
| 4. Verify cart total | Reads the cart page and compares the sum of its prices with highest + lowest |
| 5. Checkout | Fills the form from config and opens the overview page |
| 6. Order completion | Clicks Finish and asserts the confirmation message |
| 7. PDF | Clicks "Generate PDF order", waits for the download, parses the PDF and asserts its contents |

Validation criteria, each a real assertion:

1. Cart total equals highest price plus lowest price. The cart items must also be exactly the two selected products.
2. Order completion message "Thank you for your order!" is shown after checkout. The overview item total, tax and total are also checked.
3. The PDF lists exactly the two selected products with their prices, and its item total, tax and bill amount match the expected values. Ship-to name and postal code are checked too.

No product names, prices or totals are hardcoded. They are read from the page at runtime, and the PDF is compared with values taken from other pages.

## Design notes

- **Page Object Model:** pages hold locators and actions. They never assert. Tests assert.
- **Waiting:** every wait is `WebDriverWait` with an expected condition. The PDF download is awaited by polling the download folder through `WebDriverWait`.
- **Money:** prices are `Decimal`, never `float`. Rounding is half-up to cents, in one helper (`to_cents`).
- **Shared locators across pages:** product rows use the same `data-test` value on the inventory, cart and overview pages. Page methods first wait for an element unique to the target page, so they never read rows from the previous page.
- **Download handling:** Chrome is configured to save PDFs to `downloads/` without a prompt. Partial downloads (`.crdownload`) are ignored because the file pattern ends in `.pdf`.

## Assumptions

- "Cart total" is the sum of item prices shown on the cart page. The cart page has no total line.
- "Bill amount" is verified three ways in the PDF: item total, tax and total.
- Tax is 8%, rounded half-up to cents. The rate is in `config.ini`.
- The overview page shows the item total as `57.980000000000004` (a floating-point display defect on the site). The tests round displayed amounts to cents and log a warning when they do.
- On a price tie for highest or lowest, the first matching product is used.
- Credentials and checkout data are the public demo and dummy values. Nothing sensitive is stored.
- The PDF comes from the site's own "Generate PDF order" button after the order is finished.
- The order date in the PDF is not asserted. It depends on time zone.

## Continuous integration

`.github/workflows/tests.yml` runs the suite headless on every push and pull request, on Python 3.11. The HTML report and logs are uploaded as run artifacts.