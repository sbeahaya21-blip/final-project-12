"""UI tests for Invoice Upload page using Playwright."""
import pytest
from playwright.sync_api import Page, expect
from tests.ui.pages.invoice_page import InvoicePage
import json
import os
from pathlib import Path


@pytest.fixture
def invoice_page(page: Page):
    """Create an InvoicePage instance."""
    return InvoicePage(page)


@pytest.fixture
def sample_invoice_file(tmp_path):
    """Create a sample invoice file for testing."""
    file_path = tmp_path / "test_invoice.pdf"
    file_path.write_bytes(b"fake pdf content")
    return str(file_path)


@pytest.fixture(scope="session")
def test_server():
    """Start test server (if needed)."""
    # In a real scenario, you might want to start the server here
    # For now, we assume the server is running
    yield
    # Cleanup if needed


class TestInvoiceUploadUI:
    """UI tests for invoice upload functionality."""
    
    def test_page_loads(self, invoice_page: InvoicePage):
        """Test that the page loads correctly."""
        invoice_page.navigate()
        expect(invoice_page.page.locator("h1")).to_contain_text("Invoice Parser")
        expect(invoice_page.upload_section).to_be_visible()
        expect(invoice_page.upload_button).to_be_visible()
    
    def test_file_selection_updates_filename(self, invoice_page: InvoicePage, sample_invoice_file):
        """Test that selecting a file updates the filename display."""
        invoice_page.navigate()
        invoice_page.upload_file(sample_invoice_file)
        
        # Wait a bit for the file name to update
        invoice_page.page.wait_for_timeout(100)
        expect(invoice_page.file_name).to_contain_text("test_invoice.pdf")
    
    @pytest.mark.skip(reason="Requires actual server running with mocked responses")
    def test_upload_and_analyze_invoice(self, invoice_page: InvoicePage, sample_invoice_file):
        """Test complete upload and analysis flow."""
        invoice_page.navigate()
        
        # Mock the API responses
        # In a real test, you'd use a test server or mock the API
        invoice_page.page.route("**/api/invoices/upload", lambda route: route.fulfill(
            status=201,
            content_type="application/json",
            body=json.dumps({
                "id": "test-invoice-id",
                "parsed_data": {
                    "vendor_name": "Test Vendor",
                    "invoice_number": "INV-001",
                    "invoice_date": "2024-01-15T10:00:00",
                    "total_amount": 1000.0,
                    "items": [
                        {
                            "name": "Product A",
                            "quantity": 10.0,
                            "unit_price": 50.0,
                            "total_price": 500.0
                        }
                    ],
                    "currency": "USD"
                },
                "uploaded_at": "2024-01-15T10:00:00"
            })
        ))
        
        invoice_page.page.route("**/api/invoices/test-invoice-id/analyze", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "is_suspicious": False,
                "risk_score": 10,
                "anomalies": [],
                "explanation": "No anomalies detected. Invoice appears normal."
            })
        ))
        
        invoice_page.upload_file(sample_invoice_file)
        invoice_page.wait_for_processing()
        
        # Verify results are displayed
        expect(invoice_page.results.locator(".invoice-card")).to_be_visible()
        expect(invoice_page.results.locator(".risk-score")).to_contain_text("Risk Score")
    
    def test_drag_and_drop_upload(self, invoice_page: InvoicePage, sample_invoice_file):
        """Test drag and drop file upload."""
        invoice_page.navigate()
        
        # Mock API responses
        invoice_page.page.route("**/api/invoices/upload", lambda route: route.fulfill(
            status=201,
            content_type="application/json",
            body=json.dumps({
                "id": "test-id",
                "parsed_data": {
                    "vendor_name": "Test",
                    "invoice_number": "INV-001",
                    "invoice_date": "2024-01-15T10:00:00",
                    "total_amount": 100.0,
                    "items": [],
                    "currency": "USD"
                }
            })
        ))
        
        invoice_page.page.route("**/api/invoices/test-id/analyze", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "is_suspicious": False,
                "risk_score": 0,
                "anomalies": [],
                "explanation": "No anomalies"
            })
        ))
        
        invoice_page.upload_file_via_drag_drop(sample_invoice_file)
        invoice_page.wait_for_processing()
        
        expect(invoice_page.results.locator(".invoice-card, .error")).to_be_visible()
    
    def test_error_handling(self, invoice_page: InvoicePage, sample_invoice_file):
        """Test error handling when upload fails."""
        invoice_page.navigate()
        
        # Mock error response
        invoice_page.page.route("**/api/invoices/upload", lambda route: route.fulfill(
            status=400,
            content_type="application/json",
            body=json.dumps({
                "detail": "Failed to parse invoice"
            })
        ))
        
        invoice_page.upload_file(sample_invoice_file)
        invoice_page.wait_for_processing()
        
        expect(invoice_page.results.locator(".error")).to_be_visible()
        expect(invoice_page.get_error_message()).to_contain_text("Error")


class TestAnomalyDisplay:
    """Tests for anomaly detection display."""
    
    def test_suspicious_invoice_display(self, invoice_page: InvoicePage, sample_invoice_file):
        """Test display of suspicious invoice results."""
        invoice_page.navigate()
        
        # Mock suspicious invoice response
        invoice_page.page.route("**/api/invoices/upload", lambda route: route.fulfill(
            status=201,
            content_type="application/json",
            body=json.dumps({
                "id": "suspicious-id",
                "parsed_data": {
                    "vendor_name": "Vendor ABC",
                    "invoice_number": "INV-SUSP-001",
                    "invoice_date": "2024-01-15T10:00:00",
                    "total_amount": 2000.0,
                    "items": [
                        {
                            "name": "Product X",
                            "quantity": 10.0,
                            "unit_price": 200.0,
                            "total_price": 2000.0
                        }
                    ],
                    "currency": "USD"
                }
            })
        ))
        
        invoice_page.page.route("**/api/invoices/suspicious-id/analyze", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "is_suspicious": True,
                "risk_score": 75,
                "anomalies": [
                    {
                        "type": "price_increase",
                        "item_name": "Product X",
                        "severity": 75,
                        "description": "Price increased by 50% (from avg $100.00 to $200.00)"
                    }
                ],
                "explanation": "⚠️ HIGH RISK (Score: 75/100)\nDetected 1 anomaly/ies:\n1. Price increased by 50%"
            })
        ))
        
        invoice_page.upload_file(sample_invoice_file)
        invoice_page.wait_for_processing()
        
        # Verify suspicious invoice styling
        expect(invoice_page.results.locator(".invoice-card.suspicious")).to_be_visible()
        expect(invoice_page.results.locator(".risk-score.high")).to_be_visible()
        assert invoice_page.get_risk_score() >= 70
        assert invoice_page.is_suspicious() is True
        assert invoice_page.get_anomalies_count() > 0
