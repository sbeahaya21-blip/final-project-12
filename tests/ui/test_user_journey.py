"""
User journey (E2E) test: Upload invoice → view parsed results and risk → submit to ERPNext
and verify the comment/explanation that would be sent to ERPNext is correct.

By default the test mocks all API calls (no real backend/ERPNext).
Set LIVE_ERPNEXT=1 and BASE_URL to your app (e.g. http://localhost:3000) to run against
the real backend and ERPNext so the invoice appears in ERPNext (no mocks).
"""
import json
import os
import re
from pathlib import Path

import pytest

pytest.importorskip("playwright", reason="Playwright not installed")

from playwright.sync_api import Page, expect

from tests.ui.pages.react_app_pages import ReactUploadPage, ReactDetailPage

# Live mode: no mocks, real backend + ERPNext (invoice will appear in ERPNext)
LIVE_ERPNEXT = (os.environ.get("LIVE_ERPNEXT") or "").strip().lower() in ("1", "true", "yes")


def _project_root():
    return Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def upload_page(request):
    try:
        page = request.getfixturevalue("page")
        base_url = request.getfixturevalue("base_url")
    except pytest.FixtureLookupError:
        pytest.skip("Need pytest-playwright 'page' fixture and base_url (run from tests/ui/)")
    return ReactUploadPage(page, base_url=base_url)


@pytest.fixture
def detail_page(request):
    try:
        page = request.getfixturevalue("page")
        base_url = request.getfixturevalue("base_url")
    except pytest.FixtureLookupError:
        pytest.skip("Need pytest-playwright 'page' fixture and base_url (run from tests/ui/)")
    return ReactDetailPage(page, base_url=base_url)


@pytest.fixture
def sample_pdf(tmp_path):
    """Use a real parsable PDF in live mode so the backend can process it."""
    if LIVE_ERPNEXT:
        real_pdf = _project_root() / "sample_invoices" / "pdf" / "sample_invoice_1.pdf"
        if real_pdf.exists():
            return str(real_pdf)
        pytest.skip("LIVE_ERPNEXT=1 but sample_invoices/pdf/sample_invoice_1.pdf not found")
    path = tmp_path / "invoice.pdf"
    path.write_bytes(b"%PDF-1.4 fake content for test")
    return str(path)


def test_user_journey_upload_view_risk_and_submit_to_erpnext(
    upload_page: ReactUploadPage,
    detail_page: ReactDetailPage,
    sample_pdf: str,
):
    """
    User journey: Upload invoice → see parsed results and risk score → open detail →
    submit to ERPNext → verify success and that the risk explanation (comment for ERPNext) exists and is correct.
    With LIVE_ERPNEXT=1 no mocks are used; the invoice is really sent to ERPNext.
    """
    page = upload_page.page
    risk_explanation_sent_to_erpnext = (
        "No historical data available for this vendor. First invoice from this vendor."
    )

    upload_page.navigate()

    if not LIVE_ERPNEXT:
        # Mock: upload returns invoice with analysis
        page.route(
            "**/api/invoices/upload*",
            lambda route: route.fulfill(
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
                    "anomaly_explanation": risk_explanation_sent_to_erpnext,
                }),
            ),
        )

        def handle_get_invoice(route):
            if route.request.method == "GET" and "submit-to-erpnext" not in route.request.url:
                route.fulfill(
                    status=200,
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
                        "anomaly_explanation": risk_explanation_sent_to_erpnext,
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
                        "anomaly_explanation": risk_explanation_sent_to_erpnext,
                        "submitted_to_erpnext": True,
                        "erpnext_invoice_name": "PINV-00001",
                    }),
                )
            else:
                route.fallback()

        page.route("**/api/invoices/**", handle_get_invoice)
        page.route("**/submit-to-erpnext**", handle_submit)

    # User uploads file (real backend in live mode, mocked otherwise)
    upload_page.upload_file(sample_pdf)
    upload_page.wait_for_results()

    # Verify parsed results and risk are visible
    expect(upload_page.result_card).to_be_visible()
    expect(upload_page.risk_score_text).to_contain_text("Risk Score")
    if not LIVE_ERPNEXT:
        expect(upload_page.risk_score_text).to_contain_text("10/100")
        expect(upload_page.vendor_name).to_contain_text("Acme Corp")
        expect(upload_page.explanation_box).to_contain_text(risk_explanation_sent_to_erpnext)

    # User clicks "View Details"
    upload_page.view_details_button.click()
    if LIVE_ERPNEXT:
        page.wait_for_url(re.compile(r".*/invoices/[^/]+$"), timeout=15000)
    else:
        page.wait_for_url("**/invoices/journey-inv-001**")

    detail_page.wait_for_content()

    # Accept confirm ("Are you sure...") and success alert when we click Submit
    def accept_dialogs(dialog):
        dialog.accept()
    page.on("dialog", accept_dialogs)

    submit_btn = detail_page.submit_to_erpnext_button
    submit_btn.wait_for(state="visible", timeout=5000)
    submit_btn.click()

    # Wait for success: UI shows "Submitted to ERPNext" (and in live mode, real ERPNext doc name)
    expect(detail_page.submitted_status).to_be_visible(timeout=15000)
    expect(detail_page.submitted_status).to_contain_text("Submitted to ERPNext")
    if not LIVE_ERPNEXT:
        expect(detail_page.erpnext_invoice_name).to_contain_text("PINV-00001")
        expect(detail_page.explanation_text).to_contain_text(risk_explanation_sent_to_erpnext)
    else:
        # Live: ERPNext doc name and that the risk explanation (comment sent to ERPNext) exists and has content
        expect(detail_page.erpnext_invoice_name).to_be_visible()
        expect(detail_page.explanation_text).to_be_visible()
        expect(detail_page.explanation_text).to_contain_text(re.compile(r"\S"))  # at least one non-whitespace
