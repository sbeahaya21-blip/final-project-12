"""API views/endpoints for invoice operations."""
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query
from fastapi.responses import JSONResponse
from typing import List
from app.models.invoice import Invoice
from app.models.anomaly import AnomalyResult
from app.controllers.invoice_controller import InvoiceController
from app.controllers.anomaly_controller import AnomalyController
from app.exceptions import InvoiceNotFoundError, ParsingError, InvalidInvoiceFormatError
from app.services.parser_service import ParserService
from app.services.anomaly_service import AnomalyService
from app.services.storage_service import StorageService

# Initialize services (dependency injection would be better, but keeping it simple)
storage_service = StorageService()
parser_service = ParserService()
anomaly_service = AnomalyService(storage_service)
invoice_controller = InvoiceController(parser_service, storage_service)
anomaly_controller = AnomalyController(anomaly_service, invoice_controller)

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


@router.post("/upload", response_model=Invoice, status_code=status.HTTP_201_CREATED)
async def upload_invoice(
    file: UploadFile = File(...),
    sync_to_erpnext: bool = Query(False, description="DEPRECATED: Use submit-to-erpnext endpoint instead")
):
    """
    Upload and parse an invoice file.
    
    Args:
        file: Invoice file to upload
        sync_to_erpnext: DEPRECATED - This parameter is ignored. Use the submit-to-erpnext endpoint instead.
    
    Returns:
        The parsed invoice with ID.
    """
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Received upload request for file: {file.filename}")
        file_content = await file.read()
        logger.info(f"File read successfully, size: {len(file_content)} bytes")
        
        invoice = invoice_controller.upload_and_parse_invoice(
            file_content, file.filename or "unknown"
        )
        logger.info(f"Invoice parsed successfully, ID: {invoice.id}")
        
        # Analyze invoice to get risk score
        try:
            updated_invoice, analysis_result = anomaly_controller.analyze_invoice(invoice.id)
            logger.info(f"Invoice analyzed - Risk Score: {analysis_result.risk_score}/100")
            # Update invoice with analysis results
            invoice = updated_invoice
        except Exception as e:
            logger.warning(f"Could not analyze invoice: {str(e)}")
        
        # Note: sync_to_erpnext parameter is deprecated - invoices should be submitted manually
        # via the submit-to-erpnext endpoint after review
        if sync_to_erpnext:
            logger.warning("⚠ sync_to_erpnext parameter is deprecated. Use POST /api/invoices/{id}/submit-to-erpnext instead.")
        
        return invoice
    except ParsingError as e:
        logger.error(f"Parsing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process invoice: {str(e)}"
        )


@router.post("/create", response_model=Invoice, status_code=status.HTTP_201_CREATED)
async def create_invoice(invoice_data: dict):
    """
    Create an invoice from JSON data (useful for testing).
    
    Expected format:
    {
        "vendor_name": "Vendor ABC",
        "invoice_number": "INV-001",
        "invoice_date": "2024-01-15T10:00:00",
        "total_amount": 1000.0,
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
    """
    try:
        invoice = invoice_controller.create_invoice_from_data(invoice_data)
        return invoice
    except InvalidInvoiceFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create invoice: {str(e)}"
        )


@router.get("", response_model=List[Invoice])
async def list_invoices():
    """List all invoices."""
    return invoice_controller.list_invoices()


@router.post("/{invoice_id}/analyze", response_model=AnomalyResult)
async def analyze_invoice(invoice_id: str):
    """
    Analyze an invoice for anomalies and potential fraud.
    
    Returns risk score (0-100) and human-readable explanation.
    """
    try:
        invoice, anomaly_result = anomaly_controller.analyze_invoice(invoice_id)
        return anomaly_result
    except InvoiceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze invoice: {str(e)}"
        )


@router.post("/{invoice_id}/submit-to-erpnext", response_model=Invoice)
async def submit_to_erpnext(invoice_id: str):
    """
    Submit an invoice to ERPNext (create Purchase Invoice).
    
    This endpoint allows manual submission after reviewing the invoice.
    """
    import logging
    from app.services.erpnext_client import ERPNextClient
    from app.config import Config
    
    logger = logging.getLogger(__name__)
    logger.info("Submit-to-ERPNext called with invoice_id=%r (len=%s)", invoice_id, len(invoice_id))
    print(f"[Submit] POST submit-to-erpnext invoice_id={invoice_id!r}")  # visible in terminal
    print(f"[Submit] Route matched! Processing submit request...")  # Confirm route matched
    try:
        # Get invoice
        invoice = invoice_controller.get_invoice(invoice_id)
        
        # Check if already submitted
        if invoice.submitted_to_erpnext:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invoice {invoice_id} has already been submitted to ERPNext"
            )
        
        # Validate ERPNext config
        if not Config.validate_erpnext_config():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ERPNext is not configured. Please set ERPNEXT_BASE_URL, ERPNEXT_API_KEY, and ERPNEXT_API_SECRET"
            )
        
        # Analyze invoice first to get risk score
        risk_score = None
        risk_explanation = None
        try:
            updated_invoice, analysis_result = anomaly_controller.analyze_invoice(invoice.id)
            risk_score = analysis_result.risk_score
            risk_explanation = analysis_result.explanation
            invoice = updated_invoice
            logger.info(f"Invoice analyzed - Risk Score: {risk_score}/100")
        except Exception as e:
            logger.warning(f"Could not analyze invoice before ERPNext submission: {str(e)}")
        
        # Submit to ERPNext
        erpnext_client = ERPNextClient(
            base_url=Config.ERPNEXT_BASE_URL,
            api_key=Config.ERPNEXT_API_KEY,
            api_secret=Config.ERPNEXT_API_SECRET
        )
        
        logger.info(f"Submitting invoice {invoice_id} to ERPNext...")
        erpnext_result = erpnext_client.create_purchase_invoice(
            invoice.parsed_data,
            risk_score=risk_score,
            risk_explanation=risk_explanation
        )
        
        erpnext_invoice_name = erpnext_result.get('data', {}).get('name', 'unknown')
        logger.info(f"✓ Invoice submitted to ERPNext: {erpnext_invoice_name}")
        
        # Update invoice with submission status
        invoice.submitted_to_erpnext = True
        invoice.erpnext_invoice_name = erpnext_invoice_name
        invoice_controller.storage.save(invoice)
        
        return invoice
        
    except InvoiceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit invoice to ERPNext: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit invoice to ERPNext: {str(e)}"
        )


@router.get("/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: str):
    """Get invoice details by ID."""
    try:
        return invoice_controller.get_invoice(invoice_id)
    except InvoiceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{invoice_id}", status_code=status.HTTP_200_OK)
async def delete_invoice(invoice_id: str):
    """
    Delete an invoice by ID.
    
    Returns success message.
    """
    try:
        invoice_controller.delete_invoice(invoice_id)
        return {"message": f"Invoice {invoice_id} deleted successfully", "deleted": True}
    except InvoiceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete invoice: {str(e)}"
        )
