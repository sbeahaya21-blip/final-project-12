"""Invoice controller - business logic layer."""
import uuid
from datetime import datetime
from typing import List
from app.models.invoice import Invoice, ParsedInvoice
from app.services.parser_service import ParserService
from app.services.storage_service import StorageService
from app.exceptions import InvoiceNotFoundError


class InvoiceController:
    """Controller for invoice operations."""
    
    def __init__(
        self,
        parser_service: ParserService,
        storage_service: StorageService
    ):
        self.parser = parser_service
        self.storage = storage_service
    
    def upload_and_parse_invoice(
        self, file_content: bytes, filename: str
    ) -> Invoice:
        """Upload and parse an invoice file."""
        # Parse the invoice
        parsed_data = self.parser.parse_invoice(file_content, filename)
        
        # Create invoice object
        invoice = Invoice(
            id=str(uuid.uuid4()),
            parsed_data=parsed_data,
            uploaded_at=datetime.now()
        )
        
        # Save to storage
        return self.storage.save(invoice)
    
    def create_invoice_from_data(self, invoice_data: dict) -> Invoice:
        """Create an invoice from JSON data."""
        parsed_data = self.parser.parse_invoice_from_json(invoice_data)
        
        invoice = Invoice(
            id=str(uuid.uuid4()),
            parsed_data=parsed_data,
            uploaded_at=datetime.now()
        )
        
        return self.storage.save(invoice)
    
    def get_invoice(self, invoice_id: str) -> Invoice:
        """Get an invoice by ID."""
        return self.storage.get(invoice_id)
    
    def list_invoices(self) -> List[Invoice]:
        """List all invoices."""
        return self.storage.get_all()
    
    def update_invoice_analysis(
        self, invoice_id: str, is_suspicious: bool,
        risk_score: int, explanation: str
    ) -> Invoice:
        """Update invoice with analysis results."""
        return self.storage.update(
            invoice_id,
            is_suspicious=is_suspicious,
            risk_score=risk_score,
            anomaly_explanation=explanation
        )
    
    def delete_invoice(self, invoice_id: str) -> bool:
        """Delete an invoice by ID."""
        return self.storage.delete(invoice_id)
