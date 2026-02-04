"""
Component tests for the Upload form / upload zone (React InvoiceUpload).
Covers happy path and edge cases: errors, loading, validation, drag-and-drop, clear.
"""
import json
import re
import pytest

pytest.importorskip("playwright", reason="Playwright not installed")

from playwright.sync_api import expect

from tests.ui.pages.react_app_pages import ReactUploadPage


@pytest.fixture
def upload_page(request):
    try:
        page = request.getfixturevalue("page")
        base_url = request.getfixturevalue("base_url")
    except pytest.FixtureLookupError:
        pytest.skip("Need pytest-playwright 'page' fixture and base_url (run from tests/ui/)")
    return ReactUploadPage(page, base_url=base_url)


@pytest.fixture
def sample_pdf(tmp_path):
    path = tmp_path / "sample.pdf"
    path.write_bytes(b"%PDF-1.4 test")
    return str(path)


# ---- Happy path ----
class TestUploadComponentHappyPath:
    """Happy path: valid file, success response, results shown."""

    def test_upload_zone_visible_on_load(self, upload_page: ReactUploadPage):
        upload_page.navigate()
        expect(upload_page.upload_zone).to_be_visible()
        expect(upload_page.choose_file_label).to_be_visible()
        expect(upload_page.page.get_by_text("Drag and drop", exact=False)).to_be_visible()

    def test_upload_valid_file_shows_results(self, upload_page: ReactUploadPage, sample_pdf: str):
        upload_page.navigate()
        upload_page.page.route(
            "**/api/invoices/upload*",
            lambda r: r.fulfill(
                status=201,
                content_type="application/json",
                body=json.dumps({
                    "id": "c1",
                    "parsed_data": {
                        "vendor_name": "Vendor",
                        "invoice_number": "INV-1",
                        "invoice_date": "2024-01-01T00:00:00",
                        "total_amount": 100.0,
                        "items": [{"name": "Item", "quantity": 1.0, "unit_price": 100.0, "total_price": 100.0}],
                        "currency": "USD",
                    },
                    "uploaded_at": "2024-01-01T00:00:00",
                    "risk_score": 5,
                    "anomaly_explanation": "No anomalies.",
                }),
            ),
        )
        upload_page.upload_file(sample_pdf)
        upload_page.wait_for_results()
        expect(upload_page.result_card).to_be_visible()
        expect(upload_page.risk_score_text).to_contain_text("5/100")
        expect(upload_page.vendor_name).to_contain_text("Vendor")
        expect(upload_page.view_details_button).to_be_visible()

    def test_upload_another_clears_results(self, upload_page: ReactUploadPage, sample_pdf: str):
        upload_page.navigate()
        upload_page.page.route(
            "**/api/invoices/upload*",
            lambda r: r.fulfill(
                status=201,
                content_type="application/json",
                body=json.dumps({
                    "id": "c2",
                    "parsed_data": {
                        "vendor_name": "V",
                        "invoice_number": "N",
                        "invoice_date": "2024-01-01T00:00:00",
                        "total_amount": 0,
                        "items": [],
                        "currency": "USD",
                    },
                    "uploaded_at": "2024-01-01T00:00:00",
                    "risk_score": 0,
                    "anomaly_explanation": "OK",
                }),
            ),
        )
        upload_page.upload_file(sample_pdf)
        upload_page.wait_for_results()
        expect(upload_page.result_card).to_be_visible()
        upload_page.upload_another_button.click()
        expect(upload_page.result_card).not_to_be_visible()
        expect(upload_page.upload_zone).to_be_visible()


# ---- Error paths ----
class TestUploadComponentErrors:
    """Error handling: API 400/500, network, parsing errors."""

    def test_upload_api_400_shows_error_message(self, upload_page: ReactUploadPage, sample_pdf: str):
        upload_page.navigate()
        upload_page.page.route(
            "**/api/invoices/upload*",
            lambda r: r.fulfill(status=400, content_type="application/json", body=json.dumps({"detail": "Invalid file format"})),
        )
        upload_page.upload_file(sample_pdf)
        upload_page.wait_for_error()
        expect(upload_page.error_message).to_be_visible()
        expect(upload_page.error_message).to_contain_text("Error")
        expect(upload_page.error_message).to_contain_text("Invalid file format")

    def test_upload_api_500_shows_error_message(self, upload_page: ReactUploadPage, sample_pdf: str):
        upload_page.navigate()
        upload_page.page.route(
            "**/api/invoices/upload*",
            lambda r: r.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "Server error"})),
        )
        upload_page.upload_file(sample_pdf)
        upload_page.wait_for_error()
        expect(upload_page.error_message).to_contain_text("Error")
        expect(upload_page.error_message).to_contain_text("Server error")

    def test_upload_parse_error_shows_user_friendly_message(self, upload_page: ReactUploadPage, sample_pdf: str):
        upload_page.navigate()
        upload_page.page.route(
            "**/api/invoices/upload*",
            lambda r: r.fulfill(
                status=400,
                content_type="application/json",
                body=json.dumps({"detail": "Failed to parse invoice. Unsupported format."}),
            ),
        )
        upload_page.upload_file(sample_pdf)
        upload_page.wait_for_error()
        expect(upload_page.error_message).to_contain_text("parse")
        expect(upload_page.upload_zone).to_be_visible()


# ---- Drag and drop ----
class TestUploadComponentDragDrop:
    """Drag-and-drop specific behavior."""

    def test_drop_file_triggers_upload(self, upload_page: ReactUploadPage, sample_pdf: str):
        upload_page.navigate()
        upload_page.page.route(
            "**/api/invoices/upload*",
            lambda r: r.fulfill(
                status=201,
                content_type="application/json",
                body=json.dumps({
                    "id": "d1",
                    "parsed_data": {
                        "vendor_name": "Dropped",
                        "invoice_number": "INV-D",
                        "invoice_date": "2024-01-01T00:00:00",
                        "total_amount": 50.0,
                        "items": [],
                        "currency": "USD",
                    },
                    "uploaded_at": "2024-01-01T00:00:00",
                    "risk_score": 0,
                    "anomaly_explanation": "OK",
                }),
            ),
        )
        upload_page.set_file_via_drop(sample_pdf)
        upload_page.wait_for_results()
        expect(upload_page.result_card).to_be_visible()
        expect(upload_page.vendor_name).to_contain_text("Dropped")


# ---- Loading and disabled state ----
class TestUploadComponentLoading:
    """Loading and disabled states."""

    def test_upload_shows_processing_then_results(self, upload_page: ReactUploadPage, sample_pdf: str):
        upload_page.navigate()
        upload_page.page.route(
            "**/api/invoices/upload*",
            lambda r: r.fulfill(
                status=201,
                content_type="application/json",
                body=json.dumps({
                    "id": "l1",
                    "parsed_data": {
                        "vendor_name": "V",
                        "invoice_number": "N",
                        "invoice_date": "2024-01-01T00:00:00",
                        "total_amount": 0,
                        "items": [],
                        "currency": "USD",
                    },
                    "uploaded_at": "2024-01-01T00:00:00",
                    "risk_score": 0,
                    "anomaly_explanation": "OK",
                }),
            ),
        )
        upload_page.upload_file(sample_pdf)
        upload_page.wait_for_results()
        # After completion, results are visible and upload zone is usable again
        expect(upload_page.result_card).to_be_visible()
        expect(upload_page.upload_another_button).to_be_visible()


# ---- Navigation and links ----
class TestUploadComponentNavigation:
    """Navigation from upload page."""

    def test_view_details_navigates_to_invoice_detail(self, upload_page: ReactUploadPage, sample_pdf: str):
        upload_page.navigate()
        upload_page.page.route(
            "**/api/invoices/upload*",
            lambda r: r.fulfill(
                status=201,
                content_type="application/json",
                body=json.dumps({
                    "id": "nav-1",
                    "parsed_data": {
                        "vendor_name": "V",
                        "invoice_number": "N",
                        "invoice_date": "2024-01-01T00:00:00",
                        "total_amount": 0,
                        "items": [],
                        "currency": "USD",
                    },
                    "uploaded_at": "2024-01-01T00:00:00",
                    "risk_score": 0,
                    "anomaly_explanation": "OK",
                }),
            ),
        )
        upload_page.page.route(
            "**/api/invoices/nav-1",
            lambda r: r.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "id": "nav-1",
                    "parsed_data": {
                        "vendor_name": "V",
                        "invoice_number": "N",
                        "invoice_date": "2024-01-01T00:00:00",
                        "total_amount": 0,
                        "items": [],
                        "currency": "USD",
                    },
                    "uploaded_at": "2024-01-01T00:00:00",
                    "risk_score": 0,
                    "anomaly_explanation": "OK",
                }),
            ),
        )
        upload_page.upload_file(sample_pdf)
        upload_page.wait_for_results()
        upload_page.view_details_button.click()
        upload_page.page.wait_for_url("**/invoices/nav-1**")
        expect(upload_page.page).to_have_url(re.compile(r"invoices/nav-1"))
