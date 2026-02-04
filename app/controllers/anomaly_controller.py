"""Anomaly detection controller."""
from app.models.invoice import Invoice
from app.models.anomaly import AnomalyResult
from app.services.anomaly_service import AnomalyService
from app.controllers.invoice_controller import InvoiceController
from app.exceptions import InvoiceNotFoundError


class AnomalyController:
    """Controller for anomaly detection operations."""
    
    def __init__(
        self,
        anomaly_service: AnomalyService,
        invoice_controller: InvoiceController
    ):
        self.anomaly_service = anomaly_service
        self.invoice_controller = invoice_controller
    
    def analyze_invoice(self, invoice_id: str) -> tuple[Invoice, AnomalyResult]:
        """
        Analyze an invoice for anomalies.
        
        Returns:
            Tuple of (updated_invoice, anomaly_result)
        """
        # Get the invoice
        invoice = self.invoice_controller.get_invoice(invoice_id)
        
        # Perform analysis
        anomaly_result = self.anomaly_service.analyze_invoice(invoice)
        
        # Update invoice with analysis results
        updated_invoice = self.invoice_controller.update_invoice_analysis(
            invoice_id,
            is_suspicious=anomaly_result.is_suspicious,
            risk_score=anomaly_result.risk_score,
            explanation=anomaly_result.explanation
        )
        
        return updated_invoice, anomaly_result
