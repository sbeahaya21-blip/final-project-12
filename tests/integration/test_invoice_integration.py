"""
Integration tests for invoice API with real backend and ERPNext.
These tests require:
- Backend running at http://localhost:8000
- ERPNext running at http://localhost:8080 (or ERPNEXT_BASE_URL env var)
- ERPNext API credentials configured (ERPNEXT_API_KEY, ERPNEXT_API_SECRET)

Run with: pytest tests/integration/test_invoice_integration.py -v
"""
import os
import pytest
import requests
from pathlib import Path
from typing import Dict, Any


# Base URLs - can be overridden with environment variables
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
ERPNEXT_BASE_URL = os.getenv("ERPNEXT_BASE_URL", "http://localhost:8080").rstrip("/")


def _check_backend_available() -> bool:
    """Check if backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def _check_erpnext_available() -> bool:
    """Check if ERPNext is accessible."""
    try:
        response = requests.get(f"{ERPNEXT_BASE_URL}/api/method/ping", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope="session")
def backend_available():
    """Skip tests if backend is not available."""
    if not _check_backend_available():
        pytest.skip(f"Backend not available at {BACKEND_URL}. Start backend with: python run.py")


@pytest.fixture(scope="session")
def erpnext_available():
    """Skip tests if ERPNext is not available."""
    if not _check_erpnext_available():
        pytest.skip(f"ERPNext not available at {ERPNEXT_BASE_URL}. Start ERPNext or set ERPNEXT_BASE_URL env var.")


@pytest.fixture
def sample_pdf_path():
    """Path to a sample PDF invoice."""
    pdf_path = Path(__file__).parent.parent.parent / "sample_invoices" / "pdf" / "sample_invoice_1.pdf"
    if not pdf_path.exists():
        pytest.skip(f"Sample PDF not found: {pdf_path}")
    return str(pdf_path)


class TestInvoiceUploadIntegration:
    """Integration tests for invoice upload with real backend."""

    def test_upload_invoice_file(self, backend_available, sample_pdf_path):
        """Test uploading a real PDF invoice file."""
        with open(sample_pdf_path, "rb") as f:
            files = {"file": ("invoice.pdf", f, "application/pdf")}
            response = requests.post(f"{BACKEND_URL}/api/invoices/upload", files=files, timeout=30)
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data
        assert "parsed_data" in data
        assert "vendor_name" in data["parsed_data"]
        assert "risk_score" in data

    def test_create_invoice_via_json(self, backend_available):
        """Test creating an invoice via JSON API."""
        invoice_data = {
            "vendor_name": "Integration Test Vendor",
            "invoice_number": "INT-TEST-001",
            "invoice_date": "2024-01-15T10:00:00",
            "total_amount": 1500.0,
            "items": [
                {
                    "name": "Widget A",
                    "quantity": 10.0,
                    "unit_price": 50.0,
                    "total_price": 500.0
                },
                {
                    "name": "Widget B",
                    "quantity": 5.0,
                    "unit_price": 200.0,
                    "total_price": 1000.0
                }
            ],
            "currency": "USD"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/invoices/create",
            json=invoice_data,
            timeout=10
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["parsed_data"]["vendor_name"] == "Integration Test Vendor"
        assert data["parsed_data"]["invoice_number"] == "INT-TEST-001"
        assert len(data["parsed_data"]["items"]) == 2
        assert "risk_score" in data

    def test_get_invoice_after_upload(self, backend_available, sample_pdf_path):
        """Test retrieving an invoice after upload."""
        # Upload invoice
        with open(sample_pdf_path, "rb") as f:
            files = {"file": ("invoice.pdf", f, "application/pdf")}
            upload_response = requests.post(f"{BACKEND_URL}/api/invoices/upload", files=files, timeout=30)
        
        assert upload_response.status_code == 201
        invoice_id = upload_response.json()["id"]
        
        # Get invoice
        get_response = requests.get(f"{BACKEND_URL}/api/invoices/{invoice_id}", timeout=10)
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == invoice_id
        assert "parsed_data" in data
        assert "risk_score" in data

    def test_list_invoices(self, backend_available):
        """Test listing all invoices."""
        response = requests.get(f"{BACKEND_URL}/api/invoices", timeout=10)
        assert response.status_code == 200
        invoices = response.json()
        assert isinstance(invoices, list)
        # Should have at least the invoices we created in other tests


class TestERPNextIntegration:
    """Integration tests for ERPNext submission."""

    def test_submit_invoice_to_erpnext(self, backend_available, erpnext_available):
        """Test submitting an invoice to ERPNext."""
        # Create an invoice first
        invoice_data = {
            "vendor_name": "ERPNext Test Vendor",
            "invoice_number": "ERP-TEST-001",
            "invoice_date": "2024-01-15T10:00:00",
            "total_amount": 2000.0,
            "items": [
                {
                    "name": "Test Product",
                    "quantity": 1.0,
                    "unit_price": 2000.0,
                    "total_price": 2000.0
                }
            ],
            "currency": "USD"
        }
        
        create_response = requests.post(
            f"{BACKEND_URL}/api/invoices/create",
            json=invoice_data,
            timeout=10
        )
        assert create_response.status_code == 201
        invoice_id = create_response.json()["id"]
        
        # Submit to ERPNext
        submit_response = requests.post(
            f"{BACKEND_URL}/api/invoices/{invoice_id}/submit-to-erpnext",
            json={},
            timeout=30
        )
        
        assert submit_response.status_code == 200, f"Expected 200, got {submit_response.status_code}: {submit_response.text}"
        data = submit_response.json()
        assert data["submitted_to_erpnext"] is True
        assert "erpnext_invoice_name" in data
        assert data["erpnext_invoice_name"] is not None

    def test_submit_already_submitted_invoice(self, backend_available, erpnext_available):
        """Test submitting an invoice that's already been submitted."""
        # Create an invoice first
        invoice_data = {
            "vendor_name": "ERPNext Test Vendor Duplicate",
            "invoice_number": "ERP-TEST-DUP-001",
            "invoice_date": "2024-01-15T10:00:00",
            "total_amount": 2000.0,
            "items": [
                {
                    "name": "Test Product",
                    "quantity": 1.0,
                    "unit_price": 2000.0,
                    "total_price": 2000.0
                }
            ],
            "currency": "USD"
        }
        
        create_response = requests.post(
            f"{BACKEND_URL}/api/invoices/create",
            json=invoice_data,
            timeout=10
        )
        assert create_response.status_code == 201
        invoice_id = create_response.json()["id"]
        
        # Submit to ERPNext first time
        first_submit = requests.post(
            f"{BACKEND_URL}/api/invoices/{invoice_id}/submit-to-erpnext",
            json={},
            timeout=30
        )
        assert first_submit.status_code == 200
        erpnext_name = first_submit.json()["erpnext_invoice_name"]
        
        # Try to submit again - should return 400
        submit_response = requests.post(
            f"{BACKEND_URL}/api/invoices/{invoice_id}/submit-to-erpnext",
            json={},
            timeout=30
        )
        
        # Backend returns 400 when invoice is already submitted
        assert submit_response.status_code == 400
        error_data = submit_response.json()
        assert "already been submitted" in error_data["detail"].lower()


class TestFullWorkflowIntegration:
    """End-to-end integration tests for complete workflows."""

    def test_full_invoice_lifecycle(self, backend_available, erpnext_available, sample_pdf_path):
        """Test complete workflow: upload -> parse -> view -> submit to ERPNext."""
        # Step 1: Upload invoice
        with open(sample_pdf_path, "rb") as f:
            files = {"file": ("invoice.pdf", f, "application/pdf")}
            upload_response = requests.post(f"{BACKEND_URL}/api/invoices/upload", files=files, timeout=30)
        
        assert upload_response.status_code == 201
        invoice_id = upload_response.json()["id"]
        assert "risk_score" in upload_response.json()
        
        # Step 2: Get invoice details
        get_response = requests.get(f"{BACKEND_URL}/api/invoices/{invoice_id}", timeout=10)
        assert get_response.status_code == 200
        invoice_data = get_response.json()
        assert invoice_data["id"] == invoice_id
        
        # Step 3: Submit to ERPNext
        submit_response = requests.post(
            f"{BACKEND_URL}/api/invoices/{invoice_id}/submit-to-erpnext",
            json={},
            timeout=30
        )
        assert submit_response.status_code == 200
        submit_data = submit_response.json()
        assert submit_data["submitted_to_erpnext"] is True
        assert "erpnext_invoice_name" in submit_data
        
        # Step 4: Verify invoice still retrievable and shows submitted status
        final_get = requests.get(f"{BACKEND_URL}/api/invoices/{invoice_id}", timeout=10)
        assert final_get.status_code == 200
        final_data = final_get.json()
        assert final_data["submitted_to_erpnext"] is True
        assert final_data["erpnext_invoice_name"] == submit_data["erpnext_invoice_name"]
