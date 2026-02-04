# How to Generate PDF Invoices

## Method 1: Using the Batch File (Easiest - Windows)

### Step-by-Step:

1. **Open File Explorer**
   - Navigate to your project folder: `C:\Users\Admin\Desktop\אוטומציה\final project`

2. **Double-click the file**
   - Find `run_generate_pdfs.bat` in the folder
   - Double-click it
   - A command window will open and run the script

3. **Wait for completion**
   - You'll see messages like "Generating PDF Invoices..."
   - When done, it will say "PDF invoices generated successfully!"
   - Press any key to close the window

4. **Find your PDFs**
   - Go to: `sample_invoices\pdf\` folder
   - You'll find 6 PDF files ready to upload!

---

## Method 2: Using Command Line (Git Bash or PowerShell)

### Step-by-Step:

1. **Open Git Bash or PowerShell**
   - Right-click in the project folder
   - Select "Git Bash Here" or "Open PowerShell here"

2. **Run the command:**
   ```bash
   python generate_pdf_invoices.py
   ```

3. **If you get an error about reportlab:**
   ```bash
   pip install reportlab
   ```
   Then run the script again:
   ```bash
   python generate_pdf_invoices.py
   ```

4. **Check the output:**
   - You should see: "✅ Generated 6 PDF invoice(s)"
   - PDFs will be in: `sample_invoices/pdf/`

---

## Method 3: Using Python Directly

### Step-by-Step:

1. **Open Command Prompt or Terminal**
   - Press `Win + R`
   - Type `cmd` and press Enter
   - Or open PowerShell

2. **Navigate to project folder:**
   ```bash
   cd "C:\Users\Admin\Desktop\אוטומציה\final project"
   ```

3. **Install reportlab (if needed):**
   ```bash
   pip install reportlab
   ```

4. **Run the script:**
   ```bash
   python generate_pdf_invoices.py
   ```

---

## Troubleshooting

### "python is not recognized"
- Python might not be in PATH
- Try: `py generate_pdf_invoices.py` instead
- Or use the full path to Python

### "reportlab not found"
- Install it: `pip install reportlab`
- Or: `python -m pip install reportlab`

### "No such file or directory"
- Make sure you're in the project root folder
- Check that `sample_invoices/` folder exists
- Verify JSON files are present

### Batch file doesn't work
- Right-click `run_generate_pdfs.bat`
- Select "Run as administrator"
- Or use Method 2 (command line) instead

---

## What You'll Get

After running, you'll have 6 PDF files:

✅ **Normal Invoices (1-5):**
- `sample_invoice_1.pdf` - $1,250.00
- `sample_invoice_2.pdf` - $1,300.00
- `sample_invoice_3.pdf` - $1,200.00
- `sample_invoice_4.pdf` - $1,275.00
- `sample_invoice_5.pdf` - $1,280.00

⚠️ **Anomalous Invoice (6):**
- `sample_invoice_6_ANOMALOUS.pdf` - $3,500.00

All saved in: `sample_invoices\pdf\` folder

---

## Next Steps

After generating PDFs:

1. **Start the backend server:**
   ```bash
   python run.py
   ```

2. **Upload PDFs via Frontend:**
   - Start frontend: `cd frontend && npm run dev`
   - Go to: http://localhost:3000
   - Drag and drop the PDF files

3. **Or upload via API:**
   ```bash
   curl -X POST http://localhost:8000/api/invoices/upload \
     -F "file=@sample_invoices/pdf/sample_invoice_1.pdf"
   ```
