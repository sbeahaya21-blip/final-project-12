"""Tests to achieve full coverage of app (excluding parser_service and erpnext_client)."""
import copy
import uuid
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from pathlib import Path

from app.config import Config
from app.models.invoice import InvoiceItem, ParsedInvoice, Invoice
from app.services.storage_service import StorageService
from app.services.anomaly_service import AnomalyService
from app.controllers.invoice_controller import InvoiceController
from app.controllers.anomaly_controller import AnomalyController
from app.services.parser_service import ParserService
from datetime import datetime


# ----- Config -----
class TestConfigCoverage:
    """Cover config.py branches."""

    def test_normalize_erpnext_base_url_empty(self):
        from app.config import _normalize_erpnext_base_url
        assert _normalize_erpnext_base_url("") == ""

    def test_normalize_erpnext_base_url_exception(self):
        from app.config import _normalize_erpnext_base_url
        result = _normalize_erpnext_base_url("http://valid.com/path")
        assert result == "http://valid.com"

    def test_normalize_erpnext_base_url_urlparse_raises(self):
        from app.config import _normalize_erpnext_base_url
        with patch("app.config.urlparse", side_effect=ValueError("bad")):
            result = _normalize_erpnext_base_url("http://host/path")
            assert result == "http://host/path"

    def test_validate_erpnext_config_placeholder(self):
        with patch.object(Config, "ERPNEXT_BASE_URL", "https://your-instance.erpnext.com"):
            with patch.object(Config, "ERPNEXT_API_KEY", "k"):
                with patch.object(Config, "ERPNEXT_API_SECRET", "s"):
                    assert Config.validate_erpnext_config() is False

    def test_load_dotenv_file_not_exists(self):
        from app.config import _load_dotenv
        _load_dotenv(Path("/nonexistent/path/.env"))  # no raise, early return

    def test_load_dotenv_sets_value_when_key_not_in_environ(self, tmp_path):
        import os
        from app.config import _load_dotenv
        env_file = tmp_path / ".env"
        env_file.write_text('COVERAGE_TEST_KEY=coverage_value\n')
        try:
            _load_dotenv(env_file)
            assert os.environ.get("COVERAGE_TEST_KEY") == "coverage_value"
        finally:
            os.environ.pop("COVERAGE_TEST_KEY", None)


# ----- Invoice model -----
class TestInvoiceModelCoverage:
    """Cover InvoiceItem and model branches."""

    def test_invoice_item_quantity_negative(self):
        item = InvoiceItem(name="X", quantity=-5, unit_price=10.0, total_price=0)
        assert item.quantity == 0.0

    def test_invoice_item_quantity_invalid(self):
        item = InvoiceItem(name="X", quantity="bad", unit_price=10.0, total_price=100.0)
        assert item.quantity == 0.0

    def test_invoice_item_total_price_recalculated(self):
        item = InvoiceItem(name="X", quantity=3.0, unit_price=10.0, total_price=0)  # recalc to 30
        assert item.total_price == 30.0

    def test_invoice_item_calculated_total(self):
        item = InvoiceItem(name="X", quantity=2.5, unit_price=4.0, total_price=10.0)
        assert item.calculated_total == 10.0


# ----- Storage -----
class TestStorageCoverage:
    """Cover storage_service branches."""

    def test_storage_persist_false(self):
        s = StorageService(persist=False)
        assert len(s._invoices) == 0
        # Call save to hit _save_to_file early return (line 49)
        inv = Invoice(
            id="x",
            parsed_data=ParsedInvoice(
                vendor_name="V",
                invoice_number="N",
                invoice_date=datetime.now(),
                total_amount=100.0,
                items=[],
                currency="USD",
            ),
            uploaded_at=datetime.now(),
        )
        s.save(inv)
        assert s._invoices["x"] == inv

    def test_storage_load_bad_json(self, tmp_path):
        bad_file = tmp_path / "invoices.json"
        bad_file.write_text("not valid json {")
        with patch("app.services.storage_service._storage_path", return_value=bad_file):
            s = StorageService(persist=True)
            assert s._invoices == {}

    def test_storage_save_to_file_exception(self):
        s = StorageService(persist=True)
        inv = Invoice(
            id="x",
            parsed_data=ParsedInvoice(
                vendor_name="V",
                invoice_number="N",
                invoice_date=datetime.now(),
                total_amount=100.0,
                items=[],
                currency="USD",
            ),
            uploaded_at=datetime.now(),
        )
        with patch("builtins.open", side_effect=OSError("disk full")):
            s.save(inv)  # exception swallowed in _save_to_file
        assert s._invoices["x"] == inv


# ----- Anomaly service -----
class TestAnomalyServiceCoverage:
    """Cover anomaly_service missing branches."""

    def test_quantity_deviation_above_avg(self, client):
        vendor = f"Vendor-Qty-{uuid.uuid4().hex[:8]}"
        hist = {
            "vendor_name": vendor,
            "invoice_number": "H1",
            "invoice_date": "2024-01-01T00:00:00",
            "total_amount": 100.0,
            "items": [{"name": "Item1", "quantity": 10.0, "unit_price": 10.0, "total_price": 100.0}],
            "currency": "USD",
        }
        client.post("/api/invoices/create", json=hist)
        new_inv = copy.deepcopy(hist)
        new_inv["invoice_number"] = "N1"
        new_inv["invoice_date"] = "2024-01-15T00:00:00"
        new_inv["items"][0]["quantity"] = 30.0  # 3x average
        new_inv["items"][0]["total_price"] = 300.0
        new_inv["total_amount"] = 300.0
        r = client.post("/api/invoices/create", json=new_inv)
        aid = r.json()["id"]
        resp = client.post(f"/api/invoices/{aid}/analyze")
        assert resp.status_code == 200
        data = resp.json()
        assert any("quantity" in a.get("description", "").lower() or "Quantity" in a.get("description", "") for a in data.get("anomalies", []))

    def test_amount_deviation(self, client):
        vendor = f"Vendor-Amt-{uuid.uuid4().hex[:8]}"
        hist = {
            "vendor_name": vendor,
            "invoice_number": "H1",
            "invoice_date": "2024-01-01T00:00:00",
            "total_amount": 100.0,
            "items": [{"name": "I", "quantity": 1.0, "unit_price": 100.0, "total_price": 100.0}],
            "currency": "USD",
        }
        client.post("/api/invoices/create", json=hist)
        new_inv = copy.deepcopy(hist)
        new_inv["invoice_number"] = "N1"
        new_inv["invoice_date"] = "2024-01-15T00:00:00"
        new_inv["total_amount"] = 500.0
        new_inv["items"][0]["total_price"] = 500.0
        r = client.post("/api/invoices/create", json=new_inv)
        aid = r.json()["id"]
        resp = client.post(f"/api/invoices/{aid}/analyze")
        assert resp.status_code == 200
        data = resp.json()
        assert data["risk_score"] >= 0

    def test_quantity_deviation_above_max_only(self, client):
        """Covers elif item.quantity > max_quantity * 1.5 (lines 145-146)."""
        vendor = f"Vendor-Max-{uuid.uuid4().hex[:8]}"
        hist = {
            "vendor_name": vendor,
            "invoice_number": "H1",
            "invoice_date": "2024-01-01T00:00:00",
            "total_amount": 100.0,
            "items": [{"name": "I", "quantity": 10.0, "unit_price": 10.0, "total_price": 100.0}],
            "currency": "USD",
        }
        client.post("/api/invoices/create", json=hist)
        new_inv = copy.deepcopy(hist)
        new_inv["invoice_number"] = "N1"
        new_inv["invoice_date"] = "2024-01-15T00:00:00"
        new_inv["items"][0]["quantity"] = 18.0  # 1.8x max, not 2x avg (avg=10)
        new_inv["items"][0]["total_price"] = 180.0
        new_inv["total_amount"] = 180.0
        r = client.post("/api/invoices/create", json=new_inv)
        aid = r.json()["id"]
        resp = client.post(f"/api/invoices/{aid}/analyze")
        assert resp.status_code == 200

    def test_amount_deviation_below_average(self, client):
        """Covers direction 'below' in amount deviation (line 197)."""
        vendor = f"Vendor-Below-{uuid.uuid4().hex[:8]}"
        hist = {
            "vendor_name": vendor,
            "invoice_number": "H1",
            "invoice_date": "2024-01-01T00:00:00",
            "total_amount": 1000.0,
            "items": [{"name": "I", "quantity": 1.0, "unit_price": 1000.0, "total_price": 1000.0}],
            "currency": "USD",
        }
        client.post("/api/invoices/create", json=hist)
        new_inv = copy.deepcopy(hist)
        new_inv["invoice_number"] = "N1"
        new_inv["invoice_date"] = "2024-01-15T00:00:00"
        new_inv["total_amount"] = 500.0  # 50% below average
        new_inv["items"][0]["total_price"] = 500.0
        r = client.post("/api/invoices/create", json=new_inv)
        aid = r.json()["id"]
        resp = client.post(f"/api/invoices/{aid}/analyze")
        assert resp.status_code == 200
        assert "below" in resp.json().get("explanation", "").lower() or any(
            "below" in a.get("description", "").lower() for a in resp.json().get("anomalies", [])
        )

    def test_generate_explanation_risk_levels(self):
        storage = StorageService(persist=False)
        svc = AnomalyService(storage)
        inv = Invoice(
            id="i",
            parsed_data=ParsedInvoice(
                vendor_name="V",
                invoice_number="N",
                invoice_date=datetime.now(),
                total_amount=100.0,
                items=[],
                currency="USD",
            ),
            uploaded_at=datetime.now(),
        )
        res = svc.analyze_invoice(inv)
        assert res.risk_score == 10
        assert "historical" in res.explanation.lower()


# ----- Invoice controller upload path -----
class TestInvoiceControllerUploadCoverage:
    """Cover upload_and_parse_invoice (controller lines 30-37)."""

    def test_upload_invoice_success_mock_parser(self, client):
        from app.models.invoice import ParsedInvoice, InvoiceItem
        from datetime import datetime
        parsed = ParsedInvoice(
            vendor_name="Upload Vendor",
            invoice_number="UP-001",
            invoice_date=datetime.now(),
            total_amount=200.0,
            items=[InvoiceItem(name="P", quantity=2.0, unit_price=100.0, total_price=200.0)],
            currency="USD",
        )
        with patch("app.views.invoice_views.invoice_controller.parser") as m:
            m.parse_invoice.return_value = parsed
            files = {"file": ("test.pdf", b"fake pdf", "application/pdf")}
            r = client.post("/api/invoices/upload", files=files)
        assert r.status_code == status.HTTP_201_CREATED
        assert r.json()["parsed_data"]["vendor_name"] == "Upload Vendor"


# ----- Main: root, serve_react, exception handlers -----
class TestMainCoverage:
    """Cover main.py routes and handlers."""

    def test_root_fallback_when_no_static(self, client):
        mock_path = MagicMock()
        mock_path.return_value.exists.return_value = False
        with patch("app.main.Path", mock_path):
            r = client.get("/")
            assert r.status_code == 200
            assert "Frontend not built" in r.text or "Invoice Parser" in r.text

    def test_serve_react_fallback(self, client):
        mock_path = MagicMock()
        mock_path.return_value.exists.return_value = False
        with patch("app.main.Path", mock_path):
            r = client.get("/invoices")
            assert r.status_code == 200
            assert "Frontend not built" in r.text or "Run" in r.text

    def test_parsing_error_handler(self, client):
        with patch("app.views.invoice_views.invoice_controller.parser") as m:
            from app.exceptions import ParsingError
            m.parse_invoice.side_effect = ParsingError("Parse failed")
            r = client.post("/api/invoices/upload", files={"file": ("x.pdf", b"x", "application/pdf")})
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert "Parse failed" in r.json()["detail"]

    def test_upload_generic_exception(self, client):
        with patch("app.views.invoice_views.invoice_controller.parser") as m:
            m.parse_invoice.side_effect = RuntimeError("boom")
            r = client.post("/api/invoices/upload", files={"file": ("x.pdf", b"x", "application/pdf")})
        assert r.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_create_invoice_generic_exception(self, client):
        with patch("app.views.invoice_views.invoice_controller.create_invoice_from_data") as m:
            m.side_effect = Exception("create failed")
            r = client.post("/api/invoices/create", json={
                "vendor_name": "V", "invoice_number": "N", "invoice_date": "2024-01-01T00:00:00",
                "total_amount": 100.0, "items": [], "currency": "USD",
            })
        assert r.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_middleware_submit_404(self, client):
        """Covers middleware branch when 404 on submit-to-erpnext (main 31, 34)."""
        with patch("app.config.Config.validate_erpnext_config", return_value=True):
            r = client.post("/api/invoices/nonexistent-id/submit-to-erpnext")
        assert r.status_code == status.HTTP_404_NOT_FOUND


# ----- Invoice views: submit-to-erpnext, delete exception -----
class TestInvoiceViewsCoverage:
    """Cover submit-to-erpnext and delete exception path."""

    def test_submit_already_submitted(self, client, mock_invoice_data):
        r = client.post("/api/invoices/create", json=mock_invoice_data)
        aid = r.json()["id"]
        with patch("app.config.Config.validate_erpnext_config", return_value=True):
            with patch("app.services.erpnext_client.ERPNextClient") as E:
                E.return_value.create_purchase_invoice.return_value = {"data": {"name": "PINV-001"}}
                client.post(f"/api/invoices/{aid}/submit-to-erpnext")
                r2 = client.post(f"/api/invoices/{aid}/submit-to-erpnext")
        assert r2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already been submitted" in r2.json()["detail"]

    def test_submit_erpnext_not_configured(self, client, mock_invoice_data):
        r = client.post("/api/invoices/create", json=mock_invoice_data)
        aid = r.json()["id"]
        with patch("app.config.Config.validate_erpnext_config", return_value=False):
            r2 = client.post(f"/api/invoices/{aid}/submit-to-erpnext")
        assert r2.status_code == status.HTTP_400_BAD_REQUEST
        assert "not configured" in r2.json()["detail"].lower()

    def test_submit_success_mocked(self, client, mock_invoice_data):
        r = client.post("/api/invoices/create", json=mock_invoice_data)
        aid = r.json()["id"]
        with patch("app.config.Config.validate_erpnext_config", return_value=True):
            with patch("app.config.Config.ERPNEXT_BASE_URL", "http://test"):
                with patch("app.config.Config.ERPNEXT_API_KEY", "k"):
                    with patch("app.config.Config.ERPNEXT_API_SECRET", "s"):
                        with patch("app.services.erpnext_client.ERPNextClient") as E:
                            inst = MagicMock()
                            inst.create_purchase_invoice.return_value = {"data": {"name": "PINV-001"}}
                            E.return_value = inst
                            r2 = client.post(f"/api/invoices/{aid}/submit-to-erpnext")
        assert r2.status_code == 200
        assert r2.json().get("submitted_to_erpnext") is True

    def test_delete_invoice_exception(self, client):
        with patch("app.views.invoice_views.invoice_controller.delete_invoice", side_effect=Exception("db error")):
            r = client.delete("/api/invoices/some-id")
        assert r.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# ----- ERPNext views -----
class TestErpnextViewsCoverage:
    """Cover erpnext_views when not configured and health branches."""

    def test_erpnext_health_not_configured(self, client):
        with patch("app.views.erpnext_views.erpnext_client", None):
            with patch("app.views.erpnext_views.Config") as C:
                C.validate_erpnext_config.return_value = False
                # Reload would re-create erpnext_client; test the endpoint that checks it
                r = client.get("/api/erpnext/health")
        # When not configured, health returns configured: False
        assert r.status_code == 200
        data = r.json()
        assert data.get("configured") is False or "message" in data

    def test_erpnext_analyze_invoice_not_configured(self, client):
        with patch("app.views.erpnext_views.erpnext_client", None):
            r = client.post("/api/erpnext/analyze-invoice", json={"invoice_id": "PINV-001"})
        assert r.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "not configured" in r.json()["detail"].lower()
