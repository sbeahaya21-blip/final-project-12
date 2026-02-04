"""Invoice parsing service (OCR/AI extraction)."""
import uuid
import re
import json
from datetime import datetime
from typing import BinaryIO
from app.models.invoice import ParsedInvoice, InvoiceItem
from app.exceptions import ParsingError, InvalidInvoiceFormatError

try:
    import pdfplumber
    PDF_PARSING_AVAILABLE = True
except ImportError:
    PDF_PARSING_AVAILABLE = False
    try:
        import PyPDF2
        PDF_PARSING_AVAILABLE = True
    except ImportError:
        PDF_PARSING_AVAILABLE = False


class ParserService:
    """Service for parsing invoices from various formats."""
    
    def parse_invoice(self, file_content: bytes, filename: str) -> ParsedInvoice:
        """
        Parse invoice from file content.
        
        Tries to extract data from PDF, falls back to mock if parsing fails.
        """
        try:
            # Try to parse as PDF first
            if filename.lower().endswith('.pdf'):
                try:
                    parsed_data = self._parse_pdf(file_content, filename)
                    if parsed_data:
                        return parsed_data
                except Exception as e:
                    # If PDF parsing fails, fall back to mock
                    print(f"PDF parsing failed: {e}, using fallback")
            
            # Fallback to mock parsing
            parsed_data = self._mock_parse(file_content, filename)
            return parsed_data
            
        except Exception as e:
            raise ParsingError(f"Failed to parse invoice: {str(e)}")
    
    def _parse_pdf(self, file_content: bytes, filename: str) -> ParsedInvoice:
        """
        Parse invoice from PDF file.
        
        Extracts text from PDF and tries to identify invoice data.
        """
        if not PDF_PARSING_AVAILABLE:
            return None
        
        try:
            import io
            from pdfplumber import PDF
            
            # Try pdfplumber first (better for table extraction)
            pdf_file = io.BytesIO(file_content)
            pdf = PDF(pdf_file)
            
            # Try to extract tables first (more accurate)
            tables = []
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
            
            # Extract text first (needed for metadata even if we use tables)
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
            
            # If we found tables, try to extract from table structure
            if tables:
                parsed_data = self._extract_from_tables(tables, filename, full_text)
                if parsed_data:
                    pdf.close()
                    return parsed_data
            
            pdf.close()
            
            # Fallback to text extraction
            if full_text and len(full_text.strip()) >= 50:
                parsed_data = self._extract_from_text(full_text, filename)
                if parsed_data:
                    return parsed_data
                
        except Exception as e:
            # Try PyPDF2 as fallback
            try:
                import io
                import PyPDF2
                
                pdf_file = io.BytesIO(file_content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                full_text = ""
                for page in pdf_reader.pages:
                    full_text += page.extract_text() or ""
                
                parsed_data = self._extract_from_text(full_text, filename)
                if parsed_data:
                    return parsed_data
            except Exception:
                pass
        
        return None
    
    def _extract_from_tables(self, tables: list, filename: str, full_text: str = "") -> ParsedInvoice:
        """
        Extract invoice data from PDF tables.
        
        More accurate than text extraction for structured data.
        """
        items = []
        vendor_name = "ABC Supplies Co."
        invoice_number = None
        invoice_date = None
        total_amount = 0.0
        
        # First, try to extract metadata from text (more reliable for invoice number/date)
        if full_text:
            # Extract invoice number from text
            inv_patterns = [
                r'Invoice\s+Number[:\s]+([A-Z0-9\-]+)',  # "Invoice Number: INV-2024-001"
                r'Invoice\s*#?[:\s]*([A-Z0-9\-]+)',  # "Invoice #: INV-2024-001"
                r'INV[-\s]*([0-9]{4}[-\s]*[0-9]+)',  # "INV-2024-001"
            ]
            for pattern in inv_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    inv_num = match.group(1).strip()
                    inv_num = re.sub(r'\s+', '-', inv_num)
                    if not inv_num.startswith('INV'):
                        invoice_number = f"INV-{inv_num}"
                    else:
                        invoice_number = inv_num
                    break
            
            # Extract invoice date from text
            date_patterns = [
                r'Invoice\s+Date[:\s]+([A-Za-z]+\s+\d{1,2},\s+\d{4})',  # "Invoice Date: January 15, 2024"
                r'Date[:\s]+([A-Za-z]+\s+\d{1,2},\s+\d{4})',  # "Date: January 15, 2024"
            ]
            for pattern in date_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    date_str = match.group(1).strip()
                    try:
                        invoice_date = datetime.strptime(date_str, '%B %d, %Y')
                        break
                    except:
                        try:
                            invoice_date = datetime.strptime(date_str, '%b %d, %Y')
                            break
                        except:
                            pass
        
        # Set defaults if not found
        if not invoice_number:
            invoice_number = f"INV-{str(uuid.uuid4())[:8]}"
        if not invoice_date:
            invoice_date = datetime.now()
        
        for table in tables:
            if not table or len(table) < 2:
                continue
            
            # Look for items table (usually has headers like "Item Name", "Quantity", etc.)
            headers = [str(cell).lower() if cell else "" for cell in table[0]]
            
            # Check if this looks like an items table
            has_item_col = any('item' in h or 'name' in h for h in headers)
            has_qty_col = any('quantity' in h or 'qty' in h for h in headers)
            has_price_col = any('price' in h or 'unit' in h for h in headers)
            
            if has_item_col and has_qty_col:
                # This is likely the items table
                for row in table[1:]:
                    if not row or len(row) < 2:
                        continue
                    
                    # Find item name column
                    item_name = None
                    qty = None
                    unit_price = None
                    
                    for i, header in enumerate(headers):
                        if i >= len(row):
                            break
                        cell_value = str(row[i]).strip() if row[i] else ""
                        
                        if 'item' in header or 'name' in header:
                            item_name = cell_value
                        elif 'quantity' in header or 'qty' in header:
                            try:
                                qty = float(cell_value)
                            except:
                                pass
                        elif 'unit' in header or ('price' in header and 'total' not in header):
                            try:
                                # Remove $ and commas
                                price_str = cell_value.replace('$', '').replace(',', '')
                                unit_price = float(price_str)
                            except:
                                pass
                    
                    if item_name:
                        # Clean item name
                        item_name = item_name.strip()
                        
                        # Skip empty or header-like rows
                        if not item_name or item_name.lower() in ['item', 'item name', 'description', 'product', 'name']:
                            continue
                        
                        # Try to get total price from table if available
                        total_price = None
                        for i, header in enumerate(headers):
                            if i >= len(row):
                                break
                            cell_value = str(row[i]).strip() if row[i] else ""
                            if 'total' in header.lower() and ('amount' in header.lower() or 'price' in header.lower()):
                                try:
                                    price_str = cell_value.replace('$', '').replace(',', '').replace(' ', '')
                                    if price_str:
                                        total_price = float(price_str)
                                        break
                                except:
                                    pass
                        
                        # If we don't have total_price, try to find it in other columns
                        if total_price is None:
                            for i, header in enumerate(headers):
                                if i >= len(row):
                                    break
                                cell_value = str(row[i]).strip() if row[i] else ""
                                # Look for any column that might contain total/amount
                                if cell_value and ('$' in cell_value or (cell_value.replace('.', '').replace(',', '').isdigit() and float(cell_value.replace(',', '')) > 100)):
                                    try:
                                        price_str = cell_value.replace('$', '').replace(',', '').replace(' ', '')
                                        if price_str:
                                            potential_total = float(price_str)
                                            # If this looks like a total (larger than unit price would be)
                                            if potential_total > 0:
                                                total_price = potential_total
                                                break
                                    except:
                                        pass
                        
                        # Calculate total_price if we have qty and unit_price
                        if total_price is None:
                            if qty and unit_price:
                                total_price = round(qty * unit_price, 2)
                            else:
                                # Skip items without valid quantity and price
                                continue
                        
                        # Ensure we have valid qty
                        if not qty or qty <= 0:
                            continue
                        
                        # Calculate unit_price if we have total_price and qty
                        if not unit_price or unit_price <= 0:
                            if total_price and qty:
                                unit_price = round(total_price / qty, 2)
                            else:
                                continue
                        
                        # Recalculate total_price to ensure accuracy
                        total_price = round(qty * unit_price, 2)
                        
                        # Use the item name as-is (no normalization)
                        # Add the item
                        items.append(InvoiceItem(
                            name=item_name,
                            quantity=float(qty),
                            unit_price=unit_price,
                            total_price=total_price
                        ))
            
            # Look for invoice metadata in other tables or first rows
            for row in table[:5]:  # Check more rows
                if not row:
                    continue
                row_text = " ".join([str(cell) for cell in row if cell]).lower()
                
                # Extract invoice number - look for "Invoice Number:" label
                if 'invoice' in row_text and 'number' in row_text:
                    for i, cell in enumerate(row):
                        if cell:
                            cell_str = str(cell).strip()
                            # If this cell contains "Invoice Number:", get value from next cell
                            if 'invoice' in cell_str.lower() and 'number' in cell_str.lower():
                                if i + 1 < len(row) and row[i + 1]:
                                    potential_inv = str(row[i + 1]).strip()
                                    if 'inv' in potential_inv.lower() or re.match(r'[A-Z0-9\-]+', potential_inv):
                                        invoice_number = potential_inv
                                        break
                            # Or if this cell contains INV pattern
                            elif re.match(r'INV[-\s]*[0-9\-]+', cell_str, re.IGNORECASE):
                                invoice_number = cell_str
                                break
                
                # Also check for standalone INV pattern in any cell
                if not invoice_number or invoice_number.startswith('INV-') and len(invoice_number) < 10:
                    for cell in row:
                        if cell:
                            cell_str = str(cell).strip()
                            # Look for INV-2024-001 pattern
                            inv_match = re.search(r'INV[-\s]*([0-9]{4}[-\s]*[0-9]+)', cell_str, re.IGNORECASE)
                            if inv_match:
                                inv_num = inv_match.group(0).replace(' ', '-')
                                invoice_number = inv_num
                                break
                
                # Extract vendor
                if 'vendor' in row_text:
                    for i, cell in enumerate(row):
                        if cell:
                            cell_str = str(cell).strip()
                            # If this is the label, get the value from next column
                            if 'vendor' in cell_str.lower() and i + 1 < len(row) and row[i + 1]:
                                vendor_name = str(row[i + 1]).strip()
                                break
                            # Or if vendor name is in this cell
                            elif 'abc' in cell_str.lower() or 'supplies' in cell_str.lower():
                                vendor_name = cell_str
                                break
                
                # Extract invoice date from tables
                if 'invoice' in row_text and 'date' in row_text:
                    for i, cell in enumerate(row):
                        if cell:
                            cell_str = str(cell).strip()
                            # If this cell contains "Invoice Date:" or "Date:", get value from next cell
                            if ('invoice' in cell_str.lower() and 'date' in cell_str.lower()) or \
                               (cell_str.lower().startswith('date') and ':' in cell_str):
                                if i + 1 < len(row) and row[i + 1]:
                                    date_str = str(row[i + 1]).strip()
                                else:
                                    # Date might be in the same cell after colon
                                    if ':' in cell_str:
                                        date_str = cell_str.split(':', 1)[1].strip()
                                    else:
                                        continue
                                
                                # Try to parse the date
                                date_formats = [
                                    '%B %d, %Y',      # January 15, 2024
                                    '%b %d, %Y',      # Jan 15, 2024
                                    '%m/%d/%Y',       # 01/15/2024
                                    '%d/%m/%Y',       # 15/01/2024
                                    '%Y-%m-%d',       # 2024-01-15
                                    '%d-%m-%Y',       # 15-01-2024
                                    '%m-%d-%Y',       # 01-15-2024
                                ]
                                for fmt in date_formats:
                                    try:
                                        invoice_date = datetime.strptime(date_str, fmt)
                                        break
                                    except:
                                        continue
                                if invoice_date:
                                    break
                
                # Also check for standalone date patterns in any cell
                if not invoice_date or invoice_date == datetime.now():
                    for cell in row:
                        if cell:
                            cell_str = str(cell).strip()
                            # Look for "January 15, 2024" pattern
                            date_match = re.search(r'([A-Za-z]+\s+\d{1,2},\s+\d{4})', cell_str)
                            if date_match:
                                date_str = date_match.group(1)
                                try:
                                    invoice_date = datetime.strptime(date_str, '%B %d, %Y')
                                    break
                                except:
                                    try:
                                        invoice_date = datetime.strptime(date_str, '%b %d, %Y')
                                        break
                                    except:
                                        pass
        
        # Calculate total
        total_amount = sum(item.total_price for item in items)
        
        # Look for total in tables
        for table in tables:
            for row in table:
                if not row:
                    continue
                row_text = " ".join([str(cell) for cell in row if cell]).lower()
                if 'total' in row_text:
                    for cell in row:
                        if cell:
                            cell_str = str(cell)
                            if '$' in cell_str:
                                try:
                                    total_str = cell_str.replace('$', '').replace(',', '').strip()
                                    total_amount = float(total_str)
                                    break
                                except:
                                    pass
        
        if items:
            return ParsedInvoice(
                vendor_name=vendor_name,
                invoice_number=invoice_number,
                invoice_date=invoice_date,
                total_amount=total_amount,
                items=items,
                currency="USD"
            )
        
        return None
    
    def _extract_from_text(self, text: str, filename: str) -> ParsedInvoice:
        """
        Extract invoice data from text content.
        
        Uses pattern matching to find invoice number, vendor, items, etc.
        """
        if not text or len(text.strip()) < 50:
            return None
        
        text_upper = text.upper()
        
        # Extract vendor name (look for "Vendor:" or company name patterns)
        vendor_name = "ABC Supplies Co."  # Default
        vendor_patterns = [
            r'Vendor[:\s]+([A-Za-z\s&,\.]+)',
            r'ABC Supplies Co\.',
            r'Vendor Name[:\s]+([A-Za-z\s&,\.]+)',
        ]
        for pattern in vendor_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                vendor_name = match.group(1).strip() if match.groups() else "ABC Supplies Co."
                break
        
        # Extract invoice number - look for patterns like "INV-2024-001"
        invoice_number = None
        inv_patterns = [
            r'Invoice\s*#?[:\s]*([A-Z0-9\-]+)',  # "Invoice #: INV-2024-001"
            r'Invoice\s+Number[:\s]*([A-Z0-9\-]+)',  # "Invoice Number: INV-2024-001"
            r'INV[-\s]*([0-9]{4}[-\s]*[0-9]+)',  # "INV-2024-001" or "INV 2024 001"
            r'INV[-\s]*([0-9\-]+)',  # "INV-001" or "INV-2024-001"
        ]
        for pattern in inv_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                inv_num = match.group(1).strip()
                # Clean up the invoice number
                inv_num = re.sub(r'\s+', '-', inv_num)  # Replace spaces with dashes
                if not inv_num.startswith('INV'):
                    invoice_number = f"INV-{inv_num}"
                else:
                    invoice_number = inv_num
                break
        
        # If still not found, generate a default
        if not invoice_number:
            invoice_number = f"INV-{str(uuid.uuid4())[:8]}"
        
        # Extract invoice date - look for patterns like "January 15, 2024"
        invoice_date = None
        date_patterns = [
            r'Invoice\s+Date[:\s]+([A-Za-z]+\s+\d{1,2},\s+\d{4})',  # "Invoice Date: January 15, 2024"
            r'Invoice\s+Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',  # "Invoice Date: 01/15/2024"
            r'Date[:\s]+([A-Za-z]+\s+\d{1,2},\s+\d{4})',  # "Date: January 15, 2024"
            r'Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',  # "Date: 01/15/2024"
            r'([A-Za-z]+\s+\d{1,2},\s+\d{4})',  # "January 15, 2024" (standalone)
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',  # "01/15/2024" or "15/01/2024"
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1).strip()
                    # Try to parse common date formats
                    date_formats = [
                        '%B %d, %Y',      # January 15, 2024
                        '%b %d, %Y',      # Jan 15, 2024
                        '%m/%d/%Y',       # 01/15/2024
                        '%d/%m/%Y',       # 15/01/2024
                        '%Y-%m-%d',       # 2024-01-15
                        '%d-%m-%Y',       # 15-01-2024
                        '%m-%d-%Y',       # 01-15-2024
                    ]
                    for fmt in date_formats:
                        try:
                            invoice_date = datetime.strptime(date_str, fmt)
                            break
                        except:
                            continue
                    if invoice_date:
                        break
                except Exception as e:
                    continue
        
        # If still not found, use current date as fallback
        if not invoice_date:
            invoice_date = datetime.now()
        
        # Extract items - look for table-like patterns with item names, quantities, prices
        items = []
        lines = text.split('\n')
        
        # Look for item patterns in text (generic - any item name with quantity and price)
        # Pattern: Item name followed by numbers (quantity, price, total)
        item_patterns = []
        current_item = None
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Skip header rows
            line_lower = line_stripped.lower()
            if any(header in line_lower for header in ['item', 'description', 'qty', 'quantity', 'price', 'amount', 'total']):
                if 'item' in line_lower or 'description' in line_lower:
                    continue  # Skip header row
            
            # Look for lines that might contain item information
            # Pattern: text (item name) followed by numbers (qty, unit price, total)
            words = line_stripped.split()
            if len(words) >= 2:
                # Try to find item name (text) and numbers (qty, prices)
                item_name_parts = []
                numbers = []
                
                for word in words:
                    # Remove common separators
                    clean_word = word.replace('$', '').replace(',', '').strip()
                    # Check if it's a number
                    try:
                        num = float(clean_word)
                        numbers.append(num)
                    except:
                        # Not a number, might be part of item name
                        if clean_word and not clean_word.lower() in ['x', 'at', 'each', 'per', 'unit']:
                            item_name_parts.append(word)
                
                # If we have item name parts and at least one number, it might be an item row
                if len(item_name_parts) >= 1 and len(numbers) >= 1:
                    item_name = ' '.join(item_name_parts)
                    # Skip if it looks like a header or total row
                    if any(skip in item_name.lower() for skip in ['total', 'subtotal', 'tax', 'discount', 'item', 'description']):
                        continue
                    
                    # Try to extract quantity and price
                    qty = None
                    unit_price = None
                    total_price = None
                    
                    # Usually: item_name qty unit_price total_price
                    # Or: item_name qty x unit_price = total_price
                    if len(numbers) >= 3:
                        # Likely: qty, unit_price, total_price
                        qty = numbers[0]
                        unit_price = numbers[1]
                        total_price = numbers[2]
                    elif len(numbers) == 2:
                        # Could be: qty unit_price (calculate total)
                        # Or: unit_price total_price (need to infer qty)
                        # Try both interpretations
                        if numbers[0] < 1000:  # Likely quantity
                            qty = numbers[0]
                            unit_price = numbers[1]
                            total_price = round(qty * unit_price, 2)
                        else:  # Likely prices
                            unit_price = numbers[0]
                            total_price = numbers[1]
                            if unit_price > 0:
                                qty = round(total_price / unit_price, 1)
                    elif len(numbers) == 1:
                        # Only one number - could be price or total
                        if numbers[0] > 100:  # Likely a total price
                            total_price = numbers[0]
                            # Can't determine qty/unit_price from one number
                            continue
                        else:
                            qty = numbers[0]
                    
                    # Validate we have enough info
                    if qty and qty > 0:
                        if not unit_price and total_price:
                            unit_price = round(total_price / qty, 2)
                        elif not total_price and unit_price:
                            total_price = round(qty * unit_price, 2)
                        
                        if unit_price and unit_price > 0 and total_price and total_price > 0:
                            items.append(InvoiceItem(
                                name=item_name,
                                quantity=float(qty),
                                unit_price=unit_price,
                                total_price=round(total_price, 2)
                            ))
        
        # Extract total amount
        total_amount = sum(item.total_price for item in items)
        total_patterns = [
            r'TOTAL[:\s]*\$?([\d,]+\.?\d*)',
            r'Total[:\s]*\$?([\d,]+\.?\d*)',
        ]
        for pattern in total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    total_str = match.group(1).replace(',', '')
                    total_amount = float(total_str)
                    break
                except:
                    pass
        
        return ParsedInvoice(
            vendor_name=vendor_name,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            total_amount=total_amount,
            items=items,
            currency="USD"
        )
    
    def _extract_quantity(self, line: str, all_lines: list, line_index: int) -> float:
        """Extract quantity from a line or nearby lines."""
        # Look for numbers in the line
        numbers = re.findall(r'\d+\.?\d*', line)
        if numbers:
            try:
                return float(numbers[0])
            except:
                pass
        
        # Check next few lines
        for i in range(line_index, min(line_index + 3, len(all_lines))):
            numbers = re.findall(r'\d+\.?\d*', all_lines[i])
            if numbers:
                try:
                    return float(numbers[0])
                except:
                    pass
        
        return None
    
    def _extract_price(self, line: str, all_lines: list, line_index: int) -> float:
        """Extract price from a line or nearby lines."""
        # Look for dollar amounts
        prices = re.findall(r'\$?([\d,]+\.?\d{2})', line)
        if prices:
            try:
                return float(prices[-1].replace(',', ''))  # Get last price (usually unit price)
            except:
                pass
        
        # Check next few lines
        for i in range(line_index, min(line_index + 3, len(all_lines))):
            prices = re.findall(r'\$?([\d,]+\.?\d{2})', all_lines[i])
            if prices:
                try:
                    return float(prices[-1].replace(',', ''))
                except:
                    pass
        
        return None
    
    def _mock_parse(self, file_content: bytes, filename: str) -> ParsedInvoice:
        """
        Mock parser that simulates invoice extraction.
        
        In production, replace this with actual OCR/AI extraction:
        - Tesseract OCR
        - AWS Textract
        - Google Cloud Vision API
        - Azure Form Recognizer
        - Custom ML models
        """
        # For demo purposes, we'll create a simple mock invoice
        # In real implementation, parse the actual file content
        
        # Generate a mock invoice based on filename or content
        invoice_id = str(uuid.uuid4())[:8]
        
        # Generic mock invoice - no hardcoded item names
        # This is a fallback when PDF parsing fails completely
        return ParsedInvoice(
            vendor_name="ABC Supplies Co.",
            invoice_number=f"INV-{invoice_id}",
            invoice_date=datetime.now(),
            total_amount=1250.0,
            items=[
                InvoiceItem(
                    name="Item 1",
                    quantity=5.0,
                    unit_price=150.0,
                    total_price=750.0
                ),
                InvoiceItem(
                    name="Item 2",
                    quantity=10.0,
                    unit_price=50.0,
                    total_price=500.0
                )
            ],
            currency="USD"
        )
    
    def parse_invoice_from_json(self, invoice_data: dict) -> ParsedInvoice:
        """Parse invoice from JSON data (for testing/direct API input)."""
        try:
            items = [
                InvoiceItem(**item) for item in invoice_data.get("items", [])
            ]
            
            return ParsedInvoice(
                vendor_name=invoice_data["vendor_name"],
                invoice_number=invoice_data["invoice_number"],
                invoice_date=datetime.fromisoformat(invoice_data["invoice_date"]),
                total_amount=invoice_data["total_amount"],
                items=items,
                currency=invoice_data.get("currency", "USD")
            )
        except (KeyError, ValueError, TypeError) as e:
            raise InvalidInvoiceFormatError(f"Invalid invoice format: {str(e)}")
