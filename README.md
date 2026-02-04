# Invoice Parser and AI Invoice Anomaly & Fraud Detection

A FastAPI-based system for parsing invoices and detecting anomalies and potential fraud by comparing against historical invoice data.

## Features

- **Invoice Parsing**: OCR/AI extraction of invoice data
- **Anomaly Detection**: 
  - Sudden price increases
  - Unreasonable quantities
  - New items detection
  - Total amount deviations
- **Risk Scoring**: 0-100 risk score with human-readable explanations
- **RESTful API**: FastAPI-based endpoints
- **Web UI**: Simple interface for invoice upload and viewing results
- **Comprehensive Testing**: API tests, UI tests with Playwright, CI/CD pipeline

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── models/                 # Data models (MVC)
│   │   ├── __init__.py
│   │   ├── invoice.py
│   │   └── anomaly.py
│   ├── views/                  # API endpoints (MVC)
│   │   ├── __init__.py
│   │   └── invoice_views.py
│   ├── controllers/            # Business logic (MVC)
│   │   ├── __init__.py
│   │   ├── invoice_controller.py
│   │   └── anomaly_controller.py
│   ├── services/               # Service layer
│   │   ├── __init__.py
│   │   ├── parser_service.py
│   │   ├── anomaly_service.py
│   │   └── storage_service.py
│   └── exceptions.py           # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── test_invoice_api.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── pages/
│   │   │   ├── __init__.py
│   │   │   └── invoice_page.py
│   │   └── test_invoice_ui.py
│   └── conftest.py
├── frontend/                    # React frontend application
│   ├── src/                     # Source files
│   │   ├── pages/               # Page components
│   │   ├── services/            # API service layer
│   │   └── App.tsx              # Main app component
│   ├── package.json
│   └── vite.config.ts
├── static/                      # Built frontend (generated)
│   └── index.html
├── .github/
│   └── workflows/
│       └── ci.yml
├── pytest.ini
├── requirements.txt
└── README.md

```

## Installation

### Backend

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers (for UI tests):
```bash
playwright install
```

### Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Build the frontend:
```bash
npm run build
```

This will build the React app into the `static` directory.

## Running the Application

### Development Mode

**Backend:**
```bash
uvicorn app.main:app --reload
# or
python run.py
```

**Frontend (separate terminal):**
```bash
cd frontend
npm run dev
```

- Backend API: `http://localhost:8000`
- Frontend (dev): `http://localhost:3000` (proxies to backend)

### Production Mode

1. Build the frontend:
```bash
cd frontend
npm run build
```

2. Run the backend:
```bash
uvicorn app.main:app
```

- Full application: `http://localhost:8000`
- API: `http://localhost:8000/api`
- Frontend: `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run with Allure
pytest --alluredir=allure-results
allure serve allure-results
```

## API Endpoints

### Invoice Management (Standalone)
- `POST /api/invoices/upload` - Upload and parse an invoice
- `GET /api/invoices/{invoice_id}` - Get invoice details
- `GET /api/invoices` - List all invoices
- `POST /api/invoices/{invoice_id}/analyze` - Analyze invoice for anomalies
- `DELETE /api/invoices/{invoice_id}` - Delete an invoice

### ERPNext Integration
- `POST /api/erpnext/analyze-invoice` - Analyze ERPNext purchase invoice for anomalies
  - **Input**: `{ "invoice_id": "PINV-0001" }`
  - **Output**: `{ "risk_score": 82, "status": "suspicious", "reasons": [...], "invoice_id": "PINV-0001", "vendor_name": "ABC Supplies Co." }`
- `GET /api/erpnext/health` - Check ERPNext integration health

## ERPNext Integration Setup

This skill is designed to work as an external HTTP service that ERPNext can call via REST API.

### Configuration

Set the following environment variables:

```bash
export ERPNEXT_BASE_URL="https://your-instance.erpnext.com"
export ERPNEXT_API_KEY="your_api_key"
export ERPNEXT_API_SECRET="your_api_secret"
```

Or create a `.env` file:

```env
ERPNEXT_BASE_URL=https://your-instance.erpnext.com
ERPNEXT_API_KEY=your_api_key
ERPNEXT_API_SECRET=your_api_secret
```

### How It Works

1. **ERPNext calls the skill**: ERPNext sends an HTTP POST request to `/api/erpnext/analyze-invoice` with a `purchase_invoice_id`
2. **Skill fetches invoice**: The skill uses ERPNext REST API to fetch the invoice details
3. **Skill fetches history**: The skill fetches historical invoices from the same supplier
4. **Anomaly analysis**: The skill analyzes for:
   - Sudden price increases per item
   - Unusual quantities compared to history
   - New items never seen before
   - Total amount deviations
5. **Response**: Returns risk score (0-100), status (normal/suspicious), and human-readable reasons

### Example Usage

```bash
curl -X POST "http://localhost:8000/api/erpnext/analyze-invoice" \
  -H "Content-Type: application/json" \
  -d '{"invoice_id": "PINV-0001"}'
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
    "3. New item 'Premium Desk Chair' never seen before for this vendor (value: $500.00, 20.0% of total)"
  ],
  "invoice_id": "PINV-0001",
  "vendor_name": "ABC Supplies Co."
}
```

### Architecture

The skill follows MVC architecture:

- **API Layer** (`app/views/erpnext_views.py`): FastAPI endpoints
- **Service Layer** (`app/services/erpnext_client.py`): ERPNext API communication
- **Business Logic** (`app/services/anomaly_service.py`): Anomaly detection logic
- **Models** (`app/models/`): Data models

All communication is via HTTP REST APIs - no direct Python imports or function calls.