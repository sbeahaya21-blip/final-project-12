"""
User journey: Upload invoice → view parsed results and risk → submit to ERPNext.
Real integration only: no mocks. Requires backend, frontend, and ERPNext running.
"""
import os
import re
import unittest
from pathlib import Path

from tests.ui.unittest_playwright import PlaywrightTestCase
from tests.ui.pages.react_app_pages import ReactUploadPage, ReactDetailPage


def _project_root():
    return Path(__file__).resolve().parent.parent.parent


class TestUserJourneyUploadViewRiskAndSubmit(PlaywrightTestCase):
    """Upload → results and risk → detail → submit to ERPNext (real backend + ERPNext)."""

    def _sample_pdf_path(self):
        real_pdf = _project_root() / "sample_invoices" / "pdf" / "sample_invoice_1.pdf"
        if not real_pdf.exists():
            self.skipTest("sample_invoices/pdf/sample_invoice_1.pdf not found")
        return str(real_pdf)

    def test_upload_view_risk_and_submit_to_erpnext(self):
        upload_page = ReactUploadPage(self.page, base_url=self.base_url)
        detail_page = ReactDetailPage(self.page, base_url=self.base_url)
        sample_pdf = self._sample_pdf_path()
        page = self.page

        upload_page.navigate()

        upload_page.upload_file(sample_pdf)
        upload_page.wait_for_results()

        upload_page.result_card.wait_for(state="visible", timeout=15000)
        self.assertTrue(upload_page.result_card.is_visible())
        risk_text = upload_page.risk_score_text.text_content() or ""
        self.assertIn("Risk Score", risk_text)
        self.assertTrue(upload_page.vendor_name.is_visible(), "Vendor name should be visible")
        self.assertTrue(upload_page.explanation_box.count() > 0, "Risk explanation should be visible")

        upload_page.view_details_button.click()
        page.wait_for_url(re.compile(r".*/invoices/[^/]+$"), timeout=15000)

        detail_page.wait_for_content()

        def accept_dialogs(dialog):
            dialog.accept()
        page.on("dialog", accept_dialogs)

        submit_btn = detail_page.submit_to_erpnext_button
        submit_btn.wait_for(state="visible", timeout=5000)
        submit_btn.click()

        detail_page.submitted_status.wait_for(state="visible", timeout=15000)
        self.assertTrue(detail_page.submitted_status.is_visible())
        self.assertIn("Submitted to ERPNext", detail_page.submitted_status.text_content() or "")
        detail_page.erpnext_invoice_name.wait_for(state="visible", timeout=5000)
        self.assertTrue(detail_page.explanation_text.count() > 0)
        self.assertTrue((detail_page.explanation_text.text_content() or "").strip() != "")


if __name__ == "__main__":
    unittest.main()
