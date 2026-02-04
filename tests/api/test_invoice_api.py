"""API tests for invoice endpoints."""
import pytest
from fastapi import status
from unittest.mock import Mock, patch, MagicMock
from app.models.invoice import Invoice, ParsedInvoice, InvoiceItem
from datetime import datetime


class TestInvoiceUpload:
    """Tests for invoice upload endpoint."""
    
    def test_upload_invoice_success(self, client, mock_invoice_data):
        """Test successful invoice upload via JSON."""
        response = client.post("/api/invoices/create", json=mock_invoice_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data["parsed_data"]["vendor_name"] == "Test Vendor"
        assert data["parsed_data"]["invoice_number"] == "INV-001"
        assert len(data["parsed_data"]["items"]) == 2
    
    def test_upload_invoice_invalid_format(self, client):
        """Test upload with invalid invoice format."""
        invalid_data = {
            "vendor_name": "Test Vendor"
            # Missing required fields
        }
        
        response = client.post("/api/invoices/create", json=invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @patch('app.views.invoice_views.parser_service')
    def test_upload_invoice_file_parsing_error(self, mock_parser, client):
        """Test upload when parsing fails."""
        from app.exceptions import ParsingError
        
        mock_parser.parse_invoice.side_effect = ParsingError("Parsing failed")
        
        # Create a mock file
        files = {"file": ("test.pdf", b"fake content", "application/pdf")}
        response = client.post("/api/invoices/upload", files=files)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Parsing failed" in response.json()["detail"]


class TestInvoiceRetrieval:
    """Tests for invoice retrieval endpoints."""
    
    def test_get_invoice_success(self, client, mock_invoice_data):
        """Test getting an invoice by ID."""
        # Create an invoice first
        create_response = client.post("/api/invoices/create", json=mock_invoice_data)
        invoice_id = create_response.json()["id"]
        
        # Get the invoice
        response = client.get(f"/api/invoices/{invoice_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == invoice_id
        assert data["parsed_data"]["vendor_name"] == "Test Vendor"
    
    def test_get_invoice_not_found(self, client):
        """Test getting a non-existent invoice."""
        response = client.get("/api/invoices/non-existent-id")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_list_invoices(self, client, mock_invoice_data):
        """Test listing all invoices."""
        # Create multiple invoices
        client.post("/api/invoices/create", json=mock_invoice_data)
        
        # Modify for second invoice
        second_invoice = mock_invoice_data.copy()
        second_invoice["invoice_number"] = "INV-002"
        client.post("/api/invoices/create", json=second_invoice)
        
        # List all invoices
        response = client.get("/api/invoices")
        
        assert response.status_code == status.HTTP_200_OK
        invoices = response.json()
        assert len(invoices) >= 2


class TestAnomalyAnalysis:
    """Tests for anomaly analysis endpoint."""
    
    def test_analyze_invoice_no_historical_data(self, client, mock_invoice_data):
        """Test analysis when no historical data exists."""
        # Create an invoice
        create_response = client.post("/api/invoices/create", json=mock_invoice_data)
        invoice_id = create_response.json()["id"]
        
        # Analyze it
        response = client.post(f"/api/invoices/{invoice_id}/analyze")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "risk_score" in data
        assert "explanation" in data
        assert "is_suspicious" in data
        # First invoice should have low risk
        assert data["risk_score"] < 50
    
    def test_analyze_invoice_with_price_increase(self, client):
        """Test detection of price increase anomaly."""
        # Create historical invoice
        historical_invoice = {
            "vendor_name": "Vendor ABC",
            "invoice_number": "INV-HIST-001",
            "invoice_date": "2024-01-01T10:00:00",
            "total_amount": 500.0,
            "items": [
                {
                    "name": "Product X",
                    "quantity": 10.0,
                    "unit_price": 50.0,  # $50 per unit
                    "total_price": 500.0
                }
            ],
            "currency": "USD"
        }
        client.post("/api/invoices/create", json=historical_invoice)
        
        # Create new invoice with price increase
        new_invoice = historical_invoice.copy()
        new_invoice["invoice_number"] = "INV-NEW-001"
        new_invoice["invoice_date"] = "2024-01-15T10:00:00"
        new_invoice["items"][0]["unit_price"] = 75.0  # 50% increase
        new_invoice["items"][0]["total_price"] = 750.0
        new_invoice["total_amount"] = 750.0
        
        create_response = client.post("/api/invoices/create", json=new_invoice)
        invoice_id = create_response.json()["id"]
        
        # Analyze
        response = client.post(f"/api/invoices/{invoice_id}/analyze")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_suspicious"] is True
        assert data["risk_score"] >= 50
        assert "price" in data["explanation"].lower() or "increase" in data["explanation"].lower()
    
    def test_analyze_invoice_with_new_item(self, client):
        """Test detection of new item anomaly."""
        # Create historical invoice
        historical_invoice = {
            "vendor_name": "Vendor XYZ",
            "invoice_number": "INV-HIST-001",
            "invoice_date": "2024-01-01T10:00:00",
            "total_amount": 500.0,
            "items": [
                {
                    "name": "Product A",
                    "quantity": 10.0,
                    "unit_price": 50.0,
                    "total_price": 500.0
                }
            ],
            "currency": "USD"
        }
        client.post("/api/invoices/create", json=historical_invoice)
        
        # Create new invoice with new item
        new_invoice = historical_invoice.copy()
        new_invoice["invoice_number"] = "INV-NEW-001"
        new_invoice["invoice_date"] = "2024-01-15T10:00:00"
        new_invoice["items"].append({
            "name": "Product B - NEW",  # New item
            "quantity": 5.0,
            "unit_price": 100.0,
            "total_price": 500.0
        })
        new_invoice["total_amount"] = 1000.0
        
        create_response = client.post("/api/invoices/create", json=new_invoice)
        invoice_id = create_response.json()["id"]
        
        # Analyze
        response = client.post(f"/api/invoices/{invoice_id}/analyze")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should detect new item
        assert any("new" in anomaly["type"] for anomaly in data.get("anomalies", []))
    
    def test_analyze_invoice_not_found(self, client):
        """Test analysis of non-existent invoice."""
        response = client.post("/api/invoices/non-existent-id/analyze")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestInvoiceDeletion:
    """Tests for invoice deletion endpoint."""
    
    def test_delete_invoice_success(self, client, mock_invoice_data):
        """Test successful invoice deletion."""
        # Create an invoice first
        create_response = client.post("/api/invoices/create", json=mock_invoice_data)
        invoice_id = create_response.json()["id"]
        
        # Delete the invoice
        response = client.delete(f"/api/invoices/{invoice_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["deleted"] is True
        assert "deleted successfully" in data["message"].lower()
        
        # Verify invoice is deleted
        get_response = client.get(f"/api/invoices/{invoice_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_invoice_not_found(self, client):
        """Test deletion of non-existent invoice."""
        response = client.delete("/api/invoices/non-existent-id")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestHealthCheck:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
