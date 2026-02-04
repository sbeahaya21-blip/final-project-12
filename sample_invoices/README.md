# Sample Invoices for Testing

This directory contains sample invoice files for testing the Invoice Parser and Anomaly Detection system.

## Invoice Files

### Normal Invoices (1-5)
These are 5 normal invoices from the same supplier (ABC Supplies Co.) with similar but slightly different details:

- **sample_invoice_1.json** - $1,250.00 (5 chairs, 10 lamps)
- **sample_invoice_2.json** - $1,300.00 (6 chairs, 8 lamps)
- **sample_invoice_3.json** - $1,200.00 (4 chairs, 12 lamps)
- **sample_invoice_4.json** - $1,275.00 (5 chairs, 10.5 lamps)
- **sample_invoice_5.json** - $1,280.00 (5 chairs, 10.6 lamps)

### Anomalous Invoice (6)
**sample_invoice_6_ANOMALOUS.json** - $3,500.00

This invoice contains multiple anomalies:
- ⚠️ **Price Increase**: Office Chairs price increased from $150 to $250 (67% increase)
- ⚠️ **Quantity Deviation**: Desk Lamps quantity is 25 (normal is ~10, which is 2.5x)
- ⚠️ **New Item**: "Premium Monitor Stand" - never appeared in previous invoices
- ⚠️ **Amount Deviation**: Total is $3,500 vs normal ~$1,250 (180% increase)

## How to Use

### Option 1: Use the Python Script (Recommended)

```bash
# Make sure backend is running first
python run.py

# In another terminal, run:
python create_sample_invoices.py
```

This will create all 6 invoices via the API and automatically analyze the anomalous one.

### Option 2: Upload via API

You can use the JSON files with the API:

```bash
# Create invoice from JSON
curl -X POST http://localhost:8000/api/invoices/create \
  -H "Content-Type: application/json" \
  -d @sample_invoices/sample_invoice_1.json
```

### Option 3: Upload via Frontend UI

1. Start the frontend: `cd frontend && npm run dev`
2. Go to http://localhost:3000
3. Upload the JSON files (they'll be parsed as text files)

### Option 4: Use Python Script with Files

```python
import requests
import json

with open('sample_invoices/sample_invoice_1.json') as f:
    invoice_data = json.load(f)
    response = requests.post('http://localhost:8000/api/invoices/create', json=invoice_data)
    print(response.json())
```

## Expected Results

After uploading invoices 1-5 (normal), they should have:
- Low risk scores (< 50)
- No anomalies detected
- Marked as "SAFE"

After uploading invoice 6 (anomalous), it should have:
- High risk score (≥ 70)
- Multiple anomalies detected
- Marked as "⚠️ SUSPICIOUS"
- Detailed explanation of why it's suspicious

## Testing Scenarios

1. **Upload invoices 1-5 first** - These establish the baseline
2. **Upload invoice 6** - This should trigger all anomaly detection rules
3. **Check the analysis** - View the risk score and explanations
4. **Try variations** - Modify invoice 6 to test different anomaly types
