"""API views/endpoints for ERPNext integration."""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List
from app.models.anomaly import AnomalyResult
from app.services.erpnext_client import ERPNextClient
from app.services.anomaly_service import AnomalyService
from app.config import Config
from app.models.invoice import Invoice, ParsedInvoice
from app.exceptions import ParsingError


class AnalyzeInvoiceRequest(BaseModel):
    """Request model for analyze-invoice endpoint."""
    invoice_id: str


class AnalyzeInvoiceResponse(BaseModel):
    """Response model for analyze-invoice endpoint."""
    risk_score: int
    status: str  # "normal" or "suspicious"
    reasons: List[str]
    invoice_id: str
    vendor_name: str


# Initialize ERPNext client (will be None if not configured)
erpnext_client: ERPNextClient | None = None

if Config.validate_erpnext_config():
    erpnext_client = ERPNextClient(
        base_url=Config.ERPNEXT_BASE_URL,
        api_key=Config.ERPNEXT_API_KEY,
        api_secret=Config.ERPNEXT_API_SECRET
    )

router = APIRouter(prefix="/api/erpnext", tags=["erpnext"])


@router.post("/analyze-invoice", response_model=AnalyzeInvoiceResponse)
async def analyze_invoice(request: AnalyzeInvoiceRequest):
    """
    Analyze an ERPNext purchase invoice for anomalies and fraud.
    
    This endpoint:
    1. Fetches the invoice from ERPNext using the invoice_id
    2. Fetches historical invoices from the same supplier
    3. Analyzes for anomalies (price increases, quantity deviations, new items, etc.)
    4. Returns risk score, status, and human-readable reasons
    
    Args:
        request: AnalyzeInvoiceRequest with invoice_id (e.g., "PINV-0001")
    
    Returns:
        AnalyzeInvoiceResponse with risk_score (0-100), status, and reasons
    """
    if not erpnext_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ERPNext integration not configured. Please set ERPNEXT_BASE_URL, ERPNEXT_API_KEY, and ERPNEXT_API_SECRET environment variables."
        )
    
    try:
        # Step 1: Fetch invoice from ERPNext
        parsed_invoice = erpnext_client.fetch_and_parse_invoice(request.invoice_id)
        
        # Step 2: Fetch historical invoices from same supplier
        historical_parsed = erpnext_client.fetch_historical_invoices(
            supplier=parsed_invoice.vendor_name,
            exclude_invoice_id=request.invoice_id
        )
        
        # Step 3: Convert ParsedInvoice to Invoice model for analysis
        # Create a temporary Invoice object for analysis
        invoice = Invoice(
            id=request.invoice_id,
            parsed_data=parsed_invoice,
            uploaded_at=parsed_invoice.invoice_date
        )
        
        # Step 4: Convert historical ParsedInvoices to Invoice models
        historical_invoices = [
            Invoice(
                id=f"hist-{hist.invoice_number}",
                parsed_data=hist,
                uploaded_at=hist.invoice_date
            )
            for hist in historical_parsed
        ]
        
        # Step 5: Perform anomaly analysis
        # Create a temporary storage service with historical invoices
        from app.services.storage_service import StorageService
        temp_storage = StorageService()
        
        # Add historical invoices to storage
        for hist_inv in historical_invoices:
            temp_storage._invoices[hist_inv.id] = hist_inv
        
        # Create anomaly service with temporary storage
        anomaly_service = AnomalyService(temp_storage)
        
        # Analyze the invoice
        anomaly_result = anomaly_service.analyze_invoice(invoice)
        
        # Step 6: Format response
        reasons = []
        if anomaly_result.anomalies:
            for anomaly in anomaly_result.anomalies:
                reasons.append(anomaly.description)
        else:
            reasons.append("No anomalies detected.")
        
        # Add overall explanation
        if anomaly_result.explanation:
            reasons.insert(0, anomaly_result.explanation)
        
        return AnalyzeInvoiceResponse(
            risk_score=anomaly_result.risk_score,
            status="suspicious" if anomaly_result.is_suspicious else "normal",
            reasons=reasons,
            invoice_id=request.invoice_id,
            vendor_name=parsed_invoice.vendor_name
        )
    
    except ParsingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch or parse invoice from ERPNext: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze invoice: {str(e)}"
        )


@router.get("/health")
async def erpnext_health():
    """
    Check ERPNext integration health and verify API key.
    Makes a real request to ERPNext to distinguish:
    - not configured / invalid key / unreachable / connected.
    """
    if not erpnext_client:
        return {
            "configured": False,
            "message": "ERPNext integration not configured"
        }
    try:
        # Verify credentials with a real call (Frappe: get logged user)
        response = erpnext_client.session.get(
            f"{erpnext_client.base_url}/api/method/frappe.auth.get_logged_user",
            timeout=10
        )
        if response.status_code == 401:
            return {
                "configured": True,
                "base_url": Config.ERPNEXT_BASE_URL,
                "status": "invalid_credentials",
                "message": "API key or secret is wrong. In ERPNext: User → API Access → generate new keys."
            }
        if response.status_code == 403:
            return {
                "configured": True,
                "base_url": Config.ERPNEXT_BASE_URL,
                "status": "forbidden",
                "message": "API user does not have permission. Grant the user access or use a user with API Access."
            }
        response.raise_for_status()
        return {
            "configured": True,
            "base_url": Config.ERPNEXT_BASE_URL,
            "status": "connected",
            "user": response.json().get("message") if response.text else None
        }
    except Exception as e:
        err = str(e).lower()
        if "timeout" in err or "connection" in err or "unreachable" in err:
            return {
                "configured": True,
                "base_url": Config.ERPNEXT_BASE_URL,
                "status": "unreachable",
                "message": f"Cannot reach ERPNext at {Config.ERPNEXT_BASE_URL}. Check URL and network.",
                "error": str(e)
            }
        return {
            "configured": True,
            "base_url": Config.ERPNEXT_BASE_URL,
            "status": "error",
            "error": str(e)
        }
