"""Page Object Model for Invoice Upload page."""
from playwright.sync_api import Page, expect


class InvoicePage:
    """Page Object for the Invoice Upload and Analysis page."""
    
    def __init__(self, page: Page):
        self.page = page
        self.upload_section = page.locator("#uploadSection")
        self.file_input = page.locator("#fileInput")
        self.upload_button = page.locator("label.upload-btn")
        self.file_name = page.locator("#fileName")
        self.results = page.locator("#results")
    
    def navigate(self, base_url: str = "http://localhost:8000"):
        """Navigate to the invoice page."""
        self.page.goto(f"{base_url}/static/index.html")
        expect(self.page.locator("h1")).to_contain_text("Invoice Parser")
    
    def upload_file(self, file_path: str):
        """Upload a file using the file input."""
        self.file_input.set_input_files(file_path)
    
    def upload_file_via_drag_drop(self, file_path: str):
        """Upload a file via drag and drop."""
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Create a DataTransfer object simulation
        self.page.evaluate(
            """
            (fileContent, fileName) => {
                const dataTransfer = new DataTransfer();
                const file = new File([fileContent], fileName, { type: 'application/pdf' });
                dataTransfer.items.add(file);
                const event = new DragEvent('drop', { dataTransfer });
                document.getElementById('uploadSection').dispatchEvent(event);
            }
            """,
            file_content,
            file_path.split('/')[-1]
        )
    
    def wait_for_processing(self, timeout: int = 10000):
        """Wait for invoice processing to complete."""
        # Wait for loading to disappear and results to appear
        self.page.wait_for_selector(".loading", state="hidden", timeout=timeout)
        self.page.wait_for_selector(".invoice-card, .error", timeout=timeout)
    
    def get_risk_score(self) -> int:
        """Get the risk score from results."""
        risk_score_text = self.page.locator(".risk-score").text_content()
        # Extract number from text like "Risk Score: 75/100"
        import re
        match = re.search(r'(\d+)/100', risk_score_text)
        return int(match.group(1)) if match else 0
    
    def is_suspicious(self) -> bool:
        """Check if invoice is marked as suspicious."""
        suspicious_text = self.page.locator(".risk-score").text_content()
        return "SUSPICIOUS" in suspicious_text
    
    def get_explanation(self) -> str:
        """Get the explanation text."""
        return self.page.locator(".explanation").text_content()
    
    def get_vendor_name(self) -> str:
        """Get the vendor name from invoice details."""
        return self.page.locator(".invoice-details p").filter(has_text="Vendor:").text_content()
    
    def get_invoice_number(self) -> str:
        """Get the invoice number from invoice details."""
        return self.page.locator(".invoice-details p").filter(has_text="Invoice #:").text_content()
    
    def get_total_amount(self) -> float:
        """Get the total amount from invoice details."""
        amount_text = self.page.locator(".invoice-details p").filter(has_text="Total Amount:").text_content()
        # Extract number from text like "Total Amount: $1000.00"
        import re
        match = re.search(r'\$?([\d,]+\.?\d*)', amount_text)
        return float(match.group(1).replace(',', '')) if match else 0.0
    
    def has_error(self) -> bool:
        """Check if there's an error message."""
        return self.page.locator(".error").is_visible()
    
    def get_error_message(self) -> str:
        """Get the error message if present."""
        return self.page.locator(".error").text_content()
    
    def get_anomalies_count(self) -> int:
        """Get the number of detected anomalies."""
        return self.page.locator(".anomaly-item").count()
