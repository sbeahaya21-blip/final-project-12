# Run Real UI Test (No Mocks – Talks to ERPNext)

This runs the user journey test against your **real** backend and **real** ERPNext. The test uploads a sample invoice, then submits it to ERPNext; the invoice will appear in ERPNext (e.g. Accounting → Purchase Invoice).

## 1. Prerequisites

- **Backend** can reach ERPNext (same machine or network).
- **.env** in the project root with ERPNext credentials:

  ```env
  ERPNEXT_BASE_URL=http://localhost:8080
  ERPNEXT_API_KEY=your_api_key
  ERPNEXT_API_SECRET=your_api_secret
  ```

- **Playwright:** `pip install pytest-playwright` and `playwright install`.

## 2. Start Everything

**Terminal 1 – Backend**

```bash
cd "c:\Users\Admin\Desktop\final project"
python run.py
```

(Backend runs at http://localhost:8000.)

**Terminal 2 – Frontend**

```bash
cd "c:\Users\Admin\Desktop\final project\frontend"
npm run dev
```

(Frontend runs at http://localhost:3000 and proxies API to the backend.)

**ERPNext** must be running (e.g. http://localhost:8080) and the API key/secret must be valid.

## 3. Run the Real UI Test

From the project root:

**PowerShell:**

```powershell
cd "c:\Users\Admin\Desktop\final project"
$env:BASE_URL="http://localhost:3000"
$env:LIVE_ERPNEXT="1"
pytest tests/ui/test_user_journey.py::test_user_journey_upload_view_risk_and_submit_to_erpnext -v --headed
```

**CMD:**

```cmd
cd "c:\Users\Admin\Desktop\final project"
set BASE_URL=http://localhost:3000
set LIVE_ERPNEXT=1
pytest tests/ui/test_user_journey.py::test_user_journey_upload_view_risk_and_submit_to_erpnext -v --headed
```

**Or use the script:**

```cmd
run_real_ui_test.bat
```

- `BASE_URL` = your frontend URL (so the test opens the real app).
- `LIVE_ERPNEXT=1` = no mocks; the test uses the real backend and ERPNext.
- `--headed` = browser window opens so you can watch the flow.

## 4. What the Test Does

1. Opens http://localhost:3000/ (upload page).
2. Uploads `sample_invoices/pdf/sample_invoice_1.pdf` to your backend.
3. Waits for results and risk explanation.
4. Clicks “View Details”.
5. Clicks “Submit to ERPNext” and accepts the confirm dialog.
6. Asserts “Submitted to ERPNext” and that the risk explanation is shown.

The new Purchase Invoice will appear in ERPNext (Accounting → Purchase Invoice).

## 5. If the Backend Serves the Built Frontend (No Vite)

If you use the built frontend at http://localhost:8000 (no separate Vite):

```powershell
$env:BASE_URL="http://localhost:8000"
$env:LIVE_ERPNEXT="1"
pytest tests/ui/test_user_journey.py::test_user_journey_upload_view_risk_and_submit_to_erpnext -v --headed
```

Build first: `cd frontend && npm run build`, then start the backend.
