"""Page objects for the React Invoice Parser UI (Upload, List, Detail)."""
import re
from playwright.sync_api import Page, expect


class ReactUploadPage:
    """Upload page - React InvoiceUpload component."""

    def __init__(self, page: Page, base_url: str = "http://localhost:8000"):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def navigate(self):
        self.page.goto(f"{self.base_url}/", wait_until="load")
        expect(self.page.locator(".invoice-upload")).to_be_visible(timeout=15000)

    @property
    def upload_zone(self):
        return self.page.locator(".upload-zone")

    @property
    def file_input(self):
        return self.page.locator("#file-input")

    @property
    def choose_file_label(self):
        return self.page.get_by_text("Choose File", exact=True)

    def upload_file(self, file_path: str):
        self.file_input.set_input_files(file_path)

    def set_file_via_drop(self, file_path: str):
        with open(file_path, "rb") as f:
            data = f.read()
        self.page.evaluate(
            """([content, name]) => {
                const dt = new DataTransfer();
                const file = new File([new Uint8Array(content)], name, { type: 'application/pdf' });
                dt.items.add(file);
                const zone = document.querySelector('.upload-zone');
                zone.dispatchEvent(new DragEvent('drop', { dataTransfer: dt, bubbles: true }));
            }""",
            [list(data), file_path.replace("\\", "/").split("/")[-1]],
        )

    def wait_for_results(self, timeout: int = 15000):
        self.page.locator(".analysis-results .result-card").wait_for(state="visible", timeout=timeout)

    def wait_for_error(self, timeout: int = 10000):
        """Upload-area error only (scoped to avoid multiple matches in fixture)."""
        self.page.locator(".invoice-upload .error-message").wait_for(state="visible", timeout=timeout)

    @property
    def result_card(self):
        return self.page.locator(".analysis-results .result-card")

    @property
    def risk_badge(self):
        return self.page.locator(".risk-badge")

    @property
    def risk_score_text(self):
        return self.page.locator(".risk-score")

    @property
    def explanation_box(self):
        """Explanation on upload results (scoped for fixture with multiple .explanation-box)."""
        return self.page.locator(".analysis-results .explanation-box p")

    @property
    def vendor_name(self):
        return self.page.locator(".detail-item .detail-value").first

    @property
    def view_details_button(self):
        return self.page.get_by_role("button", name="View Details")

    @property
    def upload_another_button(self):
        return self.page.get_by_role("button", name="Upload Another")

    @property
    def error_message(self):
        """Upload-area error only (scoped for fixture with multiple .error-message)."""
        return self.page.locator(".invoice-upload .error-message")

    @property
    def anomalies_list(self):
        return self.page.locator(".anomaly-item")


class ReactDetailPage:
    """Invoice detail page - React InvoiceDetail component."""

    def __init__(self, page: Page, base_url: str = "http://localhost:8000"):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def navigate(self, invoice_id: str):
        self.page.goto(f"{self.base_url}/invoices/{invoice_id}", wait_until="load")

    def wait_for_content(self, timeout: int = 10000):
        self.page.locator(".invoice-detail .invoice-card").wait_for(state="visible", timeout=timeout)

    @property
    def submit_to_erpnext_button(self):
        """Match button with emoji or plain text (e.g. '📤 Submit to ERPNext')."""
        return self.page.get_by_role("button", name=re.compile(r"Submit to ERPNext"))

    @property
    def submitted_status(self):
        return self.page.locator(".submitted-status")

    @property
    def erpnext_invoice_name(self):
        return self.page.locator(".erpnext-name")

    @property
    def explanation_text(self):
        """Explanation on detail page (scoped to .invoice-detail for fixture)."""
        return self.page.locator(".invoice-detail .explanation-box p")

    @property
    def risk_score_display(self):
        return self.page.locator(".risk-badge-large, .analysis-header .risk-badge-large")

    @property
    def back_to_list(self):
        return self.page.get_by_role("button", name="Back to List")

    @property
    def detail_error_message(self):
        return self.page.locator(".invoice-detail .error-message")


class ReactListPage:
    """All Invoices list page."""

    def __init__(self, page: Page, base_url: str = "http://localhost:8000"):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def navigate(self):
        self.page.goto(f"{self.base_url}/invoices")
        self.page.wait_for_load_state("networkidle")

    @property
    def invoice_links(self):
        return self.page.locator("a[href^='/invoices/']")

    @property
    def loading(self):
        return self.page.locator(".loading-container, .loading")
