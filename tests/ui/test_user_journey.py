"""
Live UI test: Upload invoice → view parsed results and risk → submit to ERPNext.
Requires BASE_URL (e.g. ngrok URL or http://localhost:3000) and real backend + ERPNext.
Run via GitHub Actions (ngrok) or locally with run_real_ui_test.bat.
"""
import os
import re
from pathlib import Path

import pytest

pytest.importorskip("playwright", reason="Playwright not installed")

from playwright.sync_api import expect

from tests.ui.pages.react_app_pages import ReactUploadPage, ReactDetailPage


def _project_root():
    return Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def upload_page(request):
    try:
        page = request.getfixturevalue("page")
        base_url = request.getfixturevalue("base_url")
    except pytest.FixtureLookupError:
        pytest.skip("Need pytest-playwright 'page' fixture and base_url")
    return ReactUploadPage(page, base_url=base_url)


@pytest.fixture
def detail_page(request):
    try:
        page = request.getfixturevalue("page")
        base_url = request.getfixturevalue("base_url")
    except pytest.FixtureLookupError:
        pytest.skip("Need pytest-playwright 'page' fixture and base_url")
    return ReactDetailPage(page, base_url=base_url)


@pytest.fixture
def sample_pdf(tmp_path):
    """Use a real parsable PDF so the backend can process it."""
    real_pdf = _project_root() / "sample_invoices" / "pdf" / "sample_invoice_1.pdf"
    if real_pdf.exists():
        return str(real_pdf)
    pytest.skip("sample_invoices/pdf/sample_invoice_1.pdf not found")


def test_user_journey_upload_view_risk_and_submit_to_erpnext(
    upload_page: ReactUploadPage,
    detail_page: ReactDetailPage,
    sample_pdf: str,
):
    """
    User journey: Upload invoice → see parsed results and risk → open detail →
    submit to ERPNext → verify success and risk explanation. Uses real backend and ERPNext.
    """
    page = upload_page.page

    upload_page.navigate()
    upload_page.upload_file(sample_pdf)
    upload_page.wait_for_results()

    expect(upload_page.result_card).to_be_visible()
    expect(upload_page.risk_score_text).to_contain_text("Risk Score")

    upload_page.view_details_button.click()
    page.wait_for_url(re.compile(r".*/invoices/[^/]+$"), timeout=15000)
    detail_page.wait_for_content()

    def accept_dialogs(dialog):
        dialog.accept()
    page.on("dialog", accept_dialogs)

    submit_btn = detail_page.submit_to_erpnext_button
    submit_btn.wait_for(state="visible", timeout=5000)
    submit_btn.click()

    expect(detail_page.submitted_status).to_be_visible(timeout=15000)
    expect(detail_page.submitted_status).to_contain_text("Submitted to ERPNext")
    expect(detail_page.erpnext_invoice_name).to_be_visible()
    expect(detail_page.explanation_text).to_be_visible()
    expect(detail_page.explanation_text).to_contain_text(re.compile(r"\S"))
