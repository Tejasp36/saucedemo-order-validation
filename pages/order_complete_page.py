from pathlib import Path

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class OrderCompletePage(BasePage):
    COMPLETE_HEADER = (By.CSS_SELECTOR, "[data-test='complete-header']")
    GENERATE_PDF_BUTTON = (By.CSS_SELECTOR, "[data-test='generate-pdf-order']")
    PDF_FILE_PATTERN = "swag-labs-order-*.pdf"

    def get_confirmation_text(self) -> str:
        return self.get_text(self.COMPLETE_HEADER)

    def download_pdf(self, download_dir: Path) -> Path:
        self.click(self.GENERATE_PDF_BUTTON)
        pdf_path = self.wait.until(
            lambda _: self._find_finished_pdf(download_dir),
            message=f"No {self.PDF_FILE_PATTERN} appeared in {download_dir}",
        )
        self.log.info("PDF downloaded: %s", pdf_path)
        return pdf_path

    def _find_finished_pdf(self, download_dir: Path) -> Path | None:
        for candidate in download_dir.glob(self.PDF_FILE_PATTERN):
            if candidate.stat().st_size > 0:
                return candidate
        return None