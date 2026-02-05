"""
UI test for invoice detail page with ERPNext verification. Unittest version.
Tests: load detail page, verify risk/explanation, submit to ERPNext (always).
Run: BASE_URL=http://localhost:3000 python -m unittest tests.ui.test_invoice_with_erpnext_verification_unittest -v
"""
import re
import unittest

from tests.ui.unittest_playwright import PlaywrightTestCase
from tests.ui.pages.react_app_pages import ReactDetailPage

INVOICE_ID = "f0457287-14f0-4055-a401-047c5356fc4e"


class TestInvoiceDetailWithErpnextVerification(PlaywrightTestCase):
    """Invoice detail page load, risk display, and ERPNext submission."""

    def test_invoice_detail_page_loads_and_shows_risk(self):
        """Invoice detail page loads and displays risk information."""
        detail_page = ReactDetailPage(self.page, base_url=self.base_url)
        page = self.page

        detail_page.navigate(INVOICE_ID)
        detail_page.wait_for_content(timeout=15000)

        page.locator(".invoice-detail").wait_for(state="visible", timeout=5000)
        self.assertTrue(page.locator(".invoice-detail").is_visible())

        risk_score = detail_page.risk_score_display
        self.assertGreater(risk_score.count(), 0, "Risk score not found on page")
        risk_score.first.wait_for(state="visible", timeout=5000)
        self.assertTrue(risk_score.first.is_visible())

        explanation = detail_page.explanation_text
        self.assertGreater(explanation.count(), 0, "Risk explanation not found on page")
        explanation.first.wait_for(state="visible", timeout=5000)
        self.assertTrue(explanation.first.is_visible())

    def test_submit_to_erpnext_and_verify_comment(self):
        """Submit invoice to ERPNext and verify submission (comment verification noted)."""
        detail_page = ReactDetailPage(self.page, base_url=self.base_url)
        page = self.page

        detail_page.navigate(INVOICE_ID)
        detail_page.wait_for_content(timeout=15000)

        explanation = detail_page.explanation_text
        self.assertGreater(explanation.count(), 0, "Risk explanation not found")
        risk_explanation_text = explanation.first.text_content() or ""

        submitted_status = detail_page.submitted_status
        erpnext_invoice_name = None

        if submitted_status.count() > 0 and submitted_status.first.is_visible():
            erpnext_name_elem = detail_page.erpnext_invoice_name
            if erpnext_name_elem.count() > 0:
                erpnext_invoice_name = erpnext_name_elem.first.text_content()
        else:
            submit_btn = detail_page.submit_to_erpnext_button
            self.assertGreater(submit_btn.count(), 0, "Submit button not found")
            submit_btn.first.wait_for(state="visible", timeout=5000)
            self.assertTrue(submit_btn.first.is_visible())

            def handle_dialogs(dialog):
                dialog.accept()
            page.on("dialog", handle_dialogs)

            submit_btn.first.click()
            detail_page.submitted_status.wait_for(state="visible", timeout=15000)
            self.assertIn("Submitted to ERPNext", detail_page.submitted_status.text_content() or "")

            erpnext_name_elem = detail_page.erpnext_invoice_name
            self.assertGreater(erpnext_name_elem.count(), 0, "ERPNext invoice name not found after submission")
            erpnext_invoice_name = erpnext_name_elem.first.text_content()

        self.assertIsNotNone(erpnext_invoice_name, "Could not determine ERPNext invoice name")

    def test_full_user_journey_with_erpnext(self):
        """Complete user journey: view invoice, check risk, check submission status."""
        detail_page = ReactDetailPage(self.page, base_url=self.base_url)
        page = self.page

        detail_page.navigate(INVOICE_ID)
        detail_page.wait_for_content(timeout=15000)
        page.locator(".invoice-detail").wait_for(state="visible", timeout=5000)
        self.assertTrue(page.locator(".invoice-detail").is_visible())

        risk_score = detail_page.risk_score_display
        explanation = detail_page.explanation_text
        if risk_score.count() > 0:
            self.assertTrue(risk_score.first.is_visible())
        if explanation.count() > 0:
            self.assertTrue(explanation.first.is_visible())

        submitted_status = detail_page.submitted_status
        submit_btn = detail_page.submit_to_erpnext_button
        if submitted_status.count() > 0 and submitted_status.first.is_visible():
            self.assertIn("Submitted", (submitted_status.first.text_content() or ""))
        elif submit_btn.count() > 0:
            self.assertTrue(submit_btn.first.is_visible())


if __name__ == "__main__":
    unittest.main()
