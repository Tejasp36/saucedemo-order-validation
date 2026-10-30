import logging
import os
import shutil
from pathlib import Path

import pytest
from pytest_html import extras
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

from config import config_reader

DOWNLOAD_DIR = Path(__file__).resolve().parent.parent / "downloads"

log = logging.getLogger(__name__)


def _is_headless() -> bool:
    env_value = os.getenv("HEADLESS")
    if env_value is not None:
        return env_value.strip().lower() == "true"
    return config_reader.get_bool("browser", "headless")


@pytest.fixture
def download_dir() -> Path:
    shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)
    DOWNLOAD_DIR.mkdir(parents=True)
    return DOWNLOAD_DIR


@pytest.fixture
def driver(download_dir: Path):
    options = Options()
    options.add_argument("--window-size=1920,1080")
    if _is_headless():
        options.add_argument("--headless=new")
    options.add_experimental_option("prefs", {
        "download.default_directory": str(download_dir),
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    log.info("Starting Chrome (headless=%s)", _is_headless())
    browser: WebDriver = webdriver.Chrome(options=options)
    yield browser
    log.info("Closing Chrome")
    browser.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    browser = item.funcargs.get("driver")
    if report.when == "call" and report.failed and browser is not None:
        screenshot = browser.get_screenshot_as_base64()
        report.extras = getattr(report, "extras", []) + [extras.png(screenshot)]