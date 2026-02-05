# Integration Tests

Integration tests that run against **real backend and ERPNext** (no mocks). These tests verify end-to-end functionality.

## Requirements

- **Backend** running at `http://localhost:8000` (or set `BACKEND_URL` env var)
- **ERPNext** running and accessible (default: `http://localhost:8080`, or set `ERPNEXT_BASE_URL` env var)
- **ERPNext API credentials** configured in `.env`:
  - `ERPNEXT_BASE_URL`
  - `ERPNEXT_API_KEY`
  - `ERPNEXT_API_SECRET`
- **Sample PDF** at `sample_invoices/pdf/sample_invoice_1.pdf`

## Running Integration Tests

### Prerequisites

1. **Start backend:**
   ```bash
   python run.py
   ```

2. **Start ERPNext** (if testing ERPNext integration)

3. **Verify services are running:**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8080/api/method/ping
   ```

### Run All Integration Tests

```bash
pytest tests/integration/ -v
```

### Run Specific Test Classes

```bash
# Test invoice upload/retrieval only
pytest tests/integration/test_invoice_integration.py::TestInvoiceUploadIntegration -v

# Test ERPNext integration only
pytest tests/integration/test_invoice_integration.py::TestERPNextIntegration -v

# Test full workflow
pytest tests/integration/test_invoice_integration.py::TestFullWorkflowIntegration -v
```

### Custom Backend/ERPNext URLs

```bash
BACKEND_URL=http://localhost:8000 ERPNEXT_BASE_URL=http://localhost:8080 pytest tests/integration/ -v
```

## What's Tested

### TestInvoiceUploadIntegration
- Upload PDF invoice file
- Create invoice via JSON API
- Retrieve invoice after upload
- List all invoices

### TestERPNextIntegration
- Submit invoice to ERPNext
- Handle already-submitted invoices

### TestFullWorkflowIntegration
- Complete lifecycle: upload → parse → view → submit to ERPNext

## Notes

- Tests **skip automatically** if backend or ERPNext is not available
- Tests use **real HTTP requests** (no TestClient mocks)
- Tests verify **real ERPNext integration** (invoices are actually created in ERPNext)
- Tests are **idempotent** - can be run multiple times safely
