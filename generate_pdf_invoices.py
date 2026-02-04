"""Generate PDF invoices from JSON data."""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import json
from pathlib import Path
from datetime import datetime

def create_pdf_invoice(json_file_path, output_path):
    """Create a PDF invoice from JSON data."""
    # Load JSON data
    with open(json_file_path, 'r') as f:
        invoice_data = json.load(f)
    
    # Create PDF
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2490ef'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12
    )
    
    # Title
    story.append(Paragraph("INVOICE", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Invoice details table
    invoice_info = [
        ['Invoice Number:', invoice_data['invoice_number']],
        ['Invoice Date:', datetime.fromisoformat(invoice_data['invoice_date']).strftime('%B %d, %Y')],
        ['Vendor:', invoice_data['vendor_name']],
    ]
    
    info_table = Table(invoice_info, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6c757d')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#212529')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 0.4*inch))
    
    # Items table
    story.append(Paragraph("Items", heading_style))
    
    # Table data
    table_data = [['Item Name', 'Quantity', 'Unit Price', 'Total']]
    
    for item in invoice_data['items']:
        # Format quantity - show as integer if it's a whole number, otherwise show decimals
        qty = item['quantity']
        if qty == int(qty):
            qty_str = f"{int(qty)}"
        else:
            qty_str = f"{qty:.2f}"
        
        table_data.append([
            item['name'],
            qty_str,
            f"${item['unit_price']:.2f}",
            f"${item['total_price']:.2f}"
        ])
    
    # Add total row
    table_data.append(['', '', 'TOTAL:', f"${invoice_data['total_amount']:.2f}"])
    
    items_table = Table(table_data, colWidths=[3.5*inch, 1*inch, 1.2*inch, 1.3*inch])
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#212529')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 10),
        ('TEXTCOLOR', (0, 1), (-1, -2), colors.HexColor('#212529')),
        ('ALIGN', (0, 1), (0, -2), 'LEFT'),  # Item name left
        ('ALIGN', (1, 1), (-1, -2), 'RIGHT'),  # Numbers right
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 10),
        ('TOPPADDING', (0, 1), (-1, -2), 10),
        ('GRID', (0, 0), (-1, -2), 1, colors.HexColor('#dee2e6')),
        
        # Total row
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#212529')),
        ('ALIGN', (0, -1), (2, -1), 'RIGHT'),
        ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('TOPPADDING', (0, -1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#2490ef')),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Footer note if anomalous
    if 'note' in invoice_data:
        note_style = ParagraphStyle(
            'Note',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#dc3545'),
            fontName='Helvetica-Oblique',
            alignment=TA_CENTER
        )
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(invoice_data['note'], note_style))
    
    # Build PDF
    doc.build(story)
    print(f"✓ Created: {output_path}")

def main():
    """Generate all PDF invoices."""
    print("=" * 60)
    print("Generating PDF Invoices")
    print("=" * 60)
    print()
    
    # Get the script's directory
    script_dir = Path(__file__).parent
    sample_dir = script_dir / "sample_invoices"
    pdf_dir = sample_dir / "pdf"
    pdf_dir.mkdir(exist_ok=True)
    
    # Find all JSON files
    json_files = sorted(sample_dir.glob("sample_invoice_*.json"))
    
    if not json_files:
        print("⚠️  No JSON invoice files found!")
        return
    
    print(f"Found {len(json_files)} invoice file(s)\n")
    
    for json_file in json_files:
        pdf_name = json_file.stem + ".pdf"
        pdf_path = pdf_dir / pdf_name
        create_pdf_invoice(json_file, pdf_path)
    
    print()
    print("=" * 60)
    print(f"✅ Generated {len(json_files)} PDF invoice(s)")
    print("=" * 60)
    print(f"\nPDF files saved to: {pdf_dir}")
    print("\nYou can now upload these PDFs via:")
    print("1. Frontend UI: http://localhost:3000")
    print("2. API endpoint: POST /api/invoices/upload")

if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print("⚠️  reportlab library is required!")
        print("\nPlease install it:")
        print("  pip install reportlab")
        print("\nThen run this script again.")
