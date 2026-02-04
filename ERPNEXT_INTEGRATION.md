# ERPNext Integration Guide

This document explains how to integrate this Invoice Parser and Anomaly Detection skill with ERPNext.

## Overview

This skill is designed as an **external HTTP service** that ERPNext can call via REST API. ERPNext communicates with the skill using HTTP requests only - no direct Python imports or function calls.

## Architecture

```
ERPNext System                    Invoice Parser Skill
     |                                    |
     |  HTTP POST /analyze-invoice        |
     |  { "invoice_id": "PINV-0001" }     |
     |----------------------------------->|
     |                                    |
     |  HTTP GET /api/resource/           |
     |  Purchase Invoice/PINV-0001         |
     |<-----------------------------------|
     |                                    |
     |  HTTP GET /api/resource/           |
     |  Purchase Invoice?supplier=...      |
     |<-----------------------------------|
     |                                    |
     |  Analysis Results                  |
     |  { "risk_score": 82, ... }        |
     |<-----------------------------------|
     |                                    |
```

## Setup

### 1. Configure Environment Variables

Set these environment variables on the server where the skill runs:

```bash
export ERPNEXT_BASE_URL="https://your-instance.erpnext.com"
export ERPNEXT_API_KEY="your_api_key"
export ERPNEXT_API_SECRET="your_api_secret"
```

**How to get API credentials in ERPNext:**

1. Log in to ERPNext
2. Go to **Settings** → **Integrations** → **API Keys**
3. Create a new API Key
4. Copy the **API Key** and **API Secret**

### 2. Deploy the Skill

The skill should be deployed and accessible via HTTP. For example:

- Local development: `http://localhost:8000`
- Production: `https://your-skill-server.com`

### 3. Configure ERPNext to Call the Skill

In ERPNext, you can set up a webhook or custom script to call the skill when a Purchase Invoice is submitted.

**Example ERPNext Python script (Client Script):**

```python
# Trigger: Before Save, DocType: Purchase Invoice

import requests
import json

# Your skill endpoint
skill_url = "http://your-skill-server.com/api/erpnext/analyze-invoice"

# Prepare request
payload = {
    "invoice_id": doc.name  # e.g., "PINV-0001"
}

try:
    response = requests.post(
        skill_url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    response.raise_for_status()
    
    result = response.json()
    
    # Handle the result
    if result.get("status") == "suspicious":
        frappe.msgprint(
            f"⚠️ Anomaly Detected! Risk Score: {result.get('risk_score')}/100\n\n"
            + "\n".join(result.get("reasons", []))
        )
        # Optionally, add custom field to store risk score
        # doc.custom_risk_score = result.get("risk_score")
        # doc.custom_is_suspicious = True
        
except Exception as e:
    frappe.log_error(f"Failed to analyze invoice: {str(e)}")
    # Don't block invoice creation if skill is unavailable
```

**Or use ERPNext Webhook:**

1. Go to **Settings** → **Integrations** → **Webhooks**
2. Create a new webhook:
   - **Webhook Type**: Outgoing
   - **Request URL**: `http://your-skill-server.com/api/erpnext/analyze-invoice`
   - **Request Method**: POST
   - **Request Body**: 
     ```json
     {
       "invoice_id": "{{ doc.name }}"
     }
     ```
   - **Trigger**: On Submit (Purchase Invoice)

## API Endpoint

### POST /api/erpnext/analyze-invoice

Analyzes an ERPNext purchase invoice for anomalies.

**Request:**
```json
{
  "invoice_id": "PINV-0001"
}
```

**Response:**
```json
{
  "risk_score": 82,
  "status": "suspicious",
  "reasons": [
    "⚠️ HIGH RISK (Score: 82/100)",
    "Detected 3 anomaly/ies:",
    "1. Price increased by 45.2% (from avg $150.00 to $217.80)",
    "2. Quantity is 150.0% above average (avg: 5.0, current: 12.5)",
    "3. New item 'Premium Desk Chair' never seen before for this vendor"
  ],
  "invoice_id": "PINV-0001",
  "vendor_name": "ABC Supplies Co."
}
```

**Response Fields:**
- `risk_score` (int): Risk score from 0-100
- `status` (str): "normal" or "suspicious"
- `reasons` (list): Human-readable list of detected anomalies
- `invoice_id` (str): The analyzed invoice ID
- `vendor_name` (str): Supplier/vendor name

## How It Works

1. **ERPNext sends request**: ERPNext calls `/api/erpnext/analyze-invoice` with `invoice_id`

2. **Skill fetches invoice**: The skill uses ERPNext REST API to fetch:
   - Invoice details (items, quantities, prices, totals)
   - Supplier name
   - Invoice date

3. **Skill fetches history**: The skill fetches historical invoices from the same supplier:
   - Up to 100 most recent invoices
   - Excludes the current invoice being analyzed

4. **Anomaly detection**: The skill analyzes:
   - **Price increases**: Items with >20% price increase vs. historical average
   - **Quantity deviations**: Items with >2x average quantity or >1.5x historical maximum
   - **New items**: Items never seen before for this supplier
   - **Amount deviations**: Total amount >30% deviation from historical average

5. **Risk scoring**: Calculates overall risk score (0-100):
   - Base score from individual anomaly severities
   - Multiplier for multiple anomalies
   - Status: "suspicious" if score ≥ 50

6. **Response**: Returns formatted results with human-readable explanations

## Testing

### Test the Skill Directly

```bash
curl -X POST "http://localhost:8000/api/erpnext/analyze-invoice" \
  -H "Content-Type: application/json" \
  -d '{"invoice_id": "PINV-0001"}'
```

### Check ERPNext Connection

```bash
curl "http://localhost:8000/api/erpnext/health"
```

**Response:**
```json
{
  "configured": true,
  "base_url": "https://your-instance.erpnext.com",
  "status": "connected"
}
```

## Error Handling

The skill handles various error scenarios:

- **ERPNext not configured**: Returns 500 error with configuration message
- **Invoice not found**: Returns 400 error with details
- **ERPNext API error**: Returns 400 error with API error message
- **Analysis error**: Returns 500 error with error details

ERPNext should handle these errors gracefully and not block invoice processing if the skill is unavailable.

## Security Considerations

1. **API Authentication**: The skill uses ERPNext API Key/Secret for authentication
2. **HTTPS**: Use HTTPS in production to encrypt communication
3. **Network Security**: Consider firewall rules to restrict access
4. **Rate Limiting**: Consider implementing rate limiting for production use

## Troubleshooting

### Skill can't connect to ERPNext

- Verify `ERPNEXT_BASE_URL` is correct
- Verify API Key and Secret are valid
- Check network connectivity between skill server and ERPNext
- Check ERPNext API access permissions

### ERPNext can't reach the skill

- Verify skill is running and accessible
- Check firewall rules
- Verify URL is correct in ERPNext configuration
- Check CORS settings if calling from browser

### Analysis returns incorrect results

- Verify invoice data is correctly parsed from ERPNext
- Check historical invoices are being fetched correctly
- Review anomaly detection thresholds in `app/services/anomaly_service.py`

## Support

For issues or questions, check:
- API documentation: `http://your-skill-server.com/docs`
- Logs: Check application logs for detailed error messages
