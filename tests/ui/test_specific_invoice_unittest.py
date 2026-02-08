"""
Test a specific invoice detail page. Unittest version.
Usage: BASE_URL=http://localhost:3000 python -m unittest tests.ui.test_specific_invoice_unittest -v
"""
import unittest

from tests.ui.unittest_playwright import PlaywrightTestCase
from tests.ui.pages.react_app_pages import ReactDetailPage

INVOICE_ID = "f0457287-14f0-4055-a401-047c5356fc4e"


class TestSpecificInvoiceDetail(PlaywrightTestCase):
    """Test the specific invoice detail page."""

    def test_specific_invoice_detail(self):
        """Navigate to /invoices/{INVOICE_ID} and verify content loads."""
        detail_page = ReactDetailPage(self.page, base_url=self.base_url)
        page = self.page

        detail_page.navigate(INVOICE_ID)
        detail_page.wait_for_content(timeout=15000)

        page.locator(".invoice-detail").wait_for(state="visible", timeout=5000)
        self.assertTrue(page.locator(".invoice-detail").is_visible())

        explanation = detail_page.explanation_text
        if explanation.count() > 0:
            explanation.first.wait_for(state="visible", timeout=5000)
            self.assertTrue(explanation.first.is_visible())

        risk_score = detail_page.risk_score_display
        if risk_score.count() > 0:
            self.assertTrue(risk_score.first.is_visible())

        submit_btn = detail_page.submit_to_erpnext_button
        if submit_btn.count() > 0:
            self.assertTrue(submit_btn.first.is_visible())
            submitted_status = detail_page.submitted_status
            if submitted_status.count() > 0 and submitted_status.first.is_visible():
                pass  # already submitted
        else:
            submitted_status = detail_page.submitted_status
            if submitted_status.count() > 0 and submitted_status.first.is_visible():
                erpnext_name = detail_page.erpnext_invoice_name
                if erpnext_name.count() > 0:
                    self.assertTrue(erpnext_name.first.is_visible())

    def test_specific_invoice_submit_to_erpnext(self):
        """Test submitting the specific invoice to ERPNext (or verify already submitted)."""
        detail_page = ReactDetailPage(self.page, base_url=self.base_url)
        page = self.page

        detail_page.navigate(INVOICE_ID)
        detail_page.wait_for_content(timeout=15000)

        submitted_status = detail_page.submitted_status
        if submitted_status.count() > 0 and submitted_status.first.is_visible():
            # Already submitted in a previous run: verify and pass
            self.assertIn("Submitted to ERPNext", submitted_status.first.text_content() or "")
            return

        def accept_dialogs(dialog):
            dialog.accept()
        page.on("dialog", accept_dialogs)

        submit_btn = detail_page.submit_to_erpnext_button
        submit_btn.wait_for(state="visible", timeout=5000)
        submit_btn.click()

        detail_page.submitted_status.wait_for(state="visible", timeout=15000)
        self.assertTrue(detail_page.submitted_status.is_visible())
        self.assertIn("Submitted to ERPNext", detail_page.submitted_status.text_content() or "")


if __name__ == "__main__":
    unittest.main()
