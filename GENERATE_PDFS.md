# Generate PDF Invoices

## Quick Start

To generate PDF invoices from the JSON files, run:

```bash
python generate_pdf_invoices.py
```

This will create PDF files in `sample_invoices/pdf/` directory.

## Requirements

Make sure you have installed:
```bash
pip install reportlab
```

## Output

The script will generate:
- `sample_invoices/pdf/sample_invoice_1.pdf`
- `sample_invoices/pdf/sample_invoice_2.pdf`
- `sample_invoices/pdf/sample_invoice_3.pdf`
- `sample_invoices/pdf/sample_invoice_4.pdf`
- `sample_invoices/pdf/sample_invoice_5.pdf`
- `sample_invoices/pdf/sample_invoice_6_ANOMALOUS.pdf`

## Usage

After generating PDFs, you can:

1. **Upload via Frontend UI:**
   - Start frontend: `cd frontend && npm run dev`
   - Go to http://localhost:3000
   - Drag and drop the PDF files

2. **Upload via API:**
   ```bash
   curl -X POST http://localhost:8000/api/invoices/upload \
     -F "file=@sample_invoices/pdf/sample_invoice_1.pdf"
   ```

3. **Upload via Python:**
   ```python
   import requests
   
   with open('sample_invoices/pdf/sample_invoice_1.pdf', 'rb') as f:
       files = {'file': f}
       response = requests.post('http://localhost:8000/api/invoices/upload', files=files)
       print(response.json())
   ```

## Troubleshooting

If you get "No such file or directory":
- Make sure you're in the project root directory
- Check that `sample_invoices/` folder exists
- Verify JSON files are present

If reportlab is not installed:
```bash
pip install reportlab
```
