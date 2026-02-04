"""ERPNext REST API client service."""
import requests
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.invoice import ParsedInvoice, InvoiceItem
from app.exceptions import ParsingError


class ERPNextClient:
    """Client for communicating with ERPNext REST API."""
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        api_secret: str
    ):
        """
        Initialize ERPNext client.
        
        Args:
            base_url: ERPNext instance URL (e.g., "https://your-instance.erpnext.com")
            api_key: ERPNext API Key
            api_secret: ERPNext API Secret
        """
        self.base_url = base_url.rstrip('/')
        # Strip in case config had trailing newlines (e.g. from .env)
        self.api_key = (api_key or '').strip()
        self.api_secret = (api_secret or '').strip()
        self.session = requests.Session()
        # Frappe/ERPNext expect: Authorization: token api_key:api_secret
        self.session.headers.update({
            'Authorization': f'token {self.api_key}:{self.api_secret}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to ERPNext API."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 401:
                raise ParsingError(
                    "ERPNext API key or secret is invalid. "
                    "In ERPNext: User → Settings → API Access → Generate Keys. Check ERPNEXT_API_KEY and ERPNEXT_API_SECRET."
                )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ParsingError(f"Failed to fetch from ERPNext: {str(e)}")
    
    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to ERPNext API."""
        url = f"{self.base_url}{endpoint}"
        try:
            # Reduced timeout to prevent hanging (15 seconds instead of 30)
            response = self.session.post(url, json=data, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout as e:
            raise ParsingError(f"ERPNext request timed out after 15 seconds: {endpoint}. ERPNext may be slow or unreachable.")
        except requests.exceptions.HTTPError as e:
            error_detail = ""
            error_message = ""
            response_text = ""
            status_code = "Unknown"
            
            # Properly access the response object
            response = getattr(e, 'response', None)
            if response is not None:
                status_code = response.status_code
                if status_code == 401:
                    raise ParsingError(
                        "ERPNext API key or secret is invalid. "
                        "In ERPNext: User → Settings → API Access → Generate Keys. Check ERPNEXT_API_KEY and ERPNEXT_API_SECRET."
                    )
                # Get the raw response text first
                try:
                    response_text = response.text if response.text else ""
                except:
                    response_text = ""
                
                # Try to get JSON error response
                try:
                    error_json = response.json()
                    # ERPNext error format: {"message": "...", "exc_type": "...", "exception": "..."}
                    if isinstance(error_json, dict):
                        error_message = (
                            error_json.get('message', '') or 
                            error_json.get('exception', '') or 
                            error_json.get('exc', '') or
                            error_json.get('exc_type', '') or
                            str(error_json)
                        )
                    else:
                        error_message = str(error_json)
                except:
                    # If not JSON, use the text directly
                    error_message = response_text[:1000] if response_text else str(e)
                
                error_detail = f"Status: {status_code}, Response: {error_message}"
            else:
                error_detail = f"Status: Unknown, Error: {str(e)}"
            
            # Log the full error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"ERPNext API Error - URL: {url}")
            logger.error(f"ERPNext API Error - Status: {status_code}")
            logger.error(f"ERPNext API Error - Response Text: {response_text[:2000] if response_text else 'No response text'}")
            logger.error(f"ERPNext API Error - Error Message: {error_message if error_message else 'No error message'}")
            logger.error(f"ERPNext API Error - Request Data: {str(data)[:500]}")
            
            raise ParsingError(f"Failed to post to ERPNext {endpoint}: {str(e)}. Details: {error_detail}")
        except requests.exceptions.RequestException as e:
            raise ParsingError(f"Failed to post to ERPNext: {str(e)}")
    
    def test_document_type(self, doc_type: str) -> bool:
        """
        Test if a document type exists in ERPNext.
        
        Args:
            doc_type: Document type name to test (e.g., "Purchase Invoice")
        
        Returns:
            True if document type exists, False otherwise
        """
        try:
            # Try to get document list (limit 1) to test if doctype exists
            response = self.session.get(
                f"{self.base_url}/api/resource/{doc_type}",
                params={"limit_page_length": 1},
                timeout=10
            )
            # 200 or 404 are both valid responses (404 means doctype doesn't exist)
            return response.status_code == 200
        except:
            return False
    
    def get_purchase_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """
        Fetch a purchase invoice from ERPNext.
        
        Args:
            invoice_id: Purchase Invoice ID (e.g., "PINV-0001")
        
        Returns:
            Purchase Invoice document data
        """
        endpoint = f"/api/resource/Purchase Invoice/{invoice_id}"
        return self._get(endpoint)
    
    def get_purchase_invoices_by_supplier(
        self, supplier: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical purchase invoices for a supplier.
        
        Args:
            supplier: Supplier name
            limit: Maximum number of invoices to fetch
        
        Returns:
            List of Purchase Invoice documents
        """
        endpoint = "/api/resource/Purchase Invoice"
        params = {
            'filters': f'[["supplier", "=", "{supplier}"]]',
            'fields': '["name", "supplier", "posting_date", "grand_total", "items"]',
            'limit_page_length': limit,
            'order_by': 'posting_date desc'
        }
        result = self._get(endpoint, params=params)
        return result.get('data', [])
    
    def parse_erpnext_invoice(self, erpnext_data: Dict[str, Any]) -> ParsedInvoice:
        """
        Convert ERPNext Purchase Invoice to ParsedInvoice model.
        
        Args:
            erpnext_data: ERPNext Purchase Invoice document
        
        Returns:
            ParsedInvoice object
        """
        try:
            # Extract invoice items
            items = []
            erpnext_items = erpnext_data.get('items', [])
            
            for item in erpnext_items:
                item_name = item.get('item_name') or item.get('item_code', 'Unknown Item')
                quantity = float(item.get('qty', 0))
                rate = float(item.get('rate', 0))
                amount = float(item.get('amount', quantity * rate))
                
                items.append(InvoiceItem(
                    name=item_name,
                    quantity=quantity,
                    unit_price=rate,
                    total_price=amount
                ))
            
            # Parse date
            posting_date_str = erpnext_data.get('posting_date')
            if posting_date_str:
                try:
                    invoice_date = datetime.strptime(posting_date_str, '%Y-%m-%d')
                except:
                    invoice_date = datetime.now()
            else:
                invoice_date = datetime.now()
            
            # Extract vendor/supplier
            vendor_name = erpnext_data.get('supplier', 'Unknown Supplier')
            
            # Extract invoice number
            invoice_number = erpnext_data.get('name', 'UNKNOWN')
            
            # Extract total amount
            total_amount = float(erpnext_data.get('grand_total', 0))
            
            # Extract currency
            currency = erpnext_data.get('currency', 'USD')
            
            return ParsedInvoice(
                vendor_name=vendor_name,
                invoice_number=invoice_number,
                invoice_date=invoice_date,
                total_amount=total_amount,
                items=items,
                currency=currency
            )
        except Exception as e:
            raise ParsingError(f"Failed to parse ERPNext invoice data: {str(e)}")
    
    def fetch_and_parse_invoice(self, invoice_id: str) -> ParsedInvoice:
        """
        Fetch and parse a purchase invoice from ERPNext.
        
        Args:
            invoice_id: Purchase Invoice ID
        
        Returns:
            ParsedInvoice object
        """
        erpnext_data = self.get_purchase_invoice(invoice_id)
        return self.parse_erpnext_invoice(erpnext_data)
    
    def fetch_historical_invoices(
        self, supplier: str, exclude_invoice_id: Optional[str] = None
    ) -> List[ParsedInvoice]:
        """
        Fetch and parse historical invoices for a supplier.
        
        Args:
            supplier: Supplier name
            exclude_invoice_id: Invoice ID to exclude from results
        
        Returns:
            List of ParsedInvoice objects
        """
        erpnext_invoices = self.get_purchase_invoices_by_supplier(supplier)
        parsed_invoices = []
        
        for erpnext_data in erpnext_invoices:
            # Skip the invoice we're analyzing
            if exclude_invoice_id and erpnext_data.get('name') == exclude_invoice_id:
                continue
            
            try:
                parsed_invoice = self.parse_erpnext_invoice(erpnext_data)
                parsed_invoices.append(parsed_invoice)
            except Exception as e:
                # Log error but continue processing other invoices
                print(f"Warning: Failed to parse invoice {erpnext_data.get('name')}: {e}")
                continue
        
        return parsed_invoices
    
    def create_purchase_invoice(self, parsed_invoice: ParsedInvoice, risk_score: Optional[int] = None, risk_explanation: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a Purchase Invoice in ERPNext from a ParsedInvoice.
        
        Args:
            parsed_invoice: ParsedInvoice object with invoice data
        
        Returns:
            Created Purchase Invoice document data
        """
        # First, check if supplier exists, if not create it
        supplier_name = parsed_invoice.vendor_name
        
        # Check if supplier exists
        try:
            supplier_check = self._get(f"/api/resource/Supplier/{supplier_name}")
        except:
            # Supplier doesn't exist, create it
            try:
                supplier_data = {
                    "supplier_name": supplier_name,
                    "supplier_type": "Company",
                    "supplier_group": "All Supplier Groups"
                }
                self._post("/api/resource/Supplier", supplier_data)
            except Exception as e:
                # If supplier creation fails, continue anyway (might already exist)
                pass
        
        # Prepare Purchase Invoice data
        # Note: ERPNext typically requires a "company" field - try to get default company
        # If not available, we'll let ERPNext error tell us what's needed
        # Set due_date to past date so invoice shows as "Overdue" when submitted
        from datetime import datetime, timedelta
        invoice_date = parsed_invoice.invoice_date
        # Set due_date to 30 days ago to ensure it shows as overdue
        due_date = (datetime.now() - timedelta(days=30)).date()
        # But if invoice_date is older, use that instead
        if invoice_date.date() < due_date:
            due_date = invoice_date.date()
        
        invoice_data = {
            "doctype": "Purchase Invoice",
            "supplier": supplier_name,
            "posting_date": invoice_date.strftime("%Y-%m-%d"),
            "due_date": due_date.strftime("%Y-%m-%d"),
            "bill_no": parsed_invoice.invoice_number,
            "bill_date": invoice_date.strftime("%Y-%m-%d"),
            "items": [],
            "currency": parsed_invoice.currency,
        }
        
        # Try to get default company from ERPNext (if available)
        company_name = None
        try:
            # Try to get company list - use first available company
            companies = self._get("/api/resource/Company?limit_page_length=1")
            if companies.get("data") and len(companies["data"]) > 0:
                company_name = companies["data"][0].get("name", "")
                invoice_data["company"] = company_name
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Found company: {company_name}")
        except Exception as e:
            # If we can't get company, try common default names
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not fetch company list: {str(e)}")
            # Try common default company names
            for default_company in ["Your Company", "Company", "Default Company"]:
                try:
                    # Test if company exists
                    test_company = self._get(f"/api/resource/Company/{default_company}")
                    if test_company.get("name"):
                        invoice_data["company"] = default_company
                        logger.info(f"Using default company: {default_company}")
                        break
                except:
                    continue
        
        # If still no company, ERPNext will error and tell us what's needed
        if "company" not in invoice_data:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("No company field set - ERPNext may require it")
        
        # Create items in ERPNext if they don't exist (BEFORE creating invoice)
        # ERPNext requires items to exist before they can be used in Purchase Invoice
        import logging
        logger = logging.getLogger(__name__)
        
        for item in parsed_invoice.items:
            item_code = item.name
            try:
                # Check if item exists
                self._get(f"/api/resource/Item/{item_code}")
                logger.info(f"Item '{item_code}' already exists in ERPNext")
            except:
                # Item doesn't exist, create it
                try:
                    logger.info(f"Creating item '{item_code}' in ERPNext...")
                    item_data = {
                        "doctype": "Item",
                        "item_code": item_code,
                        "item_name": item.name,
                        "item_group": "Products",  # Default item group
                        "stock_uom": "Nos",  # Default unit of measure
                        "is_stock_item": 0,  # Not a stock item (service item)
                    }
                    self._post("/api/resource/Item", item_data)
                    logger.info(f"✓ Item '{item_code}' created successfully")
                except Exception as item_error:
                    logger.warning(f"Could not create item '{item_code}': {str(item_error)}")
                    # Continue anyway - ERPNext might allow using item_name directly
        
        # Add items with proper ERPNext structure (after ensuring they exist)
        for item in parsed_invoice.items:
            # Determine UOM based on quantity type
            # "Nos" requires integer quantities, so use "Unit" for decimals
            qty = item.quantity
            if qty == int(qty):
                # Integer quantity - use "Nos"
                uom = "Nos"
            else:
                # Decimal quantity - use "Unit" which allows decimals
                uom = "Unit"
            
            item_data = {
                "doctype": "Purchase Invoice Item",
                "item_code": item.name,  # Use item name as item code
                "item_name": item.name,
                "qty": qty,
                "rate": item.unit_price,
                "amount": item.total_price,
                "uom": uom
            }
            invoice_data["items"].append(item_data)
        
        # Log the invoice data being sent (for debugging)
        logger.info(f"Creating Purchase Invoice with data: {str(invoice_data)[:500]}")
        
        # Create the Purchase Invoice
        # Use "Purchase Invoice" (with space) - this is the correct document type name
        endpoint = "/api/resource/Purchase Invoice"
        
        try:
            result = self._post(endpoint, invoice_data)
            working_doc_type = "Purchase Invoice"
        except ParsingError as e:
            # If it's a 404, the document type might be different
            if "404" in str(e) or "NOT FOUND" in str(e):
                raise ParsingError(
                    f"Purchase Invoice document type not found in ERPNext. "
                    f"Please verify your ERPNext installation has the Purchase Invoice doctype enabled. "
                    f"Error: {str(e)}"
                )
            else:
                # Re-raise other errors
                raise
        
        invoice_name = result.get("data", {}).get("name", "Unknown")
        
        # Add risk score as a comment in ERPNext (if provided)
        if risk_score is not None:
            try:
                import logging
                import time
                logger = logging.getLogger(__name__)
                logger.info(f"Adding risk score ({risk_score}/100) to ERPNext invoice {invoice_name}...")
                
                # Small delay to ensure invoice is fully saved
                time.sleep(0.3)
                
                # Create a comment with risk score information
                comment_text = f"🤖 AI Risk Score: {risk_score}/100"
                if risk_explanation:
                    # Limit explanation length and format it nicely
                    explanation_short = risk_explanation[:300] + "..." if len(risk_explanation) > 300 else risk_explanation
                    comment_text += f"\n\nRisk Analysis:\n{explanation_short}"
                
                comment_data = {
                    "doctype": "Comment",
                    "reference_doctype": "Purchase Invoice",
                    "reference_name": invoice_name,
                    "content": comment_text,
                    "comment_type": "Comment"
                }
                
                try:
                    self._post("/api/resource/Comment", comment_data)
                    logger.info(f"✓ Risk score added as comment to invoice {invoice_name}")
                except Exception as comment_error:
                    # If comment creation fails, try adding to notes field instead
                    logger.warning(f"Could not add comment, trying notes field: {str(comment_error)}")
                    try:
                        # Fetch the invoice first
                        fresh_doc = self._get(f"/api/resource/{working_doc_type}/{invoice_name}")
                        doc_data = fresh_doc.get("data", {})
                        
                        # Update the invoice with notes field containing risk score
                        doc_data["notes"] = f"AI Risk Score: {risk_score}/100"
                        if risk_explanation:
                            doc_data["notes"] += f"\n\n{risk_explanation[:500]}"
                        
                        # Use PUT method to update the document
                        url = f"{self.base_url}/api/resource/{working_doc_type}/{invoice_name}"
                        response = self.session.put(url, json=doc_data, timeout=15)
                        response.raise_for_status()
                        logger.info(f"✓ Risk score added to notes field")
                    except Exception as update_error:
                        logger.warning(f"Could not add risk score to ERPNext invoice: {str(update_error)}")
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to add risk score to ERPNext: {str(e)}")
        
        # Auto-submit the invoice using ERPNext's method API
        if working_doc_type:
            try:
                import logging
                import time
                logger = logging.getLogger(__name__)
                logger.info(f"Submitting invoice {invoice_name} in ERPNext...")
                
                # Small delay to ensure document is fully saved
                time.sleep(0.5)
                
                # Fetch the document fresh to get the latest timestamp
                fresh_doc = self._get(f"/api/resource/{working_doc_type}/{invoice_name}")
                doc_data = fresh_doc.get("data", {})
                
                # ERPNext submit uses method API - need to pass the full doc object
                submit_data = {
                    "doc": doc_data  # Pass the full document object
                }
                
                # Use POST to frappe.client.submit endpoint
                url = f"{self.base_url}/api/method/frappe.client.submit"
                response = self.session.post(url, json=submit_data, timeout=15)
                response.raise_for_status()
                
                submit_result = response.json()
                logger.info(f"✓ Invoice {invoice_name} submitted successfully in ERPNext")
            except Exception as e:
                # If submit fails, invoice is still created as draft
                import logging
                import traceback
                logger = logging.getLogger(__name__)
                logger.error(f"✗ Failed to auto-submit invoice {invoice_name}: {str(e)}")
                logger.error(f"  Error type: {type(e).__name__}")
                logger.error(f"  Traceback: {traceback.format_exc()}")
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_detail = e.response.text
                        logger.error(f"  ERPNext response: {error_detail}")
                    except:
                        pass
                logger.warning("⚠ Invoice created as Draft - you can submit it manually in ERPNext")
                logger.info(f"📋 View draft invoice: {self.base_url}/app/purchase-invoice/{invoice_name}")
        
        # Notification feature can be added later if needed
        # For now, we'll skip it since the method doesn't exist
        
        return result