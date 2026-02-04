"""Tests for error handling in API."""
import pytest
from fastapi import status
from app.exceptions import InvoiceNotFoundError, ParsingError, InvalidInvoiceFormatError


class TestErrorHandling:
    """Tests for proper HTTP error handling."""
    
    def test_404_error_format(self, client):
        """Test that 404 errors return proper format."""
        response = client.get("/api/invoices/non-existent")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.json()
    
    def test_400_error_format(self, client):
        """Test that 400 errors return proper format."""
        invalid_data = {"invalid": "data"}
        response = client.post("/api/invoices/create", json=invalid_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.json()
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
