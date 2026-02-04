"""
User journey: Upload invoice → view parsed results and risk → submit to ERPNext.
- With mocks (CI): uses fixture + Playwright route mocks (ERP mocked). No real backend/ERPNext.
- Live (ngrok/local): set BASE_URL and LIVE_ERPNEXT=1; uses real backend and ERPNext.
"""
import json
import os
import re
from pathlib import Path

import pytest

pytest.importorskip("playwright", reason="Playwright not installed")

from playwright.sync_api import expect

from tests.ui.pages.react_app_pages import ReactUploadPage, ReactDetailPage

LIVE_ERPNEXT = (os.environ.get("LIVE_ERPNEXT") or "").strip().lower() in ("1", "true", "yes")


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
    """Real PDF for live mode; fake PDF for mocked mode (CI)."""
    if LIVE_ERPNEXT:
        real_pdf = _project_root() / "sample_invoices" / "pdf" / "sample_invoice_1.pdf"
        if real_pdf.exists():
            return str(real_pdf)
        pytest.skip("LIVE_ERPNEXT=1 but sample_invoices/pdf/sample_invoice_1.pdf not found")
    path = tmp_path / "invoice.pdf"
    path.write_bytes(b"%PDF-1.4 fake")
    return str(path)


def test_user_journey_upload_view_risk_and_submit_to_erpnext(
    upload_page: ReactUploadPage,
    detail_page: ReactDetailPage,
    sample_pdf: str,
):
    """
    Upload → results and risk → detail → submit to ERPNext.
    Mocked (CI): fixture + route mocks. Live: real app when BASE_URL and LIVE_ERPNEXT=1.
    """
    page = upload_page.page
    risk_explanation = "No historical data available for this vendor. First invoice from this vendor."

    upload_page.navigate()

    if not LIVE_ERPNEXT:
        # Mock upload, GET invoice, and submit (skill app + ERP mocked)
        page.route(
            "**/api/invoices/upload*",
            lambda r: r.fulfill(
                status=201,
                content_type="application/json",
                body=json.dumps({
                    "id": "journey-inv-001",
                    "parsed_data": {
                        "vendor_name": "Acme Corp",
                        "invoice_number": "INV-2024-001",
                        "invoice_date": "2024-01-15T10:00:00",
                        "total_amount": 1500.0,
                        "items": [
                            {"name": "Widget A", "quantity": 10.0, "unit_price": 50.0, "total_price": 500.0},
                            {"name": "Widget B", "quantity": 5.0, "unit_price": 200.0, "total_price": 1000.0},
                        ],
                        "currency": "USD",
                    },
                    "uploaded_at": "2024-01-15T10:00:00",
                    "is_suspicious": False,
                    "risk_score": 10,
                    "anomaly_explanation": risk_explanation,
                }),
            ),
        )

        def handle_get(route):
            if route.request.method == "GET" and "submit-to-erpnext" not in route.request.url:
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps({
                        "id": "journey-inv-001",
                        "parsed_data": {"vendor_name": "Acme Corp", "invoice_number": "INV-2024-001", "invoice_date": "2024-01-15T10:00:00", "total_amount": 1500.0, "items": [], "currency": "USD"},
                        "uploaded_at": "2024-01-15T10:00:00",
                        "is_suspicious": False,
                        "risk_score": 10,
                        "anomaly_explanation": risk_explanation,
                        "submitted_to_erpnext": False,
                    }),
                )
            else:
                route.fallback()

        def handle_submit(route):
            if route.request.method == "POST" and "submit-to-erpnext" in route.request.url:
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps({
                        "id": "journey-inv-001",
                        "parsed_data": {"vendor_name": "Acme Corp", "invoice_number": "INV-2024-001", "invoice_date": "2024-01-15T10:00:00", "total_amount": 1500.0, "items": [], "currency": "USD"},
                        "uploaded_at": "2024-01-15T10:00:00",
                        "is_suspicious": False,
                        "risk_score": 10,
                        "anomaly_explanation": risk_explanation,
                        "submitted_to_erpnext": True,
                        "erpnext_invoice_name": "PINV-00001",
                    }),
                )
            else:
                route.fallback()

        page.route("**/api/invoices/**", handle_get)
        page.route("**/submit-to-erpnext**", handle_submit)

    upload_page.upload_file(sample_pdf)
    upload_page.wait_for_results()

    expect(upload_page.result_card).to_be_visible()
    expect(upload_page.risk_score_text).to_contain_text("Risk Score")
    if not LIVE_ERPNEXT:
        expect(upload_page.risk_score_text).to_contain_text("10/100")
        expect(upload_page.vendor_name).to_contain_text("Acme Corp")
        expect(upload_page.explanation_box).to_contain_text(risk_explanation)

    upload_page.view_details_button.click()
    if LIVE_ERPNEXT:
        page.wait_for_url(re.compile(r".*/invoices/[^/]+$"), timeout=15000)
    else:
        page.wait_for_url("**/invoices/journey-inv-001**")

    detail_page.wait_for_content()

    def accept_dialogs(dialog):
        dialog.accept()
    page.on("dialog", accept_dialogs)

    submit_btn = detail_page.submit_to_erpnext_button
    submit_btn.wait_for(state="visible", timeout=5000)
    submit_btn.click()

    expect(detail_page.submitted_status).to_be_visible(timeout=15000)
    expect(detail_page.submitted_status).to_contain_text("Submitted to ERPNext")
    if not LIVE_ERPNEXT:
        expect(detail_page.erpnext_invoice_name).to_contain_text("PINV-00001")
        expect(detail_page.explanation_text).to_contain_text(risk_explanation)
    else:
        expect(detail_page.erpnext_invoice_name).to_be_visible()
        expect(detail_page.explanation_text).to_be_visible()
        expect(detail_page.explanation_text).to_contain_text(re.compile(r"\S"))
