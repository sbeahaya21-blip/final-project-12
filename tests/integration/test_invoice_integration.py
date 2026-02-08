"""
Integration tests for invoice API with real backend and ERPNext.
These tests require:
- Backend running at http://localhost:8000
- ERPNext running at http://localhost:8080 (or ERPNEXT_BASE_URL env var)
- ERPNext API credentials configured (ERPNEXT_API_KEY, ERPNEXT_API_SECRET)

Run with: python -m unittest tests.integration.test_invoice_integration -v
"""
import os
import unittest
import requests
from pathlib import Path


# Base URLs - can be overridden with environment variables
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
ERPNEXT_BASE_URL = os.getenv("ERPNEXT_BASE_URL", "http://localhost:8080").rstrip("/")


def _check_backend_available():
    """Check if backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def _check_erpnext_available():
    """Check if ERPNext is accessible."""
    try:
        response = requests.get(f"{ERPNEXT_BASE_URL}/api/method/ping", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def _get_sample_pdf_path():
    """Return path to sample PDF or None if not found."""
    pdf_path = Path(__file__).resolve().parent.parent.parent / "sample_invoices" / "pdf" / "sample_invoice_1.pdf"
    return str(pdf_path) if pdf_path.exists() else None


class IntegrationTestCase(unittest.TestCase):
    """Base for integration tests. Skips if backend is not available."""

    @classmethod
    def setUpClass(cls):
        if not _check_backend_available():
            raise unittest.SkipTest(f"Backend not available at {BACKEND_URL}. Start backend with: python run.py")


class IntegrationTestCaseWithERPNext(IntegrationTestCase):
    """Base for integration tests that need ERPNext. Skips if backend or ERPNext is not available."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not _check_erpnext_available():
            raise unittest.SkipTest(
                f"ERPNext not available at {ERPNEXT_BASE_URL}. Start ERPNext or set ERPNEXT_BASE_URL env var."
            )


class TestInvoiceUploadIntegration(IntegrationTestCase):
    """Integration tests for invoice upload with real backend."""

    def _sample_pdf_path(self):
        path = _get_sample_pdf_path()
        if not path:
            self.skipTest("Sample PDF not found: sample_invoices/pdf/sample_invoice_1.pdf")
        return path

    def test_upload_invoice_file(self):
        """Test uploading a real PDF invoice file."""
        sample_pdf_path = self._sample_pdf_path()
        with open(sample_pdf_path, "rb") as f:
            files = {"file": ("invoice.pdf", f, "application/pdf")}
            response = requests.post(f"{BACKEND_URL}/api/invoices/upload", files=files, timeout=30)

        self.assertEqual(response.status_code, 201, f"Expected 201, got {response.status_code}: {response.text}")
        data = response.json()
        self.assertIn("id", data)
        self.assertIn("parsed_data", data)
        self.assertIn("vendor_name", data["parsed_data"])
        self.assertIn("risk_score", data)

    def test_create_invoice_via_json(self):
        """Test creating an invoice via JSON API."""
        invoice_data = {
            "vendor_name": "Integration Test Vendor",
            "invoice_number": "INT-TEST-001",
            "invoice_date": "2024-01-15T10:00:00",
            "total_amount": 1500.0,
            "items": [
                {"name": "Widget A", "quantity": 10.0, "unit_price": 50.0, "total_price": 500.0},
                {"name": "Widget B", "quantity": 5.0, "unit_price": 200.0, "total_price": 1000.0},
            ],
            "currency": "USD",
        }

        response = requests.post(
            f"{BACKEND_URL}/api/invoices/create",
            json=invoice_data,
            timeout=10,
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["parsed_data"]["vendor_name"], "Integration Test Vendor")
        self.assertEqual(data["parsed_data"]["invoice_number"], "INT-TEST-001")
        self.assertEqual(len(data["parsed_data"]["items"]), 2)
        self.assertIn("risk_score", data)

    def test_get_invoice_after_upload(self):
        """Test retrieving an invoice after upload."""
        sample_pdf_path = self._sample_pdf_path()
        with open(sample_pdf_path, "rb") as f:
            files = {"file": ("invoice.pdf", f, "application/pdf")}
            upload_response = requests.post(f"{BACKEND_URL}/api/invoices/upload", files=files, timeout=30)

        self.assertEqual(upload_response.status_code, 201)
        invoice_id = upload_response.json()["id"]

        get_response = requests.get(f"{BACKEND_URL}/api/invoices/{invoice_id}", timeout=10)
        self.assertEqual(get_response.status_code, 200)
        data = get_response.json()
        self.assertEqual(data["id"], invoice_id)
        self.assertIn("parsed_data", data)
        self.assertIn("risk_score", data)

    def test_list_invoices(self):
        """Test listing all invoices."""
        response = requests.get(f"{BACKEND_URL}/api/invoices", timeout=10)
        self.assertEqual(response.status_code, 200)
        invoices = response.json()
        self.assertIsInstance(invoices, list)


class TestERPNextIntegration(IntegrationTestCaseWithERPNext):
    """Integration tests for ERPNext submission."""

    def test_submit_invoice_to_erpnext(self):
        """Test submitting an invoice to ERPNext."""
        invoice_data = {
            "vendor_name": "ERPNext Test Vendor",
            "invoice_number": "ERP-TEST-001",
            "invoice_date": "2024-01-15T10:00:00",
            "total_amount": 2000.0,
            "items": [
                {"name": "Test Product", "quantity": 1.0, "unit_price": 2000.0, "total_price": 2000.0}
            ],
            "currency": "USD",
        }

        create_response = requests.post(
            f"{BACKEND_URL}/api/invoices/create",
            json=invoice_data,
            timeout=10,
        )
        self.assertEqual(create_response.status_code, 201)
        invoice_id = create_response.json()["id"]

        submit_response = requests.post(
            f"{BACKEND_URL}/api/invoices/{invoice_id}/submit-to-erpnext",
            json={},
            timeout=30,
        )
        self.assertEqual(
            submit_response.status_code, 200,
            f"Expected 200, got {submit_response.status_code}: {submit_response.text}"
        )
        data = submit_response.json()
        self.assertTrue(data["submitted_to_erpnext"])
        self.assertIn("erpnext_invoice_name", data)
        self.assertIsNotNone(data["erpnext_invoice_name"])

    def test_submit_already_submitted_invoice(self):
        """Test submitting an invoice that's already been submitted."""
        invoice_data = {
            "vendor_name": "ERPNext Test Vendor Duplicate",
            "invoice_number": "ERP-TEST-DUP-001",
            "invoice_date": "2024-01-15T10:00:00",
            "total_amount": 2000.0,
            "items": [
                {"name": "Test Product", "quantity": 1.0, "unit_price": 2000.0, "total_price": 2000.0}
            ],
            "currency": "USD",
        }

        create_response = requests.post(
            f"{BACKEND_URL}/api/invoices/create",
            json=invoice_data,
            timeout=10,
        )
        self.assertEqual(create_response.status_code, 201)
        invoice_id = create_response.json()["id"]

        first_submit = requests.post(
            f"{BACKEND_URL}/api/invoices/{invoice_id}/submit-to-erpnext",
            json={},
            timeout=30,
        )
        self.assertEqual(first_submit.status_code, 200)

        submit_response = requests.post(
            f"{BACKEND_URL}/api/invoices/{invoice_id}/submit-to-erpnext",
            json={},
            timeout=30,
        )
        self.assertEqual(submit_response.status_code, 400)
        error_data = submit_response.json()
        self.assertIn("already been submitted", error_data["detail"].lower())


class TestFullWorkflowIntegration(IntegrationTestCaseWithERPNext):
    """End-to-end integration tests for complete workflows."""

    def _sample_pdf_path(self):
        path = _get_sample_pdf_path()
        if not path:
            self.skipTest("Sample PDF not found: sample_invoices/pdf/sample_invoice_1.pdf")
        return path

    def test_full_invoice_lifecycle(self):
        """Test complete workflow: upload -> parse -> view -> submit to ERPNext."""
        sample_pdf_path = self._sample_pdf_path()

        with open(sample_pdf_path, "rb") as f:
            files = {"file": ("invoice.pdf", f, "application/pdf")}
            upload_response = requests.post(f"{BACKEND_URL}/api/invoices/upload", files=files, timeout=30)

        self.assertEqual(upload_response.status_code, 201)
        invoice_id = upload_response.json()["id"]
        self.assertIn("risk_score", upload_response.json())

        get_response = requests.get(f"{BACKEND_URL}/api/invoices/{invoice_id}", timeout=10)
        self.assertEqual(get_response.status_code, 200)
        invoice_data = get_response.json()
        self.assertEqual(invoice_data["id"], invoice_id)

        submit_response = requests.post(
            f"{BACKEND_URL}/api/invoices/{invoice_id}/submit-to-erpnext",
            json={},
            timeout=30,
        )
        self.assertEqual(submit_response.status_code, 200)
        submit_data = submit_response.json()
        self.assertTrue(submit_data["submitted_to_erpnext"])
        self.assertIn("erpnext_invoice_name", submit_data)

        final_get = requests.get(f"{BACKEND_URL}/api/invoices/{invoice_id}", timeout=10)
        self.assertEqual(final_get.status_code, 200)
        final_data = final_get.json()
        self.assertTrue(final_data["submitted_to_erpnext"])
        self.assertEqual(final_data["erpnext_invoice_name"], submit_data["erpnext_invoice_name"])


if __name__ == "__main__":
    unittest.main()
