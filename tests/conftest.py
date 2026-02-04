"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.storage_service import StorageService
from app.services.parser_service import ParserService
from app.services.anomaly_service import AnomalyService
from app.controllers.invoice_controller import InvoiceController
from app.controllers.anomaly_controller import AnomalyController


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def storage_service():
    """Create a fresh storage service for each test."""
    return StorageService()


@pytest.fixture
def parser_service():
    """Create a parser service."""
    return ParserService()


@pytest.fixture
def mock_invoice_data():
    """Sample invoice data for testing."""
    return {
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
            },
            {
                "name": "Product B",
                "quantity": 5.0,
                "unit_price": 100.0,
                "total_price": 500.0
            }
        ],
        "currency": "USD"
    }
