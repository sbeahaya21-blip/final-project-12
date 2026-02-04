"""Invoice data models."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class InvoiceItem(BaseModel):
    """Represents a single item on an invoice."""
    name: str
    quantity: float
    unit_price: float
    total_price: float

    def __init__(self, **data):
        """Initialize with basic validation."""
        # No hardcoded item names - generic validation only
        if 'quantity' in data:
            quantity = data['quantity']
            # Ensure quantity is a valid number
            try:
                quantity = float(quantity)
                if quantity < 0:
                    quantity = 0.0
                data['quantity'] = quantity
            except (ValueError, TypeError):
                data['quantity'] = 0.0
        
        # Recalculate total_price if we have quantity and unit_price
        if 'quantity' in data and 'unit_price' in data:
            try:
                qty = float(data['quantity'])
                unit_price = float(data['unit_price'])
                if 'total_price' not in data or not data['total_price']:
                    data['total_price'] = round(qty * unit_price, 2)
            except (ValueError, TypeError):
                pass
        
        super().__init__(**data)

    @property
    def calculated_total(self) -> float:
        """Calculate total price from quantity and unit price."""
        return round(self.quantity * self.unit_price, 2)


class ParsedInvoice(BaseModel):
    """Represents a parsed invoice with extracted data."""
    vendor_name: str
    invoice_number: str
    invoice_date: datetime
    total_amount: float
    items: List[InvoiceItem]
    currency: str = "USD"


class Invoice(BaseModel):
    """Complete invoice model with metadata."""
    id: str
    parsed_data: ParsedInvoice
    uploaded_at: datetime = Field(default_factory=datetime.now)
    is_suspicious: bool = False
    risk_score: Optional[int] = None
    anomaly_explanation: Optional[str] = None
    submitted_to_erpnext: bool = False
    erpnext_invoice_name: Optional[str] = None